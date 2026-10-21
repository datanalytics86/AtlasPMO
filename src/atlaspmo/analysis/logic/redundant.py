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
    contractual_codes: frozenset[str] | None = None,
) -> tuple[tuple[LinkClass, ...], CpmResult]:
    """Return one class per relationship and the CPM of the original file.

    ``contractual_codes`` lists activity codes whose links stay. An empty
    set does not protect every milestone. UDF identification is not read:
    no verified UDF column is wired, so the list is the supported path.
    """
    chosen = options or EngineOptions()
    base = schedule_cpm(schedule, chosen)
    protected = _protected(schedule, contractual_codes or frozenset())
    candidate_ids = _candidate_ids(schedule)
    classes: list[LinkClass] = []
    candidates: list[Relationship] = []
    for link in schedule.relationships:
        identity = link.task_pred_id or ""
        if identity in protected:
            classes.append(LinkClass(identity, "protegido", protected[identity]))
            continue
        if identity in candidate_ids:
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


def _protected(schedule: Schedule, contractual_codes: frozenset[str]) -> dict[str, str]:
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
        if _listed(pred, contractual_codes) or _listed(succ, contractual_codes):
            reasons[identity] = "Entra o sale de un hito contractual."
            continue
        kinds = pair_kinds.get(frozenset({link.pred_task_id or "", link.task_id or ""}), set())
        if "PR_SS" in kinds and "PR_FF" in kinds:
            reasons[identity] = "El par SS+FF queda intacto."
    return reasons


def _listed(activity: Activity | None, codes: frozenset[str]) -> bool:
    return activity is not None and activity.task_code in codes


def _candidate_ids(schedule: Schedule) -> set[str]:
    graph = _graph(schedule)
    order = _event_topo(graph)
    # A cycle makes the longest path undefined, so the whole graph yields no candidates.
    if order is None:
        return set()
    index = {node: place for place, node in enumerate(order)}
    grouped: dict[str, list[Relationship]] = {}
    for link in schedule.relationships:
        if link.lag_hr_cnt is None:
            continue
        tail, head = _ends(link)
        if tail is None or head is None or tail not in index or head not in index:
            continue
        grouped.setdefault(tail, []).append(link)
    found: set[str] = set()
    for origin, links in grouped.items():
        found.update(_origin_candidates(graph, order, index, origin, links))
    return found


def _origin_candidates(
    graph: dict[str, list[tuple[str, int, str]]],
    order: list[str],
    index: dict[str, int],
    origin: str,
    links: list[Relationship],
) -> set[str]:
    """Longest paths from one origin, only up to its farthest destination."""
    origin_at = index[origin]
    heads: list[tuple[Relationship, int]] = []
    farthest = origin_at
    for link in links:
        head = _ends(link)[1]
        if head is None:
            continue
        place = index[head]
        if place < origin_at:
            continue
        heads.append((link, place))
        farthest = max(farthest, place)
    if not heads:
        return set()
    span = farthest - origin_at + 1
    best: list[int | None] = [None] * span
    second: list[int | None] = [None] * span
    winner: list[str | None] = [None] * span
    best[0] = 0
    for place in range(origin_at, farthest + 1):
        local = place - origin_at
        current = best[local]
        if current is None:
            continue
        carried = None if local == 0 else winner[local]
        if local != 0 and carried is None:
            continue
        for nxt, weight, identity in graph.get(order[place], ()):
            nxt_at = index.get(nxt)
            if nxt_at is None or nxt_at < origin_at or nxt_at > farthest:
                continue
            first = _stored_label(identity) if carried is None else carried
            _consider(best, second, winner, nxt_at - origin_at, current + weight, first)
    found: set[str] = set()
    for link, place in heads:
        local = place - origin_at
        link_label = "rel:" + (link.task_pred_id or "")
        marked = winner[local]
        alternate = second[local] if marked == link_label else best[local]
        if alternate is not None and alternate >= _lag_minutes(link):
            found.add(link.task_pred_id or "")
    return found


def _consider(
    best: list[int | None],
    second: list[int | None],
    winner: list[str | None],
    node: int,
    proposal: int,
    first: str,
) -> None:
    current = best[node]
    if current is None or proposal > current:
        if current is not None and winner[node] != first:
            previous = second[node]
            if previous is None or current > previous:
                second[node] = current
        best[node] = proposal
        winner[node] = first
        return
    if winner[node] != first:
        previous = second[node]
        if previous is None or proposal > previous:
            second[node] = proposal


def _stored_label(identity: str) -> str:
    return "dur" if identity == "" else identity


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
        label = "rel:" + (link.task_pred_id or "")
        graph[tail].append((head, _lag_minutes(link), label))
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


def _lag_minutes(link: Relationship) -> int:
    return int(round((link.lag_hr_cnt or 0) * 60))


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
    """Confirm a subset that still matches the CPM when removed together.

    Halves that pass on their own are not united until the whole set passes.
    Two links can each be redundant only because the other remains.
    """
    if not candidates:
        return [], []
    if _unchanged(schedule, base, candidates, options):
        return list(candidates), []
    if len(candidates) == 1:
        return [], list(candidates)
    mid = len(candidates) // 2
    left_ok, left_bad = _confirm(schedule, base, candidates[:mid], options)
    right_ok, right_bad = _confirm(schedule, base, candidates[mid:], options)
    return _join(schedule, base, left_ok, right_ok, left_bad + right_bad, options)


def _join(
    schedule: Schedule,
    base: CpmResult,
    left: list[Relationship],
    right: list[Relationship],
    rejected: list[Relationship],
    options: EngineOptions,
) -> tuple[list[Relationship], list[Relationship]]:
    pooled = left + right
    if _unchanged(schedule, base, pooled, options):
        return pooled, rejected
    confirmed: list[Relationship] = []
    rest = list(rejected)
    for link in pooled:
        trial = [*confirmed, link]
        if _unchanged(schedule, base, trial, options):
            confirmed.append(link)
        else:
            rest.append(link)
    return confirmed, rest


def _unchanged(
    schedule: Schedule,
    base: CpmResult,
    links: list[Relationship],
    options: EngineOptions,
) -> bool:
    drop = {link.task_pred_id for link in links}
    if not _events_stay_covered(schedule, drop):
        return False
    reduced = replace(
        schedule,
        relationships=tuple(
            item for item in schedule.relationships if item.task_pred_id not in drop
        ),
    )
    again = schedule_cpm(reduced, options)
    return _same(base, again)


def _events_stay_covered(schedule: Schedule, drop: set[str | None]) -> bool:
    """Reject a deletion that opens a start or closes off a finish."""
    incoming: dict[str, int] = {}
    outgoing: dict[str, int] = {}
    incoming_left: dict[str, int] = {}
    outgoing_left: dict[str, int] = {}
    for link in schedule.relationships:
        tail, head = _ends(link)
        if tail is None or head is None:
            continue
        outgoing[tail] = outgoing.get(tail, 0) + 1
        incoming[head] = incoming.get(head, 0) + 1
        if link.task_pred_id in drop:
            continue
        outgoing_left[tail] = outgoing_left.get(tail, 0) + 1
        incoming_left[head] = incoming_left.get(head, 0) + 1
    for event, count in incoming.items():
        if count > 0 and incoming_left.get(event, 0) == 0:
            return False
    for event, count in outgoing.items():
        if count > 0 and outgoing_left.get(event, 0) == 0:
            return False
    return True


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
