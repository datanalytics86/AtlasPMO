"""Compare two schedules by task_code. Stored fields only; CPM is not rerun."""

from __future__ import annotations

from dataclasses import dataclass

from atlaspmo.model.schedule import Activity, Relationship, Schedule


@dataclass(frozen=True)
class Change:
    kind: str
    task_code: str
    detail: str


@dataclass(frozen=True)
class CompareReport:
    changes: tuple[Change, ...]
    added: int
    removed: int
    links_added: int
    links_removed: int
    links_changed: int
    remain_changed: int
    target_changed: int
    constraint_changed: int
    calendar_changed: int
    actuals_changed: int
    critical_enter: int
    critical_exit: int
    float_eroded: int
    notes: tuple[str, ...]


def compare_schedules(left: Schedule, right: Schedule) -> CompareReport:
    """Match on task_code. An empty lag is not treated as zero."""
    notes = [
        "La ruta crítica de la comparación usa la holgura total guardada. No recalcula el CPM.",
        "Un lag vacío no se compara como cero.",
    ]
    left_acts = _by_code(left, notes, "izquierda")
    right_acts = _by_code(right, notes, "derecha")
    changes: list[Change] = []
    for code in sorted(set(right_acts) - set(left_acts)):
        changes.append(Change("agregada", code, "La actividad está solo en el update."))
    for code in sorted(set(left_acts) - set(right_acts)):
        changes.append(Change("eliminada", code, "La actividad ya no está en el update."))
    remain = target = constraint = calendar = actuals = eroded = entered = exited = 0
    for code in sorted(set(left_acts) & set(right_acts)):
        before = left_acts[code]
        after = right_acts[code]
        remain += _number(
            changes, code, "duracion_remanente", before.remain_drtn_hr_cnt, after.remain_drtn_hr_cnt
        )
        target += _number(
            changes, code, "duracion_original", before.target_drtn_hr_cnt, after.target_drtn_hr_cnt
        )
        if before.total_float_hr_cnt is None or after.total_float_hr_cnt is None:
            notes.append(f"{code}: sin holgura guardada en ambos updates. No entra a la ruta.")
        constraint += _text(changes, code, "restriccion", before.cstr_type, after.cstr_type)
        calendar += _text(changes, code, "calendario", before.clndr_id, after.clndr_id)
        actuals += _actuals(changes, code, before, after)
        eroded += _float(changes, code, before, after)
        entered += _critical(changes, code, before, after, entering=True)
        exited += _critical(changes, code, before, after, entering=False)
    links = _links(left, right, left_acts, right_acts, changes, notes)
    return CompareReport(
        changes=tuple(changes),
        added=sum(1 for item in changes if item.kind == "agregada"),
        removed=sum(1 for item in changes if item.kind == "eliminada"),
        links_added=links[0],
        links_removed=links[1],
        links_changed=links[2],
        remain_changed=remain,
        target_changed=target,
        constraint_changed=constraint,
        calendar_changed=calendar,
        actuals_changed=actuals,
        critical_enter=entered,
        critical_exit=exited,
        float_eroded=eroded,
        notes=tuple(dict.fromkeys(notes)),
    )


def _by_code(schedule: Schedule, notes: list[str], side: str) -> dict[str, Activity]:
    found: dict[str, Activity] = {}
    for activity in schedule.activities:
        if not activity.task_code:
            notes.append(
                f"Hay una actividad sin task_code en la {side}. No entra al emparejamiento."
            )
            continue
        if activity.task_code in found:
            notes.append(f"{activity.task_code}: código repetido en la {side}. Se usa la primera.")
            continue
        found[activity.task_code] = activity
    return found


def _number(
    changes: list[Change],
    code: str,
    kind: str,
    before: float | None,
    after: float | None,
) -> int:
    if before is None or after is None or before == after:
        return 0
    changes.append(Change(kind, code, f"{before} → {after}"))
    return 1


def _text(
    changes: list[Change],
    code: str,
    kind: str,
    before: str | None,
    after: str | None,
) -> int:
    if before == after:
        return 0
    changes.append(Change(kind, code, f"{before or 'vacío'} → {after or 'vacío'}"))
    return 1


def _actuals(changes: list[Change], code: str, before: Activity, after: Activity) -> int:
    if before.act_start_date == after.act_start_date and before.act_end_date == after.act_end_date:
        return 0
    changes.append(Change("fechas_reales", code, "Cambió el inicio o el fin real."))
    return 1


def _float(changes: list[Change], code: str, before: Activity, after: Activity) -> int:
    left = before.total_float_hr_cnt
    right = after.total_float_hr_cnt
    if left is None or right is None or right >= left:
        return 0
    changes.append(Change("erosion_holgura", code, f"{left} → {right}"))
    return 1


def _critical(
    changes: list[Change],
    code: str,
    before: Activity,
    after: Activity,
    *,
    entering: bool,
) -> int:
    left = _is_critical(before)
    right = _is_critical(after)
    if left is None or right is None:
        return 0
    if entering and not left and right:
        changes.append(Change("entra_ruta", code, "Pasa a holgura total guardada ≤ 0."))
        return 1
    if not entering and left and not right:
        changes.append(Change("sale_ruta", code, "Deja de tener holgura total guardada ≤ 0."))
        return 1
    return 0


def _is_critical(activity: Activity) -> bool | None:
    if activity.total_float_hr_cnt is None:
        return None
    return activity.total_float_hr_cnt <= 0


def _links(
    left: Schedule,
    right: Schedule,
    left_acts: dict[str, Activity],
    right_acts: dict[str, Activity],
    changes: list[Change],
    notes: list[str],
) -> tuple[int, int, int]:
    before = _link_map(left, left_acts, notes)
    after = _link_map(right, right_acts, notes)
    added = removed = changed = 0
    for key in sorted(set(before) | set(after)):
        label = f"{key[0]} → {key[1]}"
        if key not in before:
            changes.append(Change("vinculo_agregado", label, after[key]))
            added += 1
        elif key not in after:
            changes.append(Change("vinculo_eliminado", label, before[key]))
            removed += 1
        elif before[key] != after[key]:
            changes.append(Change("vinculo_modificado", label, f"{before[key]} → {after[key]}"))
            changed += 1
    return added, removed, changed


def _link_map(
    schedule: Schedule,
    activities: dict[str, Activity],
    notes: list[str],
) -> dict[tuple[str, str], str]:
    ids = {
        activity.task_id: activity.task_code
        for activity in activities.values()
        if activity.task_id
    }
    found: dict[tuple[str, str], str] = {}
    for link in schedule.relationships:
        signature = _signature(link, ids, notes)
        if signature is None:
            continue
        key, text = signature
        if key in found:
            notes.append(f"{key[0]} → {key[1]}: hay más de un vínculo. Se compara el primero.")
            continue
        found[key] = text
    return found


def _signature(
    link: Relationship,
    ids: dict[str, str | None],
    notes: list[str],
) -> tuple[tuple[str, str], str] | None:
    pred = ids.get(link.pred_task_id or "")
    succ = ids.get(link.task_id or "")
    if not pred or not succ:
        notes.append("Hay un vínculo cuyos extremos no están en el emparejamiento.")
        return None
    lag = "vacío" if link.lag_hr_cnt is None else str(link.lag_hr_cnt)
    kind = link.pred_type or "sin tipo"
    return (pred, succ), f"{kind} lag {lag}"
