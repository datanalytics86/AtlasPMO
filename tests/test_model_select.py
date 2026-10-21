"""Branches of Schedule.calendar_for and Schedule.select."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from test_cpm import _link, _load, _task


def test_calendar_lookup_and_project_filter(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8")],
        [_link("1", "1", "2")],
    )
    assert schedule.calendar_for(None) is None
    assert schedule.calendar_for("no-existe") is None
    assert schedule.calendar_for("C1") is not None
    assert schedule.select(None) is schedule
    other = replace(schedule.activities[1], proj_id="2", task_id="2")
    outside = replace(schedule.relationships[0], task_id="9", pred_task_id="8")
    schedule = replace(
        schedule,
        activities=(schedule.activities[0], other),
        relationships=(outside,),
    )
    chosen = schedule.select("1")
    assert [item.task_code for item in chosen.activities] == ["A"]
    assert chosen.relationships == ()
    assert chosen.projects[0].proj_id == "1"
