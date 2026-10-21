"""Invariant e: zero-variance Monte Carlo matches the deterministic CPM."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st
from tests.test_cpm import _PRED, _TASK, _link, _task, _week

from atlaspmo.analysis.risk.config import DurationRange, RiskConfig
from atlaspmo.analysis.risk.montecarlo import run_risk
from atlaspmo.engine.cpm import schedule_cpm
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.synthetic import encode_xer
from atlaspmo.io.xer import read_xer_bytes

_HOURS = st.sampled_from((8, 16))


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


@given(hours=_HOURS, seed=st.integers(min_value=0, max_value=5_000))
def test_zero_variance(hours: int, seed: int) -> None:
    schedule = _schedule(hours)
    base = schedule_cpm(schedule)
    width = float(hours)
    outcome = run_risk(
        schedule,
        RiskConfig(
            seed=seed,
            iterations=2,
            ranges=[
                DurationRange(task_code="A", low=width, mode=width, high=width),
                DurationRange(task_code="B", low=8, mode=8, high=8),
            ],
        ),
    )
    assert outcome.finishes == (base.project_finish,) * 2
