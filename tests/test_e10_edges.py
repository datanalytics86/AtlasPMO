"""Cross-project FS: the successor starts the next working day."""

from __future__ import annotations

from pathlib import Path

from atlaspmo.engine.cpm import schedule_cpm_reference
from atlaspmo.engine.fast import LAST, schedule_cpm_fast
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.synthetic import write_xer
from atlaspmo.io.xer import read_xer
from test_cpm import DATA, MON_8, MON_16, TUE_8, TUE_16, _week


def _two_projects(tmp_path: Path):
    path = tmp_path / "cross.xer"
    write_xer(
        path,
        "ERMHDR",
        [
            {
                "name": "PROJECT",
                "fields": ["proj_id", "clndr_id", "last_recalc_date"],
                "rows": [["1", "C1", DATA], ["2", "C1", DATA]],
            },
            {
                "name": "CALENDAR",
                "fields": ["clndr_id", "day_hr_cnt", "clndr_data"],
                "rows": [["C1", "8", _week()]],
            },
            {
                "name": "TASK",
                "fields": [
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
                ],
                "rows": [
                    ["1", "1", "C1", "W1", "A", "TT_Task", "TK_NotStart", "8", "", "", "", ""],
                    ["2", "2", "C1", "W1", "B", "TT_Task", "TK_NotStart", "8", "", "", "", ""],
                ],
            },
            {
                "name": "TASKPRED",
                "fields": [
                    "task_pred_id",
                    "task_id",
                    "pred_task_id",
                    "proj_id",
                    "pred_proj_id",
                    "pred_type",
                    "lag_hr_cnt",
                ],
                "rows": [["1", "2", "1", "2", "1", "PR_FS", "0"]],
            },
        ],
    )
    return schedule_from_xer(read_xer(path))


def test_cross_project_fs_starts_the_next_working_day(tmp_path: Path) -> None:
    schedule = _two_projects(tmp_path)
    link = schedule.relationships[0]
    by_code = {item.task_code: item for item in schedule.activities}
    assert by_code["A"].proj_id == "1"
    assert by_code["B"].proj_id == "2"
    assert link.pred_type == "PR_FS"
    assert link.pred_proj_id == "1"
    assert link.proj_id == "2"
    assert link.pred_task_id == by_code["A"].task_id
    assert link.task_id == by_code["B"].task_id
    reference = schedule_cpm_reference(schedule)
    fast = schedule_cpm_fast(schedule)
    assert LAST["path"] == "fast"
    for result in (reference, fast):
        assert result.by_id["1"].early_start == MON_8
        assert result.by_id["1"].early_finish == MON_16
        assert result.by_id["2"].early_start == TUE_8
        assert result.by_id["2"].early_finish == TUE_16
