"""Remaining hours follow the early schedule, one working day at a time."""

from __future__ import annotations

from pathlib import Path

from atlaspmo.analysis.contract import AnalysisContext
from atlaspmo.analysis.resources.module import EvmConfig, EvmModule
from test_cpm import _link, _load, _task


def test_remaining_hours_follow_the_fs_chain(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "16")],
        [_link("1", "1", "2")],
    )
    result = EvmModule().run(AnalysisContext(schedule=schedule), EvmConfig())
    text = " ".join(result.approximations).lower()
    assert "balde corte" not in text
    assert "no es una curva por periodo" not in text
    assert "distribución es lineal en tiempo laboral" in text
    frame = result.tables["days"].sort_values(["task_code", "bucket"])
    rows = [(row.task_code, row.bucket, row.hours) for row in frame.itertuples(index=False)]
    assert rows == [
        ("A", "2026-01-05", 8.0),
        ("B", "2026-01-06", 8.0),
        ("B", "2026-01-07", 8.0),
    ]
    assert float(frame["hours"].sum()) == 24.0
