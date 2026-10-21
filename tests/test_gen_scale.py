"""Scale fixtures use documented P6 tables, not the invented SYNTH table."""

from __future__ import annotations

from scripts.gen_scale import build_tables


def test_scale_tables_are_real_p6_names():
    tables = build_tables(5, series=False)
    names = [table["name"] for table in tables]
    assert names == ["PROJECT", "CALENDAR", "PROJWBS", "TASK", "TASKPRED"]
    assert "SYNTH" not in names
    tasks = tables[3]["rows"]
    assert isinstance(tasks, list)
    assert len(tasks) == 5


def test_series_has_one_predecessor_each():
    tables = build_tables(4, series=True)
    preds = tables[4]["rows"]
    assert isinstance(preds, list)
    assert len(preds) == 3
    assert {row[5] for row in preds} == {"PR_FS"}
