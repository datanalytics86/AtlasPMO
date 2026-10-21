"""B-06: accumulated working-time index, no fixed 3660-day cap."""

from datetime import date, datetime, timedelta

import pytest

from atlaspmo.calendars.worktime import CalendarLimitError, WorkCalendar

_EIGHT = ((8 * 60, 16 * 60),)


def _all_week() -> dict[int, tuple[tuple[int, int], ...]]:
    return {day: _EIGHT for day in range(7)}


def _weekdays() -> dict[int, tuple[tuple[int, int], ...]]:
    return {day: _EIGHT if day < 5 else () for day in range(7)}


def test_twenty_year_span_is_exact_and_does_not_raise():
    clock = WorkCalendar(_all_week())
    start = datetime(2026, 1, 5, 8, 0)
    work_days = 20 * 365
    assert work_days > 3660
    minutes = work_days * 8 * 60
    landed = clock.add_work(start, minutes)
    expected = datetime(2026, 1, 5, 16, 0) + timedelta(days=work_days - 1)
    assert landed == expected
    assert clock.work_between(start, landed) == minutes
    assert clock.subtract_work(landed, minutes) == start


def test_weekday_calendar_skips_weekends_and_covers_twenty_years():
    clock = WorkCalendar(_weekdays())
    monday = datetime(2026, 1, 5, 8, 0)
    assert clock.add_work(monday, 5 * 8 * 60) == datetime(2026, 1, 9, 16, 0)
    assert clock.add_work(monday, 6 * 8 * 60) == datetime(2026, 1, 12, 16, 0)
    assert clock.subtract_work(datetime(2026, 1, 12, 8, 0), 8 * 60) == datetime(2026, 1, 9, 8, 0)
    minutes = 20 * 52 * 5 * 8 * 60
    landed = clock.add_work(monday, minutes)
    assert (landed - monday).days > 3660
    assert clock.work_between(monday, landed) == minutes
    assert clock.subtract_work(landed, minutes) == monday


def test_exception_replaces_the_weekday_including_years_ahead():
    holiday = date(2026, 1, 7)
    near = WorkCalendar(_all_week(), {holiday: ()})
    monday = datetime(2026, 1, 5, 8, 0)
    assert near.shifts_on(holiday) == ()
    # Seven-day calendar: Wed 7 Jan is off, so the fifth shift ends Sat 10 Jan.
    assert near.add_work(monday, 5 * 8 * 60) == datetime(2026, 1, 10, 16, 0)
    short = date(2026, 1, 6)
    partial = WorkCalendar(_all_week(), {short: ((8 * 60, 12 * 60),)})
    assert partial.add_work(datetime(2026, 1, 6, 8, 0), 5 * 60) == datetime(2026, 1, 7, 9, 0)
    assert partial.work_between(datetime(2026, 1, 6, 8, 0), datetime(2026, 1, 7, 8, 0)) == 4 * 60
    far_day = date(2040, 6, 4)
    far = WorkCalendar(_all_week(), {far_day: ()})
    before = datetime(far_day.year, far_day.month, far_day.day, 16, 0) - timedelta(days=1)
    after = datetime(far_day.year, far_day.month, far_day.day, 8, 0) + timedelta(days=1)
    assert far.add_work(before, 0) == after
    assert far.work_between(before, after) == 0
    start = datetime(2026, 1, 5, 8, 0)
    end = datetime(2040, 6, 5, 8, 0)
    plain = WorkCalendar(_all_week())
    assert plain.work_between(start, end) - far.work_between(start, end) == 8 * 60


def test_full_day_shift_lands_on_the_next_midnight():
    clock = WorkCalendar({day: ((0, 24 * 60),) for day in range(7)})
    start = datetime(2026, 1, 5, 0, 0)
    assert clock.add_work(start, 24 * 60) == datetime(2026, 1, 6, 0, 0)
    assert clock.subtract_work(datetime(2026, 1, 6, 0, 0), 24 * 60) == start
    assert clock.work_between(start, datetime(2026, 1, 6, 0, 0)) == 24 * 60


def test_no_working_time_still_reports_the_horizon():
    clock = WorkCalendar({day: () for day in range(7)})
    with pytest.raises(CalendarLimitError, match="horizonte"):
        clock.add_work(datetime(2026, 1, 5, 8, 0), 60)
