"""Duration distributions and Iman-Conover rank correlation.

Ranges are user input. They are not XER columns. A zero-width range returns
the mode and does not draw from the generator.
"""

from __future__ import annotations

import random


def sample_duration(
    rng: random.Random,
    low: float,
    mode: float,
    high: float,
    distribution: str,
) -> float:
    """Draw one duration. Zero width returns `mode` without touching `rng`."""
    if low == mode == high:
        return mode
    if distribution == "uniform":
        return low + rng.random() * (high - low)
    if distribution == "triangular":
        return rng.triangular(low, high, mode)
    if distribution == "beta_pert":
        return _beta_pert(rng, low, mode, high)
    raise ValueError(f"distribución desconocida: {distribution}")


def iman_conover(
    columns: list[list[float]],
    correlation: list[list[float]],
    rng: random.Random,
) -> list[list[float]] | None:
    """Reorder independent columns so their ranks follow `correlation`.

    Returns None when the matrix is not a correlation or Cholesky fails.
    A coefficient of 1 or -1 copies the rank order exactly.
    """
    if not columns:
        return []
    width = len(columns)
    length = len(columns[0])
    if any(len(column) != length for column in columns):
        return None
    if not _valid_correlation(correlation, width):
        return None
    jittered = [list(row) for row in correlation]
    for index in range(width):
        jittered[index][index] += 1e-8
    factor = _cholesky(jittered)
    if factor is None:
        return None
    scores = [[rng.gauss(0.0, 1.0) for _ in range(length)] for _ in range(width)]
    mixed = _mix(scores, factor)
    _force_perfect(mixed, correlation)
    return [_reorder(columns[index], mixed[index]) for index in range(width)]


def _beta_pert(rng: random.Random, low: float, mode: float, high: float) -> float:
    span = high - low
    if span == 0:
        return mode
    alpha = 1 + 4 * (mode - low) / span
    beta = 1 + 4 * (high - mode) / span
    if alpha <= 0 or beta <= 0:
        return mode
    return low + span * rng.betavariate(alpha, beta)


def _valid_correlation(correlation: list[list[float]], width: int) -> bool:
    if len(correlation) != width:
        return False
    for row in correlation:
        if len(row) != width:
            return False
        for value in row:
            if value < -1 or value > 1:
                return False
    return True


def _cholesky(matrix: list[list[float]]) -> list[list[float]] | None:
    size = len(matrix)
    lower = [[0.0] * size for _ in range(size)]
    for row in range(size):
        for col in range(row + 1):
            total = sum(lower[row][key] * lower[col][key] for key in range(col))
            if row == col:
                diagonal = matrix[row][row] - total
                if diagonal <= 1e-12:
                    return None
                lower[row][col] = diagonal**0.5
                continue
            pivot = lower[col][col]
            if pivot == 0:
                return None
            lower[row][col] = (matrix[row][col] - total) / pivot
    return lower


def _mix(scores: list[list[float]], factor: list[list[float]]) -> list[list[float]]:
    width = len(scores)
    length = len(scores[0])
    mixed: list[list[float]] = []
    for column in range(width):
        values: list[float] = []
        for row in range(length):
            values.append(
                sum(scores[source][row] * factor[column][source] for source in range(width))
            )
        mixed.append(values)
    return mixed


def _force_perfect(mixed: list[list[float]], correlation: list[list[float]]) -> None:
    width = len(mixed)
    for left in range(width):
        for right in range(left + 1, width):
            coef = correlation[left][right]
            if coef == 1.0:
                mixed[right] = list(mixed[left])
            elif coef == -1.0:
                mixed[right] = [-item for item in mixed[left]]


def _reorder(values: list[float], scores: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: scores[index])
    ordered = sorted(values)
    placed = [0.0] * len(values)
    for rank, index in enumerate(order):
        placed[index] = ordered[rank]
    return placed
