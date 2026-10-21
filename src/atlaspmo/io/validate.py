"""Load-time checks. Messages are Spanish. Codes stay in English."""

from __future__ import annotations

from dataclasses import dataclass

from atlaspmo.model.schedule import Activity, Relationship, Schedule


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message_es: str
    object_type: str
    object_id: str | None


def validate_schedule(schedule: Schedule) -> tuple[ValidationIssue, ...]:
    """Report orphans, duplicates, missing calendars, cycles and missing dates."""
    issues: list[ValidationIssue] = []
    issues.extend(_duplicate_ids(schedule.activities))
    issues.extend(_duplicate_codes(schedule.activities))
    issues.extend(_orphans(schedule))
    issues.extend(_calendars(schedule))
    issues.extend(_cycles(schedule))
    issues.extend(_missing_dates(schedule))
    issues.extend(_external(schedule))
    return tuple(issues)


def _duplicate_ids(activities: tuple[Activity, ...]) -> list[ValidationIssue]:
    seen: set[str] = set()
    issues: list[ValidationIssue] = []
    for activity in activities:
        if activity.task_id is None:
            issues.append(
                ValidationIssue(
                    "missing_task_id",
                    "Hay una actividad sin task_id.",
                    "activity",
                    activity.task_code,
                )
            )
            continue
        if activity.task_id in seen:
            issues.append(
                ValidationIssue(
                    "duplicate_task_id",
                    f"task_id {activity.task_id} está repetido.",
                    "activity",
                    activity.task_id,
                )
            )
        seen.add(activity.task_id)
    return issues


def _duplicate_codes(activities: tuple[Activity, ...]) -> list[ValidationIssue]:
    seen: set[tuple[str | None, str]] = set()
    issues: list[ValidationIssue] = []
    for activity in activities:
        if activity.task_code is None:
            continue
        key = (activity.proj_id, activity.task_code)
        if key in seen:
            issues.append(
                ValidationIssue(
                    "duplicate_task_code",
                    f"El código {activity.task_code} está repetido en el proyecto.",
                    "activity",
                    activity.task_code,
                )
            )
        seen.add(key)
    return issues


def _orphans(schedule: Schedule) -> list[ValidationIssue]:
    ids = {item.task_id for item in schedule.activities if item.task_id is not None}
    issues: list[ValidationIssue] = []
    for link in schedule.relationships:
        if link.pred_task_id not in ids or link.task_id not in ids:
            issues.append(
                ValidationIssue(
                    "orphan_relationship",
                    "El vínculo apunta a una actividad que no está en TASK.",
                    "relationship",
                    link.task_pred_id,
                )
            )
    return issues


def _calendars(schedule: Schedule) -> list[ValidationIssue]:
    known = {item.clndr_id for item in schedule.calendars if item.clndr_id is not None}
    issues: list[ValidationIssue] = []
    for activity in schedule.activities:
        if activity.clndr_id is None:
            continue
        if activity.clndr_id not in known:
            issues.append(
                ValidationIssue(
                    "missing_calendar",
                    (
                        f"La actividad {activity.task_code or activity.task_id} "
                        "usa un calendario que no está."
                    ),
                    "activity",
                    activity.task_id,
                )
            )
    return issues


def _missing_dates(schedule: Schedule) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for activity in schedule.activities:
        if activity.status_code == "TK_Complete":
            continue
        if activity.early_start_date is None and activity.target_start_date is None:
            issues.append(
                ValidationIssue(
                    "missing_start",
                    (
                        f"La actividad {activity.task_code or activity.task_id} "
                        "no tiene inicio previsto ni planificado."
                    ),
                    "activity",
                    activity.task_id,
                )
            )
    return issues


def _external(schedule: Schedule) -> list[ValidationIssue]:
    by_id = {item.task_id: item for item in schedule.activities if item.task_id is not None}
    issues: list[ValidationIssue] = []
    for link in schedule.relationships:
        if _is_external(link, by_id):
            issues.append(
                ValidationIssue(
                    "external_relationship",
                    "Vínculo entre proyectos. Queda marcado como externo.",
                    "relationship",
                    link.task_pred_id,
                )
            )
    return issues


def _is_external(link: Relationship, by_id: dict[str, Activity]) -> bool:
    both = link.pred_proj_id is not None and link.proj_id is not None
    if both and link.pred_proj_id != link.proj_id:
        return True
    pred = by_id.get(link.pred_task_id or "")
    succ = by_id.get(link.task_id or "")
    if pred is None or succ is None:
        return False
    return pred.proj_id is not None and succ.proj_id is not None and pred.proj_id != succ.proj_id


_WHITE = 0
_GRAY = 1
_BLACK = 2


def _cycles(schedule: Schedule) -> list[ValidationIssue]:
    """Report cycles with an explicit stack.

    A serial chain of tens of thousands of activities must not recurse in Python.
    """
    graph: dict[str, list[str]] = {}
    for activity in schedule.activities:
        if activity.task_id is not None:
            graph.setdefault(activity.task_id, [])
    for link in schedule.relationships:
        if link.pred_task_id is None or link.task_id is None:
            continue
        if link.pred_task_id in graph and link.task_id in graph:
            graph[link.pred_task_id].append(link.task_id)
    color: dict[str, int] = {}
    issues: list[ValidationIssue] = []

    def walk(start: str) -> None:
        stack = [start]
        frames: list[tuple[str, int]] = [(start, 0)]
        color[start] = _GRAY
        while frames:
            node, index = frames[-1]
            successors = graph[node]
            if index >= len(successors):
                frames.pop()
                stack.pop()
                color[node] = _BLACK
                continue
            frames[-1] = (node, index + 1)
            nxt = successors[index]
            state = color.get(nxt, _WHITE)
            if state == _WHITE:
                color[nxt] = _GRAY
                stack.append(nxt)
                frames.append((nxt, 0))
            elif state == _GRAY:
                start_at = stack.index(nxt)
                cycle = stack[start_at:]
                cycle.append(nxt)
                codes = [_code(schedule, item) for item in cycle]
                issues.append(
                    ValidationIssue(
                        "cycle",
                        "Ciclo: " + " → ".join(codes),
                        "project",
                        None,
                    )
                )

    for node in graph:
        if color.get(node, _WHITE) == _WHITE:
            walk(node)
    return issues


def _code(schedule: Schedule, task_id: str) -> str:
    for activity in schedule.activities:
        if activity.task_id == task_id:
            return activity.task_code or task_id
    return task_id
