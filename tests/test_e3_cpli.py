"""CPLI uses working time on the project calendar, not the sum of durations."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from pathlib import Path

from atlaspmo.analysis.quality.check import evaluate
from atlaspmo.analysis.quality.profiles import load_profile
from test_cpm import _load, _task

MON_8 = datetime(2026, 1, 5, 8, 0)
WED_16 = datetime(2026, 1, 7, 16, 0)
FRI_16 = datetime(2026, 1, 9, 16, 0)


def test_cpli_ignores_the_sum_of_remaining_durations(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "80"), _task("2", "M", "0", "TT_FinMile")],
        [],
    )
    project = replace(
        schedule.projects[0],
        last_recalc_date=MON_8,
        plan_end_date=FRI_16,
    )
    milestone = replace(
        schedule.activities[1],
        total_float_hr_cnt=0,
        early_end_date=WED_16,
        remain_drtn_hr_cnt=0,
    )
    long = replace(schedule.activities[0], total_float_hr_cnt=0, remain_drtn_hr_cnt=80)
    schedule = replace(schedule, projects=(project,), activities=(long, milestone))
    profile, _note = load_profile("dcma_estricto")
    metrics, _findings, _notes = evaluate(schedule, profile, None)
    # Mon 08:00 to Wed 16:00 is 24 h. Wed 16:00 to Fri 16:00 is 16 h. 40/24.
    # A sum of the 80 h remainder would not produce that ratio.
    assert metrics["cpli"].status == "cumple"
    assert metrics["cpli"].value == (24 + 16) / 24
