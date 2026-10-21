"""Working-time clock. Instants are naive and truncated to the minute.

``add_work``, ``subtract_work`` and ``work_between`` use an accumulated
working-minute index. A probe is O(log n) in the distance from the epoch
plus O(log E) in the exception list. The horizon grows with the request.
There is no fixed day cap. A calendar with no working time still raises
``CalendarLimitError``.
"""

from __future__ import annotations

import bisect
from collections.abc import Mapping
from datetime import date, datetime, timedelta

from atlaspmo.calendars.data import ParsedCalendar

# Monday, so weekday prefixes line up with datetime.weekday().
_EPOCH = date(1, 1, 1)
_DAY_MINUTES = 24 * 60
_MAX_OFFSET = (date.max - _EPOCH).days * _DAY_MINUTES + (_DAY_MINUTES - 1)
_HORIZON = "horizonte de calendario agotado"


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
        self._build_index()

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
        day, minute = instant.date(), _minute_of(instant)
        if minutes == 0:
            return self._snap_forward(day, minute)
        target = self._cumulative(day, minute) + minutes
        return self._earliest(target)

    def subtract_work(self, instant: datetime, minutes: int) -> datetime:
        """Move backward by working minutes. Zero minutes stays on a work instant."""
        if minutes < 0:
            return self.add_work(instant, -minutes)
        day, minute = instant.date(), _minute_of(instant)
        if minutes == 0:
            return self._snap_backward(day, minute)
        target = self._cumulative(day, minute) - minutes
        if target < 0:
            raise CalendarLimitError(_HORIZON)
        return self._latest(target)

    def work_between(self, start: datetime, end: datetime) -> int:
        """Working minutes from start to end. A backward span is negative."""
        start_key = (start.date(), _minute_of(start))
        end_key = (end.date(), _minute_of(end))
        if end_key == start_key:
            return 0
        return self._cumulative(*end_key) - self._cumulative(*start_key)

    def _build_index(self) -> None:
        minutes: list[int] = []
        flags: list[int] = []
        for weekday in range(7):
            total = _shift_minutes(self._week.get(weekday, ()))
            minutes.append(total)
            flags.append(1 if total else 0)
        self._week_minutes = tuple(minutes)
        self._week_total = sum(minutes)
        self._week_prefix = _exclusive_prefix(minutes)
        self._week_flags = tuple(flags)
        self._week_flag_total = sum(flags)
        self._week_flag_prefix = _exclusive_prefix(flags)
        dates = tuple(sorted(self._exceptions))
        deltas: list[int] = []
        flag_deltas: list[int] = []
        removed = 0
        for day in dates:
            exc_minutes = _shift_minutes(self._exceptions[day])
            delta = exc_minutes - minutes[day.weekday()]
            deltas.append(delta)
            if delta < 0:
                removed += -delta
            exc_flag = 1 if exc_minutes else 0
            flag_deltas.append(exc_flag - flags[day.weekday()])
        self._exc_dates = dates
        self._exc_prefix = _inclusive_prefix(deltas)
        self._exc_flag_prefix = _inclusive_prefix(flag_deltas)
        self._removed = removed

    def _open_shifts(self, day: date) -> tuple[tuple[int, int], ...]:
        return tuple(
            sorted((begin, finish) for begin, finish in self.shifts_on(day) if finish > begin)
        )

    def _has_work(self, day: date) -> bool:
        return any(finish > begin for begin, finish in self.shifts_on(day))

    def _cumulative(self, day: date, minute: int) -> int:
        total = self._work_before(day)
        if minute <= 0:
            return total
        for begin, finish in self._open_shifts(day):
            if minute <= begin:
                break
            total += min(minute, finish) - begin
        return total

    def _work_before(self, day: date) -> int:
        if day <= _EPOCH:
            return 0
        days = (day - _EPOCH).days
        weeks, rem = divmod(days, 7)
        total = weeks * self._week_total + self._week_prefix[rem]
        return total + self._delta_before(day, self._exc_prefix)

    def _working_days_before(self, day: date) -> int:
        if day <= _EPOCH:
            return 0
        days = (day - _EPOCH).days
        weeks, rem = divmod(days, 7)
        total = weeks * self._week_flag_total + self._week_flag_prefix[rem]
        return total + self._delta_before(day, self._exc_flag_prefix)

    def _delta_before(self, day: date, prefix: tuple[int, ...]) -> int:
        index = bisect.bisect_left(self._exc_dates, day)
        if index == 0:
            return 0
        return prefix[index - 1]

    def _cumulative_offset(self, offset: int) -> int:
        day, minute = _parts(offset)
        return self._cumulative(day, minute)

    def _earliest(self, target: int) -> datetime:
        """Earliest instant whose cumulative work is at least ``target``."""
        if target <= 0:
            return datetime(_EPOCH.year, _EPOCH.month, _EPOCH.day)
        hi = self._offset_reaching(target)
        lo = 0
        while lo < hi:
            mid = (lo + hi) // 2
            if self._cumulative_offset(mid) >= target:
                hi = mid
            else:
                lo = mid + 1
        return _from_offset(lo)

    def _latest(self, target: int) -> datetime:
        """Latest instant whose cumulative work is exactly ``target``."""
        nxt = self._earliest(target + 1)
        return nxt - timedelta(minutes=1)

    def _offset_reaching(self, target: int) -> int:
        hi = min(self._estimate_offset(target), _MAX_OFFSET)
        reached = self._cumulative_offset(hi)
        guard = 0
        while reached < target:
            if hi >= _MAX_OFFSET or (self._week_total <= 0 and guard > 0):
                raise CalendarLimitError(_HORIZON)
            grown = hi * 2 if hi > _DAY_MINUTES else hi + 14 * _DAY_MINUTES
            if grown <= hi:
                grown = _MAX_OFFSET
            hi = min(grown, _MAX_OFFSET)
            reached = self._cumulative_offset(hi)
            guard += 1
            if guard > 64:
                raise CalendarLimitError(_HORIZON)
        return hi

    def _estimate_offset(self, target: int) -> int:
        if self._week_total > 0:
            weeks = (target + self._removed) // self._week_total + 3
            days = weeks * 7 + 7
            return days * _DAY_MINUTES
        if not self._exc_dates:
            return 0
        last = self._exc_dates[-1]
        nxt = _add_days(last, 1)
        if nxt is None:
            return _MAX_OFFSET
        return _to_offset(nxt, 0)

    def _snap_forward(self, day: date, minute: int) -> datetime:
        for begin, finish in self._open_shifts(day):
            if begin <= minute < finish:
                return _stamp(day, minute)
            if minute < begin:
                return _stamp(day, begin)
        nxt = _add_days(day, 1)
        if nxt is None:
            raise CalendarLimitError(_HORIZON)
        found = self._next_working_day(nxt)
        if found is None:
            raise CalendarLimitError(_HORIZON)
        return _stamp(found, self._open_shifts(found)[0][0])

    def _snap_backward(self, day: date, minute: int) -> datetime:
        shifts = self._open_shifts(day)
        for begin, finish in reversed(shifts):
            if begin <= minute <= finish:
                return _stamp(day, minute)
            if minute > finish:
                return _stamp(day, finish)
        prev_day = _add_days(day, -1)
        if prev_day is None:
            raise CalendarLimitError(_HORIZON)
        found = self._previous_working_day(prev_day)
        if found is None:
            raise CalendarLimitError(_HORIZON)
        return _stamp(found, self._open_shifts(found)[-1][1])

    def _next_working_day(self, start: date) -> date | None:
        start = max(start, _EPOCH)
        if self._has_work(start):
            return start
        if not self._work_ahead(start):
            return None
        lo = start
        hi = self._next_bound(start)
        while hi is not None and self._through(hi) == self._working_days_before(start):
            grown = _add_days(hi, max((hi - lo).days, 7))
            if grown is None or grown == hi:
                return None
            hi = grown
        if hi is None:
            return None
        while lo < hi:
            mid = lo + timedelta(days=(hi - lo).days // 2)
            after = _add_days(mid, 1)
            if after is not None and self._working_days_before(after) > self._working_days_before(
                start
            ):
                hi = mid
            else:
                nxt = _add_days(mid, 1)
                if nxt is None:
                    return None
                lo = nxt
        if self._has_work(lo):
            return lo
        return None

    def _previous_working_day(self, limit: date) -> date | None:
        if limit < _EPOCH or self._through(limit) <= 0:
            return None
        if self._has_work(limit):
            return limit
        lo = _EPOCH
        hi = limit
        goal = self._through(limit)
        while lo < hi:
            mid = lo + timedelta(days=((hi - lo).days + 1) // 2)
            if self._working_days_before(mid) < goal:
                lo = mid
            else:
                prev = _add_days(mid, -1)
                if prev is None:
                    return None
                hi = prev
        return lo

    def _through(self, day: date) -> int:
        nxt = _add_days(day, 1)
        if nxt is None:
            return self._working_days_before(day) + (1 if self._has_work(day) else 0)
        return self._working_days_before(nxt)

    def _work_ahead(self, start: date) -> bool:
        if self._week_flag_total > 0 and start < date.max:
            return True
        index = bisect.bisect_left(self._exc_dates, start)
        return any(self._has_work(day) for day in self._exc_dates[index:])

    def _next_bound(self, start: date) -> date | None:
        last = self._exc_dates[-1] if self._exc_dates else start
        if self._week_flag_total > 0:
            anchor = last if last > start else start
            return _add_days(anchor, 8)
        return last if last >= start else None


def elapsed_calendar() -> WorkCalendar:
    """Clock time, 24 hours every day. Used only for an elapsed lag."""
    full = ((0, _DAY_MINUTES),)
    return WorkCalendar({day: full for day in range(7)})


def _shift_minutes(shifts: tuple[tuple[int, int], ...]) -> int:
    return sum(finish - begin for begin, finish in shifts if finish > begin)


def _exclusive_prefix(values: list[int]) -> tuple[int, ...]:
    total = 0
    found = [0]
    for value in values:
        total += value
        found.append(total)
    return tuple(found)


def _inclusive_prefix(values: list[int]) -> tuple[int, ...]:
    total = 0
    found: list[int] = []
    for value in values:
        total += value
        found.append(total)
    return tuple(found)


def _minute_of(instant: datetime) -> int:
    return instant.hour * 60 + instant.minute


def _stamp(day: date, minute: int) -> datetime:
    if minute >= _DAY_MINUTES:
        extra, minute = divmod(minute, _DAY_MINUTES)
        moved = _add_days(day, extra)
        if moved is None:
            raise CalendarLimitError(_HORIZON)
        day = moved
    if minute < 0:
        raise CalendarLimitError(_HORIZON)
    return datetime(day.year, day.month, day.day, minute // 60, minute % 60)


def _add_days(day: date, days: int) -> date | None:
    if days >= 0:
        room = (date.max - day).days
        if days > room:
            return None
    else:
        room = (day - date.min).days
        if -days > room:
            return None
    return day + timedelta(days=days)


def _to_offset(day: date, minute: int) -> int:
    return (day - _EPOCH).days * _DAY_MINUTES + minute


def _parts(offset: int) -> tuple[date, int]:
    days, minute = divmod(offset, _DAY_MINUTES)
    return _EPOCH + timedelta(days=days), minute


def _from_offset(offset: int) -> datetime:
    day, minute = _parts(offset)
    return datetime(day.year, day.month, day.day, minute // 60, minute % 60)
