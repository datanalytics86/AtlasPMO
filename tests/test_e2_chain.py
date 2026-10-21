"""A plain FS chain has no confirmed redundant link."""

from __future__ import annotations

from pathlib import Path

from atlaspmo.analysis.logic.redundant import classify_links
from test_cpm import _link, _load, _task


def test_fs_chain_of_four_has_no_confirmed_redundancy(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [
            _task("1", "A", "8"),
            _task("2", "B", "8"),
            _task("3", "C", "8"),
            _task("4", "D", "8"),
        ],
        [_link("1", "1", "2"), _link("2", "2", "3"), _link("3", "3", "4")],
    )
    classes, _base = classify_links(schedule)
    assert all(item.status != "redundante_confirmado" for item in classes)
