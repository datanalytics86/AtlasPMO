"""Iteration loop on the compiled CPM, and a tornado that walks only the successor cone."""

from __future__ import annotations

import random
from datetime import datetime
from typing import TYPE_CHECKING

import numpy as np

from atlaspmo.analysis.risk.config import RiskConfig
from atlaspmo.calendars.worktime import CalendarLimitError, WorkCalendar, elapsed_calendar
from atlaspmo.engine.cpm import (
    CpmResult,
    _clocks,
    _data_date,
    _forward,
    _nodes,
    _project_calendar,
    _project_finish,
    _topo,
    _wire,
    schedule_cpm,
)
from atlaspmo.engine.fast import LAST, Compiled, cached_compiled
from atlaspmo.engine.options import EngineOptions
from atlaspmo.model.schedule import Schedule
from atlaspmo.numeric.batch import run_batch

if TYPE_CHECKING:
    from atlaspmo.analysis.risk.montecarlo import TornadoRow

_Trace = dict[str, object]
_Clocks = dict[str, WorkCalendar]
_Iterations = tuple[
    list[datetime],
    dict[str, list[float]],
    dict[str, int],
    int,
    dict[str, list[datetime]],
    list[float],
]

_NUMBA = "Monte Carlo corre en numba sobre los arrays del motor rápido."
_FALLBACK = "El lote de Monte Carlo no corrió en numba: el calendario no entra en el motor rápido."
_CONE = "El tornado solo recalcula la actividad atrasada y su cono de sucesoras."
_EPOCH = np.datetime64("0001-01-01T00:00")
_MILESTONE = {"TT_Mile", "TT_FinMile"}


def reset_trace(trace: _Trace) -> None:
    trace["passes"] = 0
    trace["full_cpm"] = 0
    trace["tornado_visited"] = 0
    trace["cones"] = {}
    trace["columns"] = {}
    trace["critical"] = []
    trace["rng_next"] = None


def use_fast(schedule: Schedule, options: EngineOptions) -> Compiled | None:
    compiled = cached_compiled(schedule, options)
    if compiled is None or compiled.empty is not None or compiled.tables is None:
        return None
    if LAST.get("path") != "fast":
        return None
    return compiled


def run_iterations(
    schedule: Schedule,
    config: RiskConfig,
    options: EngineOptions,
    base: CpmResult,
    draws: dict[str, list[float]],
    rng: random.Random,
    notes: list[str],
    clocks: _Clocks,
    trace: _Trace,
    anchor: WorkCalendar | None,
) -> _Iterations:
    compiled = use_fast(schedule, options)
    if compiled is None:
        notes.append(_FALLBACK)
        return _reference_iterations(
            schedule, config, options, base, draws, rng, notes, clocks, trace, anchor
        )
    notes.append(_NUMBA)
    return _fast_iterations(
        schedule, config, options, base, compiled, draws, rng, notes, trace, anchor
    )


def tornado_rows(
    schedule: Schedule,
    config: RiskConfig,
    base: CpmResult,
    clocks: _Clocks,
    notes: list[str],
    trace: _Trace,
) -> list[TornadoRow]:
    from atlaspmo.analysis.risk.montecarlo import TornadoRow  # noqa: PLC0415

    if config.tornado_hours <= 0:
        return []
    if base.project_finish is None:
        notes.append("Sin término determinístico: el tornado no se calcula.")
        return []
    notes.append(_CONE)
    scratch: list[str] = []
    data_date = _data_date(schedule, scratch)
    if data_date is None:
        return []
    built, built_notes = _clocks(schedule)
    del built_notes
    nodes, _skipped = _nodes(schedule, built, scratch)
    _wire(schedule, nodes, scratch)
    order = _topo(nodes)
    if len(order) < len(nodes) or not order:
        return []
    chosen = EngineOptions(config.progress)
    project_cal = _project_calendar(schedule, built)
    elapsed = elapsed_calendar()
    _forward(nodes, order, data_date, chosen, project_cal, elapsed, scratch)
    saved = {
        task_id: (
            node.duration,
            node.early_start,
            node.early_finish,
            node.remaining_start,
            list(node.driving_preds),
            node.finished,
        )
        for task_id, node in nodes.items()
    }
    successors = {
        task_id: [link.task_id for link in node.succs if link.task_id in nodes]
        for task_id, node in nodes.items()
    }
    extra = int(round(config.tornado_hours * 60))
    cones: dict[str, frozenset[str]] = {}
    rows = []
    for activity in schedule.activities:
        if activity.task_id not in base.by_id or not activity.task_code:
            continue
        if activity.remain_drtn_hr_cnt is None:
            continue
        clock = clocks.get(activity.clndr_id or "")
        if clock is None:
            notes.append(f"{activity.task_code}: sin calendario, el tornado no se calcula.")
            continue
        if activity.task_id not in nodes:
            continue
        cone = _cone(activity.task_id, successors)
        ordered = [task_id for task_id in order if task_id in cone]
        cone_codes: list[str] = []
        for task_id in ordered:
            code = nodes[task_id].activity.task_code
            if code:
                cone_codes.append(code)
        cones[activity.task_code] = frozenset(cone_codes)
        origin = nodes[activity.task_id]
        origin.duration = saved[activity.task_id][0] + extra
        _forward(nodes, ordered, data_date, chosen, project_cal, elapsed, scratch)
        finish = _project_finish(nodes)
        for task_id in ordered:
            duration, early_s, early_f, remaining, driving, done = saved[task_id]
            item = nodes[task_id]
            item.duration = duration
            item.early_start = early_s
            item.early_finish = early_f
            item.remaining_start = remaining
            item.driving_preds = list(driving)
            item.finished = done
        if finish is None:
            notes.append(f"{activity.task_code}: el atraso no tiene término.")
            continue
        try:
            minutes = clock.work_between(base.project_finish, finish)
        except CalendarLimitError:
            notes.append(f"{activity.task_code}: el calendario no alcanza para el tornado.")
            continue
        rows.append(TornadoRow(activity.task_code, minutes / 60))
    trace["cones"] = cones
    trace["tornado_visited"] = sum(len(codes) for codes in cones.values())
    return rows


def _cone(origin: str, successors: dict[str, list[str]]) -> set[str]:
    seen = {origin}
    pending = [origin]
    while pending:
        current = pending.pop()
        for nxt in successors.get(current, []):
            if nxt not in seen:
                seen.add(nxt)
                pending.append(nxt)
    return seen


def _fast_iterations(
    schedule: Schedule,
    config: RiskConfig,
    options: EngineOptions,
    base: CpmResult,
    compiled: Compiled,
    draws: dict[str, list[float]],
    rng: random.Random,
    notes: list[str],
    trace: _Trace,
    anchor: WorkCalendar | None,
) -> _Iterations:
    del options
    columns = _columns(compiled, draws, config, rng, notes, trace)
    varied_index, row_minutes = _minutes(compiled, columns, config.iterations)
    watch, watched_codes = _watch(schedule, compiled)
    finishes_m, total, flags, watched = run_batch(compiled, varied_index, row_minutes, watch)
    trace["passes"] = int(config.iterations)
    finish_dates = _as_datetimes(finishes_m)
    finish_by_code = _watched_dates(watched, watched_codes)
    critical_hits = _hits(compiled, total)
    if len(compiled.activities) <= 256:
        trace["critical"] = _flag_rows(compiled, flags)
    durations = {code: values for code, values in columns.items() if _varies(values)}
    project_hours = _project_hours(base, anchor, finish_dates, notes)
    kept = finish_dates
    if anchor is None or base.project_finish is None:
        kept = []
        project_hours = []
    return kept, durations, critical_hits, config.iterations, finish_by_code, project_hours


def _reference_iterations(
    schedule: Schedule,
    config: RiskConfig,
    options: EngineOptions,
    base: CpmResult,
    draws: dict[str, list[float]],
    rng: random.Random,
    notes: list[str],
    clocks: _Clocks,
    trace: _Trace,
    anchor: WorkCalendar | None,
) -> _Iterations:
    from atlaspmo.analysis.risk.montecarlo import (  # noqa: PLC0415
        _apply_events,
        _code,
        _with_hours,
    )

    finishes: list[datetime] = []
    durations: dict[str, list[float]] = {}
    critical_hits: dict[str, int] = {}
    finish_by_code: dict[str, list[datetime]] = {}
    project_hours: list[float] = []
    seen = 0
    for index in range(config.iterations):
        chosen = {code: values[index] for code, values in draws.items()}
        _apply_events(chosen, config, rng, notes)
        seen_cpm = trace["full_cpm"]
        trace["full_cpm"] = (seen_cpm if isinstance(seen_cpm, int) else 0) + 1
        result = schedule_cpm(_with_hours(schedule, chosen), options)
        seen += 1
        for task_id, item in result.by_id.items():
            code = _code(schedule, task_id)
            if code is None:
                continue
            finish_by_code.setdefault(code, []).append(item.early_finish)
            if item.critical:
                critical_hits[code] = critical_hits.get(code, 0) + 1
        if result.project_finish is None or anchor is None or base.project_finish is None:
            continue
        try:
            delta = anchor.work_between(base.project_finish, result.project_finish) / 60
        except CalendarLimitError:
            notes.append("El calendario no alcanza para medir el término.")
            continue
        finishes.append(result.project_finish)
        project_hours.append(delta)
        for code, hours in chosen.items():
            durations.setdefault(code, []).append(hours)
    if config.events:
        trace["rng_next"] = rng.random()
    del clocks, seen
    return finishes, durations, critical_hits, config.iterations, finish_by_code, project_hours


def _columns(
    compiled: Compiled,
    draws: dict[str, list[float]],
    config: RiskConfig,
    rng: random.Random,
    notes: list[str],
    trace: _Trace,
) -> dict[str, list[float]]:
    from atlaspmo.analysis.risk.montecarlo import _apply_events  # noqa: PLC0415

    needed: list[str] = []
    seen: set[str] = set()
    for item in config.ranges:
        if item.task_code in draws and item.task_code not in seen:
            needed.append(item.task_code)
            seen.add(item.task_code)
    for event in config.events:
        for code in event.task_codes:
            if code not in seen:
                needed.append(code)
                seen.add(code)
    columns = {code: list(draws[code]) for code in needed if code in draws}
    if config.events:
        for index in range(config.iterations):
            chosen = {code: columns[code][index] for code in columns}
            _apply_events(chosen, config, rng, notes)
            for code, values in columns.items():
                values[index] = chosen[code]
        trace["rng_next"] = rng.random()
    trace["columns"] = columns
    return columns


def _minutes(
    compiled: Compiled,
    columns: dict[str, list[float]],
    iterations: int,
) -> tuple[np.ndarray, np.ndarray]:
    index_of: dict[str, int] = {}
    milestone: set[str] = set()
    for index, activity in enumerate(compiled.activities):
        code = activity.task_code
        if not code or code in index_of:
            continue
        index_of[code] = index
        if activity.task_type in _MILESTONE:
            milestone.add(code)
    indices: list[int] = []
    matrix: list[list[int]] = []
    for code, values in columns.items():
        if code not in index_of or code in milestone:
            continue
        base = int(compiled.duration[index_of[code]])
        minutes = [int(round(value * 60)) for value in values]
        if all(item == base for item in minutes):
            continue
        indices.append(index_of[code])
        matrix.append(minutes)
    if not indices:
        return np.zeros(0, dtype=np.int64), np.zeros((iterations, 0), dtype=np.int64)
    return (
        np.asarray(indices, dtype=np.int64),
        np.asarray(matrix, dtype=np.int64).T,
    )


def _watch(schedule: Schedule, compiled: Compiled) -> tuple[np.ndarray, list[str]]:
    needed: set[str] = set()
    for activity in schedule.activities:
        if activity.task_type in _MILESTONE and activity.task_code:
            needed.add(activity.task_code)
    counts: dict[str, int] = {}
    for link in schedule.relationships:
        if link.task_id:
            counts[link.task_id] = counts.get(link.task_id, 0) + 1
    codes = {activity.task_id: activity.task_code for activity in schedule.activities}
    for task_id, count in counts.items():
        code = codes.get(task_id)
        if count >= 2 and code:
            needed.add(code)
    index_of: dict[str, int] = {}
    for index, activity in enumerate(compiled.activities):
        if activity.task_code and activity.task_code not in index_of:
            index_of[activity.task_code] = index
    chosen = [code for code in sorted(needed) if code in index_of]
    if not chosen:
        return np.zeros(0, dtype=np.int64), []
    return np.asarray([index_of[code] for code in chosen], dtype=np.int64), chosen


def _as_datetimes(minutes: np.ndarray) -> list[datetime]:
    if minutes.size == 0:
        return []
    values = _EPOCH + minutes.astype(np.int64).astype("timedelta64[m]")
    return list(values.tolist())


def _watched_dates(watched: np.ndarray, codes: list[str]) -> dict[str, list[datetime]]:
    found: dict[str, list[datetime]] = {}
    for column, code in enumerate(codes):
        found[code] = _as_datetimes(watched[:, column])
    return found


def _hits(compiled: Compiled, total: np.ndarray) -> dict[str, int]:
    hits: dict[str, int] = {}
    for index, activity in enumerate(compiled.activities):
        if activity.task_code:
            hits[activity.task_code] = int(total[index])
    return hits


def _flag_rows(compiled: Compiled, flags: np.ndarray) -> list[dict[str, bool]]:
    rows: list[dict[str, bool]] = []
    count = int(flags.shape[0])
    for index in range(count):
        row: dict[str, bool] = {}
        for activity_index, activity in enumerate(compiled.activities):
            if activity.task_code:
                row[activity.task_code] = bool(flags[index, activity_index])
        rows.append(row)
    return rows


def _varies(values: list[float]) -> bool:
    if len(values) < 2:
        return False
    first = values[0]
    return any(item != first for item in values)


def _project_hours(
    base: CpmResult,
    anchor: WorkCalendar | None,
    finishes: list[datetime],
    notes: list[str],
) -> list[float]:
    if anchor is None or base.project_finish is None:
        return []
    hours: list[float] = []
    for finish in finishes:
        if finish == base.project_finish:
            hours.append(0.0)
            continue
        try:
            hours.append(anchor.work_between(base.project_finish, finish) / 60)
        except CalendarLimitError:
            notes.append("El calendario no alcanza para medir el término.")
    return hours
