"""Library trend keeps insertion order. It is not a trend of real schedules."""

from __future__ import annotations

from pathlib import Path

from atlaspmo.analysis.contract import Metric, ModuleResult, RunMetadata, empty_findings
from atlaspmo.library.store import Library


def _result(index: float) -> ModuleResult:
    return ModuleResult(
        module_id="quality",
        metrics={"quality_index": Metric(index, None, "info")},
        findings=empty_findings(),
        tables={},
        approximations=[],
        metadata=RunMetadata(app_version="test"),
    )


def test_trend_follows_insertion_order(tmp_path: Path) -> None:
    library = Library(tmp_path / "lib.duckdb")
    try:
        first = library.save_run([_result(10)], input_name="uno.xer")
        second = library.save_run([_result(20)], input_name="dos.xer")
        assert library.trend("quality_index") == [(first, 10.0), (second, 20.0)]
    finally:
        library.close()
