"""Array CPM. The pure-Python engine stays in ``cpm.py`` as the oracle."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta

import numpy as np

from atlaspmo.calendars.worktime import CalendarLimitError, WorkCalendar, elapsed_calendar
from atlaspmo.engine.cpm import (
    CpmResult,
    ScheduledActivity,
    _clocks,
    _data_date,
    _Node,
    _nodes,
    _pack,
    _project_calendar,
    _rollup,
    _topo,
    _wire,
    schedule_cpm_reference,
)
from atlaspmo.engine.options import EngineOptions
from atlaspmo.io.validate import validate_schedule
from atlaspmo.model.schedule import Activity, Schedule
from atlaspmo.numeric.intervals import UnsupportedCalendar, build_tables, from_minute, to_minute
from atlaspmo.numeric.kernels import GROW, LIMIT, execute

_EPOCH = date(1, 1, 1)
_PROGRESS = {"retained": 0, "progress_override": 1, "actual_dates": 2}
_FLOAT = {"minimum": 0, "start": 1, "finish": 2}
_RULE = {"float": 0, "longest": 1}
_LINK = {"PR_FS": 0, "PR_SS": 1, "PR_FF": 2, "PR_SF": 3}
_CSTR = {
    "CS_MSO": 1,
    "CS_MSOA": 2,
    "CS_MSOB": 3,
    "CS_MEO": 4,
    "CS_MEOA": 5,
    "CS_MEOB": 6,
    "CS_MANDSTART": 7,
    "CS_MANDFIN": 8,
    "CS_ALAP": 9,
}
_CACHE: dict[tuple[object, ...], Compiled] = {}
_KEYS: list[tuple[object, ...]] = []
LAST: dict[str, object] = {
    "path": "fast",
    "compile_s": 0.0,
    "pass_s": 0.0,
    "pack_s": 0.0,
    "cached": False,
}


def horizon_days(total_minutes: int, daily: float) -> int:
    """Calendar days that cover a serial chain on this daily rate."""
    if daily <= 0:
        daily = 60.0
    return max(21, int(total_minutes / daily) + 14)


@dataclass
class Compiled:
    empty: CpmResult | None
    notes: list[str]
    skipped: tuple[str, ...]
    schedule: Schedule
    options: EngineOptions
    task_ids: list[str]
    labels: list[str]
    activities: list[Activity]
    node_clocks: list[WorkCalendar]
    scan: list[int]
    pred_ids: list[str]
    raw_start: list[datetime | None]
    raw_end: list[datetime | None]
    clocks: list[WorkCalendar]
    clock_map: dict[str, WorkCalendar]
    total_minutes: int
    daily: float
    lag_days: int
    min_day: date
    max_day: date
    progress: int
    float_kind: int
    float_name: str
    critical_minutes: int
    rule: int
    rule_name: str
    data_date: int
    has_rollup: bool
    cal: np.ndarray
    duration: np.ndarray
    started: np.ndarray
    finished: np.ndarray
    act_start: np.ndarray
    act_end: np.ndarray
    task_type: np.ndarray
    cstr_a: np.ndarray
    cstr_a_at: np.ndarray
    cstr_b: np.ndarray
    cstr_b_at: np.ndarray
    pred_ptr: np.ndarray
    pred_from: np.ndarray
    pred_type: np.ndarray
    pred_lag: np.ndarray
    pred_lag_cal: np.ndarray
    succ_ptr: np.ndarray
    succ_to: np.ndarray
    succ_type: np.ndarray
    succ_lag: np.ndarray
    succ_lag_cal: np.ndarray
    es: np.ndarray
    ef: np.ndarray
    ls: np.ndarray
    lf: np.ndarray
    ef_pre: np.ndarray
    remain: np.ndarray
    total_f: np.ndarray
    free_f: np.ndarray
    critical: np.ndarray
    drive: np.ndarray
    done: np.ndarray
    on_long: np.ndarray
    viol_ms_f: np.ndarray
    viol_mf_f: np.ndarray
    viol_ms_b: np.ndarray
    viol_mf_b: np.ndarray
    logic_es: np.ndarray
    logic_ef: np.ndarray
    logic_ls: np.ndarray
    logic_lf: np.ndarray
    alap_blocked: np.ndarray
    tables: (
        tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int]
        | None
    ) = None


def schedule_cpm_fast(schedule: Schedule, options: EngineOptions | None = None) -> CpmResult:
    """Same dates as the reference engine, computed from arrays."""
    started_at = time.perf_counter()
    chosen, notes = _normalize(options or EngineOptions())
    key = _key(schedule, chosen)
    compiled = _CACHE.get(key)
    cached = compiled is not None
    if compiled is None:
        try:
            compiled = _compile(schedule, chosen, notes)
        except UnsupportedCalendar:
            LAST["path"] = "reference"
            return schedule_cpm_reference(schedule, replace(chosen, engine="reference"))
        _remember(key, compiled)
    LAST["compile_s"] = 0.0 if cached else time.perf_counter() - started_at
    LAST["cached"] = cached
    if compiled.empty is not None:
        LAST["path"] = "fast"
        LAST["pass_s"] = 0.0
        LAST["pack_s"] = 0.0
        return compiled.empty
    try:
        code = _ensure(compiled)
    except UnsupportedCalendar:
        LAST["path"] = "reference"
        return schedule_cpm_reference(schedule, replace(chosen, engine="reference"))
    if code == LIMIT:
        raise CalendarLimitError("horizonte de calendario agotado")
    if code != 0:
        raise CalendarLimitError("horizonte de calendario agotado")
    packed_at = time.perf_counter()
    result = _result(compiled)
    LAST["pack_s"] = time.perf_counter() - packed_at
    LAST["path"] = "fast"
    return result


def _normalize(options: EngineOptions) -> tuple[EngineOptions, list[str]]:
    notes: list[str] = []
    rule = options.critical_rule
    if rule not in _RULE:
        notes.append("Criterio de crítico desconocido. Se usó holgura.")
        rule = "float"
    progress = options.progress
    if progress not in _PROGRESS:
        notes.append("Opción de avance desconocida. Se usó retained logic.")
        progress = "retained"
    chosen = EngineOptions(
        progress,
        options.lag_calendar,
        options.float_kind,
        options.critical_hours,
        rule,
        "fast",
    )
    return chosen, notes


def _key(schedule: Schedule, options: EngineOptions) -> tuple[object, ...]:
    return (
        id(schedule.activities),
        id(schedule.relationships),
        id(schedule.calendars),
        id(schedule.projects),
        options.progress,
        options.lag_calendar,
        options.float_kind,
        options.critical_hours,
        options.critical_rule,
    )


def _remember(key: tuple[object, ...], compiled: Compiled) -> None:
    if key not in _CACHE:
        _KEYS.append(key)
    _CACHE[key] = compiled
    while len(_KEYS) > 4:
        _CACHE.pop(_KEYS.pop(0), None)


def _compile(schedule: Schedule, options: EngineOptions, notes: list[str]) -> Compiled:
    cycles = [item.message_es for item in validate_schedule(schedule) if item.code == "cycle"]
    if cycles:
        return _empty(schedule, options, notes + cycles, ())
    data_date = _data_date(schedule, notes)
    if data_date is None:
        return _empty(schedule, options, notes, ())
    clocks, clock_notes = _clocks(schedule)
    notes.extend(clock_notes)
    if any(item.task_type == "TT_Rsrc" for item in schedule.activities):
        notes.append("TT_Rsrc usa el calendario de la actividad. El del recurso no se lee.")
    if any(item.expect_end_date is not None for item in schedule.activities):
        notes.append("expect_end_date no mueve fechas en esta fase.")
    nodes, skipped = _nodes(schedule, clocks, notes)
    _wire(schedule, nodes, notes)
    order = _topo(nodes)
    if len(order) < len(nodes):
        notes.append("Ciclo: el motor no asigna fechas.")
        return _empty(schedule, options, notes, tuple(skipped))
    if not order:
        return _empty(schedule, options, notes, tuple(skipped))
    return _arrays(schedule, options, notes, tuple(skipped), clocks, nodes, order, data_date)


def _empty(
    schedule: Schedule,
    options: EngineOptions,
    notes: list[str],
    skipped: tuple[str, ...],
) -> Compiled:
    blank = np.zeros(0, dtype=np.int64)
    flags = np.zeros(0, dtype=np.uint8)
    return Compiled(
        empty=CpmResult({}, None, tuple(notes), skipped),
        notes=list(notes),
        skipped=skipped,
        schedule=schedule,
        options=options,
        task_ids=[],
        labels=[],
        activities=[],
        node_clocks=[],
        scan=[],
        pred_ids=[],
        raw_start=[],
        raw_end=[],
        clocks=[],
        clock_map={},
        total_minutes=0,
        daily=60.0,
        lag_days=2,
        min_day=_EPOCH,
        max_day=_EPOCH,
        progress=0,
        float_kind=0,
        float_name=options.float_kind,
        critical_minutes=0,
        rule=0,
        rule_name=options.critical_rule,
        data_date=0,
        has_rollup=False,
        cal=blank,
        duration=blank,
        started=flags,
        finished=flags,
        act_start=blank,
        act_end=blank,
        task_type=flags,
        cstr_a=flags,
        cstr_a_at=blank,
        cstr_b=flags,
        cstr_b_at=blank,
        pred_ptr=np.zeros(1, dtype=np.int64),
        pred_from=blank,
        pred_type=flags,
        pred_lag=blank,
        pred_lag_cal=blank,
        succ_ptr=np.zeros(1, dtype=np.int64),
        succ_to=blank,
        succ_type=flags,
        succ_lag=blank,
        succ_lag_cal=blank,
        es=blank,
        ef=blank,
        ls=blank,
        lf=blank,
        ef_pre=blank,
        remain=blank,
        total_f=blank,
        free_f=blank,
        critical=flags,
        drive=flags,
        done=flags,
        on_long=flags,
        viol_ms_f=flags,
        viol_mf_f=flags,
        viol_ms_b=flags,
        viol_mf_b=flags,
        logic_es=blank,
        logic_ef=blank,
        logic_ls=blank,
        logic_lf=blank,
        alap_blocked=flags,
    )


def _arrays(
    schedule: Schedule,
    options: EngineOptions,
    notes: list[str],
    skipped: tuple[str, ...],
    clocks: dict[str, WorkCalendar],
    nodes: dict[str, _Node],
    order: list[str],
    data_date: datetime,
) -> Compiled:
    project = _project_calendar(schedule, clocks)
    elapsed = elapsed_calendar()
    pool: list[WorkCalendar] = []
    index_of: dict[int, int] = {}

    def intern(clock: WorkCalendar) -> int:
        key = id(clock)
        found = index_of.get(key)
        if found is not None:
            return found
        index_of[key] = len(pool)
        pool.append(clock)
        return index_of[key]

    place = {task_id: index for index, task_id in enumerate(order)}
    n = len(order)
    cal = np.empty(n, dtype=np.int64)
    duration = np.empty(n, dtype=np.int64)
    started = np.empty(n, dtype=np.uint8)
    finished = np.empty(n, dtype=np.uint8)
    act_start = np.full(n, -1, dtype=np.int64)
    act_end = np.full(n, -1, dtype=np.int64)
    task_type = np.empty(n, dtype=np.uint8)
    cstr_a = np.zeros(n, dtype=np.uint8)
    cstr_a_at = np.full(n, -1, dtype=np.int64)
    cstr_b = np.zeros(n, dtype=np.uint8)
    cstr_b_at = np.full(n, -1, dtype=np.int64)
    pred_ptr = [0]
    pred_from: list[int] = []
    pred_type: list[int] = []
    pred_lag: list[int] = []
    pred_lag_cal: list[int] = []
    pred_ids: list[str] = []
    succ_ptr = [0]
    succ_to: list[int] = []
    succ_type: list[int] = []
    succ_lag: list[int] = []
    succ_lag_cal: list[int] = []
    task_ids: list[str] = []
    labels: list[str] = []
    activities: list[Activity] = []
    node_clocks: list[WorkCalendar] = []
    raw_start: list[datetime | None] = []
    raw_end: list[datetime | None] = []
    total = 0
    moments = [data_date]
    for task_id in order:
        node = nodes[task_id]
        index = place[task_id]
        activity = node.activity
        cal[index] = intern(node.calendar)
        duration[index] = node.duration
        total += node.duration
        started[index] = 1 if node.started else 0
        finished[index] = 1 if node.finished else 0
        if activity.act_start_date is not None:
            act_start[index] = to_minute(activity.act_start_date)
            moments.append(activity.act_start_date)
        if activity.act_end_date is not None:
            act_end[index] = to_minute(activity.act_end_date)
            moments.append(activity.act_end_date)
        if activity.cstr_date is not None:
            moments.append(activity.cstr_date)
        if activity.cstr_date2 is not None:
            moments.append(activity.cstr_date2)
        task_type[index] = _type_code(activity.task_type)
        _store_constraint(activity.cstr_type, activity.cstr_date, cstr_a, cstr_a_at, index)
        _store_constraint(activity.cstr_type2, activity.cstr_date2, cstr_b, cstr_b_at, index)
        task_ids.append(task_id)
        labels.append(activity.task_code or activity.task_id or "")
        activities.append(activity)
        node_clocks.append(node.calendar)
        raw_start.append(activity.act_start_date)
        raw_end.append(activity.act_end_date)
        for link in node.preds:
            pred_from.append(place[link.pred_task_id or ""])
            pred_type.append(_LINK[link.pred_type or "PR_FS"])
            lag = int(round((link.lag_hr_cnt or 0) * 60))
            pred_lag.append(lag)
            pred_lag_cal.append(
                _lag_index(options, nodes[link.pred_task_id or ""], node, project, elapsed, intern)
            )
            pred_ids.append(link.pred_task_id or "")
        pred_ptr.append(len(pred_from))
        for link in node.succs:
            succ_to.append(place[link.task_id or ""])
            succ_type.append(_LINK[link.pred_type or "PR_FS"])
            lag = int(round((link.lag_hr_cnt or 0) * 60))
            succ_lag.append(lag)
            succ_lag_cal.append(
                _lag_index(options, node, nodes[link.task_id or ""], project, elapsed, intern)
            )
        succ_ptr.append(len(succ_to))
    scan = [place[task_id] for task_id in nodes]
    max_lag = 0
    for lag in pred_lag:
        max_lag = max(max_lag, abs(lag))
    daily = _daily(pool)
    lag_days = int(max_lag / daily) + 2 if daily > 0 else max_lag + 2
    flags = np.zeros(n, dtype=np.uint8)
    edges = np.zeros(len(pred_from), dtype=np.uint8)
    return Compiled(
        empty=None,
        notes=list(notes),
        skipped=skipped,
        schedule=schedule,
        options=options,
        task_ids=task_ids,
        labels=labels,
        activities=activities,
        node_clocks=node_clocks,
        scan=scan,
        pred_ids=pred_ids,
        raw_start=raw_start,
        raw_end=raw_end,
        clocks=pool,
        clock_map=clocks,
        total_minutes=total,
        daily=daily,
        lag_days=lag_days,
        min_day=min(item.date() for item in moments),
        max_day=max(item.date() for item in moments),
        progress=_PROGRESS[options.progress],
        float_kind=_FLOAT.get(options.float_kind, 0),
        float_name=options.float_kind,
        critical_minutes=int(round(options.critical_hours * 60)),
        rule=_RULE[options.critical_rule],
        rule_name=options.critical_rule,
        data_date=to_minute(data_date),
        has_rollup=any(item.task_type in {"TT_LOE", "TT_WBS"} for item in schedule.activities),
        cal=cal,
        duration=duration,
        started=started,
        finished=finished,
        act_start=act_start,
        act_end=act_end,
        task_type=task_type,
        cstr_a=cstr_a,
        cstr_a_at=cstr_a_at,
        cstr_b=cstr_b,
        cstr_b_at=cstr_b_at,
        pred_ptr=np.asarray(pred_ptr, dtype=np.int64),
        pred_from=np.asarray(pred_from, dtype=np.int64),
        pred_type=np.asarray(pred_type, dtype=np.uint8),
        pred_lag=np.asarray(pred_lag, dtype=np.int64),
        pred_lag_cal=np.asarray(pred_lag_cal, dtype=np.int64),
        succ_ptr=np.asarray(succ_ptr, dtype=np.int64),
        succ_to=np.asarray(succ_to, dtype=np.int64),
        succ_type=np.asarray(succ_type, dtype=np.uint8),
        succ_lag=np.asarray(succ_lag, dtype=np.int64),
        succ_lag_cal=np.asarray(succ_lag_cal, dtype=np.int64),
        es=np.empty(n, dtype=np.int64),
        ef=np.empty(n, dtype=np.int64),
        ls=np.empty(n, dtype=np.int64),
        lf=np.empty(n, dtype=np.int64),
        ef_pre=np.empty(n, dtype=np.int64),
        remain=np.full(n, -1, dtype=np.int64),
        total_f=np.empty(n, dtype=np.int64),
        free_f=np.empty(n, dtype=np.int64),
        critical=flags,
        drive=edges,
        done=np.zeros(n, dtype=np.uint8),
        on_long=np.zeros(n, dtype=np.uint8),
        viol_ms_f=np.zeros(n, dtype=np.uint8),
        viol_mf_f=np.zeros(n, dtype=np.uint8),
        viol_ms_b=np.zeros(n, dtype=np.uint8),
        viol_mf_b=np.zeros(n, dtype=np.uint8),
        logic_es=np.empty(n, dtype=np.int64),
        logic_ef=np.empty(n, dtype=np.int64),
        logic_ls=np.empty(n, dtype=np.int64),
        logic_lf=np.empty(n, dtype=np.int64),
        alap_blocked=np.zeros(n, dtype=np.uint8),
    )


def _type_code(task_type: str | None) -> int:
    if task_type == "TT_Mile":
        return 1
    if task_type == "TT_FinMile":
        return 2
    return 0


def _store_constraint(
    code: str | None,
    when: datetime | None,
    codes: np.ndarray,
    moments: np.ndarray,
    index: int,
) -> None:
    if code == "CS_ALAP":
        codes[index] = 9
        return
    number = _CSTR.get(code or "", 0)
    if number == 0 or when is None:
        return
    codes[index] = number
    moments[index] = to_minute(when)


def _lag_index(
    options: EngineOptions,
    pred: _Node,
    succ: _Node,
    project: WorkCalendar | None,
    elapsed: WorkCalendar,
    intern: Callable[[WorkCalendar], int],
) -> int:
    if options.lag_calendar == "elapsed":
        return intern(elapsed)
    if options.lag_calendar == "successor":
        return intern(succ.calendar)
    if options.lag_calendar == "project" and project is not None:
        return intern(project)
    return intern(pred.calendar)


def _daily(clocks: list[WorkCalendar]) -> float:
    start = datetime(2026, 1, 5)
    end = datetime(2026, 1, 12)
    rates: list[float] = []
    for clock in clocks:
        try:
            worked = clock.work_between(start, end)
        except CalendarLimitError:
            continue
        if worked > 0:
            rates.append(worked / 7.0)
    if not rates:
        return 60.0
    return min(rates)


def _shift_day(day: date, delta: int) -> date:
    if delta >= 0:
        room = (date.max - day).days
        return day + timedelta(days=min(delta, room))
    room = (day - _EPOCH).days
    return day - timedelta(days=min(-delta, room))


def _ensure(compiled: Compiled) -> int:
    if compiled.tables is not None:
        return _invoke(compiled)
    days = max(horizon_days(compiled.total_minutes, compiled.daily), compiled.lag_days)
    code = GROW
    for _ in range(6):
        start = _shift_day(compiled.min_day, -days)
        end = _shift_day(compiled.max_day, days)
        compiled.tables = build_tables(compiled.clocks, start, end)
        code = _invoke(compiled)
        if code in (0, LIMIT):
            if code == LIMIT:
                compiled.tables = None
            return code
        days *= 2
    compiled.tables = None
    return code


def _invoke(compiled: Compiled) -> int:
    assert compiled.tables is not None
    starts, ends, cum, cum_end, off, base_cum, window_lo, window_hi = compiled.tables
    started_at = time.perf_counter()
    code = execute(
        compiled.cal,
        compiled.duration,
        compiled.started,
        compiled.finished,
        compiled.act_start,
        compiled.act_end,
        compiled.task_type,
        compiled.cstr_a,
        compiled.cstr_a_at,
        compiled.cstr_b,
        compiled.cstr_b_at,
        compiled.pred_ptr,
        compiled.pred_from,
        compiled.pred_type,
        compiled.pred_lag,
        compiled.pred_lag_cal,
        compiled.succ_ptr,
        compiled.succ_to,
        compiled.succ_type,
        compiled.succ_lag,
        compiled.succ_lag_cal,
        starts,
        ends,
        cum,
        cum_end,
        off,
        base_cum,
        window_lo,
        window_hi,
        compiled.data_date,
        compiled.progress,
        compiled.float_kind,
        compiled.critical_minutes,
        compiled.rule,
        compiled.es,
        compiled.ef,
        compiled.ls,
        compiled.lf,
        compiled.ef_pre,
        compiled.remain,
        compiled.total_f,
        compiled.free_f,
        compiled.critical,
        compiled.drive,
        compiled.done,
        compiled.on_long,
        compiled.viol_ms_f,
        compiled.viol_mf_f,
        compiled.viol_ms_b,
        compiled.viol_mf_b,
        compiled.logic_es,
        compiled.logic_ef,
        compiled.logic_ls,
        compiled.logic_lf,
        compiled.alap_blocked,
    )
    LAST["pass_s"] = time.perf_counter() - started_at
    return code


def _result(compiled: Compiled) -> CpmResult:
    notes = list(compiled.notes)
    by_id: dict[str, ScheduledActivity] = {}
    finishes: list[datetime] = []
    driving_by_index: list[tuple[str, ...]] = []
    for index, task_id in enumerate(compiled.task_ids):
        early_s, early_f, late_s, late_f = _dates(compiled, index)
        finishes.append(_pre_finish(compiled, index))
        driving = _driving(compiled, index)
        driving_by_index.append(driving)
        by_id[task_id] = ScheduledActivity(
            task_id=task_id,
            early_start=early_s,
            early_finish=early_f,
            late_start=late_s,
            late_finish=late_f,
            total_float_hours=int(compiled.total_f[index]) / 60,
            free_float_hours=int(compiled.free_f[index]) / 60,
            critical=bool(compiled.critical[index]),
            driving_pred_ids=driving,
        )
        if compiled.viol_ms_f[index] == 1:
            notes.append(_forward_note(compiled.labels[index], compiled, index, start=True))
        if compiled.viol_mf_f[index] == 1:
            notes.append(_forward_note(compiled.labels[index], compiled, index, start=False))
    for index in range(len(compiled.task_ids) - 1, -1, -1):
        if compiled.viol_ms_b[index] == 1:
            notes.append(_backward_note(compiled.labels[index], compiled, index, start=True))
        if compiled.viol_mf_b[index] == 1:
            notes.append(_backward_note(compiled.labels[index], compiled, index, start=False))
    for index in compiled.scan:
        if compiled.alap_blocked[index] == 1:
            code = compiled.activities[index].task_code
            notes.append(f"{code}: ALAP con sucesoras no se reprograma en esta fase.")
    project_finish = max(finishes) if finishes else None
    _restore_finish_seconds(compiled, by_id, project_finish)
    on_longest = _longest(compiled, finishes, driving_by_index, project_finish)
    if compiled.rule == 1:
        for task_id, item in list(by_id.items()):
            by_id[task_id] = replace(
                item,
                critical=task_id in on_longest,
            )
    if compiled.has_rollup:
        _attach_rollup(compiled, by_id, notes, on_longest)
    return CpmResult(by_id, project_finish, tuple(dict.fromkeys(notes)), compiled.skipped)


def _pre_finish(compiled: Compiled, index: int) -> datetime:
    """Early finish from before ALAP. An actual keeps its seconds."""
    pre = int(compiled.ef_pre[index])
    raw_end = compiled.raw_end[index]
    if compiled.done[index] == 1 and raw_end is not None and to_minute(raw_end) == pre:
        return raw_end
    return from_minute(pre)


def _driving(compiled: Compiled, index: int) -> tuple[str, ...]:
    raw = compiled.raw_start[index]
    # Only a started activity publishes the actual. A calendar bound has no seconds,
    # so that actual is not a driving match. A not-started actual is ignored.
    if compiled.started[index] == 1:
        anchor = int(compiled.logic_es[index])
        if raw is not None and (raw.second or raw.microsecond) and to_minute(raw) == anchor:
            return ()
    found: list[str] = []
    for edge in range(int(compiled.pred_ptr[index]), int(compiled.pred_ptr[index + 1])):
        if compiled.drive[edge] == 1:
            found.append(compiled.pred_ids[edge])
    return tuple(found)


def _open_alap(compiled: Compiled, index: int) -> bool:
    if int(compiled.succ_ptr[index + 1]) != int(compiled.succ_ptr[index]):
        return False
    return int(compiled.cstr_a[index]) == 9 or int(compiled.cstr_b[index]) == 9


# These codes do not enter the backward constraint pass, so they leave the project finish.
_LATE_NEUTRAL = {None, "CS_ALAP", "CS_MSOA", "CS_MEOA"}


def _finish_anchor(compiled: Compiled, index: int, project_finish: datetime | None) -> bool:
    if project_finish is None or compiled.done[index] == 1:
        return False
    if int(compiled.succ_ptr[index + 1]) != int(compiled.succ_ptr[index]):
        return False
    if int(compiled.lf[index]) != to_minute(project_finish):
        return False
    activity = compiled.activities[index]
    # A not-started start milestone snaps the late dates onto the calendar, dropping seconds.
    if activity.task_type == "TT_Mile" and compiled.started[index] == 0:
        return False
    return _constraints_leave_project_finish(compiled, index, project_finish)


def _constraints_leave_project_finish(
    compiled: Compiled,
    index: int,
    project_finish: datetime,
) -> bool:
    activity = compiled.activities[index]
    clock = compiled.node_clocks[index]
    duration = int(compiled.duration[index])
    pairs = (
        (activity.cstr_type, activity.cstr_date),
        (activity.cstr_type2, activity.cstr_date2),
    )
    for code, raw in pairs:
        if code in _LATE_NEUTRAL or raw is None:
            continue
        if code in {"CS_MEO", "CS_MEOB"}:
            if clock.subtract_work(raw, 0) < project_finish:
                return False
            continue
        if code in {"CS_MSO", "CS_MSOB"}:
            capped = clock.subtract_work(raw, 0)
            from_start = capped if duration == 0 else clock.add_work(capped, duration)
            if from_start < project_finish:
                return False
            continue
        return False
    return True


def _restore_finish_seconds(
    compiled: Compiled,
    by_id: dict[str, ScheduledActivity],
    project_finish: datetime | None,
) -> None:
    for index, task_id in enumerate(compiled.task_ids):
        item = by_id[task_id]
        late_f = item.late_finish
        early_s = item.early_start
        early_f = item.early_finish
        if _finish_anchor(compiled, index, project_finish) and project_finish is not None:
            late_f = project_finish
        if _open_alap(compiled, index):
            early_s = item.late_start
            early_f = late_f
        unchanged = (
            late_f is item.late_finish
            and early_s is item.early_start
            and early_f is item.early_finish
        )
        if unchanged:
            continue
        by_id[task_id] = replace(
            item,
            early_start=early_s,
            early_finish=early_f,
            late_finish=late_f,
        )


def _longest(
    compiled: Compiled,
    finishes: list[datetime],
    driving: list[tuple[str, ...]],
    project_finish: datetime | None,
) -> set[str]:
    if project_finish is None or compiled.rule != 1:
        return set()
    by_id = {task_id: index for index, task_id in enumerate(compiled.task_ids)}
    stack = [
        compiled.task_ids[index]
        for index, finish in enumerate(finishes)
        if finish == project_finish
    ]
    on: set[str] = set()
    while stack:
        current = stack.pop()
        if current in on:
            continue
        on.add(current)
        for pred_id in driving[by_id[current]]:
            if pred_id in by_id and pred_id not in on:
                stack.append(pred_id)
    return on


def _dates(compiled: Compiled, index: int) -> tuple[datetime, datetime, datetime, datetime]:
    if compiled.done[index] == 1:
        early_s = compiled.raw_start[index] or from_minute(int(compiled.es[index]))
        early_f = compiled.raw_end[index] or from_minute(int(compiled.ef[index]))
        return early_s, early_f, early_s, early_f
    if compiled.started[index] == 1:
        early_s = _keep(int(compiled.es[index]), compiled.raw_start[index])
    else:
        early_s = from_minute(int(compiled.es[index]))
    return (
        early_s,
        from_minute(int(compiled.ef[index])),
        from_minute(int(compiled.ls[index])),
        from_minute(int(compiled.lf[index])),
    )


def _keep(minute: int, raw: datetime | None) -> datetime:
    if raw is not None and to_minute(raw) == minute:
        return raw
    return from_minute(minute)


def _shown(minute: int) -> str:
    return from_minute(minute).strftime("%Y-%m-%d %H:%M")


def _forward_note(label: str, compiled: Compiled, index: int, *, start: bool) -> str:
    if start:
        imposed = _first(compiled, index, 7)
        logic = int(compiled.logic_es[index])
        return (
            f"{label}: CS_MANDSTART impone {_shown(imposed)} "
            f"y viola la lógica (inicio por red {_shown(logic)})."
        )
    imposed = _first(compiled, index, 8)
    logic = int(compiled.logic_ef[index])
    return (
        f"{label}: CS_MANDFIN impone {_shown(imposed)} "
        f"y viola la lógica (fin por red {_shown(logic)})."
    )


def _backward_note(label: str, compiled: Compiled, index: int, *, start: bool) -> str:
    if start:
        imposed = _first(compiled, index, 7)
        logic = int(compiled.logic_ls[index])
        return (
            f"{label}: CS_MANDSTART impone {_shown(imposed)} en el pase atrás "
            f"y viola la lógica (inicio tarde por red {_shown(logic)})."
        )
    imposed = _first(compiled, index, 8)
    logic = int(compiled.logic_lf[index])
    return (
        f"{label}: CS_MANDFIN impone {_shown(imposed)} en el pase atrás "
        f"y viola la lógica (fin tarde por red {_shown(logic)})."
    )


def _first(compiled: Compiled, index: int, code: int) -> int:
    if int(compiled.cstr_a[index]) == code and int(compiled.cstr_a_at[index]) >= 0:
        return int(compiled.cstr_a_at[index])
    return int(compiled.cstr_b_at[index])


def _attach_rollup(
    compiled: Compiled,
    by_id: dict[str, ScheduledActivity],
    notes: list[str],
    on_longest: set[str],
) -> None:
    nodes: dict[str, _Node] = {}
    for index, task_id in enumerate(compiled.task_ids):
        item = by_id[task_id]
        remain = int(compiled.remain[index])
        nodes[task_id] = _Node(
            activity=compiled.activities[index],
            duration=int(compiled.duration[index]),
            calendar=compiled.node_clocks[index],
            early_start=item.early_start,
            early_finish=item.early_finish,
            late_start=item.late_start,
            late_finish=item.late_finish,
            remaining_start=from_minute(remain) if remain >= 0 else None,
            started=bool(compiled.started[index]),
            finished=bool(compiled.finished[index]),
        )
    _rollup(compiled.schedule, nodes, compiled.clock_map, notes)
    for task_id, node in nodes.items():
        if task_id in by_id or node.early_start is None:
            continue
        by_id[task_id] = _pack(
            node,
            nodes,
            compiled.float_name,
            compiled.critical_minutes,
            compiled.rule_name,
            on_longest,
        )
