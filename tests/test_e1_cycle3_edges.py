"""Edges the E1 cycle-2 gate still left uncovered.

These cases do not claim G4 or G13. They lock parser notes, a few clock
branches, and the conformance mismatches the happy path never hits.
"""

from dataclasses import replace
from datetime import date, datetime
from pathlib import Path

import pytest

from atlaspmo.calendars.data import parse_clndr_data
from atlaspmo.calendars.worktime import CalendarLimitError, WorkCalendar, elapsed_calendar
from atlaspmo.engine.conformance import conformance
from atlaspmo.model.schedule import Schedule
from test_cpm import _load, _task


def test_missing_week_and_unclosed_marker_are_notes() -> None:
    parsed = parse_clndr_data("(0||CalendarData()())")
    assert parsed.notes == ("clndr_data no trae DaysOfWeek.",)
    unclosed = parse_clndr_data("(0||DaysOfWeek()(")
    assert unclosed.notes == ("clndr_data no trae DaysOfWeek.",)


def test_inverted_and_unordered_shifts_are_omitted() -> None:
    inverted = (
        "(0||CalendarData()((0||DaysOfWeek()((0||2()((0||0(s|16:00|f|08:00)())))))"
        "(0||VIEW(ShowTotal|N)())))"
    )
    parsed = parse_clndr_data(inverted)
    assert parsed.by_weekday[0] == ()
    assert "Turno con fin anterior al inicio: se omitió." in parsed.notes

    unordered = (
        "(0||CalendarData()((0||DaysOfWeek()((0||2()((0||0(f|08:00|s|16:00)())))))"
        "(0||VIEW(ShowTotal|N)())))"
    )
    parsed = parse_clndr_data(unordered)
    assert "Turno que no va de s| a f|: se omitió." in parsed.notes


def test_broken_exception_serials_do_not_invent_a_shift() -> None:
    week = "(0||CalendarData()((0||DaysOfWeek()((0||2()((0||0(s|08:00|f|16:00)())))))"
    open_serial = parse_clndr_data(week + "(0||Exceptions()((0||0(d|46000")
    assert open_serial.exceptions == {}
    no_group = parse_clndr_data(week + "(0||Exceptions()((0||0(d|46000))))")
    assert no_group.exceptions[date(2025, 12, 9)] == ()
    unclosed = parse_clndr_data(week + "(0||Exceptions()((0||0(d|46000)()))")
    assert unclosed.exceptions[date(2025, 12, 9)] == ()


def test_negative_minutes_delegate_and_the_epoch_floor_raises() -> None:
    week = {day: ((8 * 60, 16 * 60),) for day in range(7)}
    clock = WorkCalendar(week)
    monday = datetime(2026, 1, 5, 8, 0)
    assert clock.add_work(datetime(2026, 1, 5, 16, 0), -8 * 60) == monday
    assert clock.subtract_work(monday, -8 * 60) == datetime(2026, 1, 5, 16, 0)
    full = WorkCalendar({day: ((0, 24 * 60),) for day in range(7)})
    with pytest.raises(CalendarLimitError, match="horizonte"):
        full.subtract_work(datetime(1, 1, 1, 0, 30), 60)


def test_elapsed_calendar_and_exception_only_week() -> None:
    elapsed = elapsed_calendar()
    start = datetime(2026, 1, 5, 0, 0)
    assert elapsed.add_work(start, 60) == datetime(2026, 1, 5, 1, 0)
    assert elapsed.work_between(start, start) == 0

    holiday = date(2026, 1, 5)
    clock = WorkCalendar({day: () for day in range(7)}, {holiday: ((8 * 60, 12 * 60),)})
    assert clock.add_work(datetime(2026, 1, 5, 8, 0), 60) == datetime(2026, 1, 5, 9, 0)
    assert clock.shifts_on(date(2026, 1, 6)) == ()


def test_conformance_reports_empty_missing_and_mismatch(tmp_path: Path) -> None:
    empty = Schedule((), (), (), (), (), (), ())
    assert conformance(empty).ratio is None

    schedule = _load(tmp_path, [_task("1", "A", "8")], [])
    activity = schedule.activities[0]
    wrong = datetime(2026, 1, 1, 8, 0)
    shifted = replace(
        activity,
        early_start_date=wrong,
        total_float_hr_cnt=99,
        free_float_hr_cnt=99,
    )
    report = conformance(replace(schedule, activities=(shifted,)))
    assert report.ratio is not None
    assert report.ratio < 1
    assert "A early_start" in report.unexplained
    assert "A total_float" in report.unexplained
    assert "A free_float" in report.unexplained

    ghost = replace(activity, task_type="TT_Other", early_start_date=wrong)
    missing = conformance(replace(schedule, activities=(ghost,)))
    assert missing.unexplained == ("A: no la calculó el motor.",)

    blank = replace(activity, task_id=None, early_start_date=wrong)
    assert conformance(replace(schedule, activities=(blank,))).compared == 0
