"""DCMA checks on one hand network.

These asserts follow the code. They are not a double-signed P6 oracle.
SS overlap, a holiday, and a baseline signature are not covered here.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from pathlib import Path

from atlaspmo.analysis.contract import AnalysisContext
from atlaspmo.analysis.paths.mode_b import PathsBConfig, PathsModeB
from atlaspmo.analysis.quality.check import evaluate
from atlaspmo.analysis.quality.profiles import load_profile
from test_cpm import _link, _load, _task

BEFORE = datetime(2026, 1, 4, 8, 0)


def _network(tmp_path: Path):
    schedule = _load(
        tmp_path,
        [
            _task("1", "S", "0", "TT_Mile"),
            _task("2", "A", "8"),
            _task("3", "B", "400"),
            _task("4", "F", "0", "TT_FinMile"),
        ],
        [
            _link("1", "1", "2", "PR_FS", "0"),
            _link("2", "2", "3", "PR_FS", "8"),
            _link("3", "3", "4", "PR_SS", "-8"),
        ],
    )
    activities = (
        replace(schedule.activities[0], total_float_hr_cnt=0),
        replace(
            schedule.activities[1],
            total_float_hr_cnt=0,
            early_start_date=BEFORE,
            cstr_type="CS_MSO",
        ),
        replace(schedule.activities[2], total_float_hr_cnt=400),
        replace(schedule.activities[3], total_float_hr_cnt=-8),
    )
    kept = frozenset(item for item in schedule.absent_columns if item != "TASK.total_float_hr_cnt")
    return replace(schedule, activities=activities, absent_columns=kept)


def _run(tmp_path: Path):
    profile, note = load_profile("dcma_estricto")
    assert note is None
    return evaluate(_network(tmp_path), profile, None)


def test_logic_counts_incomplete_activities_missing_an_end(tmp_path: Path) -> None:
    metrics, _findings, _notes = _run(tmp_path)
    assert metrics["logic"].value == 0.5
    assert metrics["logic"].status == "no_cumple"


def test_leads_and_lags_are_shares_of_the_links(tmp_path: Path) -> None:
    metrics, _findings, _notes = _run(tmp_path)
    assert metrics["leads"].value == 1 / 3
    assert metrics["leads"].status == "no_cumple"
    assert metrics["lags"].value == 1 / 3
    assert metrics["lags"].status == "no_cumple"


def test_relationship_types_are_the_fs_share(tmp_path: Path) -> None:
    metrics, _findings, _notes = _run(tmp_path)
    assert metrics["relationship_types"].value == 2 / 3
    assert metrics["relationship_types"].status == "no_cumple"


def test_one_hard_constraint_is_a_quarter_of_the_population(tmp_path: Path) -> None:
    metrics, _findings, _notes = _run(tmp_path)
    assert metrics["hard_constraints"].value == 0.25
    assert metrics["hard_constraints"].status == "no_cumple"


def test_high_float_and_negative_float_use_calendar_days(tmp_path: Path) -> None:
    metrics, _findings, _notes = _run(tmp_path)
    assert metrics["high_float"].value == 0.25
    assert metrics["high_float"].status == "no_cumple"
    assert metrics["negative_float"].value == 0.25
    assert metrics["negative_float"].status == "no_cumple"


def test_high_duration_skips_milestones(tmp_path: Path) -> None:
    metrics, _findings, _notes = _run(tmp_path)
    assert metrics["high_duration"].value == 0.5
    assert metrics["high_duration"].status == "no_cumple"


def test_an_early_date_before_the_data_date_is_invalid(tmp_path: Path) -> None:
    metrics, findings, _notes = _run(tmp_path)
    assert metrics["invalid_dates"].value == 1
    assert metrics["invalid_dates"].status == "no_cumple"
    messages = findings.loc[findings["rule_id"] == "invalid_dates", "message_es"]
    assert messages.str.contains("early_start_date").any()


def test_resources_stay_informational_when_the_profile_has_no_limit(tmp_path: Path) -> None:
    metrics, _findings, _notes = _run(tmp_path)
    assert metrics["resources"].value == 1
    assert metrics["resources"].status == "info"
    assert metrics["resources"].threshold is None


def test_missing_baseline_is_not_a_zero(tmp_path: Path) -> None:
    metrics, findings, _notes = _run(tmp_path)
    for rule_id in ("missed_tasks", "bei"):
        assert metrics[rule_id].value is None
        assert metrics[rule_id].status == "no_evaluable"
        messages = findings.loc[findings["rule_id"] == rule_id, "message_es"]
        assert messages.str.contains("baseline").any()
    assert metrics["cpli"].value is None
    assert metrics["cpli"].status == "no_evaluable"
    cpli = findings.loc[findings["rule_id"] == "cpli", "message_es"]
    assert cpli.str.contains("fecha objetivo").any()


def test_evaluate_does_not_run_the_critical_path_test(tmp_path: Path) -> None:
    metrics, _findings, _notes = _run(tmp_path)
    assert "cp_test" not in metrics


def test_critical_path_test_on_a_two_activity_chain(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "16")],
        [_link("1", "1", "2")],
    )
    result = PathsModeB().run(AnalysisContext(schedule=schedule), PathsBConfig())
    assert result.metrics["cp_test"].status == "cumple"
