"""CPM on the activity calendar. LOE and WBS summary run after the main pass."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from atlaspmo.calendars.data import parse_clndr_data
from atlaspmo.calendars.worktime import WorkCalendar, elapsed_calendar
from atlaspmo.engine.options import EngineOptions
from atlaspmo.io.validate import validate_schedule
from atlaspmo.model.schedule import Activity, Calendar, Relationship, Schedule

_MAIN = {"TT_Task", "TT_Rsrc", "TT_Mile", "TT_FinMile"}
_MILESTONE = {"TT_Mile", "TT_FinMile"}
_START_ON = {"CS_MSO", "CS_MANDSTART"}
_START_AFTER = {"CS_MSOA"}
_START_BEFORE = {"CS_MSOB"}
_FINISH_ON = {"CS_MEO", "CS_MANDFIN"}
_FINISH_AFTER = {"CS_MEOA"}
_FINISH_BEFORE = {"CS_MEOB"}
_KNOWN_LINKS = {"PR_FS", "PR_SS", "PR_FF", "PR_SF"}


@dataclass(frozen=True)
class ScheduledActivity:
    task_id: str
    early_start: datetime
    early_finish: datetime
    late_start: datetime
    late_finish: datetime
    total_float_hours: float
    free_float_hours: float
    critical: bool


@dataclass(frozen=True)
class CpmResult:
    by_id: dict[str, ScheduledActivity]
    project_finish: datetime | None
    approximations: tuple[str, ...]
    skipped: tuple[str, ...]


@dataclass
class _Node:
    activity: Activity
    duration: int
    calendar: WorkCalendar
    early_start: datetime | None = None
    early_finish: datetime | None = None
    late_start: datetime | None = None
    late_finish: datetime | None = None
    remaining_start: datetime | None = None
    started: bool = False
    finished: bool = False
    preds: list[Relationship] = field(default_factory=list)
    succs: list[Relationship] = field(default_factory=list)


def schedule_cpm(schedule: Schedule, options: EngineOptions | None = None) -> CpmResult:
    """Forward and backward pass. A cycle returns no dates."""
    chosen = options or EngineOptions()
    notes: list[str] = []
    if chosen.progress not in {"retained", "progress_override", "actual_dates"}:
        notes.append("Opción de avance desconocida. Se usó retained logic.")
        chosen = EngineOptions(
            "retained", chosen.lag_calendar, chosen.float_kind, chosen.critical_hours
        )
    cycles = [item.message_es for item in validate_schedule(schedule) if item.code == "cycle"]
    if cycles:
        return CpmResult({}, None, tuple(notes + cycles), ())
    data_date = _data_date(schedule, notes)
    if data_date is None:
        return CpmResult({}, None, tuple(notes), ())
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
        return CpmResult({}, None, tuple(notes), tuple(skipped))
    project_cal = _project_calendar(schedule, clocks)
    elapsed = elapsed_calendar()
    _forward(nodes, order, data_date, chosen, project_cal, elapsed)
    finish = _project_finish(nodes)
    if finish is None:
        return CpmResult({}, None, tuple(notes), tuple(skipped))
    _backward(nodes, order, finish, chosen, project_cal, elapsed)
    _apply_alap(nodes, notes)
    _rollup(schedule, nodes, clocks, notes)
    critical_minutes = int(round(chosen.critical_hours * 60))
    built = {
        task_id: _pack(node, nodes, chosen.float_kind, critical_minutes)
        for task_id, node in nodes.items()
        if node.early_start is not None
        and node.early_finish is not None
        and node.late_start is not None
        and node.late_finish is not None
    }
    return CpmResult(built, finish, tuple(dict.fromkeys(notes)), tuple(skipped))


def _data_date(schedule: Schedule, notes: list[str]) -> datetime | None:
    dates = {item.last_recalc_date for item in schedule.projects if item.last_recalc_date}
    if not dates:
        notes.append("No hay fecha de corte (last_recalc_date).")
        return None
    if len(dates) > 1:
        notes.append("Hay más de una fecha de corte. El motor no elige una.")
        return None
    return next(iter(dates))


def build_clocks(schedule: Schedule) -> tuple[dict[str, WorkCalendar], list[str]]:
    """Calendars the engine can walk. Empty clndr_data is not invented."""
    return _clocks(schedule)


def _clocks(schedule: Schedule) -> tuple[dict[str, WorkCalendar], list[str]]:
    notes: list[str] = []
    parsed: dict[str, WorkCalendar] = {}
    pending = [item for item in schedule.calendars if item.clndr_id]
    guard = 0
    while pending and guard < len(pending) + 2:
        guard += 1
        later: list[Calendar] = []
        for calendar in pending:
            assert calendar.clndr_id is not None
            if calendar.clndr_data:
                parsed[calendar.clndr_id] = WorkCalendar.from_parsed(
                    parse_clndr_data(calendar.clndr_data)
                )
            elif calendar.base_clndr_id and calendar.base_clndr_id in parsed:
                parsed[calendar.clndr_id] = parsed[calendar.base_clndr_id]
                notes.append(f"Calendario {calendar.clndr_id} heredó el base.")
            elif calendar.base_clndr_id:
                later.append(calendar)
            else:
                notes.append(f"Calendario {calendar.clndr_id} sin clndr_data: no se usa.")
        if later == pending:
            for calendar in later:
                notes.append(f"Calendario {calendar.clndr_id} no pudo heredar.")
            break
        pending = later
    return parsed, notes


def _nodes(
    schedule: Schedule,
    clocks: dict[str, WorkCalendar],
    notes: list[str],
) -> tuple[dict[str, _Node], list[str]]:
    nodes: dict[str, _Node] = {}
    skipped: list[str] = []
    for activity in schedule.activities:
        if activity.task_id is None:
            continue
        if activity.task_type in {"TT_LOE", "TT_WBS"}:
            continue
        if activity.task_type not in _MAIN and activity.task_type is not None:
            skipped.append(activity.task_id)
            notes.append(f"{activity.task_code}: tipo {activity.task_type} no se programa.")
            continue
        clock = clocks.get(activity.clndr_id or "")
        if clock is None:
            skipped.append(activity.task_id)
            notes.append(f"{activity.task_code or activity.task_id}: sin calendario usable.")
            continue
        duration = _duration(activity)
        if duration is None:
            skipped.append(activity.task_id)
            notes.append(f"{activity.task_code or activity.task_id}: sin duración.")
            continue
        finished = activity.status_code == "TK_Complete"
        started = activity.status_code == "TK_Active" or finished
        if finished and (activity.act_start_date is None or activity.act_end_date is None):
            skipped.append(activity.task_id)
            notes.append(f"{activity.task_code}: completa sin fechas reales.")
            continue
        nodes[activity.task_id] = _Node(
            activity=activity,
            duration=duration,
            calendar=clock,
            started=started,
            finished=finished,
        )
    return nodes, skipped


def _duration(activity: Activity) -> int | None:
    if activity.task_type in _MILESTONE:
        return 0
    hours = activity.remain_drtn_hr_cnt
    if hours is None:
        hours = activity.target_drtn_hr_cnt
    if hours is None:
        return None
    return int(round(hours * 60))


def _wire(schedule: Schedule, nodes: dict[str, _Node], notes: list[str]) -> None:
    external = False
    missing_lag = False
    for link in schedule.relationships:
        pred = nodes.get(link.pred_task_id or "")
        succ = nodes.get(link.task_id or "")
        if pred is None or succ is None:
            if link.pred_task_id and link.task_id:
                external = True
            continue
        if link.pred_type not in _KNOWN_LINKS:
            notes.append(f"Vínculo {link.task_pred_id}: tipo no usado.")
            continue
        if link.lag_hr_cnt is None:
            missing_lag = True
            continue
        pred.succs.append(link)
        succ.preds.append(link)
    if external:
        notes.append("Hay vínculos cuyo extremo no está en el pase. No mueven fechas.")
    if missing_lag:
        notes.append("Hay vínculos sin lag_hr_cnt. No se tomó el vacío como cero.")


def _topo(nodes: dict[str, _Node]) -> list[str]:
    incoming = {task_id: 0 for task_id in nodes}
    for node in nodes.values():
        for link in node.succs:
            if link.task_id in incoming:
                incoming[link.task_id] += 1
    ready = [task_id for task_id, count in incoming.items() if count == 0]
    order: list[str] = []
    while ready:
        current = ready.pop()
        order.append(current)
        for link in nodes[current].succs:
            succ_id = link.task_id
            if succ_id not in incoming:
                continue
            incoming[succ_id] -= 1
            if incoming[succ_id] == 0:
                ready.append(succ_id)
    return order


def _project_calendar(schedule: Schedule, clocks: dict[str, WorkCalendar]) -> WorkCalendar | None:
    if len(schedule.projects) != 1:
        return None
    return clocks.get(schedule.projects[0].clndr_id or "")


def _forward(
    nodes: dict[str, _Node],
    order: list[str],
    data_date: datetime,
    options: EngineOptions,
    project_cal: WorkCalendar | None,
    elapsed: WorkCalendar,
) -> None:
    for task_id in order:
        node = nodes[task_id]
        pinned = (
            options.progress == "actual_dates"
            and node.activity.act_start_date is not None
            and node.activity.act_end_date is not None
        )
        if pinned:
            node.finished = True
        if node.finished:
            node.early_start = node.activity.act_start_date
            node.early_finish = node.activity.act_end_date
            continue
        ignore_preds = node.started and options.progress in {"progress_override", "actual_dates"}
        bounds: list[datetime] = []
        if node.started and options.progress == "actual_dates":
            origin = node.activity.act_start_date or data_date
            bounds.append(node.calendar.add_work(origin, 0))
        else:
            bounds.append(node.calendar.add_work(data_date, 0))
        if not ignore_preds:
            for link in node.preds:
                pred = nodes[link.pred_task_id or ""]
                if pred.early_finish is None or pred.early_start is None:
                    continue
                lag_cal = _lag_calendar(options, pred, node, project_cal, elapsed)
                bound = _early_start_bound(link, pred, node, lag_cal)
                if node.duration > 0:
                    bound = node.calendar.add_work(bound, 0)
                bounds.append(bound)
        start = _latest(bounds)
        start = _delay_start(node, start)
        finish = start if node.duration == 0 else node.calendar.add_work(start, node.duration)
        if node.started:
            node.remaining_start = start
            node.early_start = node.activity.act_start_date or start
            node.early_finish = finish
        else:
            node.early_start = start
            node.early_finish = finish
        node.early_finish = _delay_finish(node)


def _early_start_bound(
    link: Relationship,
    pred: _Node,
    succ: _Node,
    lag_cal: WorkCalendar,
) -> datetime:
    assert pred.early_start is not None and pred.early_finish is not None
    lag = int(round((link.lag_hr_cnt or 0) * 60))
    if link.pred_type == "PR_SS":
        return _shift(lag_cal, pred.early_start, lag)
    if link.pred_type == "PR_SF":
        finish = _shift(lag_cal, pred.early_start, lag)
        return succ.calendar.subtract_work(finish, succ.duration)
    if link.pred_type == "PR_FF":
        finish = _shift(lag_cal, pred.early_finish, lag)
        return succ.calendar.subtract_work(finish, succ.duration)
    return _shift(lag_cal, pred.early_finish, lag)


def _backward(
    nodes: dict[str, _Node],
    order: list[str],
    project_finish: datetime,
    options: EngineOptions,
    project_cal: WorkCalendar | None,
    elapsed: WorkCalendar,
) -> None:
    for task_id in reversed(order):
        node = nodes[task_id]
        if node.finished and node.early_start is not None and node.early_finish is not None:
            node.late_start = node.early_start
            node.late_finish = node.early_finish
            continue
        lf_bounds: list[datetime] = []
        ls_bounds: list[datetime] = []
        if not node.succs:
            lf_bounds.append(project_finish)
        for link in node.succs:
            succ = nodes[link.task_id or ""]
            if succ.late_start is None or succ.late_finish is None:
                continue
            lag_cal = _lag_calendar(options, node, succ, project_cal, elapsed)
            _late_bounds(link, node, succ, lag_cal, lf_bounds, ls_bounds)
        _constraint_late(node, lf_bounds, ls_bounds)
        late_finish = _earliest(lf_bounds) if lf_bounds else project_finish
        late_start = node.calendar.subtract_work(late_finish, node.duration)
        if ls_bounds:
            capped = _earliest(ls_bounds)
            from_start = node.calendar.add_work(capped, node.duration)
            if from_start < late_finish:
                late_finish = from_start
                late_start = node.calendar.subtract_work(late_finish, node.duration)
            late_start = min(late_start, capped)
        node.late_start = late_start
        node.late_finish = late_finish


def _late_bounds(
    link: Relationship,
    pred: _Node,
    succ: _Node,
    lag_cal: WorkCalendar,
    lf_bounds: list[datetime],
    ls_bounds: list[datetime],
) -> None:
    assert succ.late_start is not None and succ.late_finish is not None
    lag = int(round((link.lag_hr_cnt or 0) * 60))
    if link.pred_type == "PR_SS":
        ls_bounds.append(_shift(lag_cal, succ.late_start, -lag))
        return
    if link.pred_type == "PR_SF":
        ls_bounds.append(_shift(lag_cal, succ.late_finish, -lag))
        return
    if link.pred_type == "PR_FF":
        lf_bounds.append(_shift(lag_cal, succ.late_finish, -lag))
        return
    lf_bounds.append(_shift(lag_cal, succ.late_start, -lag))


def _apply_alap(nodes: dict[str, _Node], notes: list[str]) -> None:
    for node in nodes.values():
        if not _has(node, "CS_ALAP"):
            continue
        if node.succs:
            notes.append(
                f"{node.activity.task_code}: ALAP con sucesoras no se reprograma en esta fase."
            )
            continue
        if node.late_start is None or node.late_finish is None:
            continue
        node.early_start = node.late_start
        node.early_finish = node.late_finish
        node.remaining_start = node.late_start


def _rollup(
    schedule: Schedule,
    nodes: dict[str, _Node],
    clocks: dict[str, WorkCalendar],
    notes: list[str],
) -> None:
    for activity in schedule.activities:
        if activity.task_id is None or activity.task_id in nodes:
            continue
        if activity.task_type == "TT_LOE":
            _place_span(activity, _loe_span(activity, schedule, nodes), nodes, clocks, notes)
        elif activity.task_type == "TT_WBS":
            _place_span(activity, _wbs_span(activity, schedule, nodes), nodes, clocks, notes)


def _loe_span(
    activity: Activity,
    schedule: Schedule,
    nodes: dict[str, _Node],
) -> tuple[datetime, datetime] | None:
    preds = []
    succs = []
    for link in schedule.relationships:
        if link.task_id == activity.task_id and link.pred_task_id in nodes:
            preds.append(nodes[link.pred_task_id])
        if link.pred_task_id == activity.task_id and link.task_id in nodes:
            succs.append(nodes[link.task_id])
    starts = [item.early_start for item in preds if item.early_start is not None]
    finishes = [item.early_finish for item in succs if item.early_finish is not None]
    if not starts:
        starts = [item.early_start for item in succs if item.early_start is not None]
    if not finishes:
        finishes = [item.early_finish for item in preds if item.early_finish is not None]
    if not starts or not finishes:
        return None
    return min(starts), max(finishes)


def _wbs_span(
    activity: Activity,
    schedule: Schedule,
    nodes: dict[str, _Node],
) -> tuple[datetime, datetime] | None:
    children = [
        node
        for node in nodes.values()
        if node.activity.wbs_id == activity.wbs_id
        and node.activity.task_type not in {"TT_WBS", "TT_LOE"}
        and node.early_start is not None
        and node.early_finish is not None
    ]
    if not children:
        return None
    starts = [node.early_start for node in children if node.early_start is not None]
    finishes = [node.early_finish for node in children if node.early_finish is not None]
    return min(starts), max(finishes)


def _place_span(
    activity: Activity,
    span: tuple[datetime, datetime] | None,
    nodes: dict[str, _Node],
    clocks: dict[str, WorkCalendar],
    notes: list[str],
) -> None:
    if span is None or activity.task_id is None:
        notes.append(f"{activity.task_code}: resumen sin fechas de apoyo.")
        return
    clock = clocks.get(activity.clndr_id or "")
    if clock is None:
        notes.append(f"{activity.task_code}: resumen sin calendario.")
        return
    start, finish = span
    label = "LOE" if activity.task_type == "TT_LOE" else "WBS summary"
    notes.append(f"{label} se calcula después del pase y no define la ruta crítica.")
    nodes[activity.task_id] = _Node(
        activity=activity,
        duration=0,
        calendar=clock,
        early_start=start,
        early_finish=finish,
        late_start=start,
        late_finish=finish,
    )


def _pack(
    node: _Node,
    nodes: dict[str, _Node],
    float_kind: str,
    critical_minutes: int,
) -> ScheduledActivity:
    assert node.early_start is not None and node.early_finish is not None
    assert node.late_start is not None and node.late_finish is not None
    origin = node.remaining_start or node.early_start
    start_float = node.calendar.work_between(origin, node.late_start)
    finish_float = node.calendar.work_between(node.early_finish, node.late_finish)
    if float_kind == "start":
        total = start_float
    elif float_kind == "finish":
        total = finish_float
    else:
        total = min(start_float, finish_float)
    return ScheduledActivity(
        task_id=node.activity.task_id or "",
        early_start=node.early_start,
        early_finish=node.early_finish,
        late_start=node.late_start,
        late_finish=node.late_finish,
        total_float_hours=total / 60,
        free_float_hours=_free_float(node, nodes) / 60,
        critical=total <= critical_minutes and node.activity.task_type not in {"TT_LOE", "TT_WBS"},
    )


def _free_float(node: _Node, nodes: dict[str, _Node]) -> int:
    assert node.early_start is not None and node.early_finish is not None
    if not node.succs:
        if node.late_finish is None:
            return 0
        return node.calendar.work_between(node.early_finish, node.late_finish)
    slacks: list[int] = []
    for link in node.succs:
        succ = nodes.get(link.task_id or "")
        if succ is None or succ.early_start is None or succ.early_finish is None:
            continue
        lag = int(round((link.lag_hr_cnt or 0) * 60))
        if link.pred_type == "PR_SS":
            gap = node.calendar.work_between(node.early_start, succ.early_start)
        elif link.pred_type == "PR_FF":
            gap = node.calendar.work_between(node.early_finish, succ.early_finish)
        elif link.pred_type == "PR_SF":
            gap = node.calendar.work_between(node.early_start, succ.early_finish)
        else:
            gap = node.calendar.work_between(node.early_finish, succ.early_start)
        slacks.append(gap - lag)
    if not slacks:
        return 0
    return min(slacks)


def _lag_calendar(
    options: EngineOptions,
    pred: _Node,
    succ: _Node,
    project_cal: WorkCalendar | None,
    elapsed: WorkCalendar,
) -> WorkCalendar:
    if options.lag_calendar == "elapsed":
        return elapsed
    if options.lag_calendar == "successor":
        return succ.calendar
    if options.lag_calendar == "project" and project_cal is not None:
        return project_cal
    return pred.calendar


def _shift(calendar: WorkCalendar, instant: datetime, minutes: int) -> datetime:
    if minutes == 0:
        return instant.replace(second=0, microsecond=0)
    return calendar.add_work(instant, minutes)


def _latest(values: list[datetime]) -> datetime:
    return max(values)


def _earliest(values: list[datetime]) -> datetime:
    return min(values)


def _dates_for(node: _Node, codes: set[str]) -> list[datetime]:
    found: list[datetime] = []
    activity = node.activity
    if activity.cstr_type in codes and activity.cstr_date is not None:
        found.append(activity.cstr_date)
    if activity.cstr_type2 in codes and activity.cstr_date2 is not None:
        found.append(activity.cstr_date2)
    return found


def _has(node: _Node, code: str) -> bool:
    return code in {node.activity.cstr_type, node.activity.cstr_type2}


def _delay_start(node: _Node, start: datetime) -> datetime:
    chosen = start
    for raw in _dates_for(node, _START_ON | _START_AFTER):
        snapped = node.calendar.add_work(raw, 0)
        chosen = max(chosen, snapped)
    return chosen


def _delay_finish(node: _Node) -> datetime:
    assert node.early_start is not None and node.early_finish is not None
    finish = node.early_finish
    for raw in _dates_for(node, _FINISH_ON | _FINISH_AFTER):
        snapped = node.calendar.subtract_work(raw, 0)
        if snapped > finish:
            finish = snapped
            pushed = node.calendar.subtract_work(finish, node.duration)
            node.early_start = max(node.early_start, pushed)
    return finish


def _constraint_late(
    node: _Node,
    lf_bounds: list[datetime],
    ls_bounds: list[datetime],
) -> None:
    for raw in _dates_for(node, _START_ON | _START_BEFORE):
        ls_bounds.append(node.calendar.subtract_work(raw, 0))
    for raw in _dates_for(node, _FINISH_ON | _FINISH_BEFORE):
        lf_bounds.append(node.calendar.subtract_work(raw, 0))


def _project_finish(nodes: dict[str, _Node]) -> datetime | None:
    finishes = [node.early_finish for node in nodes.values() if node.early_finish is not None]
    if not finishes:
        return None
    return max(finishes)
