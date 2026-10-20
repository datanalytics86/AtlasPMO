"""Working-time clock. Instants are naive and truncated to the minute."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timedelta

from atlaspmo.calendars.data import ParsedCalendar


class CalendarLimitError(Exception):
    """The walk passed the horizon without placing the remaining work."""


class WorkCalendar:
    """One calendar. Exceptions replace the weekday; they do not add to it."""

    def __init__(
        self,
        week: Mapping[int, tuple[tuple[int, int], ...]],
        exceptions: Mapping[date, tuple[tuple[int, int], ...]] | None = None,
    ) -> None:
        self._week = {day: tuple(shifts) for day, shifts in week.items()}
        self._exceptions = dict(exceptions or {})

    @classmethod
    def from_parsed(cls, parsed: ParsedCalendar) -> WorkCalendar:
        return cls(parsed.by_weekday, parsed.exceptions)

    def shifts_on(self, day: date) -> tuple[tuple[int, int], ...]:
        if day in self._exceptions:
            return self._exceptions[day]
        return self._week.get(day.weekday(), ())

    def add_work(self, instant: datetime, minutes: int) -> datetime:
        """Move forward by working minutes. Zero minutes snaps to the next shift."""
        if minutes < 0:
            return self.subtract_work(instant, -minutes)
        day = instant.date()
        minute = _minute_of(instant)
        left = minutes
        for _step in range(3660):
            for begin, finish in self.shifts_on(day):
                if minute < begin:
                    minute = begin
                if minute >= finish:
                    continue
                room = finish - minute
                if left == 0:
                    return _stamp(day, minute)
                if left <= room:
                    return _stamp(day, minute + left)
                left -= room
                minute = finish
                if left == 0:
                    return _stamp(day, minute)
            day += timedelta(days=1)
            minute = 0
        raise CalendarLimitError("horizonte de calendario agotado")

    def subtract_work(self, instant: datetime, minutes: int) -> datetime:
        """Move backward by working minutes. Zero minutes stays on a work instant."""
        if minutes < 0:
            return self.add_work(instant, -minutes)
        day = instant.date()
        minute = _minute_of(instant)
        left = minutes
        for _step in range(3660):
            if left == 0:
                for begin, finish in self.shifts_on(day):
                    if begin <= minute <= finish:
                        return _stamp(day, minute)
                prior = [finish for _begin, finish in self.shifts_on(day) if finish < minute]
                if prior:
                    return _stamp(day, max(prior))
            else:
                window: tuple[int, int] | None = None
                for begin, finish in self.shifts_on(day):
                    edge = min(minute, finish)
                    if edge > begin:
                        window = (begin, edge)
                if window is not None:
                    begin, edge = window
                    available = edge - begin
                    if left <= available:
                        return _stamp(day, edge - left)
                    left -= available
                    minute = begin
                    continue
            day -= timedelta(days=1)
            minute = 24 * 60
        raise CalendarLimitError("horizonte de calendario agotado")

    def work_between(self, start: datetime, end: datetime) -> int:
        """Working minutes from start to end. A backward span is negative."""
        start_day, start_min = start.date(), _minute_of(start)
        end_day, end_min = end.date(), _minute_of(end)
        if (end_day, end_min) == (start_day, start_min):
            return 0
        if (end_day, end_min) < (start_day, start_min):
            return -self.work_between(end, start)
        total = 0
        day = start_day
        for _step in range(3660):
            origin = start_min if day == start_day else 0
            limit = end_min if day == end_day else 24 * 60
            for begin, finish in self.shifts_on(day):
                left = max(begin, origin)
                right = min(finish, limit)
                if right > left:
                    total += right - left
            if day == end_day:
                return total
            day += timedelta(days=1)
        raise CalendarLimitError("horizonte de calendario agotado")


def elapsed_calendar() -> WorkCalendar:
    """Clock time, 24 hours every day. Used only for an elapsed lag."""
    full = ((0, 24 * 60),)
    return WorkCalendar({day: full for day in range(7)})


def _minute_of(instant: datetime) -> int:
    return instant.hour * 60 + instant.minute


def _stamp(day: date, minute: int) -> datetime:
    return datetime(day.year, day.month, day.day, minute // 60, minute % 60)
