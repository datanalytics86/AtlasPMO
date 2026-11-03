"""E9: vectorized Monte Carlo, prange passes, and the successor-cone tornado."""

from __future__ import annotations

import random
from dataclasses import replace
from pathlib import Path

from atlaspmo.analysis.risk.config import DurationRange, RiskConfig, RiskEvent
from atlaspmo.analysis.risk.montecarlo import TRACE, run_risk
from atlaspmo.analysis.risk.sample import sample_duration
from atlaspmo.engine import fast as fast_engine
from atlaspmo.engine.cpm import build_clocks, schedule_cpm
from atlaspmo.engine.options import EngineOptions
from atlaspmo.numeric.batch import batch_passes
from test_cpm import _link, _load, _task


def test_column_matches_sample_duration_and_a_zero_event_advances_rng(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8")],
        [_link("1", "1", "2")],
    )
    config = RiskConfig(
        seed=7,
        iterations=6,
        ranges=[DurationRange(task_code="A", low=2, mode=8, high=20, distribution="uniform")],
        events=[RiskEvent(name="quieto", probability=0, impact_hours=8, task_codes=["A"])],
        tornado_hours=0,
    )
    run_risk(schedule, config)
    rng = random.Random(7)
    expected = [sample_duration(rng, 2, 8, 20, "uniform") for _ in range(6)]
    assert TRACE["columns"]["A"] == expected
    for _ in range(6):
        rng.random()
    assert TRACE["rng_next"] == rng.random()


def test_iterations_do_not_rebuild_the_schedule(tmp_path: Path, monkeypatch) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "16")],
        [_link("1", "1", "2")],
    )

    def boom(*_args, **_kwargs):
        raise AssertionError("rebuild")

    monkeypatch.setattr("atlaspmo.analysis.risk.montecarlo._with_hours", boom)
    before = schedule_cpm(schedule).project_finish
    outcome = run_risk(schedule, RiskConfig(seed=1, iterations=4, tornado_hours=8))
    assert TRACE["passes"] == 4
    assert TRACE["full_cpm"] == 0
    assert batch_passes.targetoptions["parallel"] is True
    assert schedule_cpm(schedule).project_finish == before
    assert outcome.finishes


def test_each_finish_matches_the_reference(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8")],
        [_link("1", "1", "2")],
    )
    config = RiskConfig(
        seed=4,
        iterations=5,
        ranges=[DurationRange(task_code="A", low=8, mode=16, high=40, distribution="uniform")],
        tornado_hours=0,
    )
    outcome = run_risk(schedule, config)
    rng = random.Random(4)
    hours = [sample_duration(rng, 8, 16, 40, "uniform") for _ in range(5)]
    reference = EngineOptions(engine="reference")
    finishes = []
    flags = []
    for value in hours:
        bumped = _hours(schedule, {"A": value})
        result = schedule_cpm(bumped, reference)
        finishes.append(result.project_finish)
        flags.append(
            {
                activity.task_code: result.by_id[activity.task_id].critical
                for activity in bumped.activities
                if activity.task_id in result.by_id and activity.task_code
            }
        )
    assert list(outcome.finishes) == finishes
    assert TRACE["critical"] == flags


def test_tornado_off_visits_nothing(tmp_path: Path) -> None:
    schedule = _load(tmp_path, [_task("1", "A", "8")], [])
    outcome = run_risk(schedule, RiskConfig(seed=1, iterations=2, tornado_hours=0))
    assert outcome.tornado == ()
    assert TRACE["cones"] == {}
    assert TRACE["tornado_visited"] == 0
    text = " ".join(outcome.approximations)
    assert "cronograma completo" not in text
    assert "No recorta al cono" not in text
    assert "numba no se cargó" not in text
    assert "Monte Carlo corre en numba" in text


def test_chain_cones_match_the_reference_delta(tmp_path: Path) -> None:
    codes = ["A", "B", "C", "D", "E"]
    tasks = [_task(str(index + 1), code, "8") for index, code in enumerate(codes)]
    links = [_link(str(index), str(index), str(index + 1)) for index in range(1, 5)]
    schedule = _load(tmp_path, tasks, links)
    outcome = run_risk(schedule, RiskConfig(seed=1, iterations=1, tornado_hours=8))
    assert TRACE["cones"]["E"] == frozenset({"E"})
    assert TRACE["cones"]["A"] == frozenset({"A", "B", "C", "D", "E"})
    assert TRACE["cones"]["C"] == frozenset({"C", "D", "E"})
    assert TRACE["tornado_visited"] == sum(len(item) for item in TRACE["cones"].values())
    reference = EngineOptions(engine="reference")
    got = {item.task_code: item.delta_hours for item in outcome.tornado}
    base = schedule_cpm(schedule, reference)
    clocks, _notes = build_clocks(schedule)
    for code in codes:
        bumped = _hours(schedule, {code: 16})
        finish = schedule_cpm(bumped, reference).project_finish
        assert base.project_finish is not None
        assert finish is not None
        delta = clocks["C1"].work_between(base.project_finish, finish) / 60
        assert got[code] == delta


def test_loe_stays_outside_the_cone(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8"), _task("3", "L", "8", kind="TT_LOE")],
        [_link("1", "1", "2")],
    )
    outcome = run_risk(schedule, RiskConfig(seed=1, iterations=1, tornado_hours=8))
    assert all("L" not in visited for visited in TRACE["cones"].values())
    got = {item.task_code: item.delta_hours for item in outcome.tornado}
    reference = EngineOptions(engine="reference")
    base = schedule_cpm(schedule, reference)
    bumped = _hours(schedule, {"A": 16})
    finish = schedule_cpm(bumped, reference).project_finish
    clocks, _notes = build_clocks(schedule)
    assert base.project_finish is not None
    assert finish is not None
    delta = clocks["C1"].work_between(base.project_finish, finish) / 60
    assert got["A"] == delta
    assert "L" not in got


def test_batch_edges_keep_a_pass_for_each_iteration(tmp_path: Path, monkeypatch) -> None:
    schedule = _load(
        tmp_path,
        [
            _task("1", "A", "8"),
            _task("2", "B", "8"),
            _task("3", "M", "0", "TT_Mile"),
        ],
        [_link("1", "1", "2"), _link("2", "2", "3")],
    )
    outcome = run_risk(
        schedule,
        RiskConfig(
            seed=1,
            iterations=1,
            tornado_hours=0,
            ranges=[DurationRange(task_code="A", low=8, mode=12, high=20, distribution="uniform")],
            events=[RiskEvent(name="b", probability=0, impact_hours=1, task_codes=["B", "M"])],
        ),
    )
    assert len(outcome.finishes) == 1
    assert "B" in TRACE["columns"]
    assert "M" in TRACE["columns"]

    cycled = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8")],
        [_link("1", "1", "2"), _link("2", "2", "1")],
    )
    cycled_out = run_risk(cycled, RiskConfig(seed=1, iterations=1, tornado_hours=8))
    assert cycled_out.tornado == ()

    def mark_reference(schedule, options=None):
        found = fast_engine.cached_compiled(schedule, options)
        fast_engine.LAST["path"] = "reference"
        return found

    monkeypatch.setattr("atlaspmo.analysis.risk.fastloop.cached_compiled", mark_reference)
    try:
        fallback = run_risk(
            schedule,
            RiskConfig(
                seed=1,
                iterations=1,
                tornado_hours=0,
                events=[RiskEvent(name="x", probability=0, impact_hours=1, task_codes=["A"])],
            ),
        )
    finally:
        fast_engine.LAST["path"] = "fast"
    assert TRACE["passes"] == 0
    assert TRACE["full_cpm"] == 1
    assert "no corrió en numba" in " ".join(fallback.approximations)


def test_unsupported_calendar_uses_the_reference_loop(tmp_path: Path, monkeypatch) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8")],
        [_link("1", "1", "2")],
    )
    monkeypatch.setattr(
        "atlaspmo.analysis.risk.fastloop.cached_compiled",
        lambda *_args, **_kwargs: None,
    )
    outcome = run_risk(schedule, RiskConfig(seed=1, iterations=2, tornado_hours=0))
    text = " ".join(outcome.approximations)
    assert TRACE["passes"] == 0
    assert TRACE["full_cpm"] == 2
    assert "no corrió en numba" in text
    assert "Monte Carlo corre en numba" not in text
    assert len(outcome.finishes) == 2


def _hours(schedule, hours: dict[str, float]):
    activities = []
    for activity in schedule.activities:
        value = hours.get(activity.task_code or "")
        if activity.task_code is None or value is None:
            activities.append(activity)
            continue
        activities.append(replace(activity, remain_drtn_hr_cnt=value))
    return replace(schedule, activities=tuple(activities))
