"""Parse the nested calendar text used by the fixtures.

Public shape, not checked against an export from Nicolás:

- Oracle MOSC shows `(0||CalendarData()(` / `(0||DaysOfWeek()(` / `(0||N()(`
  and shifts written `s|HH:MM|f|HH:MM`.
- PyP6Xer maps day 1 to Sunday and day 2 to Monday.
- Planning Planet and PyP6Xer's `xldate_to_datetime` count exception days
  from 1899-12-30. Empty brackets after the serial mean no work.

`s|00:00|f|00:00` is read as a 24-hour shift. That reading is an assumption:
the published MOSC sample uses it on every weekday.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta

_EXCEL_EPOCH = date(1899, 12, 30)
_P6_TO_WEEKDAY = {1: 6, 2: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5}
_SHIFT = re.compile(r"[sf]\|\d{2}:\d{2}")
_FULL_DAY = "s|00:00|f|00:00 se leyó como jornada de 24 h."


@dataclass(frozen=True)
class ParsedCalendar:
    """Working minutes after midnight, keyed by datetime.weekday()."""

    by_weekday: dict[int, tuple[tuple[int, int], ...]]
    exceptions: dict[date, tuple[tuple[int, int], ...]]
    notes: tuple[str, ...]


def parse_clndr_data(text: str) -> ParsedCalendar:
    """Read one clndr_data string. Unknown pieces become notes, not guesses."""
    notes: list[str] = []
    empty: tuple[tuple[int, int], ...] = ()
    week = {day: empty for day in range(7)}
    week_text = _section(text, "(0||DaysOfWeek()(")
    if week_text is None:
        notes.append("clndr_data no trae DaysOfWeek.")
    else:
        for p6_day, py_day in _P6_TO_WEEKDAY.items():
            body = _section(week_text, f"(0||{p6_day}()(")
            if body is None:
                continue
            shifts, shift_notes = _shifts(body)
            notes.extend(shift_notes)
            week[py_day] = tuple(shifts)
    exceptions: dict[date, tuple[tuple[int, int], ...]] = {}
    extra = _section(text, "(0||Exceptions()(")
    if extra is not None:
        exceptions, extra_notes = _exceptions(extra)
        notes.extend(extra_notes)
    return ParsedCalendar(week, exceptions, tuple(dict.fromkeys(notes)))


def _section(text: str, marker: str) -> str | None:
    start = text.find(marker)
    if start < 0:
        return None
    depth = 1
    chars: list[str] = []
    for char in text[start + len(marker) :]:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return "".join(chars)
        chars.append(char)
    return None


def _shifts(body: str) -> tuple[list[tuple[int, int]], list[str]]:
    notes: list[str] = []
    found: list[tuple[int, int]] = []
    tokens = list(_SHIFT.finditer(body))
    index = 0
    while index < len(tokens):
        current = tokens[index].group(0)
        nxt = tokens[index + 1].group(0) if index + 1 < len(tokens) else ""
        if current.startswith("s|") and nxt.startswith("f|"):
            start = _clock(current[2:])
            finish = _clock(nxt[2:])
            if start == 0 and finish == 0:
                found.append((0, 24 * 60))
                notes.append(_FULL_DAY)
            elif finish > start:
                found.append((start, finish))
            else:
                notes.append("Turno con fin anterior al inicio: se omitió.")
            index += 2
            continue
        notes.append("Turno que no va de s| a f|: se omitió.")
        index += 1
    return found, notes


def _exceptions(
    body: str,
) -> tuple[dict[date, tuple[tuple[int, int], ...]], list[str]]:
    notes: list[str] = []
    found: dict[date, tuple[tuple[int, int], ...]] = {}
    cursor = 0
    while True:
        at = body.find("(d|", cursor)
        if at < 0:
            break
        end_num = body.find(")", at)
        if end_num < 0:
            break
        serial = int(body[at + 3 : end_num])
        group, cursor = _group_after(body, end_num + 1)
        shifts, shift_notes = _shifts(group)
        notes.extend(shift_notes)
        found[_EXCEL_EPOCH + timedelta(days=serial)] = tuple(shifts)
    return found, notes


def _group_after(text: str, start: int) -> tuple[str, int]:
    while start < len(text) and text[start] != "(":
        start += 1
    if start >= len(text):
        return "", start
    section = _section(text[start:], "(")
    if section is None:
        return "", len(text)
    return section, start + 1 + len(section)


def _clock(value: str) -> int:
    hour, minute = value.split(":", maxsplit=1)
    return int(hour) * 60 + int(minute)
