"""
Compute reliability / robustness-style metrics from rows.jsonl (BQ rating experiment).

Outputs CSV tables:
  - cell: entropy, expected ordinal score, positive-rate per (question, company, level, model)
  - cross_question: across questions — std, IQR, range of expected scores per (company, level, model)
  - by_category: same, stratified by coarse question category
  - pairwise_spearman: inter-model rank correlation of per-question expected scores
  - rep_within_run: test–retest spread when replicate_id > 1 within the same run_id

Ordinal mapping: No Hire=1 .. Strong Hire=5 (same order as viz_rating_stats.RATING_ORDER).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from viz_rating_stats import RATING_ORDER, aggregate_stats, load_rows, stats_to_chart_data

RATING_TO_SCORE = {r: float(i + 1) for i, r in enumerate(RATING_ORDER)}


def question_category(question: str) -> str:
    ql = question.lower().strip()
    if ql.startswith("tell me about yourself"):
        return "intro"
    if any(
        k in ql
        for k in (
            "failed",
            "tough or critical",
            "critical feedback",
            "conflict with a teammate",
            "disagreement with your manager",
            "under pressure",
        )
    ):
        return "vulnerability"
    if "don't know the answer" in ql:
        return "epistemic"
    if "led a team" in ql or "difficult decision" in ql:
        return "leadership"
    if "above and beyond" in ql:
        return "initiative"
    return "other"


def _entropy_from_counts(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    if total == 0:
        return float("nan")
    h = 0.0
    for c in counts.values():
        if c <= 0:
            continue
        p = c / total
        h -= p * math.log(p)
    return h


def _expected_score(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    if total == 0:
        return float("nan")
    return sum(RATING_TO_SCORE[r] * counts.get(r, 0) for r in RATING_ORDER) / total


def _n_bins_used(counts: dict[str, int]) -> int:
    return sum(1 for r in RATING_ORDER if counts.get(r, 0) > 0)


def _pct_band(counts: dict[str, int], ratings: tuple[str, ...]) -> float:
    total = sum(counts.values())
    if total == 0:
        return float("nan")
    return 100.0 * sum(counts.get(r, 0) for r in ratings) / total


def _iqr(vals: list[float]) -> float:
    if len(vals) < 2:
        return float("nan")
    qs = statistics.quantiles(vals, n=4, method="inclusive")
    return qs[2] - qs[0]


def _rankdata(a: list[float]) -> list[float]:
    n = len(a)
    idx = sorted(range(n), key=lambda i: a[i])
    ranks = [0.0] * n
    pos = 0
    while pos < n:
        start = pos
        val = a[idx[pos]]
        while pos < n and a[idx[pos]] == val:
            pos += 1
        avg_rank = (start + pos - 1) / 2.0 + 1.0
        for k in range(start, pos):
            ranks[idx[k]] = avg_rank
    return ranks


def _pearson_rho(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        return float("nan")
    mx = statistics.mean(x)
    my = statistics.mean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    denx = math.fsum((a - mx) ** 2 for a in x)
    deny = math.fsum((b - my) ** 2 for b in y)
    if denx <= 0 or deny <= 0:
        return float("nan")
    return num / math.sqrt(denx * deny)


def spearman_rho(x: list[float], y: list[float]) -> float:
    return _pearson_rho(_rankdata(list(x)), _rankdata(list(y)))


def build_cell_table(data: list[dict]) -> list[dict[str, Any]]:
    rows_out: list[dict[str, Any]] = []
    for d in data:
        counts = d["counts"]
        total = d["total"]
        h_nat = _entropy_from_counts(counts)
        rows_out.append(
            {
                "question": d["question"],
                "company": d["company"],
                "level": d["level"],
                "model": d["model"],
                "category": question_category(d["question"]),
                "total": total,
                "expected_score_1_to_5": round(_expected_score(counts), 4),
                "entropy_nats": round(h_nat, 4),
                "entropy_bits": round(h_nat / math.log(2.0), 4) if total else float("nan"),
                "n_bins_nonzero": _n_bins_used(counts),
                "pct_LeaningHire_or_above": round(
                    _pct_band(counts, ("Leaning Hire", "Hire", "Strong Hire")), 2
                ),
                "pct_Hire_or_StrongHire": round(_pct_band(counts, ("Hire", "Strong Hire")), 2),
            }
        )
    return rows_out


def cross_question_stats(
    cell_rows: list[dict[str, Any]],
    min_total: int,
) -> list[dict[str, Any]]:
    """One row per (company, level, model): spread of expected_score across questions."""
    by_key: dict[tuple[str, str, str], list[tuple[str, float]]] = defaultdict(list)
    for r in cell_rows:
        if r["total"] < min_total:
            continue
        key = (r["company"], r["level"], r["model"])
        by_key[key].append((r["question"], float(r["expected_score_1_to_5"])))

    out: list[dict[str, Any]] = []
    for (company, level, model), pairs in sorted(by_key.items()):
        scores = [s for _, s in pairs]
        if len(scores) < 1:
            continue
        out.append(
            {
                "company": company,
                "level": level,
                "model": model,
                "n_questions": len(scores),
                "mean_expected_score": round(statistics.mean(scores), 4),
                "stdev_expected_score": round(statistics.pstdev(scores), 4) if len(scores) > 1 else 0.0,
                "min_expected_score": round(min(scores), 4),
                "max_expected_score": round(max(scores), 4),
                "range_expected_score": round(max(scores) - min(scores), 4) if scores else float("nan"),
                "iqr_expected_score": round(_iqr(scores), 4),
            }
        )
    return out


def by_category_stats(
    cell_rows: list[dict[str, Any]],
    min_total: int,
) -> list[dict[str, Any]]:
    by_cat: dict[tuple[str, str, str, str], list[float]] = defaultdict(list)
    for r in cell_rows:
        if r["total"] < min_total:
            continue
        key = (r["company"], r["level"], r["model"], r["category"])
        by_cat[key].append(float(r["expected_score_1_to_5"]))

    out: list[dict[str, Any]] = []
    for (company, level, model, cat), scores in sorted(by_cat.items()):
        if not scores:
            continue
        out.append(
            {
                "company": company,
                "level": level,
                "model": model,
                "category": cat,
                "n_questions": len(scores),
                "mean_expected_score": round(statistics.mean(scores), 4),
                "stdev_expected_score": round(statistics.pstdev(scores), 4) if len(scores) > 1 else 0.0,
                "range_expected_score": round(max(scores) - min(scores), 4),
            }
        )
    return out


def pairwise_spearman(
    cell_rows: list[dict[str, Any]],
    min_total: int,
) -> list[dict[str, Any]]:
    """For each (company, level), pairwise Spearman over questions shared by both models."""
    by_slice: dict[tuple[str, str], dict[str, dict[str, float]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for r in cell_rows:
        if r["total"] < min_total:
            continue
        sl = (r["company"], r["level"])
        by_slice[sl][r["model"]][r["question"]] = float(r["expected_score_1_to_5"])

    out: list[dict[str, Any]] = []
    for (company, level), qmap in sorted(by_slice.items()):
        models = sorted(qmap.keys())
        for i in range(len(models)):
            for j in range(i + 1, len(models)):
                ma, mb = models[i], models[j]
                qs = sorted(set(qmap[ma].keys()) & set(qmap[mb].keys()))
                if len(qs) < 2:
                    continue
                xa = [qmap[ma][q] for q in qs]
                xb = [qmap[mb][q] for q in qs]
                rho = spearman_rho(xa, xb)
                out.append(
                    {
                        "company": company,
                        "level": level,
                        "model_a": ma,
                        "model_b": mb,
                        "n_shared_questions": len(qs),
                        "spearman_rho": round(rho, 4) if not math.isnan(rho) else rho,
                    }
                )
    return out


def rep_within_run(rows: list[dict]) -> list[dict[str, Any]]:
    """
    Groups with same run_id, question, company, level, model_name, sample_id and >=2 ok ratings.
    """
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        if not r.get("ok") or not r.get("rating"):
            continue
        rid = r.get("run_id", "")
        q = r.get("question", "").strip()
        c = r.get("company", "").strip()
        lvl = r.get("level", "").strip().lower()
        m = r.get("model_name", "").strip()
        sid = r.get("sample_id")
        key = (rid, q, c, lvl, m, sid)
        groups[key].append(r)

    per_group: list[dict[str, Any]] = []
    for key, rs in groups.items():
        if len(rs) < 2:
            continue
        ratings = [x["rating"].strip() for x in rs if x.get("rating")]
        if len(ratings) < 2:
            continue
        scores = [RATING_TO_SCORE[rat] for rat in ratings if rat in RATING_TO_SCORE]
        if len(scores) < 2:
            continue
        rid, q, c, lvl, m, sid = key
        stdev = statistics.pstdev(scores)
        agreement = 1.0 if len(set(ratings)) == 1 else 0.0
        rep_ids = sorted({x.get("replicate_id") for x in rs})
        per_group.append(
            {
                "run_id": rid,
                "question": q,
                "company": c,
                "level": lvl,
                "model": m,
                "sample_id": sid,
                "n_reps": len(scores),
                "replicate_ids": json.dumps(rep_ids),
                "agreement_all_same_rating": agreement,
                "pstdev_ordinal_1_to_5": round(stdev, 4),
            }
        )

    by_run_model: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for g in per_group:
        by_run_model[(g["run_id"], g["model"])].append(g)

    summary: list[dict[str, Any]] = []
    for (rid, model), gs in sorted(by_run_model.items()):
        summary.append(
            {
                "run_id": rid,
                "model": model,
                "n_multi_rep_groups": len(gs),
                "mean_agreement_rate": round(statistics.mean(x["agreement_all_same_rating"] for x in gs), 4),
                "mean_pstdev_ordinal": round(statistics.mean(x["pstdev_ordinal_1_to_5"] for x in gs), 4),
            }
        )
    return per_group, summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8-sig")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Reliability / robustness metrics from rows.jsonl")
    ap.add_argument(
        "rows",
        type=Path,
        nargs="?",
        default=Path(__file__).parent / "results" / "latest" / "rows.jsonl",
        help="Path to rows.jsonl",
    )
    ap.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for CSV outputs (default: same as rows.jsonl parent)",
    )
    ap.add_argument(
        "--min-total",
        type=int,
        default=1,
        help="Minimum aggregated count per cell to include in cross-question / pairwise stats",
    )
    args = ap.parse_args()

    out_dir = args.output_dir or args.rows.parent

    raw = load_rows(args.rows)
    stats = aggregate_stats(raw)
    data = stats_to_chart_data(stats)
    cell_rows = build_cell_table(data)

    write_csv(out_dir / "reliability_cell_metrics.csv", cell_rows)
    cq = cross_question_stats(cell_rows, args.min_total)
    pw = pairwise_spearman(cell_rows, args.min_total)
    write_csv(out_dir / "reliability_cross_question.csv", cq)
    write_csv(out_dir / "reliability_by_category.csv", by_category_stats(cell_rows, args.min_total))
    write_csv(out_dir / "reliability_pairwise_spearman.csv", pw)

    rep_detail, rep_summary = rep_within_run(raw)
    write_csv(out_dir / "reliability_rep_per_group.csv", rep_detail)
    write_csv(out_dir / "reliability_rep_summary_by_run_model.csv", rep_summary)

    print(f"Wrote CSVs under {out_dir}")
    print(f"  cells: {len(cell_rows)}")
    print(f"  cross_question rows: {len(cq)}")
    print(f"  pairwise spearman rows: {len(pw)}")
    print(f"  multi-rep groups: {len(rep_detail)}; rep summaries: {len(rep_summary)}")


if __name__ == "__main__":
    main()
