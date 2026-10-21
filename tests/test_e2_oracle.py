"""QC-2 slice: one alternate path, added by hand, not by the engine."""

from __future__ import annotations

from tests.oracle.pathlen import alternate_is_long_enough


def test_eight_plus_eight_covers_a_zero_lag() -> None:
    assert alternate_is_long_enough((8, 8), 0)
    assert alternate_is_long_enough((8, 8), 16)
    assert not alternate_is_long_enough((8, 8), 17)
