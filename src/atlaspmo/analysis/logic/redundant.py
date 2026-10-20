"""Redundant logic. A link is confirmed only when removing it leaves the CPM still."""

from __future__ import annotations

from dataclasses import dataclass, replace

from atlaspmo.engine.cpm import CpmResult, schedule_cpm
from atlaspmo.engine.options import EngineOptions
from atlaspmo.model.schedule import Activity, Relationship, Schedule

_MILESTONE = {"TT_Mile", "TT_FinMile"}


@dataclass(frozen=True)
class LinkClass:
    task_pred_id: str
    status: str
    reason: str


def classify_links(
    schedule: Schedule,
    options: EngineOptions | None = None,
) -> tuple[tuple[LinkClass, ...], CpmResult]:
    """Return one class per relationship and the CPM of the original file."""
    chosen = options or EngineOptions()
    base = schedule_cpm(schedule, chosen)
    protected = _protected(schedule)
    classes: list[LinkClass] = []
    candidates: list[Relationship] = []
    for link in schedule.relationships:
        identity = link.task_pred_id or ""
        if identity in protected:
            classes.append(LinkClass(identity, "protegido", protected[identity]))
            continue
        if link.lag_hr_cnt is not None and _is_candidate(schedule, link):
            candidates.append(link)
        else:
            classes.append(
                LinkClass(identity, "no_candidato", "No hay otro camino igual o más largo.")
            )
    if base.by_id:
        confirmed, rejected = _confirm(schedule, base, candidates, chosen)
    else:
        confirmed, rejected = [], candidates
    for link in confirmed:
        classes.append(
            LinkClass(
                link.task_pred_id or "",
                "redundante_confirmado",
                "Quitarlo no mueve fechas ni holgura.",
            )
        )
    for link in rejected:
        classes.append(
            LinkClass(
                link.task_pred_id or "",
                "candidato_no_confirmado",
                "Al quitarlo cambian fechas u holgura.",
            )
        )
    return tuple(classes), base


def _protected(schedule: Schedule) -> dict[str, str]:
    by_id = {item.task_id: item for item in schedule.activities if item.task_id}
    pair_kinds: dict[frozenset[str], set[str]] = {}
    for link in schedule.relationships:
        if link.pred_task_id and link.task_id and link.pred_type:
            key = frozenset({link.pred_task_id, link.task_id})
            pair_kinds.setdefault(key, set()).add(link.pred_type)
    reasons: dict[str, str] = {}
    for link in schedule.relationships:
        identity = link.task_pred_id or ""
        pred = by_id.get(link.pred_task_id or "")
        succ = by_id.get(link.task_id or "")
        if link.pred_proj_id and link.proj_id and link.pred_proj_id != link.proj_id:
            reasons[identity] = "Vínculo entre proyectos."
            continue
        if pred and succ and pred.proj_id and succ.proj_id and pred.proj_id != succ.proj_id:
            reasons[identity] = "Vínculo entre proyectos."
            continue
        if _milestone(pred) or _milestone(succ):
            reasons[identity] = "Entra o sale de un hito."
            continue
        kinds = pair_kinds.get(frozenset({link.pred_task_id or "", link.task_id or ""}), set())
        if "PR_SS" in kinds and "PR_FF" in kinds:
            reasons[identity] = "El par SS+FF queda intacto."
    return reasons


def _milestone(activity: Activity | None) -> bool:
    return activity is not None and activity.task_type in _MILESTONE


def _is_candidate(schedule: Schedule, link: Relationship) -> bool:
    graph = _graph(schedule)
    tail, head = _ends(link)
    weight = int(round((link.lag_hr_cnt or 0) * 60))
    if tail is None or head is None:
        return False
    reduced = {
        node: [item for item in edges if item[2] != link.task_pred_id]
        for node, edges in graph.items()
    }
    alternate = _longest(reduced, tail, head)
    return alternate is not None and alternate >= weight


def _graph(
    schedule: Schedule,
) -> dict[str, list[tuple[str, int, str]]]:
    graph: dict[str, list[tuple[str, int, str]]] = {}
    for activity in schedule.activities:
        if activity.task_id is None or activity.task_type in {"TT_LOE", "TT_WBS"}:
            continue
        start, finish = f"S:{activity.task_id}", f"F:{activity.task_id}"
        graph.setdefault(start, []).append((finish, _minutes(activity), ""))
        graph.setdefault(finish, [])
    for link in schedule.relationships:
        tail, head = _ends(link)
        if tail is None or head is None or tail not in graph or head not in graph:
            continue
        graph[tail].append((head, int(round((link.lag_hr_cnt or 0) * 60)), link.task_pred_id or ""))
    return graph


def _ends(link: Relationship) -> tuple[str | None, str | None]:
    if link.pred_task_id is None or link.task_id is None:
        return None, None
    if link.pred_type == "PR_SS":
        return f"S:{link.pred_task_id}", f"S:{link.task_id}"
    if link.pred_type == "PR_FF":
        return f"F:{link.pred_task_id}", f"F:{link.task_id}"
    if link.pred_type == "PR_SF":
        return f"S:{link.pred_task_id}", f"F:{link.task_id}"
    if link.pred_type == "PR_FS":
        return f"F:{link.pred_task_id}", f"S:{link.task_id}"
    return None, None


def _minutes(activity: Activity) -> int:
    if activity.task_type in _MILESTONE:
        return 0
    hours = activity.remain_drtn_hr_cnt
    if hours is None:
        hours = activity.target_drtn_hr_cnt
    if hours is None:
        return 0
    return int(round(hours * 60))


def _longest(
    graph: dict[str, list[tuple[str, int, str]]],
    source: str,
    target: str,
) -> int | None:
    order = _event_topo(graph)
    if order is None:
        return None
    best: dict[str, int | None] = {node: None for node in graph}
    if source not in best:
        return None
    best[source] = 0
    for node in order:
        current = best.get(node)
        if current is None:
            continue
        for nxt, weight, _identity in graph.get(node, []):
            if nxt not in best:
                continue
            proposal = current + weight
            stored = best[nxt]
            if stored is None or proposal > stored:
                best[nxt] = proposal
    return best.get(target)


def _event_topo(graph: dict[str, list[tuple[str, int, str]]]) -> list[str] | None:
    incoming = {node: 0 for node in graph}
    for edges in graph.values():
        for nxt, _weight, _identity in edges:
            if nxt in incoming:
                incoming[nxt] += 1
    ready = [node for node, count in incoming.items() if count == 0]
    order: list[str] = []
    while ready:
        current = ready.pop()
        order.append(current)
        for nxt, _weight, _identity in graph.get(current, []):
            if nxt not in incoming:
                continue
            incoming[nxt] -= 1
            if incoming[nxt] == 0:
                ready.append(nxt)
    if len(order) < len(graph):
        return None
    return order


def _confirm(
    schedule: Schedule,
    base: CpmResult,
    candidates: list[Relationship],
    options: EngineOptions,
) -> tuple[list[Relationship], list[Relationship]]:
    if not candidates:
        return [], []
    if _unchanged(schedule, base, candidates, options):
        return list(candidates), []
    if len(candidates) == 1:
        return [], list(candidates)
    mid = len(candidates) // 2
    left, right = candidates[:mid], candidates[mid:]
    left_ok = _unchanged(schedule, base, left, options)
    right_ok = _unchanged(schedule, base, right, options)
    if left_ok and right_ok:
        confirmed = list(left)
        rejected: list[Relationship] = []
        for link in right:
            if _unchanged(schedule, base, confirmed + [link], options):
                confirmed.append(link)
            else:
                rejected.append(link)
        return confirmed, rejected
    kept: list[Relationship] = []
    rejected = []
    if left_ok:
        kept.extend(left)
    else:
        nested_ok, nested_bad = _confirm(schedule, base, left, options)
        kept.extend(nested_ok)
        rejected.extend(nested_bad)
    if right_ok:
        kept.extend(right)
    else:
        nested_ok, nested_bad = _confirm(schedule, base, right, options)
        kept.extend(nested_ok)
        rejected.extend(nested_bad)
    return kept, rejected


def _unchanged(
    schedule: Schedule,
    base: CpmResult,
    links: list[Relationship],
    options: EngineOptions,
) -> bool:
    drop = {link.task_pred_id for link in links}
    reduced = replace(
        schedule,
        relationships=tuple(
            item for item in schedule.relationships if item.task_pred_id not in drop
        ),
    )
    again = schedule_cpm(reduced, options)
    return _same(base, again)


def _same(left: CpmResult, right: CpmResult) -> bool:
    if set(left.by_id) != set(right.by_id):
        return False
    for key, item in left.by_id.items():
        other = right.by_id[key]
        if abs((item.early_start - other.early_start).total_seconds()) > 60:
            return False
        if abs((item.early_finish - other.early_finish).total_seconds()) > 60:
            return False
        if abs((item.late_start - other.late_start).total_seconds()) > 60:
            return False
        if abs((item.late_finish - other.late_finish).total_seconds()) > 60:
            return False
        if abs(item.total_float_hours - other.total_float_hours) > 1 / 60:
            return False
        if abs(item.free_float_hours - other.free_float_hours) > 1 / 60:
            return False
    return True
