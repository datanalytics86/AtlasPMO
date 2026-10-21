"""DCMA 1–11, 13 and 14, GAO checks that can be automated, and extra checks.

DCMA 12 stays out: it needs the CPM engine. A missing input becomes
status `no_evaluable` with a finding that says why.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from atlaspmo.analysis.contract import FINDING_COLUMNS, Metric
from atlaspmo.analysis.quality.profiles import Profile
from atlaspmo.model.schedule import Activity, Relationship, Schedule

MILESTONES = frozenset({"TT_Mile", "TT_FinMile"})


def evaluate(
    schedule: Schedule, profile: Profile, baseline: Schedule | None
) -> tuple[
    dict[str, Metric],
    pd.DataFrame,
    list[str],
]:
    findings: list[dict[str, object]] = []
    notes: list[str] = list(schedule.parse_notes)
    if not schedule.cost_column_present:
        notes.append(
            "No está TASKRSRC.target_cost. El chequeo de recursos mira solo si hay asignación."
        )
    population = [item for item in schedule.activities if _in_logic_population(item, profile)]
    data_date = _data_date(schedule, findings)
    metrics: dict[str, Metric] = {}
    metrics["logic"] = _logic(population, schedule, profile, findings)
    metrics["leads"] = _lag_share(schedule, profile, findings, negative=True)
    metrics["lags"] = _lag_share(schedule, profile, findings, negative=False)
    metrics["relationship_types"] = _fs_share(schedule, profile, findings)
    metrics["hard_constraints"] = _hard(population, profile, findings)
    metrics["high_float"] = _float_share(population, schedule, profile, findings, high=True)
    metrics["negative_float"] = _float_share(population, schedule, profile, findings, high=False)
    metrics["high_duration"] = _duration(population, schedule, profile, findings)
    metrics["invalid_dates"] = _invalid_dates(schedule, data_date, findings)
    metrics["resources"] = _resources(population, schedule, profile, findings)
    metrics["missed_tasks"] = _baseline_ratio(
        schedule, baseline, data_date, profile, findings, missed=True
    )
    metrics["bei"] = _baseline_ratio(schedule, baseline, data_date, profile, findings, missed=False)
    metrics["cpli"] = _cpli(schedule, profile, findings)
    _extras(schedule, population, profile, data_date, findings, metrics)
    _gao(schedule, metrics, findings)
    metrics["quality_index"] = _index(metrics, profile)
    frame = pd.DataFrame(findings, columns=list(FINDING_COLUMNS))
    return metrics, frame, notes


def _in_logic_population(activity: Activity, profile: Profile) -> bool:
    excluded = activity.status_code == "TK_Complete"
    excluded = excluded or (profile.exclude_loe and activity.task_type == "TT_LOE")
    excluded = excluded or (profile.exclude_wbs_summary and activity.task_type == "TT_WBS")
    return not excluded


def _data_date(schedule: Schedule, findings: list[dict[str, object]]) -> datetime | None:
    dates = [
        item.last_recalc_date for item in schedule.projects if item.last_recalc_date is not None
    ]
    if not dates:
        _add(
            findings,
            rule_id="data_date",
            rule_name_es="Fecha de corte",
            source="ATLASPMO",
            severity="info",
            object_type="project",
            object_id=None,
            task_code=None,
            value=None,
            threshold=None,
            passed=True,
            message_es="No hay last_recalc_date. Las métricas que la piden quedan no evaluables.",
        )
        return None
    if len(set(dates)) > 1:
        _add(
            findings,
            rule_id="data_date",
            rule_name_es="Fecha de corte",
            source="ATLASPMO",
            severity="media",
            object_type="project",
            object_id=None,
            task_code=None,
            value=None,
            threshold=None,
            passed=False,
            message_es="Hay más de una fecha de corte. Elige un proyecto.",
        )
        return None
    return dates[0]


def _logic(
    population: list[Activity],
    schedule: Schedule,
    profile: Profile,
    findings: list[dict[str, object]],
) -> Metric:
    if "TASK.status_code" in schedule.absent_columns or "TASK" in schedule.absent_tables:
        return _gap(findings, "logic", "Lógica", "DCMA", "Falta TASK.status_code.")
    if not population:
        return _gap(findings, "logic", "Lógica", "DCMA", "La población de incompletas está vacía.")
    preds, succs = _ends(schedule.relationships)
    offenders = [
        item for item in population if item.task_id not in preds or item.task_id not in succs
    ]
    value = len(offenders) / len(population)
    status = _max_status(value, profile.logic_max)
    for item in offenders:
        _add(
            findings,
            rule_id="logic",
            rule_name_es="Lógica",
            source="DCMA",
            severity="alta",
            object_type="activity",
            object_id=item.task_id,
            task_code=item.task_code,
            value=value,
            threshold=profile.logic_max,
            passed=False,
            message_es="Incompleta sin predecesora o sin sucesora.",
        )
    return Metric(value, profile.logic_max, status)


def _ends(relationships: tuple[Relationship, ...]) -> tuple[set[str], set[str]]:
    preds: set[str] = set()
    succs: set[str] = set()
    for link in relationships:
        if link.task_id is not None and link.pred_task_id is not None:
            preds.add(link.task_id)
            succs.add(link.pred_task_id)
    return preds, succs


def _lag_share(
    schedule: Schedule,
    profile: Profile,
    findings: list[dict[str, object]],
    negative: bool,
) -> Metric:
    rule_id = "leads" if negative else "lags"
    name = "Adelantos" if negative else "Atrasos de vínculo"
    limit = profile.leads_max if negative else profile.lags_max
    if "TASKPRED.lag_hr_cnt" in schedule.absent_columns or "TASKPRED" in schedule.absent_tables:
        return _gap(findings, rule_id, name, "DCMA", "Falta TASKPRED.lag_hr_cnt.")
    rows = [item for item in schedule.relationships if item.pred_task_id and item.task_id]
    if any(item.lag_hr_cnt is None for item in rows):
        return _gap(findings, rule_id, name, "DCMA", "Hay vínculos con lag vacío.")
    if not rows:
        return _gap(findings, rule_id, name, "DCMA", "No hay vínculos.")
    if negative:
        hit = [item for item in rows if item.lag_hr_cnt is not None and item.lag_hr_cnt < 0]
    else:
        hit = [item for item in rows if item.lag_hr_cnt is not None and item.lag_hr_cnt > 0]
    value = len(hit) / len(rows)
    status = _max_status(value, limit)
    for item in hit:
        _add(
            findings,
            rule_id=rule_id,
            rule_name_es=name,
            source="DCMA",
            severity="alta" if negative else "media",
            object_type="relationship",
            object_id=item.task_pred_id,
            task_code=None,
            value=value,
            threshold=limit,
            passed=False,
            message_es="Lag negativo." if negative else "Lag positivo.",
        )
    return Metric(value, limit, status)


def _fs_share(
    schedule: Schedule,
    profile: Profile,
    findings: list[dict[str, object]],
) -> Metric:
    if "TASKPRED.pred_type" in schedule.absent_columns or "TASKPRED" in schedule.absent_tables:
        return _gap(
            findings,
            "relationship_types",
            "Tipos de vínculo",
            "DCMA",
            "Falta TASKPRED.pred_type.",
        )
    rows = [item for item in schedule.relationships if item.pred_task_id and item.task_id]
    if not rows:
        return _gap(findings, "relationship_types", "Tipos de vínculo", "DCMA", "No hay vínculos.")
    fs = [item for item in rows if item.pred_type == "PR_FS"]
    value = len(fs) / len(rows)
    status = _min_status(value, profile.fs_min)
    if status == "no_cumple":
        _add(
            findings,
            rule_id="relationship_types",
            rule_name_es="Tipos de vínculo",
            source="DCMA",
            severity="media",
            object_type="project",
            object_id=None,
            task_code=None,
            value=value,
            threshold=profile.fs_min,
            passed=False,
            message_es="La proporción de vínculos FS está bajo el umbral.",
        )
    return Metric(value, profile.fs_min, status)


def _hard(
    population: list[Activity],
    profile: Profile,
    findings: list[dict[str, object]],
) -> Metric:
    if not population:
        return _gap(findings, "hard_constraints", "Restricciones duras", "DCMA", "Población vacía.")
    hit = [item for item in population if _is_hard(item, profile)]
    value = len(hit) / len(population)
    status = _max_status(value, profile.hard_max)
    for item in hit:
        _add(
            findings,
            rule_id="hard_constraints",
            rule_name_es="Restricciones duras",
            source="DCMA",
            severity="alta",
            object_type="activity",
            object_id=item.task_id,
            task_code=item.task_code,
            value=value,
            threshold=profile.hard_max,
            passed=False,
            message_es="Restricción dura en una actividad incompleta.",
        )
    return Metric(value, profile.hard_max, status)


def _is_hard(activity: Activity, profile: Profile) -> bool:
    hard = profile.hard_constraints
    return activity.cstr_type in hard or activity.cstr_type2 in hard


def _float_share(
    population: list[Activity],
    schedule: Schedule,
    profile: Profile,
    findings: list[dict[str, object]],
    high: bool,
) -> Metric:
    rule_id = "high_float" if high else "negative_float"
    name = "Holgura alta" if high else "Holgura negativa"
    limit = profile.high_float_max if high else profile.negative_float_max
    if "TASK.total_float_hr_cnt" in schedule.absent_columns:
        return _gap(findings, rule_id, name, "DCMA", "Falta TASK.total_float_hr_cnt.")
    if not population:
        return _gap(findings, rule_id, name, "DCMA", "Población vacía.")
    days: list[tuple[Activity, float]] = []
    for item in population:
        converted = _days(item.total_float_hr_cnt, item, schedule, profile)
        if converted is None and item.total_float_hr_cnt is not None:
            return _gap(
                findings,
                rule_id,
                name,
                "DCMA",
                "Falta day_hr_cnt y el perfil no fija hours_per_day.",
            )
        if converted is None:
            return _gap(findings, rule_id, name, "DCMA", "Hay holgura total vacía.")
        days.append((item, converted))
    if high:
        hit = [item for item, value in days if value > profile.high_float_days]
        text = f"Holgura total mayor que {profile.high_float_days:g} días."
    else:
        hit = [item for item, value in days if value < 0]
        text = "Holgura total negativa."
    value = len(hit) / len(population)
    status = _max_status(value, limit)
    for item in hit:
        _add(
            findings,
            rule_id=rule_id,
            rule_name_es=name,
            source="DCMA",
            severity="media" if high else "alta",
            object_type="activity",
            object_id=item.task_id,
            task_code=item.task_code,
            value=value,
            threshold=limit,
            passed=False,
            message_es=text,
        )
    return Metric(value, limit, status)


def _duration(
    population: list[Activity],
    schedule: Schedule,
    profile: Profile,
    findings: list[dict[str, object]],
) -> Metric:
    column = "remain_drtn_hr_cnt" if profile.duration_field == "remain" else "target_drtn_hr_cnt"
    if f"TASK.{column}" in schedule.absent_columns:
        return _gap(findings, "high_duration", "Duración alta", "DCMA", f"Falta TASK.{column}.")
    group = [
        item
        for item in population
        if not (profile.exclude_milestones_from_duration and item.task_type in MILESTONES)
    ]
    if not group:
        return _gap(findings, "high_duration", "Duración alta", "DCMA", "Población vacía.")
    hit: list[Activity] = []
    for item in group:
        if profile.duration_field == "remain":
            hours = item.remain_drtn_hr_cnt
        else:
            hours = item.target_drtn_hr_cnt
        converted = _days(hours, item, schedule, profile)
        if converted is None and hours is not None:
            return _gap(
                findings,
                "high_duration",
                "Duración alta",
                "DCMA",
                "Falta day_hr_cnt y el perfil no fija hours_per_day.",
            )
        if converted is None:
            return _gap(findings, "high_duration", "Duración alta", "DCMA", "Hay duración vacía.")
        if converted > profile.high_duration_days:
            hit.append(item)
    value = len(hit) / len(group)
    status = _max_status(value, profile.high_duration_max)
    for item in hit:
        _add(
            findings,
            rule_id="high_duration",
            rule_name_es="Duración alta",
            source="DCMA",
            severity="media",
            object_type="activity",
            object_id=item.task_id,
            task_code=item.task_code,
            value=value,
            threshold=profile.high_duration_max,
            passed=False,
            message_es=f"Duración mayor que {profile.high_duration_days:g} días.",
        )
    return Metric(value, profile.high_duration_max, status)


def _invalid_dates(
    schedule: Schedule,
    data_date: datetime | None,
    findings: list[dict[str, object]],
) -> Metric:
    if data_date is None:
        return _gap(
            findings, "invalid_dates", "Fechas inválidas", "DCMA", "Falta la fecha de corte."
        )
    count = 0
    for item in schedule.activities:
        reasons: list[str] = []
        if item.status_code != "TK_Complete":
            for label, value in (
                ("early_start_date", item.early_start_date),
                ("early_end_date", item.early_end_date),
            ):
                if value is not None and value < data_date:
                    reasons.append(label)
        for label, value in (
            ("act_start_date", item.act_start_date),
            ("act_end_date", item.act_end_date),
        ):
            if value is not None and value > data_date:
                reasons.append(label)
        if reasons:
            count += 1
            _add(
                findings,
                rule_id="invalid_dates",
                rule_name_es="Fechas inválidas",
                source="DCMA",
                severity="alta",
                object_type="activity",
                object_id=item.task_id,
                task_code=item.task_code,
                value=None,
                threshold=0,
                passed=False,
                message_es="Fecha fuera de la fecha de corte: " + ", ".join(reasons),
            )
    status = "cumple" if count == 0 else "no_cumple"
    return Metric(float(count), 0.0, status)


def _resources(
    population: list[Activity],
    schedule: Schedule,
    profile: Profile,
    findings: list[dict[str, object]],
) -> Metric:
    group = [
        item
        for item in population
        if item.task_type not in MILESTONES and _duration_hours(item, profile) not in (None, 0)
    ]
    if not group:
        return _gap(findings, "resources", "Recursos", "DCMA", "No hay incompletas con duración.")
    assigned = {item.task_id for item in schedule.assignments if item.rsrc_id}
    if schedule.cost_column_present:
        assigned |= {
            item.task_id
            for item in schedule.assignments
            if item.task_id and _has_cost(item.target_cost, item.act_reg_cost, item.remain_cost)
        }
    hit = [item for item in group if item.task_id not in assigned]
    value = len(hit) / len(group)
    status = "info" if profile.resources_max is None else _max_status(value, profile.resources_max)
    for item in hit:
        _add(
            findings,
            rule_id="resources",
            rule_name_es="Recursos",
            source="DCMA",
            severity="info" if status == "info" else "media",
            object_type="activity",
            object_id=item.task_id,
            task_code=item.task_code,
            value=value,
            threshold=profile.resources_max,
            passed=status != "no_cumple",
            message_es="Incompleta con duración y sin recurso ni costo.",
        )
    return Metric(value, profile.resources_max, status)


def _has_cost(*values: float | None) -> bool:
    return any(value not in (None, 0) for value in values)


def _baseline_ratio(
    schedule: Schedule,
    baseline: Schedule | None,
    data_date: datetime | None,
    profile: Profile,
    findings: list[dict[str, object]],
    missed: bool,
) -> Metric:
    rule_id = "missed_tasks" if missed else "bei"
    name = "Actividades perdidas" if missed else "BEI"
    limit = profile.missed_max if missed else profile.bei_min
    if baseline is None:
        return _gap(findings, rule_id, name, "DCMA", "Falta el proyecto baseline.")
    if data_date is None:
        return _gap(findings, rule_id, name, "DCMA", "Falta la fecha de corte.")
    baseline_end = {
        item.task_code: item.target_end_date
        for item in baseline.activities
        if item.task_code and item.target_end_date is not None
    }
    if "TASK.target_end_date" in baseline.absent_columns:
        return _gap(findings, rule_id, name, "DCMA", "El baseline no trae target_end_date.")
    due = []
    for item in schedule.activities:
        end = baseline_end.get(item.task_code or "")
        if end is not None and end <= data_date:
            due.append((item, end))
    if not due:
        return _gap(
            findings,
            rule_id,
            name,
            "DCMA",
            "Ninguna actividad tenía fin baseline en o antes de la fecha de corte.",
        )
    if missed:
        hit = []
        for item, end in due:
            late = item.act_end_date is not None and item.act_end_date > end
            if item.status_code != "TK_Complete" or late:
                hit.append(item)
        value = len(hit) / len(due)
        status = _max_status(value, limit)
        message = "Debió terminar y llegó tarde o sigue abierta."
    else:
        completed = [item for item, _end in due if item.status_code == "TK_Complete"]
        value = len(completed) / len(due)
        status = _min_status(value, limit)
        if status == "no_cumple":
            hit = [item for item, _end in due if item.status_code != "TK_Complete"]
        else:
            hit = []
        message = "No está completa y su fin baseline ya venció."
    for item in hit:
        _add(
            findings,
            rule_id=rule_id,
            rule_name_es=name,
            source="DCMA",
            severity="alta",
            object_type="activity",
            object_id=item.task_id,
            task_code=item.task_code,
            value=value,
            threshold=limit,
            passed=False,
            message_es=message,
        )
    return Metric(value, limit, status)


def _cpli(schedule: Schedule, profile: Profile, findings: list[dict[str, object]]) -> Metric:
    column, order_column = _path_columns(schedule)
    if column is None:
        return _gap(
            findings,
            "cpli",
            "CPLI",
            "DCMA",
            "No está TASK.float_path ni TASK.int_path. El CPLI de la fase 1 no inventa la ruta.",
        )
    group = [item for item in schedule.activities if _path_value(item, column) == "1"]
    if not group:
        return _gap(findings, "cpli", "CPLI", "DCMA", "No hay actividades con ruta 1.")
    hours = 0.0
    for item in group:
        if item.remain_drtn_hr_cnt is None:
            return _gap(
                findings, "cpli", "CPLI", "DCMA", "Hay duración remanente vacía en la ruta 1."
            )
        converted = _days(item.remain_drtn_hr_cnt, item, schedule, profile)
        if converted is None:
            return _gap(
                findings, "cpli", "CPLI", "DCMA", "Falta day_hr_cnt para convertir la ruta 1."
            )
        hours += converted
    if hours == 0:
        return _gap(findings, "cpli", "CPLI", "DCMA", "El largo remanente de la ruta 1 es cero.")
    finish = _path_finish(group, order_column)
    if finish is None or finish.total_float_hr_cnt is None:
        return _gap(
            findings,
            "cpli",
            "CPLI",
            "DCMA",
            "La actividad final de la ruta 1 no tiene holgura total.",
        )
    tf_days = _days(finish.total_float_hr_cnt, finish, schedule, profile)
    if tf_days is None:
        return _gap(
            findings, "cpli", "CPLI", "DCMA", "No se pudo convertir la holgura del fin de ruta."
        )
    value = (hours + tf_days) / hours
    status = _min_status(value, profile.cpli_min)
    if status == "no_cumple":
        _add(
            findings,
            rule_id="cpli",
            rule_name_es="CPLI",
            source="DCMA",
            severity="alta",
            object_type="project",
            object_id=None,
            task_code=None,
            value=value,
            threshold=profile.cpli_min,
            passed=False,
            message_es="CPLI bajo el umbral, calculado con la ruta 1 guardada.",
        )
    return Metric(value, profile.cpli_min, status)


def _path_columns(schedule: Schedule) -> tuple[str | None, str | None]:
    if "TASK.float_path" not in schedule.absent_columns and "TASK" not in schedule.absent_tables:
        return "float_path", "float_path_order"
    if "TASK.int_path" not in schedule.absent_columns and "TASK" not in schedule.absent_tables:
        return "int_path", "int_path_order"
    return None, None


def _path_value(activity: Activity, column: str) -> str | None:
    if column == "float_path":
        return activity.float_path
    return activity.int_path


def _path_finish(group: list[Activity], order_column: str | None) -> Activity | None:
    def order_of(item: Activity) -> float:
        raw = item.float_path_order if order_column == "float_path_order" else item.int_path_order
        if raw is None:
            return -1
        try:
            return float(raw)
        except ValueError:
            return -1

    if not group:
        return None
    return max(group, key=order_of)


def _extras(
    schedule: Schedule,
    population: list[Activity],
    profile: Profile,
    data_date: datetime | None,
    findings: list[dict[str, object]],
    metrics: dict[str, Metric],
) -> None:
    by_id = {item.task_id: item for item in schedule.activities if item.task_id}
    preds, succs = _ends(schedule.relationships)
    open_start = [item for item in population if item.task_id not in preds]
    open_finish = [item for item in population if item.task_id not in succs]
    metrics["open_starts"] = Metric(float(len(open_start)), None, "info")
    metrics["open_finishes"] = Metric(float(len(open_finish)), None, "info")
    for item in open_start:
        _extra(findings, "open_start", "Inicio abierto", item, "Sin predecesora.")
    for item in open_finish:
        _extra(findings, "open_finish", "Fin abierto", item, "Sin sucesora.")
    sf = [link for link in schedule.relationships if link.pred_type == "PR_SF"]
    metrics["sf_links"] = Metric(float(len(sf)), 0.0, "cumple" if not sf else "no_cumple")
    for link in sf:
        _add(
            findings,
            rule_id="sf_links",
            rule_name_es="Vínculo SF",
            source="ATLASPMO",
            severity="media",
            object_type="relationship",
            object_id=link.task_pred_id,
            task_code=None,
            value=float(len(sf)),
            threshold=0,
            passed=False,
            message_es="Vínculo inicio-fin.",
        )
    incoming: dict[str, int] = {}
    for link in schedule.relationships:
        if link.task_id:
            incoming[link.task_id] = incoming.get(link.task_id, 0) + 1
    convergent = [
        item
        for item in schedule.activities
        if item.task_id and incoming.get(item.task_id, 0) >= profile.convergence_predecessors
    ]
    metrics["convergence"] = Metric(
        float(len(convergent)), float(profile.convergence_predecessors), "info"
    )
    for item in convergent:
        _extra(findings, "convergence", "Convergencia", item, "Muchas predecesoras.")
    oos = _out_of_sequence(schedule, by_id)
    metrics["out_of_sequence"] = Metric(float(len(oos)), 0.0, "cumple" if not oos else "no_cumple")
    for item in oos:
        _extra(
            findings,
            "out_of_sequence",
            "Avance fuera de secuencia",
            item,
            "Empezó con una predecesora incompleta.",
        )
    if data_date is not None:
        late_actual = [
            item
            for item in schedule.activities
            if (item.act_start_date and item.act_start_date > data_date)
            or (item.act_end_date and item.act_end_date > data_date)
        ]
        metrics["actual_after_data_date"] = Metric(
            float(len(late_actual)), 0.0, "cumple" if not late_actual else "no_cumple"
        )
    lag_long = []
    for link in schedule.relationships:
        succ = by_id.get(link.task_id or "")
        if link.lag_hr_cnt is None or succ is None or succ.remain_drtn_hr_cnt is None:
            continue
        if link.lag_hr_cnt > succ.remain_drtn_hr_cnt:
            lag_long.append(link)
    metrics["lag_vs_successor"] = Metric(float(len(lag_long)), 0.0, "info")
    calendars = [item.clndr_id for item in schedule.activities if item.clndr_id]
    dominant = max(set(calendars), key=calendars.count) if calendars else None
    odd = [item for item in schedule.activities if item.clndr_id and item.clndr_id != dominant]
    metrics["odd_calendar"] = Metric(float(len(odd)), None, "info")
    loe_bad = []
    for link in schedule.relationships:
        pred = by_id.get(link.pred_task_id or "")
        succ = by_id.get(link.task_id or "")
        if pred and succ and pred.task_type == "TT_LOE" and succ.task_type == "TT_Task":
            loe_bad.append(pred)
    loe_status = "cumple" if not loe_bad else "no_cumple"
    metrics["loe_logic"] = Metric(float(len(loe_bad)), 0.0, loe_status)
    for item in loe_bad:
        _extra(
            findings,
            "loe_logic",
            "LOE con lógica impropia",
            item,
            "Una LOE precede a una actividad discreta.",
        )
    if profile.required_code_type_ids:
        coded = {
            (item.task_id, item.actv_code_type_id)
            for item in schedule.activity_codes
            if item.task_id and item.actv_code_type_id
        }
        missing = []
        for activity in schedule.activities:
            for type_id in profile.required_code_type_ids:
                if (activity.task_id, type_id) not in coded:
                    missing.append(activity)
                    break
        code_status = "cumple" if not missing else "no_cumple"
        metrics["missing_codes"] = Metric(float(len(missing)), 0.0, code_status)
    else:
        metrics["missing_codes"] = _gap(
            findings,
            "missing_codes",
            "Códigos requeridos",
            "ATLASPMO",
            "El perfil no exige códigos.",
        )
    density = len(schedule.relationships) / len(schedule.activities) if schedule.activities else 0.0
    metrics["logic_density"] = Metric(density, None, "info")


def _out_of_sequence(schedule: Schedule, by_id: dict[str, Activity]) -> list[Activity]:
    found: list[Activity] = []
    seen: set[str] = set()
    for link in schedule.relationships:
        pred = by_id.get(link.pred_task_id or "")
        succ = by_id.get(link.task_id or "")
        if pred is None or succ is None or succ.task_id is None:
            continue
        started = succ.act_start_date is not None
        open_pred = pred.status_code != "TK_Complete"
        if started and open_pred and succ.task_id not in seen:
            found.append(succ)
            seen.add(succ.task_id)
    return found


def _gao(
    schedule: Schedule,
    metrics: dict[str, Metric],
    findings: list[dict[str, object]],
) -> None:
    checks = (
        ("gao_01", "Capturar actividades", "cumple" if schedule.activities else "no_cumple"),
        ("gao_02", "Secuenciar", _gao_from(metrics.get("logic"))),
        ("gao_03", "Asignar recursos", _gao_from(metrics.get("resources"))),
        ("gao_04", "Establecer duraciones", _gao_from(metrics.get("high_duration"))),
        ("gao_05", "Trazabilidad", _trace(metrics)),
        ("gao_06", "Ruta crítica válida", "manual"),
        (
            "gao_07",
            "Holgura razonable",
            _both(metrics.get("high_float"), metrics.get("negative_float")),
        ),
        ("gao_08", "Análisis de riesgo", "manual"),
        ("gao_09", "Actualizar con avance", _progress(schedule)),
        ("gao_10", "Mantener el baseline", _baseline_practice(metrics)),
    )
    for rule_id, name, status in checks:
        metrics[rule_id] = Metric(None, None, status)
        if status == "manual":
            _add(
                findings,
                rule_id=rule_id,
                rule_name_es=name,
                source="GAO",
                severity="info",
                object_type="project",
                object_id=None,
                task_code=None,
                value=None,
                threshold=None,
                passed=True,
                message_es="Requiere revisión manual.",
            )


def _baseline_practice(metrics: dict[str, Metric]) -> str:
    bei = metrics.get("bei")
    if bei is not None and bei.status == "no_evaluable":
        return "manual"
    return _gao_from(bei)


def _gao_from(metric: Metric | None) -> str:
    if metric is None or metric.status == "no_evaluable":
        return "manual"
    if metric.status == "info":
        return "manual"
    return metric.status


def _trace(metrics: dict[str, Metric]) -> str:
    starts = metrics.get("open_starts")
    finishes = metrics.get("open_finishes")
    if starts is None or finishes is None or starts.value is None or finishes.value is None:
        return "manual"
    if starts.value <= 1 and finishes.value <= 1:
        return "cumple"
    return "no_cumple"


def _both(left: Metric | None, right: Metric | None) -> str:
    states = [_gao_from(left), _gao_from(right)]
    if "no_cumple" in states:
        return "no_cumple"
    if "manual" in states:
        return "manual"
    return "cumple"


def _progress(schedule: Schedule) -> str:
    if any(item.act_start_date or item.act_end_date for item in schedule.activities):
        return "cumple"
    return "manual"


def _index(metrics: dict[str, Metric], profile: Profile) -> Metric:
    weighted = 0.0
    total = 0.0
    for key, weight in profile.weights.items():
        metric = metrics.get(key)
        if metric is None or metric.status not in ("cumple", "no_cumple"):
            continue
        total += weight
        if metric.status == "cumple":
            weighted += weight
    if total == 0:
        return Metric(None, None, "no_evaluable")
    return Metric(100.0 * weighted / total, None, "info")


def _days(
    hours: float | None,
    activity: Activity,
    schedule: Schedule,
    profile: Profile,
) -> float | None:
    if hours is None:
        return None
    if profile.hours_per_day is not None:
        if profile.hours_per_day == 0:
            return None
        return hours / profile.hours_per_day
    calendar = schedule.calendar_for(activity.clndr_id)
    if calendar is None or calendar.day_hr_cnt in (None, 0):
        return None
    return hours / calendar.day_hr_cnt


def _duration_hours(activity: Activity, profile: Profile) -> float | None:
    if profile.duration_field == "remain":
        return activity.remain_drtn_hr_cnt
    return activity.target_drtn_hr_cnt


def _max_status(value: float, limit: float) -> str:
    return "cumple" if value <= limit else "no_cumple"


def _min_status(value: float, limit: float) -> str:
    return "cumple" if value >= limit else "no_cumple"


def _gap(
    findings: list[dict[str, object]],
    rule_id: str,
    name: str,
    source: str,
    reason: str,
) -> Metric:
    _add(
        findings,
        rule_id=rule_id,
        rule_name_es=name,
        source=source,
        severity="info",
        object_type="project",
        object_id=None,
        task_code=None,
        value=None,
        threshold=None,
        passed=True,
        message_es=reason,
    )
    return Metric(None, None, "no_evaluable")


def _extra(
    findings: list[dict[str, object]],
    rule_id: str,
    name: str,
    activity: Activity,
    message: str,
) -> None:
    _add(
        findings,
        rule_id=rule_id,
        rule_name_es=name,
        source="ATLASPMO",
        severity="media",
        object_type="activity",
        object_id=activity.task_id,
        task_code=activity.task_code,
        value=None,
        threshold=None,
        passed=False,
        message_es=message,
    )


def _add(findings: list[dict[str, object]], **kwargs: object) -> None:
    row: dict[str, object] = {column: None for column in FINDING_COLUMNS}
    row.update(kwargs)
    findings.append(row)
