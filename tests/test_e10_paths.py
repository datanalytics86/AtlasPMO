"""Contract float paths and the mode A activity flag. Not a P6 export."""

from __future__ import annotations

import inspect
from dataclasses import replace
from pathlib import Path

import pandas as pd

from atlaspmo.analysis.contract import AnalysisContext, ModuleResult
from atlaspmo.analysis.paths import mode_a
from atlaspmo.analysis.paths.mode_a import PathsConfig, PathsModeA
from atlaspmo.analysis.paths.mode_b import PathsBConfig, PathsModeB
from atlaspmo.engine.cpm import schedule_cpm_reference
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.synthetic import write_xer
from atlaspmo.io.xer import read_xer
from atlaspmo.model.schedule import Schedule
from test_cpm import _PRED, _TASK, _link, _load, _task, _week

_NOT_CALCULATED = "Multiple float paths no se calculan"
_NOT_CHECKED = "La continuidad desde la fecha de corte hasta el término no se verifica"
_LINKS = "Los vínculos driving no se marcan en modo A"


def _notes(result: ModuleResult) -> str:
    return " ".join(result.approximations)


def _ordered(frame: pd.DataFrame, number: int) -> list[tuple[str, int]]:
    chosen = frame.loc[frame["float_path"] == number].sort_values("float_path_order")
    return [
        (str(row.task_code), int(row.float_path_order)) for row in chosen.itertuples(index=False)
    ]


def test_contract_paths_number_long_then_join_and_then_short(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [
            _task("1", "SHORT", "8"),
            _task("2", "LONG", "16"),
            _task("3", "JOIN", "8"),
            _task("4", "LOE", "8", kind="TT_LOE"),
            _task("5", "WBS", "8", kind="TT_WBS"),
        ],
        [_link("1", "1", "3"), _link("2", "2", "3")],
    )
    result = PathsModeB().run(AnalysisContext(schedule=schedule), PathsBConfig())
    text = _notes(result)
    assert _NOT_CALCULATED not in text
    assert _NOT_CHECKED not in text
    paths = result.tables["float_paths"]
    assert _ordered(paths, 1) == [("LONG", 1), ("JOIN", 2)]
    assert _ordered(paths, 2) == [("SHORT", 1)]
    assert set(paths["task_code"]).isdisjoint({"LOE", "WBS"})
    rows = result.tables["cpm"].set_index("task_code")
    assert rows.loc["JOIN", "driving_codes"] == "LONG"


def test_path_one_is_continuous_from_the_reference_start(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8"), _task("3", "C", "8")],
        [_link("1", "1", "2"), _link("2", "2", "3")],
    )
    reference = schedule_cpm_reference(schedule)
    by_code = {item.task_code: item.task_id for item in schedule.activities}
    start = reference.by_id[by_code["A"] or ""].early_start
    finish = reference.by_id[by_code["C"] or ""].early_finish
    assert schedule.projects[0].last_recalc_date == start
    assert finish == reference.project_finish
    result = PathsModeB().run(AnalysisContext(schedule=schedule), PathsBConfig())
    assert _ordered(result.tables["float_paths"], 1) == [("A", 1), ("B", 2), ("C", 3)]
    assert result.metrics["continuity"].status == "verdadera"
    assert result.metrics["continuity"].value == 1.0
    assert _NOT_CHECKED not in _notes(result)


def test_a_start_on_after_the_data_date_breaks_continuity(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "SOLO", "8", cstr="CS_MSO", cstr_date="2026-01-07 08:00")],
        [],
    )
    reference = schedule_cpm_reference(schedule)
    start = reference.by_id["1"].early_start
    cutoff = schedule.projects[0].last_recalc_date
    assert cutoff is not None
    assert start > cutoff
    result = PathsModeB().run(AnalysisContext(schedule=schedule), PathsBConfig())
    assert _ordered(result.tables["float_paths"], 1) == [("SOLO", 1)]
    assert result.metrics["continuity"].status == "falsa"
    assert result.metrics["continuity"].value != 1.0
    assert "quiebre" in _notes(result)
    assert _NOT_CHECKED not in _notes(result)


def test_missing_data_date_is_not_continuous(tmp_path: Path) -> None:
    schedule = _load(tmp_path, [_task("1", "A", "8")], [], data="")
    assert schedule.projects[0].last_recalc_date is None
    result = PathsModeB().run(AnalysisContext(schedule=schedule), PathsBConfig())
    assert result.metrics["continuity"].status == "no_evaluable"
    assert result.metrics["continuity"].value != 1.0
    assert result.metrics["continuity"].status != "verdadera"
    text = _notes(result).lower()
    assert "falta la fecha de corte" in text
    assert _NOT_CHECKED not in _notes(result)


def test_mode_a_marks_the_activity_from_the_flag(tmp_path: Path) -> None:
    assert "schedule_cpm" not in inspect.getsource(mode_a)
    present = _load_flags(
        tmp_path / "present.xer",
        [
            (*_task("1", "YES", "8"), "Y"),
            (*_task("2", "YES2", "8"), "y"),
            (*_task("3", "NO", "8"), "N"),
            (*_task("4", "OTHER", "8"), "Yes"),
            (*_task("5", "BLANK", "8"), ""),
        ],
        [_link("1", "1", "2")],
    )
    stored = {item.task_code: item.driving_path_flag for item in present.activities}
    assert stored == {"YES": "Y", "YES2": "y", "NO": "N", "OTHER": "Yes", "BLANK": None}
    marked = _bands(present)
    assert set(marked.loc[marked["driving_activity"], "task_code"]) == {"YES", "YES2"}
    absent = _load(tmp_path, [_task("1", "A", "8"), _task("2", "B", "8")], [_link("1", "1", "2")])
    assert all(item.driving_path_flag is None for item in absent.activities)
    quiet = _bands(absent)
    assert not quiet["driving_activity"].any()
    assert list(quiet.columns) == [
        "task_code",
        "task_name",
        "float_days",
        "band",
        "critical",
        "path",
        "driving_activity",
    ]
    ran = PathsModeA().run(AnalysisContext(schedule=absent), PathsConfig())
    assert _LINKS in _notes(ran)
    assert set(ran.tables) == {"bands"}


def _bands(schedule: Schedule) -> pd.DataFrame:
    activities = tuple(replace(item, total_float_hr_cnt=0.0) for item in schedule.activities)
    loaded = replace(schedule, activities=activities)
    result = PathsModeA().run(AnalysisContext(schedule=loaded), PathsConfig())
    return result.tables["bands"]


def _load_flags(path: Path, tasks: list[tuple[str, ...]], links: list[list[str]]) -> Schedule:
    write_xer(
        path,
        "ERMHDR",
        [
            {
                "name": "PROJECT",
                "fields": ["proj_id", "clndr_id", "last_recalc_date"],
                "rows": [["1", "C1", "2026-01-05 08:00"]],
            },
            {
                "name": "CALENDAR",
                "fields": ["clndr_id", "day_hr_cnt", "clndr_data"],
                "rows": [["C1", "8", _week()]],
            },
            {
                "name": "TASK",
                "fields": [*_TASK, "driving_path_flag"],
                "rows": [list(row) for row in tasks],
            },
            {"name": "TASKPRED", "fields": _PRED, "rows": links},
        ],
    )
    return schedule_from_xer(read_xer(path))
