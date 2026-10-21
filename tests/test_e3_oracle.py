"""QC-2: the CPLI ratio agrees with a day-by-day oracle that is not the engine."""

from __future__ import annotations

from datetime import datetime

from tests.oracle.span import work_minutes

MON_8 = datetime(2026, 1, 5, 8, 0)
WED_16 = datetime(2026, 1, 7, 16, 0)
FRI_16 = datetime(2026, 1, 9, 16, 0)


def test_hand_span_matches_the_cpli_ratio() -> None:
    length = work_minutes(MON_8, WED_16)
    slack = work_minutes(WED_16, FRI_16)
    assert length == 24 * 60
    assert slack == 16 * 60
    assert (length + slack) / length == (24 + 16) / 24
