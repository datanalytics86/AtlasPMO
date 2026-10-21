"""MSPDI, update comparison, batch ranking, DuckDB, Parquet and PBIP."""

from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

import duckdb
import pandas as pd
import pytest

from atlaspmo.analysis.compare.diff import compare_schedules
from atlaspmo.analysis.compare.module import CompareModule
from atlaspmo.analysis.contract import (
    FINDING_COLUMNS,
    AnalysisContext,
    Metric,
    ModuleResult,
    RunMetadata,
)
from atlaspmo.batch import BatchRow, rank_rows, run_folder, write_ranking
from atlaspmo.io.mpp import MppUnavailable, read_mpp
from atlaspmo.io.mspdi import schedule_from_mspdi
from atlaspmo.io.synthetic import write_xer
from atlaspmo.library.store import Library
from atlaspmo.model.schedule import Activity, Project, Relationship, Schedule
from atlaspmo.reports.parquet_star import write_star
from atlaspmo.reports.pbip import write_pbip

ROOT = Path(__file__).resolve().parents[1]
CHAIN = ROOT / "tests" / "fixtures" / "synthetic" / "mspdi" / "chain.xml"


def test_mspdi_chain_skips_the_summary_task():
    schedule = schedule_from_mspdi(CHAIN)
    assert [item.task_code for item in schedule.activities] == ["A", "B"]
    assert schedule.activities[0].remain_drtn_hr_cnt == 8
    assert schedule.activities[1].remain_drtn_hr_cnt == 16
    assert schedule.relationships[0].pred_type == "PR_FS"
    assert schedule.relationships[0].lag_hr_cnt == 0
    assert schedule.projects[0].last_recalc_date == datetime(2026, 1, 5, 8, 0)
    assert "0" not in {item.task_id for item in schedule.activities}


def test_mspdi_lag_is_tenths_of_a_minute(tmp_path: Path):
    path = tmp_path / "lag.xml"
    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
        <Project xmlns="http://schemas.microsoft.com/project">
          <Name>Lag</Name>
          <StatusDate>2026-01-05T08:00:00</StatusDate>
          <Tasks>
            <Task><UID>1</UID><Name>A</Name><WBS>A</WBS>
              <Duration>P1DT2H</Duration><RemainingDuration>PT1H30M</RemainingDuration>
            </Task>
            <Task><UID>2</UID><Name>B</Name><WBS>B</WBS>
              <PredecessorLink>
                <PredecessorUID>1</PredecessorUID><Type>3</Type><LinkLag>600</LinkLag>
              </PredecessorLink>
            </Task>
          </Tasks>
        </Project>
        """,
        encoding="utf-8",
    )
    schedule = schedule_from_mspdi(path)
    assert schedule.activities[0].target_drtn_hr_cnt == 26
    assert schedule.activities[0].remain_drtn_hr_cnt == 1.5
    assert schedule.relationships[0].pred_type == "PR_SS"
    assert schedule.relationships[0].lag_hr_cnt == 1
    assert any("24 horas" in note for note in schedule.parse_notes)


def test_mpp_is_skipped_without_the_extra():
    with pytest.raises(MppUnavailable, match="Java"):
        read_mpp(Path("missing.mpp"))


def test_compare_reports_the_hand_differences():
    left = _schedule(
        (
            _act("1", "A", remain=8, total_float=0),
            _act("2", "B", remain=16),
            _act("3", "D", total_float=16),
        ),
        (_link("1", "2", "1", "PR_FS", 0),),
    )
    changed = _act(
        "1",
        "A",
        remain=16,
        total_float=8,
        cstr="CS_MSO",
        calendar="C2",
        actual=datetime(2026, 1, 5, 8),
    )
    right = _schedule((changed, _act("4", "C"), _act("3", "D", total_float=0)), ())
    report = compare_schedules(left, right)
    assert report.added == 1
    assert report.removed == 1
    assert report.links_removed == 1
    assert report.remain_changed == 1
    assert report.constraint_changed == 1
    assert report.calendar_changed == 1
    assert report.actuals_changed == 1
    assert report.critical_exit == 1
    assert report.critical_enter == 1
    assert report.float_eroded == 1
    result = CompareModule().run(
        AnalysisContext(schedule=left, other=right),
        CompareModule.config_model(),
    )
    assert result.metrics["added"].value == 1


def test_changed_link_is_not_a_new_link():
    left = _schedule((_act("1", "A"), _act("2", "B")), (_link("1", "2", "1", "PR_FS", 0),))
    right = _schedule((_act("1", "A"), _act("2", "B")), (_link("1", "2", "1", "PR_SS", 8),))
    report = compare_schedules(left, right)
    assert report.links_changed == 1
    assert report.links_added == 0
    assert report.links_removed == 0


def test_ranking_puts_the_higher_index_first(tmp_path: Path):
    ordered = rank_rows([BatchRow("b.xer", 10), BatchRow("c.xer", None), BatchRow("a.xer", 90)])
    assert [item.name for item in ordered] == ["a.xer", "b.xer", "c.xer"]
    for name in ("a.xer", "b.xer"):
        _xer(tmp_path / name)
    rows = run_folder(tmp_path)
    assert {item.name for item in rows} == {"a.xer", "b.xer"}
    assert rows == rank_rows(rows)
    book = tmp_path / "ranking.xlsx"
    write_ranking(book, rows)
    shared = ZipFile(book).read("xl/sharedStrings.xml").decode("utf-8")
    assert "a.xer" in shared
    assert "b.xer" in shared


def test_library_keeps_metrics_and_skips_the_schedule(tmp_path: Path):
    library = Library(tmp_path / "atlas.duckdb")
    try:
        library.save_run([_result(80)], input_name="uno.xer")
        quiet = _schedule((_act("1", "A"),), ())
        library.save_run([_result(50)], schedule=quiet, store_schedule=False)
        assert [value for _run, value in library.trend("quality_index")] == [80, 50]
        assert library.activity_count() == 0
        library.save_run([_result(70)], schedule=quiet, store_schedule=True)
        assert library.activity_count() == 1
    finally:
        library.close()


def test_star_parquet_and_pbip(tmp_path: Path):
    folder = tmp_path / "parquet"
    written = write_star(folder, [_result(80)], project_name="Cadena", run_id="run-1")
    assert set(written) == {
        "dim_project",
        "dim_run",
        "dim_activity",
        "dim_rule",
        "fact_finding",
        "fact_timephased",
        "fact_risk",
    }
    con = duckdb.connect()
    try:
        findings = _count(con, written["fact_finding"])
        phased = _count(con, written["fact_timephased"])
        risk = _count(con, written["fact_risk"])
    finally:
        con.close()
    assert findings == 1
    assert phased == 0
    assert risk == 0
    pbip = write_pbip(tmp_path / "pbip", folder)
    text = pbip.read_text(encoding="utf-8")
    assert "AtlasPMO.Report" in text
    report = (tmp_path / "pbip" / "AtlasPMO.Report" / "definition.pbir").read_text(encoding="utf-8")
    assert "../AtlasPMO.SemanticModel" in report
    model = tmp_path / "pbip" / "AtlasPMO.SemanticModel"
    assert '"version": "4.2"' in (model / "definition.pbism").read_text(encoding="utf-8")
    expression = (model / "definition" / "expressions.tmdl").read_text(encoding="utf-8")
    assert "ParquetFolder" in expression
    relations = (model / "definition" / "relationships.tmdl").read_text(encoding="utf-8")
    assert "fact_finding.run_id" in relations
    table = model / "definition" / "tables" / "fact_finding.tmdl"
    assert "Hallazgos" in table.read_text(encoding="utf-8")


def _count(con: duckdb.DuckDBPyConnection, path: Path) -> int:
    target = str(path).replace("\\", "/")
    row = con.execute(f"SELECT COUNT(*) FROM read_parquet('{target}')").fetchone()
    return int(row[0]) if row else 0


def _result(index: float) -> ModuleResult:
    row = {column: None for column in FINDING_COLUMNS}
    row.update(
        {
            "rule_id": "logic",
            "rule_name_es": "Lógica",
            "source": "DCMA",
            "severity": "media",
            "object_type": "project",
            "object_id": "1",
            "task_code": "A",
            "value": index,
            "threshold": 5,
            "passed": False,
            "message_es": "Ejemplo.",
        }
    )
    return ModuleResult(
        module_id="quality",
        metrics={"quality_index": Metric(index, None, "info")},
        findings=pd.DataFrame([row]),
        tables={},
        approximations=[],
        metadata=RunMetadata(app_version="0.1.0", seed=7),
    )


def _xer(path: Path) -> None:
    write_xer(
        path,
        "ERMHDR",
        [
            {
                "name": "PROJECT",
                "fields": ["proj_id", "last_recalc_date"],
                "rows": [["1", "2026-01-05 08:00"]],
            },
            {
                "name": "TASK",
                "fields": ["task_id", "proj_id", "task_code", "status_code", "task_type"],
                "rows": [["1", "1", "A", "TK_NotStart", "TT_Task"]],
            },
        ],
    )


def _schedule(activities: tuple[Activity, ...], links: tuple[Relationship, ...]) -> Schedule:
    return Schedule(
        projects=(Project("1", "P", "P", "C1", datetime(2026, 1, 5, 8), None, None),),
        calendars=(),
        wbs=(),
        activities=activities,
        relationships=links,
        assignments=(),
        activity_codes=(),
    )


def _act(
    task_id: str,
    code: str,
    remain: float = 8,
    total_float: float = 0,
    cstr: str | None = None,
    calendar: str = "C1",
    actual: datetime | None = None,
) -> Activity:
    return Activity(
        task_id=task_id,
        proj_id="1",
        wbs_id="W1",
        clndr_id=calendar,
        task_code=code,
        task_name=code,
        task_type="TT_Task",
        status_code="TK_NotStart",
        complete_pct_type=None,
        cstr_type=cstr,
        cstr_type2=None,
        target_drtn_hr_cnt=8,
        remain_drtn_hr_cnt=remain,
        total_float_hr_cnt=total_float,
        free_float_hr_cnt=None,
        target_start_date=None,
        target_end_date=None,
        act_start_date=actual,
        act_end_date=None,
        early_start_date=None,
        early_end_date=None,
        late_start_date=None,
        late_end_date=None,
        float_path=None,
        float_path_order=None,
        int_path=None,
        int_path_order=None,
        phys_complete_pct=None,
    )


def _link(link_id: str, succ: str, pred: str, kind: str, lag: float) -> Relationship:
    return Relationship(link_id, succ, pred, "1", "1", kind, lag)
