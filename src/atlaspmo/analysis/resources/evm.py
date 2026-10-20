"""EVM and earned schedule from loaded cost and duration fields.

Percent-complete codes CP_Phys, CP_Drtn and CP_Units are names seen in public
XER files. They are not confirmed on an export from Nicolás. CP_Units stays
no_evaluable: this build does not load an actual quantity.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from atlaspmo.calendars.worktime import CalendarLimitError, WorkCalendar
from atlaspmo.engine.cpm import build_clocks
from atlaspmo.model.schedule import Activity, Assignment, Schedule

_CODES = (
    "CP_Phys, CP_Drtn y CP_Units son códigos vistos en XER públicos, "
    "sin confirmar en un export de Nicolás."
)
_LINEAR = "PV lineal en tiempo laboral; no hay curva de recurso."
_LIMIT = "límite de recurso no evaluable: no hay un campo citado de tope."
_ES = "Earned Schedule asume PV lineal: ES = (EV/BAC) × PD, SPI(t) = ES/AT, IEAC(t) = PD/SPI(t)."
_PHYS = "CP_Phys mayor que 1 se lee como porcentaje de 0 a 100."
_UNITS = "CP_Units queda no evaluable: no hay un campo de cantidad real cargado."
_CLOCK = "Sin calendario laboral: el PV usa tiempo de reloj."
_CURVE = "La tabla scurve tiene un solo punto, en la fecha de corte."


@dataclass(frozen=True)
class EvmOutcome:
    pv: float | None
    ev: float | None
    ac: float | None
    spi: float | None
    cpi: float | None
    es_hours: float | None
    at_hours: float | None
    spi_t: float | None
    ieac_t: float | None
    activities: tuple[dict[str, object], ...]
    wbs: tuple[dict[str, object], ...]
    resources: tuple[dict[str, object], ...]
    scurve: tuple[dict[str, object], ...]
    approximations: tuple[str, ...]


def earned_value(schedule: Schedule) -> EvmOutcome:
    """PV, EV and AC at the single data date, plus linear earned schedule."""
    notes = [_CODES, _LINEAR, _LIMIT, _ES, _CURVE, *schedule.parse_notes]
    clocks, clock_notes = build_clocks(schedule)
    notes.extend(clock_notes)
    data_date, date_note = _data_date(schedule)
    if date_note:
        notes.append(date_note)
    rows = [
        _activity_row(schedule, activity, clocks, data_date, notes)
        for activity in schedule.activities
    ]
    pv = _total(row["pv"] for row in rows)
    ev = _total(row["ev"] for row in rows)
    ac = _total(row["ac"] for row in rows)
    bac = _total(row["bac"] for row in rows)
    spi = _ratio(ev, pv)
    cpi = _ratio(ev, ac)
    es_hours, at_hours, spi_t, ieac_t = _earned_schedule(
        schedule, rows, clocks, data_date, ev, bac, notes
    )
    return EvmOutcome(
        pv=pv,
        ev=ev,
        ac=ac,
        spi=spi,
        cpi=cpi,
        es_hours=es_hours,
        at_hours=at_hours,
        spi_t=spi_t,
        ieac_t=ieac_t,
        activities=tuple(rows),
        wbs=tuple(_wbs(rows)),
        resources=tuple(_resources(schedule)),
        scurve=({"point": "corte", "pv": pv, "ev": ev, "ac": ac},),
        approximations=tuple(dict.fromkeys(notes)),
    )


def _activity_row(
    schedule: Schedule,
    activity: Activity,
    clocks: dict[str, WorkCalendar],
    data_date: datetime | None,
    notes: list[str],
) -> dict[str, object]:
    owned = [item for item in schedule.assignments if item.task_id == activity.task_id]
    bac = _sum_attr(owned, "target_cost")
    ac = _sum_attr(owned, "act_reg_cost")
    pct = _percent(activity, notes)
    ev = None if bac is None or pct is None else bac * pct
    clock = clocks.get(activity.clndr_id or "")
    pv = None
    if bac is not None and data_date is not None:
        pv = _pv(bac, activity, clock, data_date, notes)
    return {
        "task_code": activity.task_code,
        "wbs_id": activity.wbs_id,
        "bac": bac,
        "pv": pv,
        "ev": ev,
        "ac": ac,
        "pct": pct,
    }


def _percent(activity: Activity, notes: list[str]) -> float | None:
    kind = activity.complete_pct_type
    if kind == "CP_Drtn":
        target = activity.target_drtn_hr_cnt
        remain = activity.remain_drtn_hr_cnt
        if target is None or remain is None or target <= 0:
            notes.append(f"{activity.task_code}: duración original inválida para CP_Drtn.")
            return None
        return _clamp(1 - remain / target)
    if kind == "CP_Phys":
        raw = activity.phys_complete_pct
        if raw is None:
            notes.append(f"{activity.task_code}: sin phys_complete_pct.")
            return None
        if raw > 1:
            notes.append(_PHYS)
            raw = raw / 100
        return _clamp(raw)
    if kind == "CP_Units":
        notes.append(_UNITS)
        return None
    notes.append(f"{activity.task_code}: tipo de % completo no reconocido ({kind}).")
    return None


def _pv(
    bac: float,
    activity: Activity,
    clock: WorkCalendar | None,
    data_date: datetime,
    notes: list[str],
) -> float | None:
    start = activity.target_start_date
    end = activity.target_end_date
    if start is None or end is None:
        notes.append(f"{activity.task_code}: sin fechas baseline para el PV.")
        return None
    if data_date <= start:
        return 0.0
    if clock is None:
        notes.append(_CLOCK)
        return _clock_pv(bac, start, end, data_date)
    try:
        span = clock.work_between(start, end)
        if span <= 0:
            return bac if data_date >= end else 0.0
        if data_date >= end:
            return bac
        return bac * clock.work_between(start, data_date) / span
    except CalendarLimitError:
        notes.append(f"{activity.task_code}: el calendario no alcanza para el PV.")
        return None


def _clock_pv(bac: float, start: datetime, end: datetime, data_date: datetime) -> float:
    span = (end - start).total_seconds()
    if span <= 0:
        return bac if data_date >= end else 0.0
    if data_date >= end:
        return bac
    done = (data_date - start).total_seconds()
    return bac * _clamp(done / span)


def _earned_schedule(
    schedule: Schedule,
    rows: list[dict[str, object]],
    clocks: dict[str, WorkCalendar],
    data_date: datetime | None,
    ev: float | None,
    bac: float | None,
    notes: list[str],
) -> tuple[float | None, float | None, float | None, float | None]:
    if ev is None or bac is None or bac <= 0 or data_date is None:
        return None, None, None, None
    window = _window(schedule, rows, clocks, notes)
    if window is None:
        notes.append("Earned Schedule no tiene fechas baseline.")
        return None, None, None, None
    start, end, clock = window
    if clock is None:
        notes.append(_CLOCK)
        pd_hours, at_hours = _clock_window(start, end, data_date)
    else:
        try:
            pd_hours = clock.work_between(start, end) / 60
            if data_date <= start:
                at_hours = 0.0
            else:
                at_hours = clock.work_between(start, min(data_date, end)) / 60
        except CalendarLimitError:
            notes.append("El calendario no alcanza para Earned Schedule.")
            return None, None, None, None
    if pd_hours <= 0:
        return None, at_hours, None, None
    es_hours = (min(ev, bac) / bac) * pd_hours
    spi_t = es_hours / at_hours if at_hours > 0 else None
    ieac_t = pd_hours / spi_t if spi_t is not None and spi_t > 0 else None
    return es_hours, at_hours, spi_t, ieac_t


def _window(
    schedule: Schedule,
    rows: list[dict[str, object]],
    clocks: dict[str, WorkCalendar],
    notes: list[str],
) -> tuple[datetime, datetime, WorkCalendar | None] | None:
    usable = [
        activity
        for activity, row in zip(schedule.activities, rows, strict=True)
        if row["bac"] is not None
        and activity.target_start_date is not None
        and activity.target_end_date is not None
    ]
    if not usable:
        return None
    start = min(activity.target_start_date for activity in usable if activity.target_start_date)
    end = max(activity.target_end_date for activity in usable if activity.target_end_date)
    if start is None or end is None:
        return None
    chosen: list[WorkCalendar] = []
    for activity in usable:
        clock = clocks.get(activity.clndr_id or "")
        if clock is not None and clock not in chosen:
            chosen.append(clock)
    if len(chosen) > 1:
        notes.append("Earned Schedule usa el calendario de la primera actividad con BAC.")
    return start, end, chosen[0] if chosen else None


def _clock_window(start: datetime, end: datetime, data_date: datetime) -> tuple[float, float]:
    pd_hours = max((end - start).total_seconds() / 3600, 0)
    if data_date <= start:
        return pd_hours, 0.0
    at_hours = (min(data_date, end) - start).total_seconds() / 3600
    return pd_hours, max(at_hours, 0)


def _data_date(schedule: Schedule) -> tuple[datetime | None, str | None]:
    dates = {
        item.last_recalc_date
        for item in schedule.projects
        if item.last_recalc_date is not None
    }
    if not dates:
        return None, "No hay fecha de corte (last_recalc_date)."
    if len(dates) > 1:
        return None, "Hay más de una fecha de corte. EVM no elige una."
    return next(iter(dates)), None


def _sum_attr(rows: list[Assignment], name: str) -> float | None:
    values = [getattr(item, name) for item in rows if getattr(item, name) is not None]
    if not values:
        return None
    return float(sum(values))


def _total(values: Iterable[object]) -> float | None:
    numbers = [item for item in values if isinstance(item, int | float)]
    if not numbers:
        return None
    return float(sum(numbers))


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return numerator / denominator


def _wbs(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, dict[str, float]] = {}
    for row in rows:
        key = str(row["wbs_id"] or "")
        bucket = grouped.setdefault(key, {"pv": 0.0, "ev": 0.0, "ac": 0.0})
        for name in ("pv", "ev", "ac"):
            value = row[name]
            if isinstance(value, int | float):
                bucket[name] += float(value)
    table = [{"wbs_id": key, **value} for key, value in grouped.items()]
    table.append(
        {
            "wbs_id": "total",
            "pv": _total(row["pv"] for row in rows),
            "ev": _total(row["ev"] for row in rows),
            "ac": _total(row["ac"] for row in rows),
        }
    )
    return table


def _resources(schedule: Schedule) -> list[dict[str, object]]:
    totals: dict[str, float] = {}
    for item in schedule.assignments:
        if item.rsrc_id is None or item.target_qty is None:
            continue
        totals[item.rsrc_id] = totals.get(item.rsrc_id, 0.0) + item.target_qty
    return [{"rsrc_id": key, "target_qty": value} for key, value in sorted(totals.items())]


def _clamp(value: float) -> float:
    return min(1.0, max(0.0, value))
