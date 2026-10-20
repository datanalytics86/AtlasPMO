"""Pure-Python Monte Carlo on the same CPM. numba is not loaded."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from datetime import datetime

from atlaspmo.analysis.risk.config import RiskConfig
from atlaspmo.analysis.risk.sample import iman_conover, sample_duration
from atlaspmo.calendars.worktime import CalendarLimitError, WorkCalendar
from atlaspmo.engine.cpm import CpmResult, build_clocks, schedule_cpm
from atlaspmo.engine.options import EngineOptions
from atlaspmo.model.schedule import Schedule

_NUMBA = "Monte Carlo en Python puro. numba no se cargó en esta fase."
_RANGES = "Los rangos de duración son configuración del usuario, no columnas del XER."
_EVENTS = "Los eventos de riesgo suman horas al remanente. No son un campo del XER."


@dataclass(frozen=True)
class ActivityRisk:
    task_code: str
    criticality: float
    sigma_hours: float
    ssi: float | None
    cruciality: float | None
    spearman: float | None


@dataclass(frozen=True)
class TornadoRow:
    task_code: str
    delta_hours: float


@dataclass(frozen=True)
class MilestonePercentile:
    task_code: str
    p50: datetime
    p80: datetime
    p90: datetime


@dataclass(frozen=True)
class ConvergenceRow:
    task_code: str
    deterministic_finish: datetime
    p50_finish: datetime


@dataclass(frozen=True)
class RiskOutcome:
    finishes: tuple[datetime, ...]
    activities: tuple[ActivityRisk, ...]
    tornado: tuple[TornadoRow, ...]
    milestones: tuple[MilestonePercentile, ...]
    convergence: tuple[ConvergenceRow, ...]
    approximations: tuple[str, ...]
    iterations: int
    ssi_status: str
    sensitivity_status: str


def run_risk(schedule: Schedule, config: RiskConfig) -> RiskOutcome:
    """Sample durations, reschedule, and compare with the deterministic CPM."""
    notes = [_NUMBA, _RANGES]
    if config.iterations < 1:
        notes.append("Las iteraciones deben ser al menos 1.")
        return _empty(notes)
    options = EngineOptions(config.progress)
    clocks, clock_notes = build_clocks(schedule)
    notes.extend(clock_notes)
    base = schedule_cpm(schedule, options)
    notes.extend(base.approximations)
    draws, ranged = _draws(schedule, config, notes)
    rng = random.Random(config.seed)
    _consume_duration_rng(rng, config, draws)
    draws = _apply_correlation(draws, ranged, config, rng, notes)
    if config.events:
        notes.append(_EVENTS)
    finishes: list[datetime] = []
    durations: dict[str, list[float]] = {}
    critical_hits: dict[str, int] = {}
    finish_by_code: dict[str, list[datetime]] = {}
    seen = 0
    anchor, anchor_note = _anchor(schedule, base, clocks)
    if anchor_note:
        notes.append(anchor_note)
    project_hours: list[float] = []
    for index in range(config.iterations):
        chosen = {code: values[index] for code, values in draws.items()}
        _apply_events(chosen, config, rng, notes)
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
    activities, ssi_status, sensitivity_status = _activity_rows(
        schedule, base, durations, critical_hits, seen, project_hours
    )
    tornado = _tornado(schedule, config, options, clocks, base, notes)
    milestones = _milestones(schedule, finishes, finish_by_code)
    convergence = _convergence(schedule, base, finish_by_code)
    return RiskOutcome(
        finishes=tuple(finishes),
        activities=tuple(activities),
        tornado=tuple(tornado),
        milestones=tuple(milestones),
        convergence=tuple(convergence),
        approximations=tuple(dict.fromkeys(notes)),
        iterations=config.iterations,
        ssi_status=ssi_status,
        sensitivity_status=sensitivity_status,
    )


def _empty(notes: list[str]) -> RiskOutcome:
    return RiskOutcome(
        (),
        (),
        (),
        (),
        (),
        tuple(dict.fromkeys(notes)),
        0,
        "no_evaluable",
        "no_evaluable",
    )


def _draws(
    schedule: Schedule,
    config: RiskConfig,
    notes: list[str],
) -> tuple[dict[str, list[float]], set[str]]:
    current = _current_hours(schedule, notes)
    draws: dict[str, list[float]] = {
        code: [hours] * config.iterations for code, hours in current.items()
    }
    ranged: set[str] = set()
    known = set(current)
    for item in config.ranges:
        if item.task_code not in known:
            notes.append(f"No está la actividad {item.task_code}.")
            continue
        if item.low > item.mode or item.mode > item.high:
            notes.append(f"{item.task_code}: el rango no cumple mínimo ≤ probable ≤ máximo.")
            continue
        if item.low == item.mode == item.high:
            draws[item.task_code] = [item.mode] * config.iterations
            continue
        ranged.add(item.task_code)
        draws[item.task_code] = [item.mode] * config.iterations
    return draws, ranged


def _consume_duration_rng(
    rng: random.Random,
    config: RiskConfig,
    draws: dict[str, list[float]],
) -> None:
    for item in config.ranges:
        if item.task_code not in draws:
            continue
        if item.low == item.mode == item.high:
            continue
        if item.low > item.mode or item.mode > item.high:
            continue
        draws[item.task_code] = [
            sample_duration(rng, item.low, item.mode, item.high, item.distribution)
            for _ in range(config.iterations)
        ]


def _apply_correlation(
    draws: dict[str, list[float]],
    ranged: set[str],
    config: RiskConfig,
    rng: random.Random,
    notes: list[str],
) -> dict[str, list[float]]:
    if not config.correlations:
        return draws
    codes = sorted(ranged)
    if len(codes) < 2:
        notes.append("Iman-Conover no se aplicó: ningún rango tiene ancho.")
        return draws
    matrix = _matrix(codes, config)
    columns = [list(draws[code]) for code in codes]
    mixed = iman_conover(columns, matrix, rng)
    if mixed is None:
        notes.append("Iman-Conover no se aplicó: la matriz no admite Cholesky.")
        return draws
    notes.append(
        "Iman-Conover reordena las muestras. Se suma 1e-8 a la diagonal para aceptar correlación 1."
    )
    updated = dict(draws)
    for code, column in zip(codes, mixed, strict=True):
        updated[code] = column
    return updated


def _matrix(codes: list[str], config: RiskConfig) -> list[list[float]]:
    size = len(codes)
    index = {code: position for position, code in enumerate(codes)}
    matrix = [[1.0 if row == col else 0.0 for col in range(size)] for row in range(size)]
    for pair in config.correlations:
        left = index.get(pair.left)
        right = index.get(pair.right)
        if left is None or right is None or left == right:
            continue
        matrix[left][right] = pair.coefficient
        matrix[right][left] = pair.coefficient
    return matrix


def _apply_events(
    chosen: dict[str, float],
    config: RiskConfig,
    rng: random.Random,
    notes: list[str],
) -> None:
    for event in config.events:
        if event.probability < 0 or event.probability > 1:
            notes.append(f"{event.name}: la probabilidad debe estar entre 0 y 1.")
            continue
        if rng.random() >= event.probability:
            continue
        for code in event.task_codes:
            if code not in chosen:
                notes.append(f"{event.name}: no está la actividad {code}.")
                continue
            chosen[code] = chosen[code] + event.impact_hours


def _with_hours(schedule: Schedule, hours: dict[str, float]) -> Schedule:
    activities = []
    for activity in schedule.activities:
        value = hours.get(activity.task_code or "")
        if activity.task_code is None or value is None:
            activities.append(activity)
            continue
        activities.append(replace(activity, remain_drtn_hr_cnt=value))
    return replace(schedule, activities=tuple(activities))


def _current_hours(schedule: Schedule, notes: list[str]) -> dict[str, float]:
    found: dict[str, float] = {}
    for activity in schedule.activities:
        if activity.task_code is None or activity.remain_drtn_hr_cnt is None:
            continue
        if activity.task_code in found:
            notes.append(f"{activity.task_code}: hay más de una actividad con ese código.")
        found[activity.task_code] = activity.remain_drtn_hr_cnt
    return found


def _code(schedule: Schedule, task_id: str) -> str | None:
    for activity in schedule.activities:
        if activity.task_id == task_id:
            return activity.task_code
    return None


def _anchor(
    schedule: Schedule,
    base: CpmResult,
    clocks: dict[str, WorkCalendar],
) -> tuple[WorkCalendar | None, str | None]:
    ranked = sorted(
        (
            activity
            for activity in schedule.activities
            if activity.task_id in base.by_id and activity.task_code is not None
        ),
        key=lambda activity: activity.task_code or "",
    )
    for activity in ranked:
        clock = clocks.get(activity.clndr_id or "")
        if clock is not None:
            return clock, f"La desviación del término usa el calendario de {activity.task_code}."
    return None, None


def _activity_rows(
    schedule: Schedule,
    base: CpmResult,
    durations: dict[str, list[float]],
    critical_hits: dict[str, int],
    seen: int,
    project_hours: list[float],
) -> tuple[list[ActivityRisk], str, str]:
    project_sigma = _stdev(project_hours)
    ssi_status = "no_evaluable" if project_sigma == 0 else "info"
    sensitivity_status = "no_evaluable" if project_sigma == 0 else "info"
    rows: list[ActivityRisk] = []
    codes: list[str] = []
    for activity in schedule.activities:
        if activity.task_id not in base.by_id or not activity.task_code:
            continue
        if activity.task_code not in codes:
            codes.append(activity.task_code)
    for code in codes:
        samples = durations.get(code, [])
        sigma = _stdev(samples)
        criticality = critical_hits.get(code, 0) / seen if seen else 0.0
        ssi: float | None = None
        cruciality: float | None = None
        spearman: float | None = None
        if project_sigma > 0:
            ssi = criticality * sigma / project_sigma
            paired = _paired(samples, project_hours)
            if sigma > 0 and paired is not None:
                cruciality = _pearson(paired[0], paired[1])
                spearman = _pearson(_ranks(paired[0]), _ranks(paired[1]))
        rows.append(ActivityRisk(code, criticality, sigma, ssi, cruciality, spearman))
    return rows, ssi_status, sensitivity_status


def _paired(
    samples: list[float],
    project_hours: list[float],
) -> tuple[list[float], list[float]] | None:
    size = min(len(samples), len(project_hours))
    if size < 2:
        return None
    return samples[:size], project_hours[:size]


def _tornado(
    schedule: Schedule,
    config: RiskConfig,
    options: EngineOptions,
    clocks: dict[str, WorkCalendar],
    base: CpmResult,
    notes: list[str],
) -> list[TornadoRow]:
    if base.project_finish is None:
        notes.append("Sin término determinístico: el tornado no se calcula.")
        return []
    rows: list[TornadoRow] = []
    for activity in schedule.activities:
        if activity.task_id not in base.by_id or activity.task_code is None:
            continue
        if activity.remain_drtn_hr_cnt is None:
            continue
        clock = clocks.get(activity.clndr_id or "")
        if clock is None:
            notes.append(f"{activity.task_code}: sin calendario, el tornado no se calcula.")
            continue
        delayed = activity.remain_drtn_hr_cnt + config.tornado_hours
        result = schedule_cpm(_with_hours(schedule, {activity.task_code: delayed}), options)
        if result.project_finish is None:
            notes.append(f"{activity.task_code}: el atraso no tiene término.")
            continue
        try:
            minutes = clock.work_between(base.project_finish, result.project_finish)
        except CalendarLimitError:
            notes.append(f"{activity.task_code}: el calendario no alcanza para el tornado.")
            continue
        rows.append(TornadoRow(activity.task_code, minutes / 60))
    return rows


def _milestones(
    schedule: Schedule,
    finishes: list[datetime],
    finish_by_code: dict[str, list[datetime]],
) -> list[MilestonePercentile]:
    rows: list[MilestonePercentile] = []
    if finishes:
        rows.append(
            MilestonePercentile(
                "proyecto",
                _percentile(finishes, 0.50),
                _percentile(finishes, 0.80),
                _percentile(finishes, 0.90),
            )
        )
    milestone_codes = {
        activity.task_code
        for activity in schedule.activities
        if activity.task_type in {"TT_Mile", "TT_FinMile"} and activity.task_code
    }
    for code in sorted(milestone_codes):
        values = finish_by_code.get(code, [])
        if not values:
            continue
        rows.append(
            MilestonePercentile(
                code,
                _percentile(values, 0.50),
                _percentile(values, 0.80),
                _percentile(values, 0.90),
            )
        )
    return rows


def _convergence(
    schedule: Schedule,
    base: CpmResult,
    finish_by_code: dict[str, list[datetime]],
) -> list[ConvergenceRow]:
    counts: dict[str, int] = {}
    for link in schedule.relationships:
        if link.task_id:
            counts[link.task_id] = counts.get(link.task_id, 0) + 1
    rows: list[ConvergenceRow] = []
    for activity in schedule.activities:
        if activity.task_id is None or counts.get(activity.task_id, 0) < 2:
            continue
        if activity.task_code is None or activity.task_id not in base.by_id:
            continue
        values = finish_by_code.get(activity.task_code, [])
        if not values:
            continue
        rows.append(
            ConvergenceRow(
                activity.task_code,
                base.by_id[activity.task_id].early_finish,
                _percentile(values, 0.50),
            )
        )
    return rows


def _percentile(values: list[datetime], fraction: float) -> datetime:
    ordered = sorted(values)
    index = math.ceil(fraction * len(ordered)) - 1
    return ordered[min(max(index, 0), len(ordered) - 1)]


def _stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((item - mean) ** 2 for item in values) / (len(values) - 1)
    return math.sqrt(variance)


def _pearson(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    mean_left = sum(left) / len(left)
    mean_right = sum(right) / len(right)
    numerator = sum((a - mean_left) * (b - mean_right) for a, b in zip(left, right, strict=True))
    left_ss = sum((item - mean_left) ** 2 for item in left)
    right_ss = sum((item - mean_right) ** 2 for item in right)
    if left_ss == 0 or right_ss == 0:
        return None
    return numerator / math.sqrt(left_ss * right_ss)


def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    cursor = 0
    while cursor < len(order):
        end = cursor
        while end + 1 < len(order) and values[order[end + 1]] == values[order[cursor]]:
            end += 1
        average = (cursor + 1 + end + 1) / 2
        for position in range(cursor, end + 1):
            ranks[order[position]] = average
        cursor = end + 1
    return ranks
