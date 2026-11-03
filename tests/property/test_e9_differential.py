"""Each Monte Carlo finish matches the reference engine on a tiny network."""

from __future__ import annotations

import random
from dataclasses import replace

from hypothesis import given
from hypothesis import strategies as st
from tests.test_cpm import _PRED, _TASK, _link, _task, _week

from atlaspmo.analysis.risk.config import DurationRange, RiskConfig
from atlaspmo.analysis.risk.montecarlo import run_risk
from atlaspmo.analysis.risk.sample import sample_duration
from atlaspmo.engine.cpm import schedule_cpm
from atlaspmo.engine.options import EngineOptions
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.synthetic import encode_xer
from atlaspmo.io.xer import read_xer_bytes

_REFERENCE = EngineOptions(engine="reference")


def _schedule(hours: int):
    raw = encode_xer(
        "ERMHDR",
        [
            {
                "name": "PROJECT",
                "fields": ["proj_id", "clndr_id", "last_recalc_date"],
                "rows": [["1", "C1", "2026-01-05 08:00"]],
            },
            {
                "name": "CALENDAR",
                "fields": ["clndr_id", "day_hr_cnt", "clndr_data"],
                "rows": [["C1", "8", _week()]],
            },
            {
                "name": "TASK",
                "fields": _TASK,
                "rows": [_task("1", "A", str(hours)), _task("2", "B", "8")],
            },
            {"name": "TASKPRED", "fields": _PRED, "rows": [_link("1", "1", "2")]},
        ],
    )
    return schedule_from_xer(read_xer_bytes(raw))


def _bumped(schedule, code: str, value: float):
    activities = tuple(
        replace(activity, remain_drtn_hr_cnt=value) if activity.task_code == code else activity
        for activity in schedule.activities
    )
    return replace(schedule, activities=activities)


@given(
    hours=st.sampled_from((8, 16)),
    seed=st.integers(min_value=0, max_value=40),
)
def test_finishes_match_the_reference(hours: int, seed: int) -> None:
    schedule = _schedule(hours)
    low = float(hours)
    outcome = run_risk(
        schedule,
        RiskConfig(
            seed=seed,
            iterations=2,
            tornado_hours=0,
            ranges=[
                DurationRange(
                    task_code="A",
                    low=low,
                    mode=low + 8,
                    high=low + 16,
                    distribution="uniform",
                )
            ],
        ),
    )
    rng = random.Random(seed)
    drawn = [sample_duration(rng, low, low + 8, low + 16, "uniform") for _ in range(2)]
    expected = tuple(
        schedule_cpm(_bumped(schedule, "A", value), _REFERENCE).project_finish for value in drawn
    )
    assert outcome.finishes == expected
