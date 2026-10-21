"""Invariants b, c and d on small calendared networks."""

from __future__ import annotations

from dataclasses import replace

from hypothesis import given
from hypothesis import strategies as st
from tests.test_cpm import _PRED, _TASK, _link, _task, _week

from atlaspmo.analysis.logic.clean import _same_result, clean_document
from atlaspmo.analysis.logic.redundant import classify_links
from atlaspmo.engine.cpm import schedule_cpm
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.synthetic import encode_xer
from atlaspmo.io.xer import read_xer_bytes

_HOURS = st.sampled_from(("8", "16", "24"))


def _network(tasks: list[list[str]], links: list[list[str]]):
    raw = encode_xer(
        "ERMHDR",
        [
            {
                "name": "PROJECT",
                "fields": ["proj_id", "clndr_id", "last_recalc_date"],
                "rows": [["1", "C1", "2026-01-05 08:00"]],
            },
            {
                "name": "CALENDAR",
                "fields": ["clndr_id", "day_hr_cnt", "clndr_data"],
                "rows": [["C1", "8", _week()]],
            },
            {"name": "TASK", "fields": _TASK, "rows": tasks},
            {"name": "TASKPRED", "fields": _PRED, "rows": links},
        ],
    )
    document = read_xer_bytes(raw)
    return document, schedule_from_xer(document)


@given(hours=_HOURS)
def test_clean_unchanged(hours: str) -> None:
    document, schedule = _network(
        [_task("1", "A", "8"), _task("2", "B", hours), _task("3", "C", "8")],
        [_link("1", "1", "2"), _link("2", "2", "3"), _link("3", "1", "3")],
    )
    cleaned, before, _after, _removed = clean_document(document, schedule)
    again = schedule_cpm(schedule_from_xer(cleaned))
    assert _same_result(before, again)


@given(hours=_HOURS)
def test_implicit_redundant(hours: str) -> None:
    _document, schedule = _network(
        [_task("1", "A", "8"), _task("2", "B", hours), _task("3", "C", "8")],
        [_link("1", "1", "2"), _link("2", "2", "3"), _link("3", "1", "3")],
    )
    classes, _base = classify_links(schedule)
    by_id = {item.task_pred_id: item.status for item in classes}
    assert by_id["3"] == "redundante_confirmado"


@given(hours=_HOURS)
def test_driving_not_redundant(hours: str) -> None:
    _document, schedule = _network(
        [_task("1", "A", hours), _task("2", "B", "8")],
        [_link("1", "1", "2")],
    )
    classes, base = classify_links(schedule)
    assert classes[0].status != "redundante_confirmado"
    reduced = replace(schedule, relationships=())
    again = schedule_cpm(reduced)
    assert again.by_id["2"].early_start != base.by_id["2"].early_start
