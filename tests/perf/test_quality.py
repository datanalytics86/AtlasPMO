"""DCMA on a realistic 30k network. The clock covers evaluate only."""

from __future__ import annotations

import time

import pytest
from scripts.gen_scale import write_scale

from atlaspmo.analysis.quality.check import evaluate
from atlaspmo.analysis.quality.profiles import load_profile
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.xer import read_xer

pytestmark = pytest.mark.perf


def test_dcma_30k_under_10_seconds(tmp_path) -> None:
    path = tmp_path / "scale30k.xer"
    write_scale(path, 30_000, series=False)
    schedule = schedule_from_xer(read_xer(path))
    profile, _note = load_profile("dcma_estricto")
    started = time.perf_counter()
    metrics, _frame, _notes = evaluate(schedule, profile, None)
    elapsed = time.perf_counter() - started
    assert "logic" in metrics
    assert elapsed < 10, f"DCMA 30k: {elapsed:.3f} s"
