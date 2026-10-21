"""GAO statuses follow the automated checks. Items 6 and 8 stay manual."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from atlaspmo.analysis.quality.check import evaluate
from atlaspmo.analysis.quality.profiles import load_profile
from test_cpm import _link, _load, _task


def _chain(tmp_path: Path, started: bool = False):
    schedule = _load(
        tmp_path,
        [
            _task("1", "A", "8", act_start="2026-01-05 08:00" if started else ""),
            _task("2", "B", "8"),
        ],
        [_link("1", "1", "2")],
    )
    activities = tuple(replace(item, total_float_hr_cnt=0) for item in schedule.activities)
    kept = frozenset(item for item in schedule.absent_columns if item != "TASK.total_float_hr_cnt")
    schedule = replace(schedule, activities=activities, absent_columns=kept)
    profile, _note = load_profile("dcma_estricto")
    return evaluate(schedule, profile, None)


def test_gao_items_on_a_two_activity_chain(tmp_path: Path) -> None:
    metrics, findings, _notes = _chain(tmp_path)
    assert metrics["gao_01"].status == "cumple"
    assert metrics["gao_02"].status == "no_cumple"
    assert metrics["gao_03"].status == "manual"
    assert metrics["gao_04"].status == "cumple"
    assert metrics["gao_05"].status == "cumple"
    assert metrics["gao_06"].status == "manual"
    assert metrics["gao_07"].status == "cumple"
    assert metrics["gao_08"].status == "manual"
    assert metrics["gao_09"].status == "manual"
    assert metrics["gao_10"].status == "manual"
    manual = findings.loc[findings["rule_id"].isin(["gao_06", "gao_08"]), "message_es"]
    assert set(manual) == {"Requiere revisión manual."}
    assert metrics["gao_06"].value is None
    assert metrics["gao_08"].value is None


def test_an_actual_start_marks_the_progress_check(tmp_path: Path) -> None:
    metrics, _findings, _notes = _chain(tmp_path, started=True)
    assert metrics["gao_09"].status == "cumple"


def test_an_empty_schedule_fails_activity_capture(tmp_path: Path) -> None:
    schedule = _load(tmp_path, [_task("1", "A", "8")], [])
    schedule = replace(schedule, activities=())
    profile, _note = load_profile("dcma_estricto")
    metrics, _findings, _notes = evaluate(schedule, profile, None)
    assert metrics["gao_01"].status == "no_cumple"
