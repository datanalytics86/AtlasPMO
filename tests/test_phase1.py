"""Phase 1: round trip, hand-calculated quality, validation, reports."""

from __future__ import annotations

import time
from pathlib import Path

import pytest
import yaml
from scripts.sanitize_fixture import sanitize

from atlaspmo.analysis.contract import AnalysisContext
from atlaspmo.analysis.paths.mode_a import PathsConfig, PathsModeA
from atlaspmo.analysis.quality.module import QualityConfig, QualityModule
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.p6xml import schedule_from_p6xml
from atlaspmo.io.synthetic import write_xer
from atlaspmo.io.validate import validate_schedule
from atlaspmo.io.xer import read_xer
from atlaspmo.reports.export import write_excel, write_manifest, write_pdf

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "tests" / "fixtures" / "synthetic" / "cases"


def _quality(name: str, proj_id: str | None = None, baseline_proj_id: str | None = None):
    document = read_xer(CASES / name)
    schedule = schedule_from_xer(document)
    config = QualityConfig(proj_id=proj_id, baseline_proj_id=baseline_proj_id)
    result = QualityModule().run(AnalysisContext(schedule=schedule), config)
    return document, schedule, result


@pytest.mark.parametrize("spec_path", sorted(CASES.glob("*.yaml")))
def test_hand_calculated_metrics(spec_path: Path):
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    _document, _schedule, result = _quality(
        spec["file"],
        spec.get("proj_id"),
        spec.get("baseline_proj_id"),
    )
    for key, expected in spec["expect"].items():
        metric = result.metrics[key]
        assert metric.status == expected["status"], key
        if expected["value"] is None:
            assert metric.value is None
        else:
            assert metric.value == pytest.approx(expected["value"])


def test_round_trip_cases():
    for path in sorted(CASES.glob("*.xer")):
        original = path.read_bytes()
        assert read_xer(path).to_bytes() == original


def test_drop_taskpred_keeps_other_lines():
    path = CASES / "chain.xer"
    document = read_xer(path)
    table = document.table("TASKPRED")
    assert table is not None
    target = table.rows[0].line_index
    cleaned = document.drop_rows("TASKPRED", {target})
    assert cleaned.to_bytes().count(b"%R") == document.to_bytes().count(b"%R") - 1
    assert b"ERMHDR" in cleaned.to_bytes()


def test_cycle_is_reported():
    document = read_xer(CASES / "cycle.xer")
    issues = validate_schedule(schedule_from_xer(document))
    cycle = [
        item
        for item in issues
        if item.code == "cycle" and "A" in item.message_es and "B" in item.message_es
    ]
    assert cycle


def test_mode_a_marks_negative_float_critical():
    document = read_xer(CASES / "floatdur.xer")
    result = PathsModeA().run(
        AnalysisContext(schedule=schedule_from_xer(document)),
        PathsConfig(),
    )
    frame = result.tables["bands"]
    critical = set(frame.loc[frame["critical"], "task_code"])
    assert critical == {"A", "C"}


def test_p6xml_maps_status():
    schedule = schedule_from_p6xml(ROOT / "tests" / "fixtures" / "synthetic" / "minimal.xml")
    assert schedule.activities[0].task_code == "A1"
    assert schedule.activities[0].status_code == "TK_NotStart"
    assert schedule.activities[0].task_type == "TT_Task"
    assert schedule.relationships[0].pred_type == "PR_FS"


def test_sanitize_clears_header_and_user_column(tmp_path: Path):
    source = tmp_path / "named.xer"
    write_xer(
        source,
        "ERMHDR\t20.12\tNicolás\tP6DB",
        [
            {
                "name": "TASK",
                "fields": ["task_id", "create_user"],
                "rows": [["1", "Nicolás"]],
            }
        ],
    )
    cleaned = sanitize(source.read_bytes()).decode("cp1252")
    assert "Nicolás" not in cleaned
    assert "P6DB" not in cleaned
    assert "ANON" in cleaned


def test_reports_write(tmp_path: Path):
    _document, _schedule, result = _quality("chain.xer")
    excel = tmp_path / "out.xlsx"
    pdf = tmp_path / "out.pdf"
    manifest = tmp_path / "run_manifest.json"
    write_excel(excel, [result])
    write_pdf(pdf, [result])
    write_manifest(manifest, [result], CASES / "chain.xer", ROOT)
    assert excel.stat().st_size > 0
    assert pdf.stat().st_size > 0
    assert "quality" in manifest.read_text(encoding="utf-8")


def test_external_relationship_is_marked(tmp_path: Path):
    path = tmp_path / "external.xer"
    task_fields = ["task_id", "proj_id", "task_code", "status_code", "target_start_date"]
    pred_fields = [
        "task_pred_id",
        "task_id",
        "pred_task_id",
        "proj_id",
        "pred_proj_id",
        "pred_type",
        "lag_hr_cnt",
    ]
    write_xer(
        path,
        "ERMHDR",
        [
            {"name": "PROJECT", "fields": ["proj_id"], "rows": [["1"], ["2"]]},
            {
                "name": "TASK",
                "fields": task_fields,
                "rows": [
                    ["10", "1", "A", "TK_NotStart", "2026-01-01 00:00"],
                    ["20", "2", "B", "TK_NotStart", "2026-01-01 00:00"],
                ],
            },
            {
                "name": "TASKPRED",
                "fields": pred_fields,
                "rows": [["1", "20", "10", "2", "1", "PR_FS", "0"]],
            },
        ],
    )
    issues = validate_schedule(schedule_from_xer(read_xer(path)))
    assert any(item.code == "external_relationship" for item in issues)


def test_read_30k_under_15_seconds(tmp_path: Path):
    rows = [[str(index), f"A{index}"] for index in range(30_000)]
    path = tmp_path / "scale.xer"
    write_xer(path, "ERMHDR", [{"name": "TASK", "fields": ["task_id", "task_code"], "rows": rows}])
    started = time.perf_counter()
    document = read_xer(path)
    elapsed = time.perf_counter() - started
    assert len(document.table("TASK").rows) == 30_000
    assert elapsed < 15
