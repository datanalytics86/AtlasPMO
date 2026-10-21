"""B-14: the structural generator no longer emits the invented SYNTH table."""

from __future__ import annotations

from scripts.gen_synthetic import MINIMAL_TABLES


def test_generator_tables_are_documented_p6_names() -> None:
    names = [str(table["name"]) for table in MINIMAL_TABLES]
    assert "SYNTH" not in names
    assert names == ["PROJECT", "CALENDAR", "TASK", "TASKPRED"]
    fields = {str(table["name"]): table["fields"] for table in MINIMAL_TABLES}
    assert "task_code" in fields["TASK"]
    assert "col_a" not in fields["TASK"]
