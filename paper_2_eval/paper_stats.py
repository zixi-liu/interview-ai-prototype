"""
Formal statistical tests for the paper:
"Scale Collapse, Model Disagreement, and False Precision"

Computes:
  1. Friedman test — do models give significantly different ratings?
  2. Kendall's W — inter-model concordance
  3. ICC (Intraclass Correlation) — test-retest reliability
  4. Krippendorff's alpha — inter-rater reliability (ordinal)
  5. Scale utilization statistics — formal quantification of collapse
  6. Wilcoxon signed-rank — flagship vs lightweight tier comparison

Run:
    python paper_2_eval/paper_stats.py [rows.jsonl] [-o output_dir]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

RATING_ORDER = (
    "No Hire",
    "Leaning No Hire",
    "Leaning Hire",
    "Hire",
    "Strong Hire",
)
RATING_TO_SCORE = {r: float(i + 1) for i, r in enumerate(RATING_ORDER)}

FLAGSHIP_MODELS = {"gpt-5.4-pro", "claude-opus-4-6", "gemini/gemini-3.1-pro-preview"}


def load_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


# ---------------------------------------------------------------------------
# 1. Friedman test (non-parametric repeated measures across models)
# ---------------------------------------------------------------------------

def _rank_within_block(values: list[float]) -> list[float]:
    """Assign average ranks within a block (handles ties)."""
    n = len(values)
    indexed = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n
    pos = 0
    while pos < n:
        start = pos
        val = values[indexed[pos]]
        while pos < n and values[indexed[pos]] == val:
            pos += 1
        avg_rank = (start + pos + 1) / 2.0
        for k in range(start, pos):
            ranks[indexed[k]] = avg_rank
    return ranks


def friedman_test(data_matrix: list[list[float]]) -> dict[str, float]:
    """
    Friedman test for k related samples.

    data_matrix: list of blocks, each block is a list of k treatments.
    Returns: chi2 statistic, approximate p-value, k, n.
    """
    n = len(data_matrix)
    if n < 2:
        return {"chi2": float("nan"), "p_value": float("nan"), "n": n, "k": 0}

    k = len(data_matrix[0])
    if k < 2:
        return {"chi2": float("nan"), "p_value": float("nan"), "n": n, "k": k}

    rank_sums = [0.0] * k
    for block in data_matrix:
        ranks = _rank_within_block(block)
        for j in range(k):
            rank_sums[j] += ranks[j]

    mean_rank = n * (k + 1) / 2.0
    ss = sum((rs - mean_rank) ** 2 for rs in rank_sums)
    chi2 = (12.0 / (n * k * (k + 1))) * ss

    # Approximate p-value via chi-squared distribution with k-1 df
    # Using Wilson-Hilferty approximation for chi2 CDF
    df = k - 1
    p_value = _chi2_survival(chi2, df)

    return {
        "chi2": round(chi2, 4),
        "p_value": round(p_value, 6),
        "n_blocks": n,
        "k_treatments": k,
        "mean_ranks": [round(rs / n, 4) for rs in rank_sums],
    }


def _chi2_survival(x: float, df: int) -> float:
    """Approximate upper-tail probability of chi-squared distribution."""
    if df <= 0 or x <= 0:
        return 1.0
    # Wilson-Hilferty normal approximation
    z = ((x / df) ** (1 / 3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
    return _normal_survival(z)


def _normal_survival(z: float) -> float:
    """Approximate P(Z > z) for standard normal using Abramowitz & Stegun."""
    if z < -8:
        return 1.0
    if z > 8:
        return 0.0
    t = 1.0 / (1.0 + 0.2316419 * abs(z))
    d = 0.3989422804014327  # 1/sqrt(2*pi)
    p = d * math.exp(-z * z / 2.0) * (
        t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
    )
    return p if z > 0 else 1.0 - p


# ---------------------------------------------------------------------------
# 2. Kendall's W (coefficient of concordance)
# ---------------------------------------------------------------------------

def kendalls_w(data_matrix: list[list[float]]) -> dict[str, float]:
    """
    Kendall's W for k raters ranking n items.

    data_matrix: list of n items, each with k rater scores.
    Returns W, chi2, p-value.
    """
    n = len(data_matrix)
    if n < 2:
        return {"W": float("nan"), "chi2": float("nan"), "p_value": float("nan")}

    k = len(data_matrix[0])
    if k < 2:
        return {"W": float("nan"), "chi2": float("nan"), "p_value": float("nan")}

    rank_sums = [0.0] * n
    for j in range(k):
        col = [data_matrix[i][j] for i in range(n)]
        ranks = _rank_within_block(col)
        for i in range(n):
            rank_sums[i] += ranks[i]

    mean_R = sum(rank_sums) / n
    S = sum((r - mean_R) ** 2 for r in rank_sums)

    W = (12.0 * S) / (k ** 2 * (n ** 3 - n))
    chi2 = k * (n - 1) * W
    p_value = _chi2_survival(chi2, n - 1)

    return {
        "W": round(W, 4),
        "chi2": round(chi2, 4),
        "p_value": round(p_value, 6),
        "n_items": n,
        "k_raters": k,
    }


# ---------------------------------------------------------------------------
# 3. ICC (Intraclass Correlation Coefficient) — two-way random, single measures
# ---------------------------------------------------------------------------

def icc_two_way_random(scores_by_subject: list[list[float]]) -> dict[str, float]:
    """
    ICC(2,1) — two-way random effects, absolute agreement, single measures.

    scores_by_subject: list of subjects, each with k repeated measurements.
    Handles unbalanced data by using the minimum common count.
    """
    if not scores_by_subject or not scores_by_subject[0]:
        return {"ICC": float("nan"), "n": 0, "k": 0}

    k = min(len(s) for s in scores_by_subject)
    n = len(scores_by_subject)

    if n < 2 or k < 2:
        return {"ICC": float("nan"), "n": n, "k": k}

    trimmed = [s[:k] for s in scores_by_subject]

    grand_mean = sum(x for row in trimmed for x in row) / (n * k)

    ss_between = k * sum((statistics.mean(row) - grand_mean) ** 2 for row in trimmed)

    col_means = [statistics.mean(trimmed[i][j] for i in range(n)) for j in range(k)]
    ss_within_cols = n * sum((cm - grand_mean) ** 2 for cm in col_means)

    ss_total = sum((x - grand_mean) ** 2 for row in trimmed for x in row)
    ss_error = ss_total - ss_between - ss_within_cols

    ms_between = ss_between / (n - 1) if n > 1 else 0
    ms_within_cols = ss_within_cols / (k - 1) if k > 1 else 0
    df_error = (n - 1) * (k - 1)
    ms_error = ss_error / df_error if df_error > 0 else 0

    numerator = ms_between - ms_error
    denominator = ms_between + (k - 1) * ms_error + (k / n) * (ms_within_cols - ms_error)

    icc_val = numerator / denominator if denominator != 0 else float("nan")

    return {
        "ICC_2_1": round(icc_val, 4),
        "n_subjects": n,
        "k_raters": k,
        "MS_between": round(ms_between, 4),
        "MS_error": round(ms_error, 4),
    }


# ---------------------------------------------------------------------------
# 4. Krippendorff's alpha (ordinal)
# ---------------------------------------------------------------------------

def krippendorff_alpha_ordinal(
    units: list[list[float | None]],
) -> dict[str, float]:
    """
    Krippendorff's alpha for ordinal data.

    units: list of units (items), each with values from multiple coders.
           None means missing.
    """
    all_vals = sorted({v for u in units for v in u if v is not None})
    if len(all_vals) < 2:
        return {"alpha": float("nan"), "n_units": len(units)}

    val_to_rank = {v: i for i, v in enumerate(all_vals)}
    n_vals = len(all_vals)

    def ordinal_delta_sq(c: int, k: int) -> float:
        """Ordinal difference function between ranks c and k."""
        if c == k:
            return 0.0
        lo, hi = min(c, k), max(c, k)
        # Cumulative frequency approach for ordinal metric
        return float((hi - lo) ** 2)

    # Observed disagreement
    Do = 0.0
    total_pairs_observed = 0
    all_values_flat: list[float] = []

    for unit in units:
        vals = [v for v in unit if v is not None]
        if len(vals) < 2:
            continue
        m_u = len(vals)
        all_values_flat.extend(vals)
        for i in range(m_u):
            for j in range(i + 1, m_u):
                ri = val_to_rank[vals[i]]
                rj = val_to_rank[vals[j]]
                Do += ordinal_delta_sq(ri, rj)
                total_pairs_observed += 1

    if total_pairs_observed == 0:
        return {"alpha": float("nan"), "n_units": len(units)}

    Do /= total_pairs_observed

    # Expected disagreement
    n_total = len(all_values_flat)
    freq = defaultdict(int)
    for v in all_values_flat:
        freq[val_to_rank[v]] += 1

    De = 0.0
    total_pairs_expected = 0
    for c in range(n_vals):
        for k in range(c + 1, n_vals):
            De += freq[c] * freq[k] * ordinal_delta_sq(c, k)
            total_pairs_expected += freq[c] * freq[k]

    if total_pairs_expected == 0:
        return {"alpha": float("nan"), "n_units": len(units)}

    De /= total_pairs_expected

    alpha = 1.0 - (Do / De) if De > 0 else float("nan")

    return {
        "alpha": round(alpha, 4),
        "Do": round(Do, 4),
        "De": round(De, 4),
        "n_units": len(units),
        "n_coders_total_values": n_total,
    }


# ---------------------------------------------------------------------------
# 5. Scale utilization statistics
# ---------------------------------------------------------------------------

def scale_utilization_stats(rows: list[dict]) -> dict[str, Any]:
    """Formal quantification of scale collapse."""
    rating_counts = defaultdict(int)
    total = 0
    for r in rows:
        rat = r.get("rating", "").strip()
        if rat in RATING_TO_SCORE:
            rating_counts[rat] += 1
            total += 1

    if total == 0:
        return {}

    dist = {rat: rating_counts.get(rat, 0) / total for rat in RATING_ORDER}
    bins_used = sum(1 for rat in RATING_ORDER if rating_counts.get(rat, 0) > 0)

    # Effective number of categories (exp of entropy)
    entropy = 0.0
    for p in dist.values():
        if p > 0:
            entropy -= p * math.log(p)
    effective_categories = math.exp(entropy)

    # Gini-Simpson diversity index
    gini_simpson = 1.0 - sum(p ** 2 for p in dist.values())

    return {
        "total_ratings": total,
        "bins_used": bins_used,
        "distribution": {k: round(v, 4) for k, v in dist.items()},
        "entropy_nats": round(entropy, 4),
        "effective_categories": round(effective_categories, 4),
        "gini_simpson_diversity": round(gini_simpson, 4),
        "max_possible_entropy": round(math.log(5), 4),
        "normalized_entropy": round(entropy / math.log(5), 4) if math.log(5) > 0 else 0,
    }


# ---------------------------------------------------------------------------
# 6. Wilcoxon signed-rank test — flagship vs lightweight tier
# ---------------------------------------------------------------------------

def wilcoxon_signed_rank(x: list[float], y: list[float]) -> dict[str, float]:
    """
    Wilcoxon signed-rank test for paired samples.
    Tests H0: median difference = 0.
    """
    if len(x) != len(y):
        return {"W": float("nan"), "p_value": float("nan")}

    diffs = [(xi - yi) for xi, yi in zip(x, y) if xi != yi]
    n = len(diffs)

    if n < 5:
        return {
            "W": float("nan"),
            "p_value": float("nan"),
            "n_pairs": len(x),
            "n_nonzero": n,
            "note": "Too few non-zero differences for reliable test",
        }

    abs_diffs = [abs(d) for d in diffs]
    ranked = _rank_within_block(abs_diffs)

    W_plus = sum(r for d, r in zip(diffs, ranked) if d > 0)
    W_minus = sum(r for d, r in zip(diffs, ranked) if d < 0)
    W = min(W_plus, W_minus)

    # Normal approximation for large n
    mean_W = n * (n + 1) / 4.0
    std_W = math.sqrt(n * (n + 1) * (2 * n + 1) / 24.0)

    if std_W == 0:
        z = 0.0
    else:
        z = (W - mean_W) / std_W

    p_value = 2 * _normal_survival(abs(z))

    return {
        "W": round(W, 4),
        "W_plus": round(W_plus, 4),
        "W_minus": round(W_minus, 4),
        "z": round(z, 4),
        "p_value": round(p_value, 6),
        "n_pairs": len(x),
        "n_nonzero_diffs": n,
        "mean_x": round(statistics.mean(x), 4),
        "mean_y": round(statistics.mean(y), 4),
        "mean_diff": round(statistics.mean(xi - yi for xi, yi in zip(x, y)), 4),
    }


# ---------------------------------------------------------------------------
# Orchestration: build all test inputs from raw rows
# ---------------------------------------------------------------------------

def _build_question_model_matrix(
    rows: list[dict],
    company: str = "Google",
    level: str = "senior",
) -> tuple[list[str], list[str], list[list[float]]]:
    """
    Build a questions x models matrix of expected scores.
    Returns (questions, models, matrix) where matrix[q_idx][m_idx] = expected score.
    """
    cell_scores: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in rows:
        if not r.get("ok") or not r.get("rating"):
            continue
        if r.get("company", "").strip() != company:
            continue
        if r.get("level", "").strip().lower() != level.lower():
            continue
        q = r["question"].strip()
        m = r["model_name"].strip()
        score = RATING_TO_SCORE.get(r["rating"].strip())
        if score is not None:
            cell_scores[(q, m)].append(score)

    questions_set = sorted({q for q, _ in cell_scores})
    models_set = sorted({m for _, m in cell_scores})

    # Only keep models that have data for all questions
    complete_models = []
    for m in models_set:
        if all((q, m) in cell_scores for q in questions_set):
            complete_models.append(m)

    matrix = []
    for q in questions_set:
        row = []
        for m in complete_models:
            scores = cell_scores[(q, m)]
            row.append(statistics.mean(scores))
        matrix.append(row)

    return questions_set, complete_models, matrix


def _build_retest_groups(rows: list[dict]) -> dict[str, list[list[float]]]:
    """
    Group ratings by (question, company, level, model, sample_id, run_id)
    for ICC computation. Returns {model: [[scores_subject_1], [scores_subject_2], ...]}.
    """
    groups: dict[tuple, list[float]] = defaultdict(list)
    for r in rows:
        if not r.get("ok") or not r.get("rating"):
            continue
        q = r.get("question", "").strip()
        c = r.get("company", "").strip()
        lvl = r.get("level", "").strip().lower()
        m = r.get("model_name", "").strip()
        sid = r.get("sample_id")
        rid = r.get("run_id", "")
        score = RATING_TO_SCORE.get(r["rating"].strip())
        if score is not None:
            groups[(q, c, lvl, m, sid, rid)].append(score)

    by_model: dict[str, list[list[float]]] = defaultdict(list)
    for key, scores in groups.items():
        if len(scores) >= 2:
            m = key[3]
            by_model[m].append(scores)

    return dict(by_model)


def _build_tier_comparison(
    rows: list[dict],
) -> tuple[list[float], list[float], list[str]]:
    """Build paired flagship vs lightweight expected scores per question."""
    cell_scores: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in rows:
        if not r.get("ok") or not r.get("rating"):
            continue
        q = r["question"].strip()
        m = r["model_name"].strip()
        score = RATING_TO_SCORE.get(r["rating"].strip())
        if score is not None:
            cell_scores[(q, m)].append(score)

    questions = sorted({q for q, _ in cell_scores})

    flagship_scores = []
    lightweight_scores = []
    matched_questions = []

    for q in questions:
        f_vals = []
        l_vals = []
        for (qq, m), scores in cell_scores.items():
            if qq != q:
                continue
            if m in FLAGSHIP_MODELS:
                f_vals.extend(scores)
            else:
                l_vals.extend(scores)
        if f_vals and l_vals:
            flagship_scores.append(statistics.mean(f_vals))
            lightweight_scores.append(statistics.mean(l_vals))
            matched_questions.append(q)

    return flagship_scores, lightweight_scores, matched_questions


def run_all_tests(rows: list[dict], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, Any] = {}

    # --- Scale utilization ---
    print("Computing scale utilization statistics...")
    ok_rows = [r for r in rows if r.get("ok") and r.get("rating")]
    results["scale_utilization"] = scale_utilization_stats(ok_rows)

    # --- Friedman test & Kendall's W (Google Senior slice) ---
    print("Computing Friedman test & Kendall's W...")
    questions, models, matrix = _build_question_model_matrix(rows, "Google", "senior")

    if matrix and matrix[0]:
        results["friedman_test"] = {
            "description": "Friedman test: do models give significantly different ratings? (Google Senior)",
            "questions": questions,
            "models": models,
            **friedman_test(matrix),
        }

        # For Kendall's W: transpose matrix (models as items, questions as raters)
        transposed = [[matrix[q][m] for q in range(len(questions))] for m in range(len(models))]
        results["kendalls_w"] = {
            "description": "Kendall's W: inter-model concordance on question ranking (Google Senior)",
            "models": models,
            **kendalls_w(matrix),
        }

    # --- ICC for test-retest ---
    print("Computing ICC for test-retest reliability...")
    retest_groups = _build_retest_groups(rows)
    icc_results = {}
    for model, subject_scores in sorted(retest_groups.items()):
        if len(subject_scores) >= 3:
            icc_results[model] = icc_two_way_random(subject_scores)
    results["icc_test_retest"] = {
        "description": "ICC(2,1) test-retest reliability per model",
        "per_model": icc_results,
    }

    # --- Krippendorff's alpha ---
    print("Computing Krippendorff's alpha...")
    if matrix and len(models) >= 2:
        units_for_alpha = []
        for q_idx in range(len(questions)):
            unit = [matrix[q_idx][m_idx] for m_idx in range(len(models))]
            units_for_alpha.append(unit)

        results["krippendorff_alpha"] = {
            "description": "Krippendorff's alpha (ordinal): inter-model agreement (Google Senior)",
            "models": models,
            **krippendorff_alpha_ordinal(units_for_alpha),
        }

    # --- Wilcoxon: flagship vs lightweight ---
    print("Computing Wilcoxon signed-rank test (flagship vs lightweight)...")
    f_scores, l_scores, matched_qs = _build_tier_comparison(rows)
    if len(f_scores) >= 5:
        results["wilcoxon_tier_comparison"] = {
            "description": "Wilcoxon signed-rank: flagship vs lightweight model tier",
            "matched_questions": matched_qs,
            **wilcoxon_signed_rank(f_scores, l_scores),
        }

    # --- Write output ---
    out_path = out_dir / "paper_statistical_tests.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nResults written to {out_path}")
    _print_summary(results)


def _print_summary(results: dict[str, Any]) -> None:
    print("\n" + "=" * 70)
    print("STATISTICAL TEST SUMMARY")
    print("=" * 70)

    su = results.get("scale_utilization", {})
    if su:
        print(f"\n--- Scale Utilization ---")
        print(f"  Total ratings: {su['total_ratings']}")
        print(f"  Bins used: {su['bins_used']}/5")
        print(f"  Effective categories (exp entropy): {su['effective_categories']:.2f}")
        print(f"  Normalized entropy: {su['normalized_entropy']:.4f} (1.0 = uniform)")
        print(f"  Distribution: {su['distribution']}")

    ft = results.get("friedman_test", {})
    if ft:
        print(f"\n--- Friedman Test (do models differ?) ---")
        print(f"  chi2 = {ft.get('chi2')}, p = {ft.get('p_value')}")
        print(f"  N blocks (questions) = {ft.get('n_blocks')}, K treatments (models) = {ft.get('k_treatments')}")
        sig = "***" if ft.get("p_value", 1) < 0.001 else "**" if ft.get("p_value", 1) < 0.01 else "*" if ft.get("p_value", 1) < 0.05 else "ns"
        print(f"  Significance: {sig}")

    kw = results.get("kendalls_w", {})
    if kw:
        print(f"\n--- Kendall's W (inter-model concordance) ---")
        print(f"  W = {kw.get('W')}, chi2 = {kw.get('chi2')}, p = {kw.get('p_value')}")
        interp = "strong" if kw.get("W", 0) >= 0.7 else "moderate" if kw.get("W", 0) >= 0.5 else "weak"
        print(f"  Interpretation: {interp} agreement")

    icc = results.get("icc_test_retest", {})
    if icc and icc.get("per_model"):
        print(f"\n--- ICC Test-Retest ---")
        for model, vals in sorted(icc["per_model"].items()):
            icc_v = vals.get("ICC_2_1", float("nan"))
            interp = "excellent" if icc_v >= 0.75 else "good" if icc_v >= 0.60 else "moderate" if icc_v >= 0.40 else "poor"
            print(f"  {model}: ICC(2,1) = {icc_v:.4f} ({interp})")

    ka = results.get("krippendorff_alpha", {})
    if ka:
        print(f"\n--- Krippendorff's Alpha ---")
        print(f"  alpha = {ka.get('alpha')}")
        a = ka.get("alpha", 0)
        interp = "reliable" if a >= 0.80 else "tentatively reliable" if a >= 0.67 else "unreliable"
        print(f"  Interpretation: {interp} (Krippendorff: >=0.80 reliable, >=0.67 tentative)")

    wil = results.get("wilcoxon_tier_comparison", {})
    if wil:
        print(f"\n--- Wilcoxon: Flagship vs Lightweight ---")
        print(f"  W = {wil.get('W')}, z = {wil.get('z')}, p = {wil.get('p_value')}")
        print(f"  Mean flagship: {wil.get('mean_x')}, Mean lightweight: {wil.get('mean_y')}")
        print(f"  Mean diff: {wil.get('mean_diff')}")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Formal statistical tests for the paper")
    ap.add_argument(
        "rows",
        type=Path,
        nargs="?",
        default=Path(__file__).parent / "results" / "latest" / "rows.jsonl",
        help="Path to rows.jsonl",
    )
    ap.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: same as rows.jsonl parent)",
    )
    args = ap.parse_args()
    out_dir = args.output_dir or args.rows.parent

    print(f"Loading rows from {args.rows}...")
    rows = load_rows(args.rows)
    print(f"Loaded {len(rows)} rows")

    run_all_tests(rows, out_dir)


if __name__ == "__main__":
    main()
