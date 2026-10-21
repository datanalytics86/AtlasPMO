"""Float bands follow the edges passed in. Driving chains are not claimed here."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from atlaspmo.analysis.contract import AnalysisContext
from atlaspmo.analysis.paths.mode_a import PathsConfig, PathsModeA, _classify
from atlaspmo.analysis.paths.mode_b import PathsBConfig, PathsModeB
from atlaspmo.analysis.quality.profiles import load_profile
from test_cpm import _link, _load, _task


def test_custom_edges_move_the_same_float(tmp_path: Path) -> None:
    schedule = _load(tmp_path, [_task("1", "A", "8"), _task("2", "B", "8")], [])
    low = replace(schedule.activities[0], total_float_hr_cnt=16)
    high = replace(schedule.activities[1], total_float_hr_cnt=48)
    schedule = replace(schedule, activities=(low, high))
    profile, _note = load_profile("dcma_estricto", hours_per_day=8)
    _rows, counts, _critical = _classify(schedule, profile, [], (0, 5))
    assert counts["0-5"] == 1
    assert counts[">5"] == 1
    _rows, defaults, _critical = _classify(schedule, profile, [])
    assert defaults["0-10"] == 2


def test_mode_a_does_not_trace_a_driving_chain(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8")],
        [_link("1", "1", "2")],
    )
    activities = tuple(replace(item, total_float_hr_cnt=0) for item in schedule.activities)
    schedule = replace(schedule, activities=activities)
    result = PathsModeA().run(AnalysisContext(schedule=schedule), PathsConfig())
    text = " ".join(result.approximations)
    assert "driving no se marcan" in text
    assert list(result.tables["bands"].columns) == [
        "task_code",
        "task_name",
        "float_days",
        "band",
        "critical",
        "path",
    ]


def test_the_longer_predecessor_is_the_driving_one(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "SHORT", "8"), _task("2", "LONG", "16"), _task("3", "JOIN", "8")],
        [_link("1", "1", "3"), _link("2", "2", "3")],
    )
    result = PathsModeB().run(AnalysisContext(schedule=schedule), PathsBConfig())
    rows = result.tables["cpm"].set_index("task_code")
    assert rows.loc["JOIN", "driving_codes"] == "LONG"
    assert set(result.tables["driving_chain"]["task_code"]) == {"LONG", "JOIN"}
    targeted = PathsModeB().run(
        AnalysisContext(schedule=schedule),
        PathsBConfig(milestone_code="JOIN"),
    )
    assert set(targeted.tables["driving_chain"]["task_code"]) == {"LONG", "JOIN"}
