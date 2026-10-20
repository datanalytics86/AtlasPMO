"""Hand checks for distributions, zero-variance Monte Carlo and the tornado."""

import random
from dataclasses import replace

from atlaspmo.analysis.contract import AnalysisContext
from atlaspmo.analysis.risk.config import CorrelationPair, DurationRange, RiskConfig, RiskEvent
from atlaspmo.analysis.risk.module import RiskModule
from atlaspmo.analysis.risk.montecarlo import run_risk
from atlaspmo.analysis.risk.sample import iman_conover, sample_duration
from atlaspmo.engine.cpm import schedule_cpm
from test_cpm import THU_16, TUE_16, WED_16, _link, _load, _task

_NUMBA = "Monte Carlo en Python puro. numba no se cargó en esta fase."


def test_zero_width_returns_mode_without_drawing():
    rng = random.Random(1)
    probe = random.Random(1)
    expected = probe.random()
    assert sample_duration(rng, 5, 5, 5, "beta_pert") == 5
    assert sample_duration(rng, 5, 5, 5, "uniform") == 5
    assert sample_duration(rng, 5, 5, 5, "triangular") == 5
    assert rng.random() == expected


def test_samples_stay_inside_the_range_and_repeat_with_the_seed():
    first = _draw(7)
    assert first == _draw(7)
    assert first != _draw(8)
    for kind in ("uniform", "triangular", "beta_pert"):
        rng = random.Random(4)
        for _ in range(40):
            value = sample_duration(rng, 2, 5, 9, kind)
            assert 2 <= value <= 9


def test_perfect_correlation_matches_ranks():
    rng = random.Random(3)
    left = [rng.random() for _ in range(25)]
    right = [rng.random() for _ in range(25)]
    perfect = iman_conover([left, right], [[1.0, 1.0], [1.0, 1.0]], random.Random(9))
    opposite = iman_conover([list(left), list(right)], [[1.0, -1.0], [-1.0, 1.0]], random.Random(9))
    assert perfect is not None and opposite is not None
    assert _order(perfect[0]) == _order(perfect[1])
    assert _order(opposite[1]) == list(reversed(_order(opposite[0])))
    rejected = iman_conover(
        [[1.0, 2.0], [3.0, 4.0]],
        [[1.0, 2.0], [2.0, 1.0]],
        random.Random(1),
    )
    assert rejected is None


def test_zero_variance_reproduces_the_cpm(tmp_path):
    schedule = replace(
        _load(
            tmp_path,
            [_task("A", "A", "8"), _task("B", "B", "16")],
            [_link("1", "A", "B")],
        ),
        parse_notes=("nota de carga visible",),
    )
    base = schedule_cpm(schedule)
    config = RiskConfig(
        seed=11,
        iterations=5,
        ranges=[
            DurationRange(task_code="A", low=8, mode=8, high=8),
            DurationRange(task_code="B", low=16, mode=16, high=16),
        ],
        events=[RiskEvent(name="quieto", probability=0, impact_hours=8, task_codes=["A"])],
        tornado_hours=8,
    )
    outcome = run_risk(schedule, config)
    assert base.project_finish == WED_16
    assert outcome.finishes == (WED_16,) * 5
    by_code = {item.task_code: item for item in outcome.activities}
    assert by_code["A"].criticality == 1
    assert by_code["B"].criticality == 1
    assert by_code["A"].ssi is None
    assert outcome.ssi_status == "no_evaluable"
    assert outcome.sensitivity_status == "no_evaluable"
    assert _NUMBA in outcome.approximations
    assert any("ceil(p * n) - 1" in note for note in outcome.approximations)
    assert "nota de carga visible" in outcome.approximations
    tornado = {item.task_code: item.delta_hours for item in outcome.tornado}
    assert tornado["A"] == 8
    assert tornado["B"] == 8
    project = next(item for item in outcome.milestones if item.task_code == "proyecto")
    assert project.p50 == project.p80 == project.p90 == WED_16
    result = RiskModule().run(AnalysisContext(schedule=schedule), config)
    assert result.metadata.seed == 11
    assert list(result.tables["finishes"]["cumulative"])[-1] == 1


def test_certain_event_moves_the_finish(tmp_path):
    schedule = _load(
        tmp_path,
        [_task("A", "A", "8"), _task("B", "B", "16")],
        [_link("1", "A", "B")],
    )
    config = RiskConfig(
        seed=3,
        iterations=4,
        ranges=[
            DurationRange(task_code="A", low=8, mode=8, high=8),
            DurationRange(task_code="B", low=16, mode=16, high=16),
        ],
        events=[RiskEvent(name="golpe", probability=1, impact_hours=8, task_codes=["A"])],
    )
    outcome = run_risk(schedule, config)
    assert outcome.finishes == (THU_16,) * 4


def test_float_absorbs_an_eight_hour_delay(tmp_path):
    schedule = _load(
        tmp_path,
        [_task("A", "A", "8"), _task("B", "B", "8"), _task("C", "C", "24")],
        [_link("1", "A", "B"), _link("2", "A", "C")],
    )
    outcome = run_risk(schedule, RiskConfig(seed=1, iterations=2, tornado_hours=8))
    tornado = {item.task_code: item.delta_hours for item in outcome.tornado}
    assert tornado["A"] == 8
    assert tornado["B"] == 0
    assert tornado["C"] == 8


def test_join_with_zero_variance_keeps_the_deterministic_finish(tmp_path):
    schedule = _load(
        tmp_path,
        [_task("A", "A", "8"), _task("B", "B", "8"), _task("C", "C", "8")],
        [_link("1", "A", "C"), _link("2", "B", "C")],
    )
    outcome = run_risk(
        schedule,
        RiskConfig(
            seed=1,
            iterations=3,
            ranges=[
                DurationRange(task_code="A", low=8, mode=8, high=8),
                DurationRange(task_code="B", low=8, mode=8, high=8),
                DurationRange(task_code="C", low=8, mode=8, high=8),
            ],
        ),
    )
    row = next(item for item in outcome.convergence if item.task_code == "C")
    assert row.deterministic_finish == row.p50_finish == TUE_16


def test_wide_ranges_publish_sensitivity(tmp_path):
    schedule = _load(
        tmp_path,
        [_task("A", "A", "8"), _task("B", "B", "16")],
        [_link("1", "A", "B")],
    )
    outcome = run_risk(
        schedule,
        RiskConfig(
            seed=2,
            iterations=20,
            ranges=[
                DurationRange(task_code="A", low=8, mode=16, high=40, distribution="uniform"),
                DurationRange(task_code="B", low=16, mode=16, high=16),
            ],
        ),
    )
    row = next(item for item in outcome.activities if item.task_code == "A")
    assert outcome.ssi_status == "info"
    assert outcome.sensitivity_status == "info"
    assert row.ssi is not None and abs(row.ssi - 1) < 0.05
    assert row.spearman is not None and row.spearman > 0.95
    assert row.cruciality is not None and row.cruciality > 0.95


def test_invalid_correlation_is_skipped(tmp_path):
    schedule = _load(tmp_path, [_task("A", "A", "8"), _task("B", "B", "8")], [_link("1", "A", "B")])
    outcome = run_risk(
        schedule,
        RiskConfig(
            seed=1,
            iterations=4,
            ranges=[
                DurationRange(task_code="A", low=8, mode=12, high=24, distribution="uniform"),
                DurationRange(task_code="B", low=8, mode=12, high=24, distribution="uniform"),
            ],
            correlations=[CorrelationPair(left="A", right="B", coefficient=2)],
        ),
    )
    assert len(outcome.finishes) == 4
    assert any("no admite Cholesky" in note for note in outcome.approximations)


def _draw(seed: int) -> list[float]:
    rng = random.Random(seed)
    return [sample_duration(rng, 1, 3, 8, "beta_pert") for _ in range(10)]


def _order(values: list[float]) -> list[int]:
    return sorted(range(len(values)), key=lambda index: values[index])
