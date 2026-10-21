"""Extra M1 checks. A required WBS is not implemented and is not treated as a pass."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from atlaspmo.analysis.quality.check import evaluate
from atlaspmo.analysis.quality.profiles import load_profile
from test_cpm import _link, _load, _task


def _mixed(tmp_path: Path):
    schedule = _load(
        tmp_path,
        [
            _task("1", "LOE", "8", "TT_LOE"),
            _task("2", "DISC", "8"),
            _task("3", "P1", "8"),
            _task("4", "P2", "8"),
            _task("5", "P3", "8"),
            _task("6", "P4", "8"),
            _task("7", "JOIN", "8"),
        ],
        [
            _link("1", "1", "2", "PR_FS", "0"),
            _link("2", "3", "7", "PR_SF", "0"),
            _link("3", "4", "7", "PR_FS", "0"),
            _link("4", "5", "7", "PR_FS", "0"),
            _link("5", "6", "7", "PR_FS", "16"),
        ],
    )
    odd = replace(schedule.activities[1], clndr_id="C2")
    activities = (schedule.activities[0], odd, *schedule.activities[2:])
    return replace(schedule, activities=activities)


def _metrics(tmp_path: Path):
    profile, _note = load_profile("dcma_estricto")
    return evaluate(_mixed(tmp_path), profile, None)


def test_a_lag_longer_than_the_successor_is_counted(tmp_path: Path) -> None:
    metrics, _findings, _notes = _metrics(tmp_path)
    assert metrics["lag_vs_successor"].value == 1
    assert metrics["lag_vs_successor"].status == "info"
    assert metrics["lag_vs_successor"].threshold == 0


def test_an_sf_link_is_a_quality_finding(tmp_path: Path) -> None:
    metrics, findings, _notes = _metrics(tmp_path)
    assert metrics["sf_links"].value == 1
    assert metrics["sf_links"].status == "no_cumple"
    messages = findings.loc[findings["rule_id"] == "sf_links", "message_es"]
    assert messages.str.contains("inicio-fin").any()


def test_four_predecessors_count_as_convergence(tmp_path: Path) -> None:
    metrics, _findings, _notes = _metrics(tmp_path)
    assert metrics["convergence"].value == 1
    assert metrics["convergence"].threshold == 4
    assert metrics["convergence"].status == "info"


def test_a_calendar_other_than_the_dominant_one_is_counted(tmp_path: Path) -> None:
    metrics, _findings, _notes = _metrics(tmp_path)
    assert metrics["odd_calendar"].value == 1
    assert metrics["odd_calendar"].status == "info"


def test_loe_ahead_of_a_discrete_activity_fails(tmp_path: Path) -> None:
    metrics, _findings, _notes = _metrics(tmp_path)
    assert metrics["loe_logic"].value == 1
    assert metrics["loe_logic"].status == "no_cumple"


def test_codes_are_unevaluable_until_the_profile_requires_one(tmp_path: Path) -> None:
    metrics, findings, _notes = _metrics(tmp_path)
    assert metrics["missing_codes"].status == "no_evaluable"
    assert metrics["missing_codes"].value is None
    reason = findings.loc[findings["rule_id"] == "missing_codes", "message_es"]
    assert reason.str.contains("no exige códigos").any()
    profile, _note = load_profile("dcma_estricto")
    required = replace(profile, required_code_type_ids=("AREA",))
    again, _findings, _notes = evaluate(_mixed(tmp_path), required, None)
    assert again["missing_codes"].status == "no_cumple"
    assert again["missing_codes"].value == 7


def test_logic_density_is_reported_without_a_threshold(tmp_path: Path) -> None:
    metrics, _findings, _notes = _metrics(tmp_path)
    assert metrics["logic_density"].value == 5 / 7
    assert metrics["logic_density"].threshold is None
    assert metrics["logic_density"].status == "info"
