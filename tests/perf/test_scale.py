"""Section 11 read benchmark. Other criteria stay unmeasured until their stage."""

from __future__ import annotations

import time

import pytest
from scripts.gen_scale import write_scale

from atlaspmo.io.xer import read_xer

pytestmark = pytest.mark.perf


def test_read_30k_realistic_under_15_seconds(tmp_path) -> None:
    path = tmp_path / "scale30k.xer"
    write_scale(path, 30_000, series=False)
    started = time.perf_counter()
    read_xer(path)
    elapsed = time.perf_counter() - started
    assert elapsed < 15, f"lectura 30k realista: {elapsed:.3f} s"
