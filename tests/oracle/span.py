"""Day-by-day span for one 7-day, 08:00-16:00 calendar.

This module must not import atlaspmo. It is the second calculation for the
CPLI example: walk each shift instead of using the accumulated index.
"""

from __future__ import annotations

from datetime import datetime, timedelta


def work_minutes(start: datetime, end: datetime) -> int:
    """Working minutes between two instants. A backward span is negative."""
    if end < start:
        return -work_minutes(end, start)
    total = 0
    cursor = start
    while cursor < end:
        shift_open = cursor.replace(hour=8, minute=0, second=0, microsecond=0)
        shift_close = cursor.replace(hour=16, minute=0, second=0, microsecond=0)
        if cursor < shift_open:
            cursor = shift_open
            continue
        if cursor >= shift_close:
            next_day = cursor + timedelta(days=1)
            cursor = next_day.replace(hour=8, minute=0, second=0, microsecond=0)
            continue
        stop = end if end < shift_close else shift_close
        total += int((stop - cursor).total_seconds() // 60)
        cursor = stop
    return total
