"""Reference and fast CPM stay identical to the minute on generated nets."""

from dataclasses import replace
from datetime import date, datetime

from hypothesis import given, settings
from hypothesis import strategies as st

from atlaspmo.engine.cpm import schedule_cpm
from atlaspmo.engine.options import EngineOptions
from atlaspmo.model.schedule import Activity, Calendar, Project, Relationship, Schedule

DATA = datetime(2026, 1, 5, 8, 0)
_EXCEL = date(1899, 12, 30)
_LINKS = ("PR_FS", "PR_SS", "PR_FF", "PR_SF")
_CSTR = (
    None,
    "CS_MSO",
    "CS_MSOA",
    "CS_MSOB",
    "CS_MEO",
    "CS_MEOA",
    "CS_MEOB",
    "CS_MANDSTART",
    "CS_MANDFIN",
    "CS_ALAP",
)


def _calendar(kind: str, holiday: date | None) -> str:
    if kind == "all":
        working = set(range(1, 8))
        start, finish = "08:00", "16:00"
    elif kind == "week":
        working = {2, 3, 4, 5, 6}
        start, finish = "08:00", "17:00"
    elif kind == "half":
        working = {2, 3, 4, 5, 6}
        start, finish = "08:00", "12:00"
    else:
        working = set(range(1, 8))
        start, finish = "00:00", "00:00"
    chunks = []
    for number in range(1, 8):
        if number in working:
            chunks.append(f"(0||{number}()((0||0(s|{start}|f|{finish})())))")
        else:
            chunks.append(f"(0||{number}()())")
    extra = ""
    if holiday is not None:
        serial = (holiday - _EXCEL).days
        extra = f"(0||Exceptions()((0||0(d|{serial})())))"
    body = "".join(chunks)
    return f"(0||CalendarData()((0||DaysOfWeek()({body})){extra}(0||VIEW(ShowTotal|N)())))"


def _activity(index: int, draw) -> Activity:
    kind = draw(
        st.sampled_from(
            ("TT_Task", "TT_Task", "TT_Mile", "TT_FinMile", "TT_Rsrc", "TT_LOE", "TT_WBS")
        )
    )
    hours = (
        0
        if kind in {"TT_Mile", "TT_FinMile", "TT_LOE", "TT_WBS"}
        else draw(st.sampled_from((1, 4, 8, 16, 24)))
    )
    status = draw(st.sampled_from(("TK_NotStart", "TK_NotStart", "TK_Active", "TK_Complete")))
    if kind in {"TT_LOE", "TT_WBS"}:
        status = "TK_NotStart"
    cstr = draw(st.sampled_from(_CSTR))
    day = draw(st.integers(5, 20))
    cstr_date = (
        None
        if cstr in {None, "CS_ALAP"}
        else datetime(2026, 1, day, draw(st.sampled_from((8, 12, 16))), 0)
    )
    act_start = None
    act_end = None
    if status == "TK_Active":
        second = draw(st.sampled_from((0, 45)))
        act_start = datetime(2026, 1, draw(st.integers(5, 12)), 8, 0, second)
    if status == "TK_Complete":
        act_start = datetime(2026, 1, 5, 8, 0, draw(st.sampled_from((0, 30))))
        act_end = datetime(2026, 1, draw(st.integers(5, 9)), 16, 0, draw(st.sampled_from((0, 45))))
    return Activity(
        task_id=str(index),
        proj_id="1",
        wbs_id=draw(st.sampled_from(("W1", "W2"))),
        clndr_id=draw(st.sampled_from(("C1", "C2"))),
        task_code=f"A{index}",
        task_name=f"A{index}",
        task_type=kind,
        status_code=status,
        complete_pct_type=None,
        cstr_type=cstr,
        cstr_type2=draw(st.sampled_from((None, "CS_MSO", "CS_MEO", "CS_ALAP"))),
        target_drtn_hr_cnt=hours,
        remain_drtn_hr_cnt=hours,
        total_float_hr_cnt=None,
        free_float_hr_cnt=None,
        target_start_date=None,
        target_end_date=None,
        act_start_date=act_start,
        act_end_date=act_end,
        early_start_date=None,
        early_end_date=None,
        late_start_date=None,
        late_end_date=None,
        float_path=None,
        float_path_order=None,
        int_path=None,
        int_path_order=None,
        phys_complete_pct=None,
        cstr_date=cstr_date,
        cstr_date2=None if cstr == "CS_ALAP" else datetime(2026, 1, min(day + 1, 28), 8, 0),
        expect_end_date=datetime(2026, 1, 20, 8, 0) if draw(st.booleans()) else None,
    )


@st.composite
def _nets(draw: st.DrawFn) -> tuple[Schedule, EngineOptions]:
    count = draw(st.integers(3, 7))
    holiday = date(2026, 1, 7) if draw(st.booleans()) else None
    calendars = (
        Calendar(
            "C1", "C1", "1", 8, None, _calendar(draw(st.sampled_from(("all", "week"))), holiday)
        ),
        Calendar(
            "C2",
            "C2",
            "1",
            8,
            None,
            _calendar(draw(st.sampled_from(("half", "full", "week"))), None),
        ),
    )
    activities = tuple(_activity(index, draw) for index in range(1, count + 1))
    links: list[Relationship] = []
    link_id = 1
    for pred in range(1, count):
        if draw(st.booleans()):
            succ = draw(st.integers(pred + 1, count))
            lag = (
                None if draw(st.integers(0, 12)) == 0 else draw(st.sampled_from((-8, -1, 0, 4, 8)))
            )
            kind = draw(st.sampled_from(_LINKS)) if draw(st.integers(0, 10)) else "PR_OTHER"
            links.append(Relationship(str(link_id), str(succ), str(pred), "1", "1", kind, lag))
            link_id += 1
    if draw(st.booleans()):
        links.append(Relationship(str(link_id), "99", "1", "1", "1", "PR_FS", 0))
    options = EngineOptions(
        progress=draw(st.sampled_from(("retained", "progress_override", "actual_dates"))),
        lag_calendar=draw(st.sampled_from(("predecessor", "successor", "elapsed", "project"))),
        float_kind=draw(st.sampled_from(("minimum", "start", "finish"))),
        critical_hours=draw(st.sampled_from((0.0, 8.0))),
        critical_rule=draw(st.sampled_from(("float", "longest"))),
    )
    schedule = Schedule(
        projects=(Project("1", "P", "P", "C1", DATA, None, None),),
        calendars=calendars,
        wbs=(),
        activities=activities,
        relationships=tuple(links),
        assignments=(),
        activity_codes=(),
    )
    return schedule, options


def _minute(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.replace(second=0, microsecond=0)


@given(_nets())
@settings(max_examples=500, deadline=None, derandomize=True)
def test_fast_matches_reference_to_the_minute(case: tuple[Schedule, EngineOptions]) -> None:
    schedule, options = case
    reference = schedule_cpm(schedule, replace(options, engine="reference"))
    fast = schedule_cpm(schedule, replace(options, engine="fast"))
    assert fast.skipped == reference.skipped
    assert fast.approximations == reference.approximations
    assert _minute(fast.project_finish) == _minute(reference.project_finish)
    assert set(fast.by_id) == set(reference.by_id)
    for task_id, left in reference.by_id.items():
        right = fast.by_id[task_id]
        assert _minute(right.early_start) == _minute(left.early_start)
        assert _minute(right.early_finish) == _minute(left.early_finish)
        assert _minute(right.late_start) == _minute(left.late_start)
        assert _minute(right.late_finish) == _minute(left.late_finish)
        assert round(right.total_float_hours * 60) == round(left.total_float_hours * 60)
        assert round(right.free_float_hours * 60) == round(left.free_float_hours * 60)
        assert right.critical is left.critical
        assert right.driving_pred_ids == left.driving_pred_ids
        if left.early_start.second or left.early_start.microsecond:
            assert right.early_start == left.early_start
            assert right.early_finish == left.early_finish
