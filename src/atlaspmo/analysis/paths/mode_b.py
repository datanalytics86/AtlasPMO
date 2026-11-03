"""Critical path from the project CPM, plus the DCMA critical-path test."""

from __future__ import annotations

from dataclasses import replace

import pandas as pd
from pydantic import BaseModel

from atlaspmo import __version__
from atlaspmo.analysis.contract import (
    AnalysisContext,
    Metric,
    ModuleResult,
    Requirement,
    RunMetadata,
    empty_findings,
)
from atlaspmo.calendars.data import parse_clndr_data
from atlaspmo.calendars.worktime import WorkCalendar
from atlaspmo.engine.cpm import CpmResult, schedule_cpm
from atlaspmo.engine.options import EngineOptions
from atlaspmo.model.schedule import Activity, Schedule

_SKIP = {"TT_Mile", "TT_FinMile", "TT_LOE", "TT_WBS"}


class PathsBConfig(BaseModel):
    progress: str = "retained"
    lag_calendar: str = "predecessor"
    float_kind: str = "minimum"
    critical_hours: float = 0.0
    proj_id: str | None = None
    milestone_code: str | None = None


class PathsModeB:
    id = "paths_b"
    name_es = "Ruta crítica (modo B)"
    description_es = "Recalcula la ruta con el motor. Incluye la prueba DCMA 12."
    requires: set[Requirement] = {Requirement.CPM_ENGINE}
    config_model: type[BaseModel] = PathsBConfig

    def run(self, ctx: AnalysisContext, config: BaseModel) -> ModuleResult:
        chosen = config if isinstance(config, PathsBConfig) else PathsBConfig()
        options = EngineOptions(
            chosen.progress,
            chosen.lag_calendar,
            chosen.float_kind,
            chosen.critical_hours,
        )
        if ctx.schedule is None:
            return _empty(["No hay cronograma cargado."], ctx)
        schedule = ctx.schedule.select(chosen.proj_id)
        result = schedule_cpm(schedule, options)
        codes = {item.task_id: item.task_code for item in schedule.activities}
        rows = [
            {
                "task_code": codes.get(item.task_id),
                "early_start": item.early_start,
                "early_finish": item.early_finish,
                "late_start": item.late_start,
                "late_finish": item.late_finish,
                "total_float_hours": item.total_float_hours,
                "free_float_hours": item.free_float_hours,
                "critical": item.critical,
                "driving_codes": _driving_codes(item.driving_pred_ids, codes),
            }
            for item in result.by_id.values()
        ]
        chain = _driving_chain(result, codes, chosen.milestone_code)
        paths, continuity_value, continuity_status, path_notes = _contract_float_paths(
            schedule, result
        )
        critical = sum(1 for item in result.by_id.values() if item.critical)
        status, detail = _cp_test(schedule, options)
        return ModuleResult(
            module_id=self.id,
            metrics={
                "critical_count": Metric(float(critical), options.critical_hours, "info"),
                "cp_test": Metric(None, None, status),
                "continuity": Metric(continuity_value, None, continuity_status),
            },
            findings=empty_findings(),
            tables={
                "cpm": pd.DataFrame(rows),
                "driving_chain": pd.DataFrame(chain),
                "float_paths": paths,
            },
            approximations=list(
                dict.fromkeys(
                    [
                        *schedule.parse_notes,
                        *result.approximations,
                        (
                            "La cadena driving recorre las predecesoras cuyo límite "
                            "fija el inicio temprano. No es un float path de P6."
                        ),
                        (
                            "Estas rutas las calcula el motor con el algoritmo del contrato. "
                            "No son un float path de P6."
                        ),
                        *path_notes,
                        (
                            "CP Test atrasa 8 horas la primera actividad crítica "
                            "ordenada por task_code."
                        ),
                        *detail,
                    ]
                )
            ),
            metadata=RunMetadata(
                app_version=__version__,
                input_sha256=ctx.input_sha256,
                parameters={"progress": options.progress},
            ),
        )


def _driving_codes(pred_ids: tuple[str, ...], codes: dict[str | None, str | None]) -> str:
    names = [codes.get(pred_id) or pred_id for pred_id in pred_ids]
    return ",".join(name for name in names if name)


def _contract_float_paths(
    schedule: Schedule,
    result: CpmResult,
) -> tuple[pd.DataFrame, float | None, str, list[str]]:
    """Number contract float paths. This is not Primavera P6's algorithm.

    Do not present the table as a P6 float path. Eligible activities are
    those in ``result.by_id`` whose ``task_type`` is neither ``TT_LOE`` nor
    ``TT_WBS``. Repeat until every eligible activity has a path:

    1. The seed is the unassigned activity with the smallest
       ``total_float_hours``. A tie goes to the later ``early_finish``,
       then to ascending ``task_code``.
    2. The chain starts at the seed. While the cursor has a driving
       predecessor that is eligible and still unassigned, keep exactly one:
       the greatest ``remain_drtn_hr_cnt`` (0 when it is missing). A tie
       goes to ascending ``task_code``. Prepend that predecessor. The other
       driving predecessors stay free.
    3. Path k, starting at 1, numbers ``float_path_order`` from 1 at the
       start of the chain through the seed at the end.

    Continuity is judged only on path 1. Without ``last_recalc_date`` the
    status is ``no_evaluable``, the note says the data date is missing, and
    continuity is not true. It is true only when the path is not empty, the
    order-1 ``early_start`` is less than or equal to the data date, the last
    ``early_finish`` equals ``project_finish``, and every consecutive pair
    has a relationship from the earlier activity to the next. If any of
    those three is missing, continuity is false and the note contains
    «quiebre».
    """
    activities = {item.task_id: item for item in schedule.activities if item.task_id}
    eligible = {
        task_id
        for task_id, activity in activities.items()
        if task_id in result.by_id and activity.task_type not in {"TT_LOE", "TT_WBS"}
    }
    assigned: set[str] = set()
    rows: list[dict[str, object]] = []
    path_number = 0
    first_chain: list[str] = []
    while eligible - assigned:
        seed = min(
            eligible - assigned,
            key=lambda task_id: _seed_key(result, activities, task_id),
        )
        chain = [seed]
        assigned.add(seed)
        cursor = seed
        while True:
            options = [
                pred_id
                for pred_id in result.by_id[cursor].driving_pred_ids
                if pred_id in eligible and pred_id not in assigned
            ]
            if not options:
                break
            chosen = min(options, key=lambda pred_id: _duration_key(activities, pred_id))
            chain.insert(0, chosen)
            assigned.add(chosen)
            cursor = chosen
        path_number += 1
        if path_number == 1:
            first_chain = chain
        for order, task_id in enumerate(chain, start=1):
            rows.append(
                {
                    "task_code": activities[task_id].task_code,
                    "float_path": path_number,
                    "float_path_order": order,
                }
            )
    frame = pd.DataFrame(rows, columns=["task_code", "float_path", "float_path_order"])
    value, status, notes = _path_continuity(schedule, result, first_chain)
    return frame, value, status, notes


def _seed_key(
    result: CpmResult,
    activities: dict[str, Activity],
    task_id: str,
) -> tuple[float, float, str]:
    item = result.by_id[task_id]
    code = activities[task_id].task_code or ""
    return (item.total_float_hours, -item.early_finish.timestamp(), code)


def _duration_key(activities: dict[str, Activity], task_id: str) -> tuple[float, str]:
    hours = activities[task_id].remain_drtn_hr_cnt
    duration = 0.0 if hours is None else hours
    return (-duration, activities[task_id].task_code or "")


def _path_continuity(
    schedule: Schedule,
    result: CpmResult,
    chain: list[str],
) -> tuple[float | None, str, list[str]]:
    dates = {
        item.last_recalc_date for item in schedule.projects if item.last_recalc_date is not None
    }
    if len(dates) != 1:
        if not dates:
            return None, "no_evaluable", ["Falta la fecha de corte."]
        return None, "no_evaluable", ["Hay más de una fecha de corte."]
    cutoff = next(iter(dates))
    broken = ["La ruta 1 tiene un quiebre desde la fecha de corte hasta el término."]
    if not chain or result.project_finish is None:
        return 0.0, "falsa", broken
    first = result.by_id[chain[0]]
    last = result.by_id[chain[-1]]
    start_ok = first.early_start <= cutoff
    finish_ok = last.early_finish == result.project_finish
    links_ok = all(
        _has_link(schedule, chain[index], chain[index + 1]) for index in range(len(chain) - 1)
    )
    if start_ok and finish_ok and links_ok:
        return 1.0, "verdadera", []
    return 0.0, "falsa", broken


def _has_link(schedule: Schedule, pred_id: str, succ_id: str) -> bool:
    return any(
        link.pred_task_id == pred_id and link.task_id == succ_id for link in schedule.relationships
    )


def _driving_chain(
    result: CpmResult,
    codes: dict[str | None, str | None],
    milestone_code: str | None,
) -> list[dict[str, object]]:
    """Walk driving predecessors back from a milestone or the project finish.

    A predecessor is driving when the CPM bound it imposes equals the
    successor's early start, including the open-milestone rule in the engine.
    This walk is the driving chain. Contract float paths are numbered apart
    and are not a P6 float path.
    """
    starts: list[str] = []
    if milestone_code:
        starts = [
            item.task_id
            for item in result.by_id.values()
            if codes.get(item.task_id) == milestone_code
        ]
    elif result.project_finish is not None:
        starts = [
            item.task_id
            for item in result.by_id.values()
            if item.early_finish == result.project_finish
        ]
    seen: set[str] = set()
    ordered: list[str] = []
    stack = list(starts)
    while stack:
        current = stack.pop()
        if current in seen or current not in result.by_id:
            continue
        seen.add(current)
        ordered.append(current)
        stack.extend(result.by_id[current].driving_pred_ids)
    return [
        {"task_code": codes.get(task_id), "step": index} for index, task_id in enumerate(ordered)
    ]


def _cp_test(schedule: Schedule, options: EngineOptions) -> tuple[str, list[str]]:
    base = schedule_cpm(schedule, options)
    if base.project_finish is None:
        return "no_evaluable", ["CP Test: el motor no tiene término de proyecto."]
    pool = [
        activity
        for activity in schedule.activities
        if activity.task_id in base.by_id
        and base.by_id[activity.task_id or ""].critical
        and activity.task_type not in _SKIP
        and (activity.remain_drtn_hr_cnt or 0) > 0
    ]
    if not pool:
        return "no_evaluable", ["CP Test: no hay actividad crítica con duración."]
    target = sorted(pool, key=lambda item: item.task_code or "")[0]
    clock = _clock(schedule, target)
    if clock is None or target.remain_drtn_hr_cnt is None:
        return "no_evaluable", ["CP Test: la actividad crítica no tiene calendario."]
    delayed = replace(target, remain_drtn_hr_cnt=target.remain_drtn_hr_cnt + 8)
    activities = tuple(
        delayed if item.task_id == delayed.task_id else item for item in schedule.activities
    )
    again = schedule_cpm(replace(schedule, activities=activities), options)
    if again.project_finish is None:
        return "no_evaluable", ["CP Test: el atraso no produjo término."]
    delta = clock.work_between(base.project_finish, again.project_finish)
    if delta == 8 * 60:
        return "cumple", []
    return "no_cumple", [f"CP Test: el término se movió {delta} minutos, no 480."]


def _clock(schedule: Schedule, activity: Activity) -> WorkCalendar | None:
    calendar = schedule.calendar_for(activity.clndr_id)
    if calendar is None or not calendar.clndr_data:
        return None
    return WorkCalendar.from_parsed(parse_clndr_data(calendar.clndr_data))


def _empty(notes: list[str], ctx: AnalysisContext) -> ModuleResult:
    return ModuleResult(
        module_id="paths_b",
        metrics={},
        findings=empty_findings(),
        tables={},
        approximations=notes,
        metadata=RunMetadata(app_version=__version__, input_sha256=ctx.input_sha256),
    )
