"""Protections: contractual list, external links. Milestones are not all protected."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from atlaspmo.analysis.logic.redundant import classify_links
from test_cpm import _link, _load, _task


def test_a_milestone_is_protected_only_when_its_code_is_listed(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "H", "0", "TT_Mile")],
        [_link("1", "1", "2")],
    )
    open_classes, _base = classify_links(schedule)
    assert open_classes[0].status != "protegido"
    listed, _base = classify_links(schedule, contractual_codes=frozenset({"H"}))
    assert listed[0].status == "protegido"
    assert listed[0].reason == "Entra o sale de un hito contractual."


def test_external_link_is_protected(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8")],
        [_link("1", "1", "2")],
    )
    link = schedule.relationships[0]
    external = replace(link, pred_proj_id="9")
    schedule = replace(schedule, relationships=(external,))
    classes, _base = classify_links(schedule)
    assert classes[0].status == "protegido"
    assert classes[0].reason == "Vínculo entre proyectos."
