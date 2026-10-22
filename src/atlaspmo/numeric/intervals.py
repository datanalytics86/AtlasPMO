"""Work intervals for one searchsorted per calendar move.

Intervals are half-open [start, end) in absolute minutes from 0001-01-01.
The cumulative value stored on an interval is the work strictly before it.
A finish instant equal to ``end`` has accumulated the whole interval, matching
``WorkCalendar``.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

import numpy as np

from atlaspmo.calendars.worktime import WorkCalendar

EPOCH = date(1, 1, 1)
DAY = 24 * 60


class UnsupportedCalendar(Exception):
    """Shifts overlap or leave the day. The reference engine still schedules them."""


def to_minute(instant: datetime) -> int:
    """Absolute minute, dropping seconds the same way the reference clock does."""
    day = instant.date()
    return (day - EPOCH).days * DAY + instant.hour * 60 + instant.minute


def from_minute(minute: int) -> datetime:
    days, rem = divmod(int(minute), DAY)
    found = EPOCH + timedelta(days=days)
    return datetime(found.year, found.month, found.day, rem // 60, rem % 60)


def build_tables(
    clocks: list[WorkCalendar],
    start: date,
    end: date,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int]:
    """Concatenate one interval table per calendar.

    Returns starts, ends, cum, cum_end, offsets, base_cum, window_lo, window_hi.
    ``window_hi`` is the last minute the table is allowed to answer.
    """
    end = max(end, start)
    window_lo = to_minute(datetime(start.year, start.month, start.day))
    window_hi = to_minute(datetime(end.year, end.month, end.day)) + DAY - 1
    origin = datetime(EPOCH.year, EPOCH.month, EPOCH.day)
    starts: list[int] = []
    ends: list[int] = []
    cum: list[int] = []
    offsets = [0]
    base_cum: list[int] = []
    day_count = (end - start).days + 1
    for clock in clocks:
        stamp = datetime(start.year, start.month, start.day)
        base_cum.append(clock.work_between(origin, stamp))
        running = base_cum[-1]
        day = start
        for _ in range(day_count):
            base = (day - EPOCH).days * DAY
            shifts = sorted(
                (begin, finish) for begin, finish in clock.shifts_on(day) if finish > begin
            )
            previous = -1
            for begin, finish in shifts:
                if begin < 0 or finish > DAY or begin < previous:
                    raise UnsupportedCalendar()
                previous = finish
                starts.append(base + begin)
                ends.append(base + finish)
                cum.append(running)
                running += finish - begin
            nxt = day + timedelta(days=1)
            day = nxt
        offsets.append(len(starts))
    start_arr = np.asarray(starts, dtype=np.int64)
    end_arr = np.asarray(ends, dtype=np.int64)
    cum_arr = np.asarray(cum, dtype=np.int64)
    cum_end = cum_arr + (end_arr - start_arr)
    return (
        start_arr,
        end_arr,
        cum_arr,
        cum_end,
        np.asarray(offsets, dtype=np.int64),
        np.asarray(base_cum, dtype=np.int64),
        window_lo,
        window_hi,
    )


def table_add(
    tables: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int],
    clock: int,
    instant: datetime,
    minutes: int,
) -> datetime:
    """Same move as the kernel, for one calendar already tabulated."""
    found = _add_minutes(tables, clock, to_minute(instant), minutes)
    if found < 0:
        raise UnsupportedCalendar()
    return from_minute(found)


def table_subtract(
    tables: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int],
    clock: int,
    instant: datetime,
    minutes: int,
) -> datetime:
    # Zero minutes snaps backward. Routing that through add would snap forward.
    found = _sub_minutes(tables, clock, to_minute(instant), minutes)
    if found < 0:
        raise UnsupportedCalendar()
    return from_minute(found)


def table_between(
    tables: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int],
    clock: int,
    start: datetime,
    end: datetime,
) -> int:
    left = _cumulative(tables, clock, to_minute(start))
    right = _cumulative(tables, clock, to_minute(end))
    if left < 0 or right < 0:
        raise UnsupportedCalendar()
    return right - left


def _cumulative(
    tables: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int],
    clock: int,
    minute: int,
) -> int:
    starts, ends, cum, cum_end, offsets, base_cum, window_lo, window_hi = tables
    if minute < window_lo or minute > window_hi:
        return -1
    lo = int(offsets[clock])
    hi = int(offsets[clock + 1])
    if hi <= lo:
        return int(base_cum[clock])
    relative = int(np.searchsorted(starts[lo:hi], minute, side="right")) - 1
    if relative < 0:
        return int(base_cum[clock])
    index = lo + relative
    if minute < int(ends[index]):
        return int(cum[index]) + (minute - int(starts[index]))
    return int(cum_end[index])


def _earliest(
    tables: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int],
    clock: int,
    target: int,
) -> int:
    starts, _ends, cum, cum_end, offsets, _base, _lo, _hi = tables
    if target <= 0:
        return 0
    lo = int(offsets[clock])
    hi = int(offsets[clock + 1])
    if hi <= lo or target <= int(cum[lo]) or target > int(cum_end[hi - 1]):
        return -1
    index = lo + int(np.searchsorted(cum_end[lo:hi], target, side="left"))
    if index >= hi:
        return -1
    return int(starts[index]) + (target - int(cum[index]))


def _add_minutes(
    tables: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int],
    clock: int,
    minute: int,
    amount: int,
) -> int:
    if amount < 0:
        return _sub_minutes(tables, clock, minute, -amount)
    if amount == 0:
        return _snap_forward(tables, clock, minute)
    base = _cumulative(tables, clock, minute)
    if base < 0:
        return base
    return _earliest(tables, clock, base + amount)


def _sub_minutes(
    tables: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int],
    clock: int,
    minute: int,
    amount: int,
) -> int:
    if amount == 0:
        return _snap_backward(tables, clock, minute)
    base = _cumulative(tables, clock, minute)
    if base < 0:
        return base
    target = base - amount
    if target < 0:
        return -1
    nxt = _earliest(tables, clock, target + 1)
    if nxt < 0:
        return nxt
    return nxt - 1


def _snap_forward(
    tables: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int],
    clock: int,
    minute: int,
) -> int:
    starts, ends, _cum, _cum_end, offsets, _base, window_lo, window_hi = tables
    if minute < window_lo or minute > window_hi:
        return -1
    lo = int(offsets[clock])
    hi = int(offsets[clock + 1])
    if hi <= lo:
        return -1
    relative = int(np.searchsorted(starts[lo:hi], minute, side="right")) - 1
    if relative >= 0:
        index = lo + relative
        if minute < int(ends[index]):
            return minute
    nxt = lo + int(np.searchsorted(starts[lo:hi], minute, side="left"))
    if nxt < hi:
        return int(starts[nxt])
    return -1


def _snap_backward(
    tables: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int],
    clock: int,
    minute: int,
) -> int:
    starts, ends, _cum, _cum_end, offsets, _base, window_lo, window_hi = tables
    if minute < window_lo or minute > window_hi:
        return -1
    lo = int(offsets[clock])
    hi = int(offsets[clock + 1])
    if hi <= lo:
        return -1
    relative = int(np.searchsorted(starts[lo:hi], minute, side="right")) - 1
    if relative < 0:
        return -1
    index = lo + relative
    if minute <= int(ends[index]):
        return minute
    return int(ends[index])
