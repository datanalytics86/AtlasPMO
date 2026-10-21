"""The cleaner returns the original bytes when the CPM delta is not zero."""

from __future__ import annotations

from pathlib import Path

from atlaspmo.analysis.logic.clean import clean_document
from atlaspmo.analysis.logic.redundant import LinkClass
from atlaspmo.engine.cpm import schedule_cpm
from atlaspmo.io.xer import read_xer
from test_cpm import _link, _load, _task


def test_clean_keeps_the_file_when_a_confirmed_link_moves_dates(
    tmp_path: Path, monkeypatch
) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8")],
        [_link("1", "1", "2")],
    )
    document = read_xer(tmp_path / "case.xer")

    def _lie(schedule, options=None, contractual_codes=None):
        base = schedule_cpm(schedule, options)
        link = schedule.relationships[0]
        return (LinkClass(link.task_pred_id or "", "redundante_confirmado", "falso"),), base

    monkeypatch.setattr("atlaspmo.analysis.logic.clean.classify_links", _lie)
    cleaned, before, after, removed = clean_document(document, schedule)
    assert removed == 0
    assert cleaned.to_bytes() == document.to_bytes()
    assert before.by_id["2"].early_start != after.by_id["2"].early_start
