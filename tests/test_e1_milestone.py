"""B-21: a start milestone on the shift close moves to the next open."""

from datetime import datetime
from pathlib import Path

from atlaspmo.engine.cpm import schedule_cpm
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.synthetic import write_xer
from atlaspmo.io.xer import read_xer
from atlaspmo.model.schedule import Schedule

DATA = "2026-01-05 08:00"
MON_8 = datetime(2026, 1, 5, 8, 0)
MON_16 = datetime(2026, 1, 5, 16, 0)
TUE_8 = datetime(2026, 1, 6, 8, 0)

_TASK = [
    "task_id",
    "proj_id",
    "clndr_id",
    "wbs_id",
    "task_code",
    "task_type",
    "status_code",
    "remain_drtn_hr_cnt",
    "cstr_type",
    "cstr_date",
    "act_start_date",
    "act_end_date",
]
_PRED = [
    "task_pred_id",
    "task_id",
    "pred_task_id",
    "proj_id",
    "pred_proj_id",
    "pred_type",
    "lag_hr_cnt",
]


def _week() -> str:
    days = "".join(f"(0||{number}()((0||0(s|08:00|f|16:00)())))" for number in range(1, 8))
    return f"(0||CalendarData()((0||DaysOfWeek()({days}))(0||VIEW(ShowTotal|N)())))"


def _task(task_id: str, code: str, kind: str, hours: str = "0") -> list[str]:
    return [task_id, "1", "C1", "W1", code, kind, "TK_NotStart", hours, "", "", "", ""]


def _link(link_id: str, pred: str, succ: str) -> list[str]:
    return [link_id, succ, pred, "1", "1", "PR_FS", "0"]


def _load(tmp_path: Path, tasks: list[list[str]], links: list[list[str]]) -> Schedule:
    path = tmp_path / "case.xer"
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
                "fields": ["clndr_id", "day_hr_cnt", "clndr_data"],
                "rows": [["C1", "8", _week()]],
            },
            {"name": "TASK", "fields": _TASK, "rows": tasks},
            {"name": "TASKPRED", "fields": _PRED, "rows": links},
        ],
    )
    return schedule_from_xer(read_xer(path))


def test_start_milestone_on_the_close_moves_to_the_next_open(tmp_path: Path):
    schedule = _load(
        tmp_path,
        [_task("1", "A", "TT_Task", "8"), _task("2", "S", "TT_Mile")],
        [_link("1", "1", "2")],
    )
    result = schedule_cpm(schedule)
    assert result.by_id["1"].early_finish == MON_16
    row = result.by_id["2"]
    assert row.early_start == TUE_8
    assert row.early_finish == TUE_8
    assert row.early_start != MON_16
    assert row.late_start == TUE_8
    assert row.late_finish == TUE_8


def test_finish_milestone_stays_on_the_close(tmp_path: Path):
    schedule = _load(
        tmp_path,
        [_task("1", "A", "TT_Task", "8"), _task("2", "F", "TT_FinMile")],
        [_link("1", "1", "2")],
    )
    result = schedule_cpm(schedule)
    row = result.by_id["2"]
    assert row.early_start == MON_16
    assert row.early_finish == MON_16
    assert row.late_start == MON_16
    assert row.late_finish == MON_16


def test_start_milestone_already_on_the_open_stays(tmp_path: Path):
    schedule = _load(tmp_path, [_task("1", "S", "TT_Mile")], [])
    result = schedule_cpm(schedule)
    assert result.by_id["1"].early_start == MON_8
    assert result.by_id["1"].early_finish == MON_8
