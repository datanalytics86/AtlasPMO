"""Interval tables against WorkCalendar, inside a window that covers the probes."""

from datetime import date, datetime, timedelta

from atlaspmo.calendars.worktime import WorkCalendar
from atlaspmo.numeric.intervals import build_tables, table_add, table_between, table_subtract

WEEK = {day: ((8 * 60, 16 * 60),) if day < 5 else () for day in range(7)}
ALL = {day: ((8 * 60, 16 * 60),) for day in range(7)}
FULL = {day: ((0, 24 * 60),) for day in range(7)}
HALF = {day: ((8 * 60, 12 * 60),) if day < 5 else () for day in range(7)}
HOLIDAY = date(2026, 1, 7)


def _tables(clock: WorkCalendar):
    return build_tables([clock], date(2025, 12, 1), date(2026, 3, 1))


def _same(clock: WorkCalendar, start: datetime, minutes: int) -> None:
    tables = _tables(clock)
    assert table_add(tables, 0, start, minutes) == clock.add_work(start, minutes)
    assert table_subtract(tables, 0, start, minutes) == clock.subtract_work(start, minutes)


def test_zero_minute_snaps_forward_and_backward():
    clock = WorkCalendar(WEEK)
    monday = datetime(2026, 1, 5, 8, 0)
    close = datetime(2026, 1, 5, 16, 0)
    _same(clock, monday, 0)
    _same(clock, close, 0)
    _same(clock, datetime(2026, 1, 4, 12, 0), 0)
    assert clock.add_work(close, 0) == datetime(2026, 1, 6, 8, 0)
    assert clock.subtract_work(monday, 0) == monday


def test_weekend_gap_and_full_shift():
    clock = WorkCalendar(WEEK)
    friday_close = datetime(2026, 1, 9, 16, 0)
    monday_open = datetime(2026, 1, 12, 8, 0)
    _same(clock, friday_close, 8 * 60)
    _same(clock, monday_open, 8 * 60)
    tables = _tables(clock)
    assert table_between(tables, 0, friday_close, monday_open) == clock.work_between(
        friday_close, monday_open
    )
    assert table_between(tables, 0, monday_open, friday_close) == clock.work_between(
        monday_open, friday_close
    )


def test_holiday_is_not_work_and_half_day_stays_at_noon():
    clock = WorkCalendar(WEEK, {HOLIDAY: ()})
    tuesday_close = datetime(2026, 1, 6, 16, 0)
    _same(clock, tuesday_close, 0)
    assert clock.add_work(tuesday_close, 0) == datetime(2026, 1, 8, 8, 0)
    half = WorkCalendar(HALF)
    _same(half, datetime(2026, 1, 5, 8, 0), 4 * 60)
    assert half.add_work(datetime(2026, 1, 5, 12, 0), 0) == datetime(2026, 1, 6, 8, 0)


def test_full_day_shift_moves_twenty_four_hours():
    clock = WorkCalendar(FULL)
    start = datetime(2026, 1, 5, 0, 0)
    _same(clock, start, 24 * 60)
    _same(clock, datetime(2026, 1, 5, 23, 59), 1)
    tables = _tables(clock)
    end = start + timedelta(days=2)
    assert table_between(tables, 0, start, end) == clock.work_between(start, end)


def test_seven_day_calendar_matches_a_grid_of_moves():
    clock = WorkCalendar(ALL)
    tables = _tables(clock)
    origin = datetime(2026, 1, 5, 7, 30)
    for step in range(0, 3 * 24 * 60, 30):
        instant = origin + timedelta(minutes=step)
        for amount in (0, 1, 30, 60, 8 * 60):
            assert table_add(tables, 0, instant, amount) == clock.add_work(instant, amount)
            assert table_subtract(tables, 0, instant, amount) == clock.subtract_work(
                instant, amount
            )
        later = instant + timedelta(hours=10)
        assert table_between(tables, 0, instant, later) == clock.work_between(instant, later)
