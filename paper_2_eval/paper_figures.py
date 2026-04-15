"""
Publication-quality figures for the paper:
"Scale Collapse, Model Disagreement, and False Precision"

Generates:
  Figure 1: Scale usage heatmap (question x model → dominant rating bin)
  Figure 2: Test-retest reliability comparison (bar chart)
  Figure 3: Inter-model Spearman rho heatmap
  Figure 4: Cross-question volatility comparison (dot + range plot)
  Figure 5: Flagship vs lightweight tier comparison (paired lollipop)
  Figure 6: Model robustness radar chart
  Figure 7: Scale collapse — effective bins histogram

Requirements:
    pip install matplotlib numpy

Run:
    python paper_2_eval/paper_figures.py [rows.jsonl] [-o output_dir]
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

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import numpy as np
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

RATING_ORDER = (
    "No Hire",
    "Leaning No Hire",
    "Leaning Hire",
    "Hire",
    "Strong Hire",
)
RATING_TO_SCORE = {r: float(i + 1) for i, r in enumerate(RATING_ORDER)}
RATING_COLORS = {
    "No Hire": "#d32f2f",
    "Leaning No Hire": "#f57c00",
    "Leaning Hire": "#fbc02d",
    "Hire": "#388e3c",
    "Strong Hire": "#1565c0",
}

FLAGSHIP_MODELS = {"gpt-5.4-pro", "claude-opus-4-6", "gemini/gemini-3.1-pro-preview"}

MODEL_SHORT = {
    "gpt-5.4": "GPT-5.4",
    "gpt-5.4-pro": "GPT-5.4 Pro",
    "gpt-5.4-mini": "GPT-5.4 Mini",
    "claude-opus-4-6": "Claude Opus",
    "claude-sonnet-4-6": "Claude Sonnet",
    "claude-haiku-4-5": "Claude Haiku",
    "gemini/gemini-3.1-pro-preview": "Gemini Pro",
    "gemini/gemini-3-flash-preview": "Gemini Flash",
    "gemini/gemini-3.1-flash-lite-preview": "Gemini Lite",
}

Q_SHORT = {
    "Tell me about yourself.": "About yourself",
    "Describe a time you received tough or critical feedback": "Tough feedback",
    "Tell me about a time you worked well under pressure.": "Under pressure",
    "Tell me about a time you failed. How did you deal with the situation?": "Time you failed",
    "Tell me about a time you had a disagreement with your manager.": "Disagree w/ manager",
    "Tell me about a situation when you had a conflict with a teammate.": "Conflict w/ teammate",
    "Describe a time when you went above and beyond the requirements for a project.": "Above & beyond",
    "Describe a time when you led a team. What was the outcome?": "Led a team",
    "Provide an example of a time when you had to make a difficult decision.": "Difficult decision",
    "How do you handle a situation where you don't know the answer to a question?": "Don't know answer",
}


def load_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _shorten_model(m: str) -> str:
    return MODEL_SHORT.get(m, m.split("/")[-1])


def _shorten_question(q: str) -> str:
    return Q_SHORT.get(q, q[:30] + "...")


def _aggregate_cells(
    rows: list[dict],
    company: str = "Google",
    level: str = "senior",
) -> dict[tuple[str, str], dict[str, int]]:
    """Returns {(question, model): {rating: count}}."""
    cells: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in rows:
        if not r.get("ok") or not r.get("rating"):
            continue
        if r.get("company", "").strip() != company:
            continue
        if r.get("level", "").strip().lower() != level.lower():
            continue
        q = r["question"].strip()
        m = r["model_name"].strip()
        rat = r["rating"].strip()
        if rat in RATING_TO_SCORE:
            cells[(q, m)][rat] += 1
    return cells


def _expected_score(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    if total == 0:
        return float("nan")
    return sum(RATING_TO_SCORE[r] * counts.get(r, 0) for r in RATING_ORDER) / total


# ---------------------------------------------------------------------------
# Figure 1: Scale usage heatmap
# ---------------------------------------------------------------------------

def fig_scale_heatmap(rows: list[dict], out_dir: Path) -> None:
    """Heatmap: question x model → expected ordinal score (Google Senior)."""
    cells = _aggregate_cells(rows, "Google", "senior")
    questions = sorted({q for q, _ in cells})
    models = sorted({m for _, m in cells})

    matrix = []
    for q in questions:
        row = []
        for m in models:
            es = _expected_score(cells.get((q, m), {}))
            row.append(es)
        matrix.append(row)

    fig, ax = plt.subplots(figsize=(14, 7))
    data = np.array(matrix)
    im = ax.imshow(data, cmap="RdYlGn", vmin=1, vmax=5, aspect="auto")

    ax.set_xticks(range(len(models)))
    ax.set_xticklabels([_shorten_model(m) for m in models], rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(questions)))
    ax.set_yticklabels([_shorten_question(q) for q in questions], fontsize=9)

    for i in range(len(questions)):
        for j in range(len(models)):
            val = data[i, j]
            if not math.isnan(val):
                color = "white" if val < 2.5 or val > 3.8 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=7, color=color)

    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Expected Score (1=No Hire, 5=Strong Hire)", fontsize=10)
    cbar.set_ticks([1, 2, 3, 4, 5])
    cbar.set_ticklabels(RATING_ORDER)

    ax.set_title("Figure 1: Expected Rating Score by Question and Model (Google, Senior)", fontsize=12, pad=15)
    fig.tight_layout()
    fig.savefig(out_dir / "fig1_scale_heatmap.png", dpi=300, bbox_inches="tight")
    fig.savefig(out_dir / "fig1_scale_heatmap.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved fig1_scale_heatmap.png/pdf")


# ---------------------------------------------------------------------------
# Figure 2: Test-retest reliability bar chart
# ---------------------------------------------------------------------------

def fig_test_retest(rows: list[dict], out_dir: Path) -> None:
    """Bar chart: test-retest agreement rate by model."""
    groups: dict[tuple, list[float]] = defaultdict(list)
    for r in rows:
        if not r.get("ok") or not r.get("rating"):
            continue
        key = (
            r.get("run_id", ""),
            r.get("question", "").strip(),
            r.get("company", "").strip(),
            r.get("level", "").strip(),
            r.get("model_name", "").strip(),
            r.get("sample_id"),
        )
        score = RATING_TO_SCORE.get(r["rating"].strip())
        if score is not None:
            groups[key].append(score)

    by_model: dict[str, list[float]] = defaultdict(list)
    for key, scores in groups.items():
        if len(scores) >= 2:
            model = key[4]
            agreement = 1.0 if len(set(scores)) == 1 else 0.0
            by_model[model].append(agreement)

    if not by_model:
        print("  Skipping fig2 — no multi-replicate data")
        return

    models = sorted(by_model.keys(), key=lambda m: statistics.mean(by_model[m]), reverse=True)
    means = [statistics.mean(by_model[m]) for m in models]
    counts = [len(by_model[m]) for m in models]

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#2e7d32" if v >= 0.8 else "#f9a825" if v >= 0.5 else "#c62828" for v in means]
    bars = ax.barh(range(len(models)), means, color=colors, edgecolor="white", linewidth=0.5)

    for i, (m, v, n) in enumerate(zip(models, means, counts)):
        ax.text(v + 0.02, i, f"{v:.0%} (n={n})", va="center", fontsize=9)

    ax.set_yticks(range(len(models)))
    ax.set_yticklabels([_shorten_model(m) for m in models], fontsize=10)
    ax.set_xlim(0, 1.15)
    ax.set_xlabel("Agreement Rate (all replicates identical)", fontsize=11)
    ax.axvline(0.8, color="gray", linestyle="--", alpha=0.5, label="80% threshold")
    ax.legend(fontsize=9)
    ax.set_title("Figure 2: Test-Retest Agreement Rate by Model", fontsize=12, pad=10)
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(out_dir / "fig2_test_retest.png", dpi=300, bbox_inches="tight")
    fig.savefig(out_dir / "fig2_test_retest.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved fig2_test_retest.png/pdf")


# ---------------------------------------------------------------------------
# Figure 3: Inter-model Spearman rho heatmap
# ---------------------------------------------------------------------------

def _rankdata(a: list[float]) -> list[float]:
    n = len(a)
    indexed = sorted(range(n), key=lambda i: a[i])
    ranks = [0.0] * n
    pos = 0
    while pos < n:
        start = pos
        val = a[indexed[pos]]
        while pos < n and a[indexed[pos]] == val:
            pos += 1
        avg_rank = (start + pos - 1) / 2.0 + 1.0
        for k in range(start, pos):
            ranks[indexed[k]] = avg_rank
    return ranks


def _spearman(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        return float("nan")
    rx = _rankdata(x)
    ry = _rankdata(y)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.fsum((a - mx) ** 2 for a in rx)
    dy = math.fsum((b - my) ** 2 for b in ry)
    if dx <= 0 or dy <= 0:
        return float("nan")
    return num / math.sqrt(dx * dy)


def fig_spearman_heatmap(rows: list[dict], out_dir: Path) -> None:
    """Heatmap of pairwise Spearman rho (Google Senior)."""
    cells = _aggregate_cells(rows, "Google", "senior")
    questions = sorted({q for q, _ in cells})
    model_scores: dict[str, dict[str, float]] = defaultdict(dict)

    for q in questions:
        for (qq, m), counts in cells.items():
            if qq == q:
                model_scores[m][q] = _expected_score(counts)

    models = sorted(m for m in model_scores if len(model_scores[m]) >= len(questions) * 0.8)

    n = len(models)
    rho_matrix = np.ones((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            shared_qs = sorted(set(model_scores[models[i]]) & set(model_scores[models[j]]))
            if len(shared_qs) >= 3:
                x = [model_scores[models[i]][q] for q in shared_qs]
                y = [model_scores[models[j]][q] for q in shared_qs]
                rho_matrix[i, j] = _spearman(x, y)
            else:
                rho_matrix[i, j] = float("nan")

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(rho_matrix, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")

    labels = [_shorten_model(m) for m in models]
    ax.set_xticks(range(n))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(n))
    ax.set_yticklabels(labels, fontsize=9)

    for i in range(n):
        for j in range(n):
            val = rho_matrix[i, j]
            if not math.isnan(val):
                color = "white" if val < 0.5 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8, color=color)

    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Spearman rho", fontsize=10)

    ax.set_title("Figure 3: Pairwise Inter-Model Rank Correlation (Google, Senior)", fontsize=12, pad=15)
    fig.tight_layout()
    fig.savefig(out_dir / "fig3_spearman_heatmap.png", dpi=300, bbox_inches="tight")
    fig.savefig(out_dir / "fig3_spearman_heatmap.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved fig3_spearman_heatmap.png/pdf")


# ---------------------------------------------------------------------------
# Figure 4: Cross-question volatility
# ---------------------------------------------------------------------------

def fig_cross_question_volatility(rows: list[dict], out_dir: Path) -> None:
    """Dot + range plot: cross-question expected score spread per model."""
    cells = _aggregate_cells(rows, "Google", "senior")
    questions = sorted({q for q, _ in cells})

    model_data: dict[str, list[float]] = defaultdict(list)
    for q in questions:
        for (qq, m), counts in cells.items():
            if qq == q:
                model_data[m].append(_expected_score(counts))

    models = sorted(model_data.keys(), key=lambda m: statistics.pstdev(model_data[m]) if len(model_data[m]) > 1 else 0)

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, m in enumerate(models):
        scores = model_data[m]
        mn = min(scores)
        mx = max(scores)
        mean = statistics.mean(scores)
        sd = statistics.pstdev(scores) if len(scores) > 1 else 0

        ax.plot([mn, mx], [i, i], color="#616161", linewidth=2, zorder=1)
        ax.scatter([mn, mx], [i, i], color="#616161", s=30, zorder=2)
        ax.scatter([mean], [i], color="#1565c0", s=80, zorder=3, marker="D")
        ax.text(mx + 0.05, i, f"SD={sd:.3f}", va="center", fontsize=8, color="#424242")

    ax.set_yticks(range(len(models)))
    ax.set_yticklabels([_shorten_model(m) for m in models], fontsize=10)
    ax.set_xlabel("Expected Score (1–5)", fontsize=11)
    ax.set_xlim(1.0, 5.0)
    ax.axvline(3.0, color="#bdbdbd", linestyle=":", alpha=0.7)
    ax.set_title("Figure 4: Cross-Question Score Volatility by Model (Google, Senior)", fontsize=12, pad=10)
    fig.tight_layout()
    fig.savefig(out_dir / "fig4_cross_q_volatility.png", dpi=300, bbox_inches="tight")
    fig.savefig(out_dir / "fig4_cross_q_volatility.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved fig4_cross_q_volatility.png/pdf")


# ---------------------------------------------------------------------------
# Figure 5: Flagship vs lightweight paired lollipop
# ---------------------------------------------------------------------------

def fig_tier_comparison(rows: list[dict], out_dir: Path) -> None:
    """Paired lollipop: flagship avg vs lightweight avg per question."""
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
    pairs = []
    for q in questions:
        f_vals, l_vals = [], []
        for (qq, m), scores in cell_scores.items():
            if qq != q:
                continue
            if m in FLAGSHIP_MODELS:
                f_vals.extend(scores)
            else:
                l_vals.extend(scores)
        if f_vals and l_vals:
            pairs.append((_shorten_question(q), statistics.mean(f_vals), statistics.mean(l_vals)))

    pairs.sort(key=lambda t: t[1])

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, (q, f, l) in enumerate(pairs):
        ax.plot([f, l], [i, i], color="#9e9e9e", linewidth=1.5, zorder=1)
        ax.scatter([f], [i], color="#c62828", s=60, zorder=2, label="Flagship" if i == 0 else "")
        ax.scatter([l], [i], color="#1565c0", s=60, zorder=2, label="Lightweight" if i == 0 else "")

    ax.set_yticks(range(len(pairs)))
    ax.set_yticklabels([p[0] for p in pairs], fontsize=9)
    ax.set_xlabel("Weighted Average Score (1–5)", fontsize=11)
    ax.axvline(4.0, color="#388e3c", linestyle="--", alpha=0.5, label='"Hire" threshold (4.0)')
    ax.set_xlim(1.5, 4.5)
    ax.legend(fontsize=9, loc="lower right")
    ax.set_title("Figure 5: Flagship vs Lightweight Model Ratings by Question", fontsize=12, pad=10)
    fig.tight_layout()
    fig.savefig(out_dir / "fig5_tier_comparison.png", dpi=300, bbox_inches="tight")
    fig.savefig(out_dir / "fig5_tier_comparison.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved fig5_tier_comparison.png/pdf")


# ---------------------------------------------------------------------------
# Figure 6: Robustness radar chart
# ---------------------------------------------------------------------------

def fig_robustness_radar(robustness_csv: Path, out_dir: Path) -> None:
    """Radar chart from viz_model_robustness.csv."""
    if not robustness_csv.exists():
        print(f"  Skipping fig6 — {robustness_csv} not found")
        return

    data = []
    with robustness_csv.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)

    if not data:
        return

    # Normalize metrics to 0-1 (higher = better for radar)
    models = [_shorten_model(d["model"]) for d in data]

    cross_q_sds = [float(d["cross_q_sd"]) for d in data]
    entropies = [float(d["mean_entropy"]) for d in data]
    rhos = [float(d["mean_pairwise_rho"]) for d in data]

    max_sd = max(cross_q_sds) if cross_q_sds else 1
    max_ent = max(entropies) if entropies else 1

    # Lower is better for SD and entropy → invert
    stability = [1 - (v / max_sd) if max_sd > 0 else 0 for v in cross_q_sds]
    determinism = [1 - (v / max_ent) if max_ent > 0 else 0 for v in entropies]
    consensus = rhos  # already 0-1 scale

    categories = ["Stability\n(1 - cross-Q SD)", "Determinism\n(1 - entropy)", "Consensus\n(mean rho)"]
    N = len(categories)
    angles = [n / float(N) * 2 * math.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    colors_cycle = ["#1565c0", "#c62828", "#2e7d32", "#f57c00", "#6a1b9a",
                    "#00838f", "#ad1457", "#4e342e", "#37474f"]

    for i, model in enumerate(models):
        vals = [stability[i], determinism[i], consensus[i]]
        vals += vals[:1]
        color = colors_cycle[i % len(colors_cycle)]
        ax.plot(angles, vals, linewidth=1.5, label=model, color=color)
        ax.fill(angles, vals, alpha=0.08, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylim(0, 1.05)
    ax.set_title("Figure 6: Model Robustness Radar Chart", fontsize=12, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "fig6_robustness_radar.png", dpi=300, bbox_inches="tight")
    fig.savefig(out_dir / "fig6_robustness_radar.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved fig6_robustness_radar.png/pdf")


# ---------------------------------------------------------------------------
# Figure 7: Scale collapse — effective bins histogram
# ---------------------------------------------------------------------------

def fig_scale_collapse_bins(rows: list[dict], out_dir: Path) -> None:
    """Histogram of n_bins_nonzero across all cells."""
    cells = defaultdict(lambda: defaultdict(int))
    for r in rows:
        if not r.get("ok") or not r.get("rating"):
            continue
        key = (r["question"].strip(), r.get("company", ""), r.get("level", ""), r["model_name"].strip())
        rat = r["rating"].strip()
        if rat in RATING_TO_SCORE:
            cells[key][rat] += 1

    bins_used = []
    for counts in cells.values():
        n = sum(1 for r in RATING_ORDER if counts.get(r, 0) > 0)
        bins_used.append(n)

    fig, ax = plt.subplots(figsize=(7, 4))
    counts_hist = [bins_used.count(i) for i in range(1, 6)]
    pcts = [c / len(bins_used) * 100 for c in counts_hist]

    bars = ax.bar(range(1, 6), counts_hist, color=["#c62828", "#f57c00", "#fbc02d", "#388e3c", "#1565c0"],
                  edgecolor="white", linewidth=0.5)

    for bar, pct, cnt in zip(bars, pcts, counts_hist):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{cnt}\n({pct:.0f}%)", ha="center", va="bottom", fontsize=9)

    ax.set_xlabel("Number of Rating Bins Used (out of 5)", fontsize=11)
    ax.set_ylabel("Number of Evaluation Cells", fontsize=11)
    ax.set_xticks(range(1, 6))
    ax.set_title("Figure 7: Scale Collapse — Rating Bins Used per Evaluation Cell", fontsize=12, pad=10)
    fig.tight_layout()
    fig.savefig(out_dir / "fig7_scale_collapse_bins.png", dpi=300, bbox_inches="tight")
    fig.savefig(out_dir / "fig7_scale_collapse_bins.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved fig7_scale_collapse_bins.png/pdf")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not HAS_MPL:
        print("ERROR: matplotlib and numpy are required.")
        print("  pip install matplotlib numpy")
        return

    ap = argparse.ArgumentParser(description="Publication-quality figures for the paper")
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
        help="Output directory for figures (default: rows parent / figures)",
    )
    args = ap.parse_args()
    out_dir = args.output_dir or (args.rows.parent / "figures")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading rows from {args.rows}...")
    rows = load_rows(args.rows)
    print(f"Loaded {len(rows)} rows")
    print(f"Output directory: {out_dir}\n")

    print("Generating figures...")
    fig_scale_heatmap(rows, out_dir)
    fig_test_retest(rows, out_dir)
    fig_spearman_heatmap(rows, out_dir)
    fig_cross_question_volatility(rows, out_dir)
    fig_tier_comparison(rows, out_dir)

    robustness_csv = args.rows.parent / "viz_model_robustness.csv"
    fig_robustness_radar(robustness_csv, out_dir)

    fig_scale_collapse_bins(rows, out_dir)

    print(f"\nAll figures saved to {out_dir}")


if __name__ == "__main__":
    main()
