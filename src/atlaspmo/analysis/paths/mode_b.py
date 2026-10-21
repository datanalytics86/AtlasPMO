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
        critical = sum(1 for item in result.by_id.values() if item.critical)
        status, detail = _cp_test(schedule, options)
        return ModuleResult(
            module_id=self.id,
            metrics={
                "critical_count": Metric(float(critical), options.critical_hours, "info"),
                "cp_test": Metric(None, None, status),
            },
            findings=empty_findings(),
            tables={"cpm": pd.DataFrame(rows), "driving_chain": pd.DataFrame(chain)},
            approximations=list(
                dict.fromkeys(
                    [
                        *schedule.parse_notes,
                        *result.approximations,
                        (
                            "La cadena driving recorre las predecesoras cuyo límite "
                            "fija el inicio temprano. No es un float path de P6."
                        ),
                        "Multiple float paths no se calculan.",
                        "La continuidad desde la fecha de corte hasta el término no se verifica.",
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


def _driving_chain(
    result: CpmResult,
    codes: dict[str | None, str | None],
    milestone_code: str | None,
) -> list[dict[str, object]]:
    """Walk driving predecessors back from a milestone or the project finish.

    A predecessor is driving when the CPM bound it imposes equals the
    successor's early start, including the open-milestone rule in the engine.
    The walk is not multiple float paths and it does not check continuity
    from the data date.
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
