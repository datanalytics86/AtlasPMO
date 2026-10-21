"""Critical path from stored P6 dates and float. No CPM recalculation."""

from __future__ import annotations

from collections.abc import Callable

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
from atlaspmo.analysis.quality.profiles import Profile, load_profile
from atlaspmo.model.schedule import Activity, Schedule


def _band_non_positive(value: float) -> bool:
    return value <= 0


def _band_to_10(value: float) -> bool:
    return 0 < value <= 10


def _band_to_20(value: float) -> bool:
    return 10 < value <= 20


def _band_to_44(value: float) -> bool:
    return 20 < value <= 44


def _band_above_44(value: float) -> bool:
    return value > 44


_BANDS: tuple[tuple[str, Callable[[float], bool]], ...] = (
    ("<=0", _band_non_positive),
    ("0-10", _band_to_10),
    ("10-20", _band_to_20),
    ("20-44", _band_to_44),
    (">44", _band_above_44),
)


class PathsConfig(BaseModel):
    profile: str = "dcma_estricto"
    proj_id: str | None = None
    hours_per_day: float | None = None


class PathsModeA:
    id = "paths"
    name_es = "Ruta crítica (modo A)"
    description_es = "Usa la holgura y las fechas guardadas. No reprograma."
    requires: set[Requirement] = set()
    config_model: type[BaseModel] = PathsConfig

    def run(self, ctx: AnalysisContext, config: BaseModel) -> ModuleResult:
        chosen = config if isinstance(config, PathsConfig) else PathsConfig()
        profile, note = load_profile(chosen.profile, chosen.hours_per_day)
        approximations = [note] if note else []
        if chosen.hours_per_day is not None:
            approximations.append("hours_per_day del llamado reemplaza el del perfil.")
        approximations.append(
            "Los vínculos driving no se marcan en modo A: "
            "no hay un campo citado de holgura libre del vínculo."
        )
        if ctx.schedule is None:
            approximations.append("No hay cronograma cargado.")
            return _empty(approximations, ctx)
        schedule = ctx.schedule.select(chosen.proj_id)
        approximations.extend(schedule.parse_notes)
        rows, counts, critical = _classify(schedule, profile, approximations)
        metrics = {
            "critical_count": Metric(float(critical), profile.critical_float_days, "info"),
            **{
                f"band_{name}": Metric(float(count), None, "info") for name, count in counts.items()
            },
        }
        return ModuleResult(
            module_id=self.id,
            metrics=metrics,
            findings=empty_findings(),
            tables={"bands": rows},
            approximations=list(dict.fromkeys(approximations)),
            metadata=RunMetadata(
                app_version=__version__,
                input_sha256=ctx.input_sha256,
                profile=profile.id,
            ),
        )


def _classify(
    schedule: Schedule,
    profile: object,
    approximations: list[str],
) -> tuple[pd.DataFrame, dict[str, int], int]:
    if not isinstance(profile, Profile):
        raise TypeError("profile")
    counts = {name: 0 for name, _rule in _BANDS}
    records: list[dict[str, object]] = []
    critical = 0
    skipped = False
    path_column = None
    if "TASK.float_path" not in schedule.absent_columns and "TASK" not in schedule.absent_tables:
        path_column = "float_path"
    elif "TASK.int_path" not in schedule.absent_columns and "TASK" not in schedule.absent_tables:
        path_column = "int_path"
        approximations.append(
            "La ruta guardada se leyó de TASK.int_path. "
            "PyP6Xer usa ese nombre; el megaprompt dice float_path."
        )
    else:
        approximations.append("No hay columna de ruta guardada (float_path ni int_path).")
    for activity in schedule.activities:
        days = _float_days(activity, schedule, profile.hours_per_day)
        if days is None:
            skipped = True
            continue
        band = next(name for name, rule in _BANDS if rule(days))
        counts[band] += 1
        is_critical = days <= profile.critical_float_days
        if is_critical:
            critical += 1
        records.append(
            {
                "task_code": activity.task_code,
                "task_name": activity.task_name,
                "float_days": days,
                "band": band,
                "critical": is_critical,
                "path": _stored_path(activity, path_column),
            }
        )
    if skipped:
        approximations.append(
            "Hay actividades sin holgura total o sin horas por día. No entran a las bandas."
        )
    frame = pd.DataFrame(records)
    return frame, counts, critical


def _float_days(
    activity: Activity,
    schedule: Schedule,
    hours_per_day: float | None,
) -> float | None:
    if activity.total_float_hr_cnt is None:
        return None
    if hours_per_day:
        return activity.total_float_hr_cnt / hours_per_day
    calendar = schedule.calendar_for(activity.clndr_id)
    if calendar is None or not calendar.day_hr_cnt:
        return None
    return activity.total_float_hr_cnt / calendar.day_hr_cnt


def _stored_path(activity: Activity, column: str | None) -> str | None:
    if column == "float_path":
        return activity.float_path
    if column == "int_path":
        return activity.int_path
    return None


def _empty(approximations: list[str], ctx: AnalysisContext) -> ModuleResult:
    return ModuleResult(
        module_id="paths",
        metrics={},
        findings=empty_findings(),
        tables={},
        approximations=approximations,
        metadata=RunMetadata(app_version=__version__, input_sha256=ctx.input_sha256),
    )
