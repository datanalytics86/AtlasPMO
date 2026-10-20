"""Hand EVM: PV 50, EV 50, AC 40, SPI 1, CPI 1.25, ES 8, AT 8, IEAC 16."""

from datetime import datetime

from atlaspmo.analysis.contract import AnalysisContext
from atlaspmo.analysis.resources.evm import earned_value
from atlaspmo.analysis.resources.module import EvmModule
from atlaspmo.model.schedule import Activity, Assignment, Calendar, Project, Schedule
from test_cpm import MON_8, TUE_8, TUE_16, _week

_LIMIT = "límite de recurso no evaluable: no hay un campo citado de tope."
_CODES = "sin confirmar en un export de Nicolás"


def test_hand_evm_and_earned_schedule():
    schedule = _schedule()
    outcome = earned_value(schedule)
    assert outcome.pv == 50
    assert outcome.ev == 50
    assert outcome.ac == 40
    assert outcome.spi == 1
    assert outcome.cpi == 1.25
    assert outcome.es_hours == 8
    assert outcome.at_hours == 8
    assert outcome.spi_t == 1
    assert outcome.ieac_t == 16
    assert _LIMIT in outcome.approximations
    assert any(_CODES in note for note in outcome.approximations)
    assert any("PV lineal" in note for note in outcome.approximations)
    assert any("un solo punto" in note for note in outcome.approximations)
    assert len(outcome.scurve) == 1
    assert outcome.scurve[0]["pv"] == 50
    assert outcome.resources[0] == {"rsrc_id": "H1", "target_qty": 16}
    assert outcome.wbs[-1]["wbs_id"] == "total"
    assert outcome.wbs[-1]["ev"] == 50
    result = EvmModule().run(AnalysisContext(schedule=schedule), EvmModule.config_model())
    assert result.metrics["spi"].status == "info"
    assert result.metrics["resource_limit"].status == "no_evaluable"
    assert result.metrics["cpi"].value == 1.25


def test_physical_percent_above_one_is_scaled():
    schedule = _schedule(complete_pct_type="CP_Phys", phys_complete_pct=50)
    outcome = earned_value(schedule)
    assert outcome.ev == 50
    assert any("0 a 100" in note for note in outcome.approximations)


def test_units_and_unknown_percent_stay_unevaluable():
    units = earned_value(_schedule(complete_pct_type="CP_Units"))
    unknown = earned_value(_schedule(complete_pct_type="CP_Otro"))
    assert units.ev is None
    assert unknown.ev is None
    assert any("cantidad real" in note for note in units.approximations)
    assert any("no reconocido" in note for note in unknown.approximations)


def test_missing_actual_cost_leaves_cpi_unevaluable():
    outcome = earned_value(_schedule(act_reg_cost=None))
    assert outcome.ac is None
    assert outcome.cpi is None
    assert outcome.ev == 50


def test_without_a_calendar_pv_uses_clock_time():
    schedule = _schedule(clndr_data=None, hours=8, remain=4, end=datetime(2026, 1, 5, 16, 0))
    project = schedule.projects[0]
    schedule.projects = (
        Project(
            project.proj_id,
            project.proj_short_name,
            project.proj_name,
            project.clndr_id,
            datetime(2026, 1, 5, 12, 0),
            None,
            None,
        ),
    )
    outcome = earned_value(schedule)
    assert outcome.pv == 50
    assert outcome.ev == 50
    assert any("tiempo de reloj" in note for note in outcome.approximations)


def _schedule(
    complete_pct_type: str = "CP_Drtn",
    phys_complete_pct: float | None = None,
    act_reg_cost: float | None = 40,
    clndr_data: str | None = None,
    hours: float = 16,
    remain: float = 8,
    end: datetime = TUE_16,
) -> Schedule:
    if clndr_data is None and complete_pct_type == "CP_Drtn" and hours == 16:
        clndr_data = _week()
    activity = Activity(
        task_id="A",
        proj_id="1",
        wbs_id="W1",
        clndr_id="C1",
        task_code="A",
        task_name="A",
        task_type="TT_Task",
        status_code="TK_Active",
        complete_pct_type=complete_pct_type,
        cstr_type=None,
        cstr_type2=None,
        target_drtn_hr_cnt=hours,
        remain_drtn_hr_cnt=remain,
        total_float_hr_cnt=None,
        free_float_hr_cnt=None,
        target_start_date=MON_8,
        target_end_date=end,
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
        phys_complete_pct=phys_complete_pct,
    )
    return Schedule(
        projects=(
            Project("1", "P", "P", "C1", TUE_8, None, None),
        ),
        calendars=(Calendar("C1", "C", "1", 8, None, clndr_data),),
        wbs=(),
        activities=(activity,),
        relationships=(),
        assignments=(
            Assignment("TR1", "A", "H1", 10, 60, act_reg_cost, None),
            Assignment("TR2", "A", "H1", 6, 40, None, None),
        ),
        activity_codes=(),
    )
