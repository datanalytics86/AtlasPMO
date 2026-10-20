"""Hand-calculated CPM on a 7-day, 08:00-16:00 calendar."""

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
TUE_8 = datetime(2026, 1, 6, 8, 0)
TUE_16 = datetime(2026, 1, 6, 16, 0)
WED_8 = datetime(2026, 1, 7, 8, 0)
WED_16 = datetime(2026, 1, 7, 16, 0)
THU_8 = datetime(2026, 1, 8, 8, 0)
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
    days = "".join(
        f"(0||{number}()((0||0(s|08:00|f|16:00)())))" for number in range(1, 8)
    )
    return f"(0||CalendarData()((0||DaysOfWeek()({days}))(0||VIEW(ShowTotal|N)())))"


def _task(
    task_id: str,
    code: str,
    hours: str = "8",
    kind: str = "TT_Task",
    status: str = "TK_NotStart",
    cstr: str = "",
    cstr_date: str = "",
    act_start: str = "",
    act_end: str = "",
    wbs: str = "W1",
) -> list[str]:
    return [
        task_id,
        "1",
        "C1",
        wbs,
        code,
        kind,
        status,
        hours,
        cstr,
        cstr_date,
        act_start,
        act_end,
    ]


def _link(
    link_id: str,
    pred: str,
    succ: str,
    kind: str = "PR_FS",
    lag: str = "0",
) -> list[str]:
    return [link_id, succ, pred, "1", "1", kind, lag]


def _load(
    tmp_path: Path,
    tasks: list[list[str]],
    links: list[list[str]],
    data: str = DATA,
) -> Schedule:
    path = tmp_path / "case.xer"
    write_xer(
        path,
        "ERMHDR",
        [
            {
                "name": "PROJECT",
                "fields": ["proj_id", "clndr_id", "last_recalc_date"],
                "rows": [["1", "C1", data]],
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


def _at(schedule: Schedule, code: str, options: EngineOptions | None = None):
    result = schedule_cpm(schedule, options)
    by_code = {item.task_code: item.task_id for item in schedule.activities}
    return result, result.by_id[by_code[code] or ""]


def test_fs_chain_is_critical(tmp_path: Path):
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "16")],
        [_link("1", "1", "2")],
    )
    result, _row = _at(schedule, "A")
    assert result.by_id["1"].early_start == MON_8
    assert result.by_id["1"].early_finish == MON_16
    assert result.by_id["2"].early_start == TUE_8
    assert result.by_id["2"].early_finish == WED_16
    assert result.by_id["1"].total_float_hours == 0
    assert result.by_id["2"].total_float_hours == 0
    assert result.by_id["1"].critical
    assert result.by_id["2"].critical
    assert result.project_finish == WED_16


def test_parallel_branch_keeps_sixteen_hours_of_float(tmp_path: Path):
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8"), _task("3", "C", "24")],
        [_link("1", "1", "2"), _link("2", "1", "3")],
    )
    result, _row = _at(schedule, "B")
    assert result.by_id["2"].early_start == TUE_8
    assert result.by_id["2"].early_finish == TUE_16
    assert result.by_id["2"].late_start == THU_8
    assert result.by_id["2"].total_float_hours == 16
    assert result.by_id["2"].free_float_hours == 16
    assert result.by_id["3"].early_finish == THU_16
    assert result.by_id["3"].total_float_hours == 0
    assert result.by_id["1"].total_float_hours == 0
    assert not result.by_id["2"].critical


def test_ss_ff_sf_and_lead(tmp_path: Path):
    ss = _load(
        tmp_path,
        [_task("1", "A", "16"), _task("2", "B", "8")],
        [_link("1", "1", "2", "PR_SS", "8")],
    )
    ss_result, _row = _at(ss, "B")
    assert ss_result.by_id["2"].early_start == TUE_8
    assert ss_result.by_id["2"].early_finish == TUE_16
    ff = _load(
        tmp_path,
        [_task("1", "A", "24"), _task("2", "B", "8")],
        [_link("1", "1", "2", "PR_FF", "0")],
    )
    assert schedule_cpm(ff).by_id["2"].early_start == WED_8
    assert schedule_cpm(ff).by_id["2"].early_finish == WED_16
    sf = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8")],
        [_link("1", "1", "2", "PR_SF", "8")],
    )
    assert schedule_cpm(sf).by_id["2"].early_finish == MON_16
    lead = _load(
        tmp_path,
        [_task("1", "A", "16"), _task("2", "B", "8")],
        [_link("1", "1", "2", "PR_FS", "-8")],
    )
    assert schedule_cpm(lead).by_id["2"].early_start == TUE_8


def test_start_on_or_after_delays_and_gives_float_to_the_predecessor(tmp_path: Path):
    schedule = _load(
        tmp_path,
        [
            _task("1", "A", "8"),
            _task("2", "B", "8", cstr="CS_MSOA", cstr_date="2026-01-07 08:00"),
        ],
        [_link("1", "1", "2")],
    )
    result = schedule_cpm(schedule)
    assert result.by_id["2"].early_start == WED_8
    assert result.by_id["2"].early_finish == WED_16
    assert result.by_id["1"].total_float_hours == 8


def test_milestones_can_sit_on_the_shift_end(tmp_path: Path):
    schedule = _load(
        tmp_path,
        [
            _task("1", "S", "0", "TT_Mile"),
            _task("2", "A", "8"),
            _task("3", "F", "0", "TT_FinMile"),
        ],
        [_link("1", "1", "2"), _link("2", "2", "3")],
    )
    result = schedule_cpm(schedule)
    assert result.by_id["1"].early_start == MON_8
    assert result.by_id["1"].early_finish == MON_8
    assert result.by_id["3"].early_start == MON_16
    assert result.by_id["3"].early_finish == MON_16


def test_alap_without_successors_moves_to_the_project_finish(tmp_path: Path):
    schedule = _load(
        tmp_path,
        [_task("1", "A", "24"), _task("2", "C", "8", cstr="CS_ALAP")],
        [],
    )
    result = schedule_cpm(schedule)
    assert result.by_id["2"].early_start == WED_8
    assert result.by_id["2"].early_finish == WED_16
    assert result.by_id["1"].early_finish == WED_16


def test_retained_logic_waits_and_override_does_not(tmp_path: Path):
    tasks = [
        _task("1", "A", "8"),
        _task(
            "2",
            "B",
            "8",
            status="TK_Active",
            act_start="2026-01-05 08:00",
        ),
    ]
    links = [_link("1", "1", "2")]
    retained = schedule_cpm(_load(tmp_path, tasks, links, "2026-01-07 08:00"))
    assert retained.by_id["2"].early_start == MON_8
    assert retained.by_id["2"].early_finish == datetime(2026, 1, 8, 16, 0)
    override = schedule_cpm(
        _load(tmp_path, tasks, links, "2026-01-07 08:00"),
        EngineOptions(progress="progress_override"),
    )
    assert override.by_id["2"].early_finish == WED_16
    actual = schedule_cpm(
        _load(
            tmp_path,
            [
                _task("1", "A", "8"),
                _task(
                    "2",
                    "B",
                    "8",
                    status="TK_Active",
                    act_start="2026-01-05 08:00",
                    act_end="2026-01-05 16:00",
                ),
            ],
            links,
            "2026-01-07 08:00",
        ),
        EngineOptions(progress="actual_dates"),
    )
    assert actual.by_id["2"].early_start == MON_8
    assert actual.by_id["2"].early_finish == MON_16


def test_cycle_schedules_nothing(tmp_path: Path):
    schedule = _load(
        tmp_path,
        [_task("1", "A"), _task("2", "B")],
        [_link("1", "1", "2"), _link("2", "2", "1")],
    )
    result = schedule_cpm(schedule)
    assert result.by_id == {}
    assert any("Ciclo" in note for note in result.approximations)


def test_missing_lag_is_not_zero(tmp_path: Path):
    schedule = _load(
        tmp_path,
        [_task("1", "A"), _task("2", "B")],
        [_link("1", "1", "2", "PR_FS", "")],
    )
    result = schedule_cpm(schedule)
    assert any("lag_hr_cnt" in note for note in result.approximations)
    assert result.by_id["2"].early_start == MON_8


def test_loe_and_wbs_follow_the_main_pass(tmp_path: Path):
    schedule = _load(
        tmp_path,
        [
            _task("1", "A", "8", wbs="W1"),
            _task("2", "B", "8", wbs="W1"),
            _task("3", "L", "0", "TT_LOE", wbs="W1"),
            _task("4", "S", "0", "TT_WBS", wbs="W1"),
        ],
        [_link("1", "1", "2"), _link("2", "1", "3"), _link("3", "3", "2")],
    )
    result = schedule_cpm(schedule)
    assert result.by_id["3"].early_start == MON_8
    assert result.by_id["3"].early_finish == TUE_16
    assert not result.by_id["3"].critical
    assert result.by_id["4"].early_start == MON_8
    assert result.by_id["4"].early_finish == TUE_16
    assert any("LOE" in note for note in result.approximations)


def test_resource_activity_is_an_approximation(tmp_path: Path):
    schedule = _load(tmp_path, [_task("1", "A", "8", "TT_Rsrc")], [])
    result = schedule_cpm(schedule)
    assert result.by_id["1"].early_finish == MON_16
    assert any("TT_Rsrc" in note for note in result.approximations)
