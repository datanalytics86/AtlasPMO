"""Calendar text and working-time arithmetic."""

from datetime import date, datetime

import pytest

from atlaspmo.calendars.data import parse_clndr_data
from atlaspmo.calendars.worktime import WorkCalendar


def _week(start: str = "08:00", finish: str = "16:00") -> str:
    days = "".join(
        f"(0||{number}()((0||0(s|{start}|f|{finish})())))" for number in range(1, 8)
    )
    return f"(0||CalendarData()((0||DaysOfWeek()({days}))(0||VIEW(ShowTotal|N)())))"


def test_sunday_is_day_one_and_shift_is_eight_hours():
    parsed = parse_clndr_data(_week())
    assert parsed.by_weekday[6] == ((8 * 60, 16 * 60),)
    assert parsed.by_weekday[0] == ((8 * 60, 16 * 60),)
    assert parsed.notes == ()


def test_exception_serial_uses_1899_12_30_and_empty_means_no_work():
    holiday = date(2026, 1, 5)
    serial = (holiday - date(1899, 12, 30)).days
    text = (
        "(0||CalendarData()((0||DaysOfWeek()((0||2()((0||0(s|08:00|f|16:00)())))))"
        f"(0||Exceptions()((0||0(d|{serial})())))(0||VIEW(ShowTotal|N)())))"
    )
    parsed = parse_clndr_data(text)
    assert parsed.exceptions[holiday] == ()
    assert parsed.by_weekday[0] == ((8 * 60, 16 * 60),)


def test_midnight_span_is_a_full_day_and_is_noted():
    parsed = parse_clndr_data(_week("00:00", "00:00"))
    assert parsed.by_weekday[0] == ((0, 24 * 60),)
    assert parsed.notes == ("s|00:00|f|00:00 se leyó como jornada de 24 h.",)


def test_add_and_subtract_stay_on_the_eight_hour_day():
    clock = WorkCalendar.from_parsed(parse_clndr_data(_week()))
    monday = datetime(2026, 1, 5, 8, 0)
    assert clock.add_work(monday, 8 * 60) == datetime(2026, 1, 5, 16, 0)
    assert clock.add_work(datetime(2026, 1, 5, 16, 0), 0) == datetime(2026, 1, 6, 8, 0)
    assert clock.add_work(datetime(2026, 1, 5, 16, 0), 8 * 60) == datetime(2026, 1, 6, 16, 0)
    assert clock.subtract_work(datetime(2026, 1, 6, 8, 0), 8 * 60) == monday
    assert clock.subtract_work(datetime(2026, 1, 6, 16, 0), 8 * 60) == datetime(2026, 1, 6, 8, 0)
    assert clock.work_between(monday, datetime(2026, 1, 7, 8, 0)) == 16 * 60


def test_exception_removes_the_day():
    holiday = date(2026, 1, 6)
    serial = (holiday - date(1899, 12, 30)).days
    text = _week().replace(
        "(0||VIEW(ShowTotal|N)())",
        f"(0||Exceptions()((0||0(d|{serial})())))(0||VIEW(ShowTotal|N)())",
    )
    clock = WorkCalendar.from_parsed(parse_clndr_data(text))
    assert clock.add_work(datetime(2026, 1, 5, 16, 0), 0) == datetime(2026, 1, 7, 8, 0)
    assert clock.shifts_on(holiday) == ()


def test_horizon_is_explicit():
    clock = WorkCalendar({day: () for day in range(7)})
    with pytest.raises(Exception, match="horizonte"):
        clock.add_work(datetime(2026, 1, 5, 8, 0), 60)
