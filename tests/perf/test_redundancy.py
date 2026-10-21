"""Scale of the redundant-link filter. Confirmation is a separate measurement.

The filter walks each origin once. Confirming the candidates still reruns
the CPM, and on this generator that cost grows with the number of
candidates. The 30k confirmation budget is reported in docs/qa/E2/perf.md.
It is not asserted here, because a full run does not finish inside the
gate.
"""

from __future__ import annotations

import time

import pytest
from scripts.gen_scale import write_scale

from atlaspmo.analysis.logic.redundant import _candidate_ids
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.xer import read_xer

pytestmark = pytest.mark.perf


def test_candidate_filter_30k_under_15_seconds(tmp_path) -> None:
    path = tmp_path / "scale30k.xer"
    write_scale(path, 30_000, series=False)
    schedule = schedule_from_xer(read_xer(path))
    started = time.perf_counter()
    found = _candidate_ids(schedule)
    elapsed = time.perf_counter() - started
    assert found
    assert elapsed < 15, f"filtro de candidatos 30k: {elapsed:.3f} s"
