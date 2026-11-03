"""Monday-Friday span that skips Wednesday 2026-01-07.

This module must not import atlaspmo. It is the second calculation for the
CPLI case with an SS overlap: walk each 08:00-16:00 shift and leave that
holiday out.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

HOLIDAY = date(2026, 1, 7)


def work_minutes(start: datetime, end: datetime) -> int:
    """Working minutes between two instants. A backward span is negative.

    Only Monday through Friday, 08:00-16:00. 2026-01-07 has no shift.
    """
    if end < start:
        return -work_minutes(end, start)
    total = 0
    cursor = start
    while cursor < end:
        if cursor.weekday() >= 5 or cursor.date() == HOLIDAY:
            nxt = cursor + timedelta(days=1)
            cursor = nxt.replace(hour=8, minute=0, second=0, microsecond=0)
            continue
        shift_open = cursor.replace(hour=8, minute=0, second=0, microsecond=0)
        shift_close = cursor.replace(hour=16, minute=0, second=0, microsecond=0)
        if cursor < shift_open:
            cursor = shift_open
            continue
        if cursor >= shift_close:
            nxt = cursor + timedelta(days=1)
            cursor = nxt.replace(hour=8, minute=0, second=0, microsecond=0)
            continue
        stop = end if end < shift_close else shift_close
        total += int((stop - cursor).total_seconds() // 60)
        cursor = stop
    return total


def cpli_ratio(start: datetime, finish: datetime, plan_end: datetime) -> float:
    """(working time through the finish, plus slack to the plan) / that time."""
    length = work_minutes(start, finish)
    slack = work_minutes(finish, plan_end)
    return (length + slack) / length
