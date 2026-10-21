"""BEI counts every activity already complete, including early finishes."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from pathlib import Path

from atlaspmo.analysis.quality.check import evaluate
from atlaspmo.analysis.quality.profiles import load_profile
from test_cpm import _load, _task

DATA = datetime(2026, 2, 1, 0, 0)
EARLY = datetime(2026, 1, 5, 16, 0)


def test_bei_includes_a_completion_whose_baseline_is_still_ahead(tmp_path: Path) -> None:
    current = _load(
        tmp_path,
        [
            _task("1", "LATE", "0", status="TK_Complete", act_end="2026-01-12 08:00"),
            _task("2", "OPEN", "8"),
            _task("3", "EARLY", "0", status="TK_Complete", act_end="2026-01-05 16:00"),
        ],
        [],
    )
    current = replace(current, projects=(replace(current.projects[0], last_recalc_date=DATA),))
    kept = frozenset(item for item in current.absent_columns if item != "TASK.target_end_date")
    baseline = replace(
        current,
        absent_columns=kept,
        activities=(
            replace(current.activities[0], target_end_date=datetime(2026, 1, 10, 8, 0)),
            replace(current.activities[1], target_end_date=datetime(2026, 1, 20, 8, 0)),
            replace(current.activities[2], target_end_date=datetime(2026, 3, 1, 8, 0)),
        ),
    )
    profile, _note = load_profile("dcma_estricto")
    metrics, _findings, _notes = evaluate(current, profile, baseline)
    # Due are LATE and OPEN. Complete as of the data date are LATE and EARLY.
    assert metrics["bei"].value == 2 / 2
    assert metrics["bei"].status == "cumple"
    assert EARLY <= DATA
