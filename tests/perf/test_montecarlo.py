"""A small Monte Carlo finishes. This is not the 30_000 by 1_000 criterion."""

from __future__ import annotations

import time
from pathlib import Path

import pytest
from tests.test_cpm import _link, _load, _task

from atlaspmo.analysis.risk.config import RiskConfig
from atlaspmo.analysis.risk.montecarlo import run_risk

pytestmark = pytest.mark.perf


def test_four_iterations_on_two_activities_finish(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8")],
        [_link("1", "1", "2")],
    )
    started = time.perf_counter()
    outcome = run_risk(schedule, RiskConfig(seed=1, iterations=4, tornado_hours=8))
    elapsed = time.perf_counter() - started
    assert len(outcome.finishes) == 4
    assert elapsed < 30
