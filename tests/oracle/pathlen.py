"""Sum of durations along one chain.

This module must not import atlaspmo. It is the second calculation for a
single redundancy example: the long way around is at least the direct lag.
"""

from __future__ import annotations


def alternate_is_long_enough(durations: tuple[int, ...], direct_lag: int) -> bool:
    """True when the chain of durations is at least the direct lag."""
    return sum(durations) >= direct_lag
