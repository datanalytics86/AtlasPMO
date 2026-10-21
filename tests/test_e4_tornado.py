"""The tornado still reschedules the whole network once per activity."""

from __future__ import annotations

from pathlib import Path

from atlaspmo.analysis.risk.config import RiskConfig
from atlaspmo.analysis.risk.montecarlo import run_risk
from test_cpm import _link, _load, _task


def test_every_activity_is_rescheduled(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8"), _task("3", "C", "8")],
        [_link("1", "1", "2"), _link("2", "2", "3")],
    )
    outcome = run_risk(schedule, RiskConfig(seed=1, iterations=1, tornado_hours=8))
    assert {item.task_code for item in outcome.tornado} == {"A", "B", "C"}
    text = " ".join(outcome.approximations)
    assert "cronograma completo" in text
    assert "No recorta al cono" in text
