"""A risk run keeps the seed, the version and the parameters."""

from __future__ import annotations

from pathlib import Path

from atlaspmo import __version__
from atlaspmo.analysis.contract import AnalysisContext
from atlaspmo.analysis.risk.config import RiskConfig
from atlaspmo.analysis.risk.module import RiskModule
from test_cpm import _load, _task


def test_the_manifest_records_seed_and_iteration_count(tmp_path: Path) -> None:
    schedule = _load(tmp_path, [_task("1", "A", "8")], [])
    result = RiskModule().run(
        AnalysisContext(schedule=schedule, input_sha256="abc"),
        RiskConfig(seed=3, iterations=2),
    )
    assert result.metadata.app_version == __version__
    assert result.metadata.seed == 3
    assert result.metadata.input_sha256 == "abc"
    assert result.metadata.parameters["iterations"] == "2"
    assert result.approximations
