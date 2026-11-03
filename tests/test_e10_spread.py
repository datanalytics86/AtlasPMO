"""Remaining duration spread on working time. The oracle is the calendar."""

from datetime import datetime

from atlaspmo.analysis.contract import AnalysisContext
from atlaspmo.analysis.resources.evm import earned_value
from atlaspmo.analysis.resources.module import EvmModule
from atlaspmo.model.schedule import Activity, Calendar, Project, Schedule

_DATA = datetime(2026, 1, 5, 8, 0)
_SPREAD = "distribución es lineal en tiempo laboral"
_NO_ASSIGNMENT = "no hay asignación"


def test_remaining_hours_follow_working_days():
    schedule = _one_activity(24)
    outcome = earned_value(schedule)
    assert [(row["bucket"], row["hours"]) for row in outcome.days] == [
        ("2026-01-05", 8.0),
        ("2026-01-06", 8.0),
        ("2026-01-07", 8.0),
    ]
    assert sum(row["hours"] for row in outcome.days) == schedule.activities[0].remain_drtn_hr_cnt
    assert {row["bucket"] for row in outcome.weeks} == {"2026-W02"}
    assert sum(row["hours"] for row in outcome.weeks) == 24
    assert {row["bucket"] for row in outcome.months} == {"2026-01"}
    assert sum(row["hours"] for row in outcome.months) == 24
    assert [row["cumulative"] for row in outcome.curve] == [8.0, 16.0, 24.0]
    text = " ".join(outcome.approximations).lower()
    assert _SPREAD in text
    assert "balde corte" not in text
    assert "no es una curva por periodo" not in text
    assert outcome.histogram == ()
    assert _NO_ASSIGNMENT in text
    result = EvmModule().run(AnalysisContext(schedule=schedule), EvmModule.config_model())
    assert result.metrics["resource_limit"].value is None
    assert result.metrics["resource_limit"].status == "no_evaluable"
    assert result.tables["histogram"].empty


def _one_activity(hours: float) -> Schedule:
    days = "".join(f"(0||{number}()((0||0(s|08:00|f|16:00)())))" for number in range(2, 7))
    calendar = f"(0||CalendarData()((0||DaysOfWeek()({days}))(0||VIEW(ShowTotal|N)())))"
    activity = Activity(
        task_id="1",
        proj_id="1",
        wbs_id="W1",
        clndr_id="C1",
        task_code="A",
        task_name="A",
        task_type="TT_Task",
        status_code="TK_NotStart",
        complete_pct_type="CP_Drtn",
        cstr_type=None,
        cstr_type2=None,
        target_drtn_hr_cnt=hours,
        remain_drtn_hr_cnt=hours,
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
    return Schedule(
        projects=(Project("1", "P", "P", "C1", _DATA, None, None),),
        calendars=(Calendar("C1", "C", "1", 8, None, calendar),),
        wbs=(),
        activities=(activity,),
        relationships=(),
        assignments=(),
        activity_codes=(),
    )
