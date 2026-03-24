"""
Early stopping for repeated rating distributions per (company, model) layer.

Uses max absolute bin difference and Jensen–Shannon divergence on 5 rating labels.

Rule (default): after each new repetition r >= 2, compare hist[r-1] vs hist[r].
If this comparison is "stable" (both metrics below thresholds), increment streak.
If streak >= consecutive_stable_pairs AND r >= min_rep_to_check, stop before r+1.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Iterable

from bq_rating_prompt_schema import CANONICAL_RATINGS


def rating_histogram(ratings: Iterable[str]) -> dict[str, int]:
    c: Counter[str] = Counter()
    for r in ratings:
        if r in CANONICAL_RATINGS:
            c[r] += 1
    return dict(c)


def _probs(hist: dict[str, int], labels: tuple[str, ...]) -> list[float]:
    total = sum(hist.get(l, 0) for l in labels)
    if total <= 0:
        return [1.0 / len(labels)] * len(labels)
    return [hist.get(l, 0) / total for l in labels]


def max_abs_bin_diff(h1: dict[str, int], h2: dict[str, int]) -> float:
    labels = CANONICAL_RATINGS
    p = _probs(h1, labels)
    q = _probs(h2, labels)
    return max(abs(p[i] - q[i]) for i in range(len(labels)))


def js_divergence(h1: dict[str, int], h2: dict[str, int], eps: float = 1e-12) -> float:
    """Jensen–Shannon divergence (base 2), symmetric, bounded [0, 1]."""
    labels = CANONICAL_RATINGS
    p = _probs(h1, labels)
    q = _probs(h2, labels)
    m = [(p[i] + q[i]) / 2.0 for i in range(len(labels))]

    def kl(a: list[float], b: list[float]) -> float:
        s = 0.0
        for i in range(len(a)):
            ai = max(a[i], eps)
            bi = max(b[i], eps)
            s += ai * math.log2(ai / bi)
        return s

    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def pair_is_stable(
    h_prev: dict[str, int],
    h_curr: dict[str, int],
    *,
    max_abs_bin_diff_threshold: float,
    js_threshold: float,
) -> bool:
    return (
        max_abs_bin_diff(h_prev, h_curr) < max_abs_bin_diff_threshold
        and js_divergence(h_prev, h_curr) < js_threshold
    )


def should_stop_layer(
    hist_by_rep: dict[int, dict[str, int]],
    *,
    min_rep_to_check: int,
    max_abs_bin_diff_threshold: float,
    js_threshold: float,
    consecutive_stable_pairs: int,
) -> bool:
    """
    Call after completing repetition `max_r`, with histograms for reps 1..max_r.

    Walk r = 2..max_r comparing hist[r-1] vs hist[r]. Count consecutive stable
    comparisons. Stop if streak >= consecutive_stable_pairs and max_r >= min_rep_to_check.
    """
    if not hist_by_rep:
        return False
    max_r = max(hist_by_rep.keys())
    if max_r < min_rep_to_check:
        return False

    streak = 0
    for r in range(2, max_r + 1):
        if r < min_rep_to_check:
            continue
        if r - 1 not in hist_by_rep or r not in hist_by_rep:
            continue
        stable = pair_is_stable(
            hist_by_rep[r - 1],
            hist_by_rep[r],
            max_abs_bin_diff_threshold=max_abs_bin_diff_threshold,
            js_threshold=js_threshold,
        )
        if stable:
            streak += 1
            if streak >= consecutive_stable_pairs:
                return True
        else:
            streak = 0
    return False
