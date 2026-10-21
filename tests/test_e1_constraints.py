"""B-08: mandatory dates override network logic on both passes."""

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
TUE_12 = datetime(2026, 1, 6, 12, 0)
TUE_16 = datetime(2026, 1, 6, 16, 0)

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
    hours: str = "8",
    kind: str = "TT_Task",
    cstr: str = "",
    cstr_date: str = "",
) -> list[str]:
    return [task_id, "1", "C1", "W1", code, kind, "TK_NotStart", hours, cstr, cstr_date, "", ""]


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


def test_mandatory_start_overrides_a_tuesday_logic_date(tmp_path: Path):
    # A finishes Tuesday 12:00. The link would open B that Tuesday.
    # CS_MANDSTART Monday 08:00 wins on the forward and backward passes.
    schedule = _load(
        tmp_path,
        [
            _task("1", "A", "12"),
            _task("2", "B", "8", cstr="CS_MANDSTART", cstr_date="2026-01-05 08:00"),
        ],
        [_link("1", "1", "2")],
    )
    result = schedule_cpm(schedule)
    assert result.by_id["1"].early_finish == TUE_12
    row = result.by_id["2"]
    assert row.early_start == MON_8
    assert row.early_start != TUE_12
    assert row.early_finish == MON_16
    assert row.late_start == MON_8
    assert row.late_finish == MON_16
    assert any("CS_MANDSTART" in note and "viola" in note for note in result.approximations)


def test_mandatory_finish_overrides_a_later_network_finish(tmp_path: Path):
    schedule = _load(
        tmp_path,
        [
            _task("1", "A", "8"),
            _task("2", "B", "8", cstr="CS_MANDFIN", cstr_date="2026-01-05 16:00"),
            _task("3", "C", "24"),
        ],
        [_link("1", "1", "2")],
    )
    result = schedule_cpm(schedule)
    assert result.by_id["1"].early_finish == MON_16
    assert result.project_finish == datetime(2026, 1, 7, 16, 0)
    row = result.by_id["2"]
    assert row.early_finish == MON_16
    assert row.early_finish != TUE_16
    assert row.early_start == MON_8
    assert row.late_finish == MON_16
    assert row.late_finish != result.project_finish
    assert row.late_start == MON_8
    assert any("CS_MANDFIN" in note and "viola" in note for note in result.approximations)


def test_start_on_still_only_delays(tmp_path: Path):
    schedule = _load(
        tmp_path,
        [
            _task("1", "A", "12"),
            _task("2", "B", "8", cstr="CS_MSO", cstr_date="2026-01-05 08:00"),
        ],
        [_link("1", "1", "2")],
    )
    result = schedule_cpm(schedule)
    assert result.by_id["2"].early_start == TUE_12
    assert not any("CS_MANDSTART" in note for note in result.approximations)
