"""Section 11 targets at full scale, on the realistic gen_scale network.

These tests are excluded from the default suite (marker seccion11). Gate G6
runs only the ones listed in docs/qa/seccion11.toml (ADR-019). A target is
activated by the stage that makes it pass; once active, it can never be
removed. ATLASPMO_S11_SIZE overrides the network size for a smoke run only.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest
from scripts.gen_scale import write_scale

from atlaspmo.analysis.logic.redundant import classify_links
from atlaspmo.analysis.quality.check import evaluate
from atlaspmo.analysis.quality.profiles import load_profile
from atlaspmo.analysis.risk.config import RiskConfig
from atlaspmo.analysis.risk.montecarlo import run_risk
from atlaspmo.engine.cpm import schedule_cpm
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.xer import read_xer
from atlaspmo.model.schedule import Schedule

pytestmark = pytest.mark.seccion11

SIZE = int(os.environ.get("ATLASPMO_S11_SIZE", "30000"))
FULL = SIZE == 30_000


def _scale(tmp_path: Path) -> Path:
    path = tmp_path / f"scale{SIZE}.xer"
    write_scale(path, SIZE, series=False)
    return path


def _schedule(tmp_path: Path) -> Schedule:
    return schedule_from_xer(read_xer(_scale(tmp_path)))


def _report(name: str, elapsed: float, limit: float) -> None:
    print(f"S11 {name} n={SIZE} {elapsed:.3f}s limite={limit}s")
    if FULL:
        assert elapsed < limit, f"{name}: {elapsed:.3f} s >= {limit} s"


def test_s11_lectura_30k(tmp_path: Path) -> None:
    path = _scale(tmp_path)
    started = time.perf_counter()
    schedule = schedule_from_xer(read_xer(path))
    _report("lectura_30k", time.perf_counter() - started, 15)
    assert schedule.activities


def test_s11_cpm_30k(tmp_path: Path) -> None:
    schedule = _schedule(tmp_path)
    schedule_cpm(schedule)  # warm-up: JIT compilation and caches are not the target
    started = time.perf_counter()
    result = schedule_cpm(schedule)
    _report("cpm_30k", time.perf_counter() - started, 0.5)
    assert result.by_id


def test_s11_dcma_30k(tmp_path: Path) -> None:
    schedule = _schedule(tmp_path)
    profile, _note = load_profile("dcma_estricto")
    started = time.perf_counter()
    schedule_cpm(schedule)
    metrics, _frame, _notes = evaluate(schedule, profile, None)
    _report("dcma_30k", time.perf_counter() - started, 10)
    assert "logic" in metrics


def test_s11_redundancia_30k(tmp_path: Path) -> None:
    schedule = _schedule(tmp_path)
    started = time.perf_counter()
    classes, base = classify_links(schedule)
    _report("redundancia_30k", time.perf_counter() - started, 180)
    assert base.by_id
    assert classes


def test_s11_montecarlo_30k(tmp_path: Path) -> None:
    schedule = _schedule(tmp_path)
    iterations = 1000 if FULL else 5
    started = time.perf_counter()
    outcome = run_risk(schedule, RiskConfig(seed=1, iterations=iterations, tornado_hours=0))
    _report("montecarlo_30k", time.perf_counter() - started, 300)
    assert len(outcome.finishes) == iterations
