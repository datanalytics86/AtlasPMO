"""Compare recalculated dates with the dates stored on the activity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from atlaspmo.engine.cpm import schedule_cpm
from atlaspmo.engine.options import EngineOptions
from atlaspmo.model.schedule import Activity, Schedule


@dataclass(frozen=True)
class ConformanceReport:
    compared: int
    matched: int
    unexplained: tuple[str, ...]

    @property
    def ratio(self) -> float | None:
        if self.compared == 0:
            return None
        return self.matched / self.compared


def conformance(schedule: Schedule, options: EngineOptions | None = None) -> ConformanceReport:
    """Score stored ES/EF/LS/LF/TF/FF. A missing stored value is not a failure."""
    result = schedule_cpm(schedule, options)
    matched = 0
    compared = 0
    unexplained: list[str] = []
    for activity in schedule.activities:
        if activity.task_id is None:
            continue
        got = result.by_id.get(activity.task_id)
        if got is None:
            if _any_stored(activity):
                compared += 1
                code = activity.task_code or activity.task_id
                unexplained.append(f"{code}: no la calculó el motor.")
            continue
        pairs = (
            ("early_start", activity.early_start_date, got.early_start),
            ("early_finish", activity.early_end_date, got.early_finish),
            ("late_start", activity.late_start_date, got.late_start),
            ("late_finish", activity.late_end_date, got.late_finish),
        )
        for name, stored, actual in pairs:
            if stored is None:
                continue
            compared += 1
            if _close(stored, actual):
                matched += 1
            else:
                unexplained.append(f"{activity.task_code} {name}")
        if activity.total_float_hr_cnt is not None:
            compared += 1
            if abs(activity.total_float_hr_cnt - got.total_float_hours) <= 1 / 60:
                matched += 1
            else:
                unexplained.append(f"{activity.task_code} total_float")
        if activity.free_float_hr_cnt is not None:
            compared += 1
            if abs(activity.free_float_hr_cnt - got.free_float_hours) <= 1 / 60:
                matched += 1
            else:
                unexplained.append(f"{activity.task_code} free_float")
    return ConformanceReport(compared, matched, tuple(unexplained))


def _any_stored(activity: Activity) -> bool:
    return any(
        value is not None
        for value in (
            activity.early_start_date,
            activity.early_end_date,
            activity.late_start_date,
            activity.late_end_date,
            activity.total_float_hr_cnt,
            activity.free_float_hr_cnt,
        )
    )


def _close(stored: datetime, actual: datetime) -> bool:
    return abs((stored - actual).total_seconds()) <= 60
