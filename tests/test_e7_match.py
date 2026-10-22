"""Fast engine against the pure-Python reference on fixed edges."""

from dataclasses import replace
from datetime import datetime

import pytest

from atlaspmo.calendars.worktime import CalendarLimitError
from atlaspmo.engine.cpm import schedule_cpm
from atlaspmo.engine.fast import LAST, horizon_days
from atlaspmo.engine.options import EngineOptions
from atlaspmo.model.schedule import Activity, Calendar, Project, Relationship, Schedule

DATA = datetime(2026, 1, 5, 8, 0)
WEEK = "".join(f"(0||{number}()((0||0(s|08:00|f|16:00)())))" for number in range(1, 8))
WEEK_TEXT = f"(0||CalendarData()((0||DaysOfWeek()({WEEK}))(0||VIEW(ShowTotal|N)())))"
OVERLAP = (
    "(0||CalendarData()((0||DaysOfWeek()((0||2()((0||0(s|08:00|f|16:00)())"
    "(0||0(s|12:00|f|18:00)())))))(0||VIEW(ShowTotal|N)())))"
)


def _activity(
    task_id: str,
    code: str,
    *,
    hours: float = 8,
    kind: str = "TT_Task",
    status: str = "TK_NotStart",
    calendar: str = "C1",
    wbs: str = "W1",
    cstr: str | None = None,
    cstr_date: datetime | None = None,
    cstr2: str | None = None,
    cstr_date2: datetime | None = None,
    act_start: datetime | None = None,
    act_end: datetime | None = None,
    expect: datetime | None = None,
) -> Activity:
    return Activity(
        task_id=task_id,
        proj_id="1",
        wbs_id=wbs,
        clndr_id=calendar,
        task_code=code,
        task_name=code,
        task_type=kind,
        status_code=status,
        complete_pct_type=None,
        cstr_type=cstr,
        cstr_type2=cstr2,
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
        cstr_date2=cstr_date2,
        expect_end_date=expect,
    )


def _link(
    link_id: str,
    pred: str,
    succ: str,
    kind: str = "PR_FS",
    lag: float | None = 0,
) -> Relationship:
    return Relationship(link_id, succ, pred, "1", "1", kind, lag)


def _schedule(
    activities: list[Activity],
    links: list[Relationship],
    *,
    calendar: str = WEEK_TEXT,
    data: datetime | None = DATA,
    extra_project: Project | None = None,
) -> Schedule:
    projects = [Project("1", "P", "P", "C1", data, None, None)]
    if extra_project is not None:
        projects.append(extra_project)
    return Schedule(
        projects=tuple(projects),
        calendars=(Calendar("C1", "C1", "1", 8, None, calendar),),
        wbs=(),
        activities=tuple(activities),
        relationships=tuple(links),
        assignments=(),
        activity_codes=(),
    )


def _same(schedule: Schedule, options: EngineOptions | None = None) -> None:
    chosen = options or EngineOptions()
    reference = schedule_cpm(schedule, replace(chosen, engine="reference"))
    fast = schedule_cpm(schedule, replace(chosen, engine="fast"))
    assert fast.skipped == reference.skipped
    assert fast.approximations == reference.approximations
    assert fast.project_finish == reference.project_finish
    assert set(fast.by_id) == set(reference.by_id)
    for task_id, left in reference.by_id.items():
        right = fast.by_id[task_id]
        assert right.early_start == left.early_start
        assert right.early_finish == left.early_finish
        assert right.late_start == left.late_start
        assert right.late_finish == left.late_finish
        assert right.total_float_hours == left.total_float_hours
        assert right.free_float_hours == left.free_float_hours
        assert right.critical is left.critical
        assert right.driving_pred_ids == left.driving_pred_ids


def test_actual_seconds_do_not_widen_the_longest_path_or_driving():
    done = _schedule(
        [
            _activity(
                "1",
                "A",
                hours=8,
                status="TK_Complete",
                act_start=datetime(2026, 1, 5, 8, 0),
                act_end=datetime(2026, 1, 5, 16, 0, 45),
            ),
            _activity("2", "B", hours=8),
        ],
        [],
    )
    _same(done, EngineOptions(critical_rule="longest"))
    started = _schedule(
        [
            _activity(
                "1",
                "M",
                hours=0,
                kind="TT_Mile",
                cstr="CS_MSO",
                cstr_date=datetime(2026, 1, 5, 16, 0),
            ),
            _activity(
                "2",
                "S",
                hours=8,
                status="TK_Active",
                act_start=datetime(2026, 1, 6, 8, 0, 45),
            ),
        ],
        [_link("10", "1", "2", "PR_SS", 0)],
    )
    _same(started)


def test_not_started_actual_does_not_erase_driving():
    task = _schedule(
        [
            _activity("P", "P", hours=8),
            _activity(
                "B",
                "B",
                hours=8,
                act_start=datetime(2026, 1, 6, 8, 0, 45),
            ),
        ],
        [_link("10", "P", "B", "PR_FS", 0)],
    )
    _same(task, EngineOptions(critical_rule="longest"))
    _same(task)
    milestone = _schedule(
        [
            _activity("P", "P", hours=8),
            _activity(
                "B",
                "B",
                hours=0,
                kind="TT_Mile",
                act_start=datetime(2026, 1, 6, 8, 0, 45),
            ),
        ],
        [_link("10", "P", "B", "PR_FS", 0)],
    )
    _same(milestone, EngineOptions(critical_rule="longest"))


def test_project_finish_seconds_survive_a_constraint_that_does_not_bind():
    done = _activity(
        "1",
        "A",
        hours=8,
        status="TK_Complete",
        act_start=datetime(2026, 1, 5, 8, 0),
        act_end=datetime(2026, 1, 5, 16, 0, 45),
    )
    later = _activity("2", "B", hours=8, cstr="CS_MEOB", cstr_date=datetime(2026, 1, 8, 16, 0))
    _same(_schedule([done, later], []))
    early = _activity("2", "B", hours=8, cstr="CS_MSOA", cstr_date=datetime(2026, 1, 5, 8, 0))
    _same(_schedule([done, early], []))
    _same(_schedule([done, _activity("2", "B", hours=8, cstr="CS_MSO")], []))
    _same(
        _schedule(
            [
                done,
                _activity(
                    "2",
                    "B",
                    hours=8,
                    cstr="CS_ALAP",
                    cstr2="CS_MSOA",
                    cstr_date2=datetime(2026, 1, 5, 8, 0),
                ),
            ],
            [],
        )
    )
    _same(
        _schedule(
            [
                _activity(
                    "1",
                    "A",
                    hours=8,
                    status="TK_Complete",
                    act_start=datetime(2026, 1, 5, 8, 0),
                    act_end=datetime(2026, 1, 5, 15, 30, 45),
                ),
                _activity("2", "M", hours=0, kind="TT_Mile"),
            ],
            [],
        )
    )


def test_free_float_sees_the_successor_after_alap():
    schedule = _schedule(
        [
            _activity("1", "A", hours=1),
            _activity("2", "B", hours=1, cstr="CS_ALAP"),
            _activity("3", "C", hours=4),
        ],
        [_link("10", "1", "2", lag=-8)],
    )
    _same(schedule)


def test_weekday_chain_uses_the_fast_path():
    schedule = _schedule(
        [_activity("1", "A", hours=8), _activity("2", "B", hours=16)],
        [_link("10", "1", "2")],
    )
    _same(schedule)
    assert LAST["path"] == "fast"


def test_constraints_progress_milestones_and_rollup_match():
    start = datetime(2026, 1, 5, 8, 0)
    done = datetime(2026, 1, 5, 15, 30, 45)
    schedule = _schedule(
        [
            _activity("1", "A", hours=8, status="TK_Complete", act_start=start, act_end=done),
            _activity("2", "B", hours=8, cstr="CS_MSOA", cstr_date=datetime(2026, 1, 7, 8, 0)),
            _activity("3", "M", hours=0, kind="TT_Mile"),
            _activity("4", "F", hours=0, kind="TT_FinMile"),
            _activity("5", "L", hours=0, kind="TT_LOE"),
            _activity("6", "W", hours=0, kind="TT_WBS", wbs="W1"),
            _activity("7", "S", hours=8, cstr="CS_ALAP"),
            _activity(
                "8",
                "D",
                hours=4,
                status="TK_Active",
                act_start=datetime(2026, 1, 6, 8, 0),
            ),
        ],
        [
            _link("10", "1", "2"),
            _link("11", "2", "3", "PR_FF", 0),
            _link("12", "3", "4", "PR_SS", -2),
            _link("13", "2", "5"),
            _link("14", "5", "4", "PR_FS", 0),
            _link("15", "4", "7", "PR_SF", 4),
            _link("16", "1", "8", "PR_SS", 0),
        ],
    )
    for progress in ("retained", "progress_override", "actual_dates"):
        for rule in ("float", "longest"):
            for kind in ("minimum", "start", "finish"):
                _same(
                    schedule,
                    EngineOptions(
                        progress=progress,
                        float_kind=kind,
                        critical_rule=rule,
                        critical_hours=8,
                        lag_calendar="successor",
                    ),
                )


def test_both_mandatory_constraints_keep_the_notes():
    schedule = _schedule(
        [
            _activity(
                "1",
                "A",
                hours=8,
                cstr="CS_MANDSTART",
                cstr_date=datetime(2026, 1, 6, 10, 0),
                cstr2="CS_MANDFIN",
                cstr_date2=datetime(2026, 1, 6, 12, 0),
            )
        ],
        [],
    )
    _same(schedule)


def test_missing_lag_cycle_and_two_data_dates_match():
    missing = _schedule(
        [_activity("1", "A"), _activity("2", "B")],
        [_link("10", "1", "2", lag=None)],
    )
    _same(missing)
    cycle = _schedule(
        [_activity("1", "A"), _activity("2", "B")],
        [_link("10", "1", "2"), _link("11", "2", "1")],
    )
    _same(cycle)
    two = _schedule(
        [_activity("1", "A")],
        [],
        extra_project=Project("2", "Q", "Q", "C1", datetime(2026, 1, 6, 8, 0), None, None),
    )
    _same(two)


def test_overlapping_shifts_fall_back_without_an_extra_note():
    schedule = _schedule(
        [_activity("1", "A", hours=8)],
        [],
        calendar=OVERLAP,
    )
    reference = schedule_cpm(schedule, EngineOptions(engine="reference"))
    fast = schedule_cpm(schedule, EngineOptions(engine="fast"))
    assert fast.approximations == reference.approximations
    assert fast.by_id["1"].early_finish == reference.by_id["1"].early_finish
    assert LAST["path"] == "reference"


def test_short_horizon_grows_and_still_matches(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("atlaspmo.engine.fast.horizon_days", lambda _total, _daily: 1)
    assert horizon_days(100, 10) == max(21, int(100 / 10) + 14)
    schedule = _schedule(
        [_activity("1", "A", hours=40), _activity("2", "B", hours=40)],
        [_link("10", "1", "2")],
    )
    _same(schedule)
    assert LAST["path"] == "fast"


def test_exhausted_horizon_names_the_limit(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("atlaspmo.engine.fast.horizon_days", lambda _total, _daily: 1)
    monkeypatch.setattr("atlaspmo.engine.fast._shift_day", lambda day, _delta: day)
    schedule = _schedule([_activity("1", "A", hours=40)], [])
    with pytest.raises(CalendarLimitError, match="horizonte de calendario agotado"):
        schedule_cpm(schedule, EngineOptions(engine="fast"))
