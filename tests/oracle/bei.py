"""BEI count over plain tuples.

This module must not import atlaspmo. Completed activities as of the data
date, including early finishes, divided by activities whose baseline finish
is on or before that date.
"""

from __future__ import annotations

from datetime import datetime

Row = tuple[str, str, datetime | None, datetime]


def ratio(rows: tuple[Row, ...], data_date: datetime) -> float:
    """Completions as of the data date over baseline finishes due by then.

    Each row is (code, status, actual finish, baseline finish). ``TK_Complete``
    with no actual finish, or an actual finish on or before the data date,
    counts as complete. A baseline finish after the data date is not due.
    """
    due = 0
    completed = 0
    for _code, status, actual, baseline in rows:
        if baseline <= data_date:
            due += 1
        if status == "TK_Complete" and (actual is None or actual <= data_date):
            completed += 1
    return completed / due
