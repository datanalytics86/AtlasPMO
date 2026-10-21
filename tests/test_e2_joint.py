"""Two links that are redundant only because of each other stay jointly safe."""

from __future__ import annotations

from pathlib import Path

from atlaspmo.analysis.logic.clean import clean_document
from atlaspmo.analysis.logic.redundant import classify_links
from atlaspmo.io.xer import read_xer
from test_cpm import _link, _load, _task


def test_mutual_pair_is_not_confirmed_together(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8")],
        [_link("1", "1", "2"), _link("2", "1", "2")],
    )
    classes, _base = classify_links(schedule)
    confirmed = [item.task_pred_id for item in classes if item.status == "redundante_confirmado"]
    assert len(confirmed) == 1
    document = read_xer(tmp_path / "case.xer")
    cleaned, before, after, removed = clean_document(document, schedule)
    assert removed == 1
    assert before.project_finish == after.project_finish
    assert cleaned.to_bytes().count(b"%R\t") == document.to_bytes().count(b"%R\t") - 1
