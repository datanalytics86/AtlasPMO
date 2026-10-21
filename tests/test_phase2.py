"""Redundant logic, cleaning, CP test, conformance and Gantt."""

from pathlib import Path

from scripts.run_conformance import main as conformance_main

from atlaspmo.analysis.contract import AnalysisContext
from atlaspmo.analysis.logic.clean import clean_document
from atlaspmo.analysis.logic.redundant import classify_links
from atlaspmo.analysis.paths.mode_b import PathsBConfig, PathsModeB
from atlaspmo.engine.conformance import conformance
from atlaspmo.engine.cpm import schedule_cpm
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.synthetic import write_xer
from atlaspmo.io.xer import read_xer
from atlaspmo.reports.gantt import gantt_figure
from test_cpm import DATA, MON_8, MON_16, WED_16, _link, _load, _task


def _chain(tmp_path: Path):
    return _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8"), _task("3", "C", "8")],
        [_link("1", "1", "2"), _link("2", "2", "3"), _link("3", "1", "3")],
    )


def test_shortcut_is_confirmed_redundant(tmp_path: Path):
    schedule = _chain(tmp_path)
    classes, _base = classify_links(schedule)
    by_id = {item.task_pred_id: item.status for item in classes}
    assert by_id["3"] == "redundante_confirmado"
    assert by_id["1"] == "no_candidato"
    assert by_id["2"] == "no_candidato"


def test_ss_ff_pair_is_protected(tmp_path: Path):
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8")],
        [_link("1", "1", "2", "PR_SS", "0"), _link("2", "1", "2", "PR_FF", "0")],
    )
    classes, _base = classify_links(schedule)
    assert {item.status for item in classes} == {"protegido"}


def test_clean_removes_only_the_shortcut_and_dates_stay(tmp_path: Path):
    path = tmp_path / "case.xer"
    schedule = _chain(tmp_path)
    # _load already wrote case.xer
    document = read_xer(path)
    cleaned, before, after, removed = clean_document(document, schedule)
    assert removed == 1
    assert cleaned.to_bytes().count(b"%R") == document.to_bytes().count(b"%R") - 1
    assert b"ERMHDR" in cleaned.to_bytes()
    for task_id in ("1", "2", "3"):
        assert before.by_id[task_id].early_start == after.by_id[task_id].early_start
        assert before.by_id[task_id].early_finish == after.by_id[task_id].early_finish
        assert before.by_id[task_id].late_start == after.by_id[task_id].late_start
        assert before.by_id[task_id].total_float_hours == after.by_id[task_id].total_float_hours


def test_cp_test_passes_on_the_critical_chain(tmp_path: Path):
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "16")],
        [_link("1", "1", "2")],
    )
    result = PathsModeB().run(AnalysisContext(schedule=schedule), PathsBConfig())
    assert result.metrics["cp_test"].status == "cumple"
    assert len(result.tables["cpm"]) == 2
    figure = gantt_figure(result.tables["cpm"])
    assert len(figure.data) == 2


def test_conformance_is_exact_when_stored_dates_match(tmp_path: Path):
    fields = [
        "task_id",
        "proj_id",
        "clndr_id",
        "task_code",
        "task_type",
        "status_code",
        "remain_drtn_hr_cnt",
        "early_start_date",
        "early_end_date",
        "late_start_date",
        "late_end_date",
        "total_float_hr_cnt",
        "free_float_hr_cnt",
    ]
    path = tmp_path / "stored.xer"
    write_xer(
        path,
        "ERMHDR",
        [
            {
                "name": "PROJECT",
                "fields": ["proj_id", "clndr_id", "last_recalc_date"],
                "rows": [["1", "C1", DATA]],
            },
            {
                "name": "CALENDAR",
                "fields": ["clndr_id", "clndr_data"],
                "rows": [["C1", _week()]],
            },
            {
                "name": "TASK",
                "fields": fields,
                "rows": [
                    [
                        "1",
                        "1",
                        "C1",
                        "A",
                        "TT_Task",
                        "TK_NotStart",
                        "8",
                        "2026-01-05 08:00",
                        "2026-01-05 16:00",
                        "2026-01-05 08:00",
                        "2026-01-06 08:00",
                        "0",
                        "0",
                    ],
                    [
                        "2",
                        "1",
                        "C1",
                        "B",
                        "TT_Task",
                        "TK_NotStart",
                        "16",
                        "2026-01-06 08:00",
                        "2026-01-07 16:00",
                        "2026-01-06 08:00",
                        "2026-01-07 16:00",
                        "0",
                        "0",
                    ],
                ],
            },
            {
                "name": "TASKPRED",
                "fields": ["task_pred_id", "task_id", "pred_task_id", "pred_type", "lag_hr_cnt"],
                "rows": [["1", "2", "1", "PR_FS", "0"]],
            },
        ],
    )
    report = conformance(schedule_from_xer(read_xer(path)))
    assert report.compared > 0
    assert report.ratio == 1
    assert schedule_cpm(schedule_from_xer(read_xer(path))).by_id["1"].early_start == MON_8
    assert schedule_cpm(schedule_from_xer(read_xer(path))).by_id["1"].early_finish == MON_16
    assert schedule_cpm(schedule_from_xer(read_xer(path))).by_id["2"].early_finish == WED_16


def _week() -> str:
    days = "".join(f"(0||{number}()((0||0(s|08:00|f|16:00)())))" for number in range(1, 8))
    return f"(0||CalendarData()((0||DaysOfWeek()({days}))(0||VIEW(ShowTotal|N)())))"


def test_script_skips_missing_golden(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("ATLASPMO_GOLDEN_DIR", raising=False)
    assert conformance_main([str(tmp_path)]) == 0
