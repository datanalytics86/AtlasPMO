"""B-05: cycle detection must stay iterative on a long serial chain."""

from __future__ import annotations

from atlaspmo.io.validate import validate_schedule
from atlaspmo.model.schedule import Activity, Relationship, Schedule

_CHAIN_LENGTH = 60_000


def _activity(task_id: str, task_code: str | None = None) -> Activity:
    return Activity(
        task_id=task_id,
        proj_id=None,
        wbs_id=None,
        clndr_id=None,
        task_code=task_code,
        task_name=None,
        task_type="TT_Task",
        status_code="TK_Complete",
        complete_pct_type=None,
        cstr_type=None,
        cstr_type2=None,
        target_drtn_hr_cnt=None,
        remain_drtn_hr_cnt=None,
        total_float_hr_cnt=None,
        free_float_hr_cnt=None,
        target_start_date=None,
        target_end_date=None,
        act_start_date=None,
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


def _link(pred_id: str, succ_id: str, link_id: str) -> Relationship:
    return Relationship(
        task_pred_id=link_id,
        task_id=succ_id,
        pred_task_id=pred_id,
        proj_id=None,
        pred_proj_id=None,
        pred_type="PR_FS",
        lag_hr_cnt=0.0,
    )


def _schedule(
    activities: tuple[Activity, ...],
    relationships: tuple[Relationship, ...],
) -> Schedule:
    return Schedule(
        projects=(),
        calendars=(),
        wbs=(),
        activities=activities,
        relationships=relationships,
        assignments=(),
        activity_codes=(),
    )


def test_serial_chain_of_60k_does_not_recurse() -> None:
    activities = tuple(_activity(str(index)) for index in range(_CHAIN_LENGTH))
    relationships = tuple(
        _link(str(index), str(index + 1), str(index)) for index in range(_CHAIN_LENGTH - 1)
    )
    issues = validate_schedule(_schedule(activities, relationships))
    assert not any(item.code == "cycle" for item in issues)


def test_cycle_of_three_is_reported() -> None:
    activities = (
        _activity("1", "A"),
        _activity("2", "B"),
        _activity("3", "C"),
    )
    relationships = (
        _link("1", "2", "10"),
        _link("2", "3", "11"),
        _link("3", "1", "12"),
    )
    issues = validate_schedule(_schedule(activities, relationships))
    cycles = [item for item in issues if item.code == "cycle"]
    assert len(cycles) == 1
    assert cycles[0].message_es == "Ciclo: A → B → C → A"
