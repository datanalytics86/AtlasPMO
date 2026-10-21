"""B-09: critical by total float or by longest path."""

from datetime import datetime
from pathlib import Path

from atlaspmo.engine.cpm import schedule_cpm
from atlaspmo.engine.options import EngineOptions
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.synthetic import write_xer
from atlaspmo.io.xer import read_xer
from atlaspmo.model.schedule import Schedule

DATA = "2026-01-05 08:00"
MON_8 = datetime(2026, 1, 5, 8, 0)
MON_16 = datetime(2026, 1, 5, 16, 0)
THU_16 = datetime(2026, 1, 8, 16, 0)

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


def _task(
    task_id: str,
    code: str,
    hours: str,
    cstr: str = "",
    cstr_date: str = "",
) -> list[str]:
    return [
        task_id,
        "1",
        "C1",
        "W1",
        code,
        "TT_Task",
        "TK_NotStart",
        hours,
        cstr,
        cstr_date,
        "",
        "",
    ]


def _link(link_id: str, pred: str, succ: str) -> list[str]:
    return [link_id, succ, pred, "1", "1", "PR_FS", "0"]


def _load(tmp_path: Path) -> Schedule:
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
            {
                "name": "TASK",
                "fields": _TASK,
                "rows": [
                    _task("1", "A", "16"),
                    _task("2", "B", "16"),
                    _task("3", "C", "8", "CS_MEO", "2026-01-05 16:00"),
                ],
            },
            {
                "name": "TASKPRED",
                "fields": _PRED,
                "rows": [_link("1", "1", "2")],
            },
        ],
    )
    return schedule_from_xer(read_xer(path))


def test_float_and_longest_path_disagree_on_a_pinned_side_activity(tmp_path: Path):
    schedule = _load(tmp_path)
    by_float = schedule_cpm(schedule)
    by_path = schedule_cpm(schedule, EngineOptions(critical_rule="longest"))
    assert by_float.project_finish == THU_16
    assert by_float.by_id["1"].early_start == MON_8
    assert by_float.by_id["2"].early_finish == THU_16
    assert by_float.by_id["3"].early_finish == MON_16
    assert by_float.by_id["3"].total_float_hours == 0
    assert by_float.by_id["1"].critical
    assert by_float.by_id["2"].critical
    assert by_float.by_id["3"].critical
    assert by_path.by_id["1"].critical
    assert by_path.by_id["2"].critical
    assert not by_path.by_id["3"].critical
    assert by_path.by_id["1"].early_finish == by_float.by_id["1"].early_finish
    assert by_path.by_id["3"].total_float_hours == 0
