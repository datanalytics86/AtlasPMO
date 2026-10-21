"""Percentiles and convergence on a zero-variance join. Not a P6 signature."""

from __future__ import annotations

from pathlib import Path

from atlaspmo.analysis.risk.config import DurationRange, RiskConfig
from atlaspmo.analysis.risk.montecarlo import run_risk
from atlaspmo.engine.cpm import schedule_cpm
from test_cpm import _link, _load, _task


def test_percentiles_and_the_join_match_the_deterministic_finish(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "C", "8"), _task("3", "JOIN", "8")],
        [_link("1", "1", "3"), _link("2", "2", "3")],
    )
    config = RiskConfig(
        seed=4,
        iterations=4,
        ranges=[
            DurationRange(task_code="A", low=8, mode=8, high=8),
            DurationRange(task_code="C", low=8, mode=8, high=8),
            DurationRange(task_code="JOIN", low=8, mode=8, high=8),
        ],
    )
    base = schedule_cpm(schedule)
    outcome = run_risk(schedule, config)
    project = next(item for item in outcome.milestones if item.task_code == "proyecto")
    assert project.p50 == project.p80 == project.p90 == base.project_finish
    row = next(item for item in outcome.convergence if item.task_code == "JOIN")
    assert row.deterministic_finish == row.p50_finish == base.by_id["3"].early_finish
