"""The three YAML profiles load, and the index uses only scored metrics."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from atlaspmo.analysis.quality.check import evaluate
from atlaspmo.analysis.quality.profiles import load_profile
from test_cpm import _load, _task


def test_the_three_profiles_keep_their_thresholds() -> None:
    strict, strict_note = load_profile("dcma_estricto")
    corporate, corporate_note = load_profile("corporativo")
    contractor, contractor_note = load_profile("contratista")
    assert strict_note is None
    assert corporate_note is None
    assert contractor_note is None
    assert strict.id == "dcma_estricto"
    assert strict.fs_min == 0.90
    assert corporate.lags_max == 0.10
    assert contractor.logic_max == 0.10
    assert contractor.hard_constraints == frozenset({"CS_MANDSTART", "CS_MANDFIN"})


def test_the_index_ignores_metrics_that_cannot_be_scored(tmp_path: Path) -> None:
    schedule = _load(tmp_path, [_task("1", "A", "8"), _task("2", "B", "8")], [])
    activities = tuple(replace(item, total_float_hr_cnt=0) for item in schedule.activities)
    kept = frozenset(item for item in schedule.absent_columns if item != "TASK.total_float_hr_cnt")
    schedule = replace(schedule, activities=activities, absent_columns=kept)
    profile, _note = load_profile("dcma_estricto")
    metrics, _findings, _notes = evaluate(schedule, profile, None)
    assert metrics["logic"].status == "no_cumple"
    assert metrics["hard_constraints"].status == "cumple"
    assert metrics["leads"].status == "no_evaluable"
    assert metrics["resources"].status == "info"
    assert metrics["quality_index"].value == 100 * 5 / 6
    assert metrics["quality_index"].status == "info"
    only_logic = replace(profile, weights={"logic": 1.0})
    scored, _findings, _notes = evaluate(schedule, only_logic, None)
    assert scored["quality_index"].value == 0
