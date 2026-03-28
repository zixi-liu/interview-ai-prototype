"""
Visualize BQ rating statistics from rows.jsonl.

Aggregates ratings by (question, company, level, model) and generates
an interactive HTML dashboard for browser viewing.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import webbrowser
from collections import defaultdict
from pathlib import Path

RATING_ORDER = (
    "No Hire",
    "Leaning No Hire",
    "Leaning Hire",
    "Hire",
    "Strong Hire",
)

RATING_VALUES = {
    "No Hire": 1,
    "Leaning No Hire": 2,
    "Leaning Hire": 3,
    "Hire": 4,
    "Strong Hire": 5,
}

FLAGSHIP_MODELS = {"gpt-5.4-pro", "claude-opus-4-6", "gemini/gemini-3.1-pro-preview"}


def load_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def aggregate_stats(rows: list[dict]) -> dict:
    """
    Aggregate ratings by (question, company, level, model).
    Returns dict: key -> {rating: count, ...}
    """
    stats: dict[tuple, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in rows:
        if not r.get("ok") or not r.get("rating"):
            continue
        q = r.get("question", "").strip()
        c = r.get("company", "").strip()
        lvl = r.get("level", "").strip().lower()
        m = r.get("model_name", "").strip()
        rating = r.get("rating", "").strip()
        key = (q, c, lvl, m)
        stats[key][rating] += 1
    return dict(stats)


def stats_to_chart_data(stats: dict) -> list[dict]:
    """Convert aggregated stats to chart-friendly structure."""
    out = []
    for (question, company, level, model), rating_counts in sorted(stats.items()):
        total = sum(rating_counts.values())
        dist = {r: rating_counts.get(r, 0) for r in RATING_ORDER}
        pct = {r: round(100 * c / total, 1) if total else 0 for r, c in dist.items()}
        out.append({
            "question": question,
            "company": company,
            "level": level,
            "model": model,
            "total": total,
            "counts": dist,
            "pct": pct,
        })
    return out


def compute_question_tier_averages(data: list[dict]) -> list[dict]:
    """Weighted-average rating per question for flagship vs lightweight models.

    Rating scale: No Hire=1, Leaning No Hire=2, Leaning Hire=3, Hire=4, Strong Hire=5.
    Returns one dict per question with flagship_avg, lightweight_avg, totals.
    """
    accum: dict[str, dict[str, dict[str, float]]] = defaultdict(
        lambda: {
            "flagship": {"total": 0, "wsum": 0.0},
            "lightweight": {"total": 0, "wsum": 0.0},
        }
    )
    for d in data:
        tier = "flagship" if d["model"] in FLAGSHIP_MODELS else "lightweight"
        for rating, count in d["counts"].items():
            accum[d["question"]][tier]["total"] += count
            accum[d["question"]][tier]["wsum"] += RATING_VALUES.get(rating, 0) * count

    result = []
    for question in sorted(accum):
        row: dict = {"question": question}
        for tier in ("flagship", "lightweight"):
            t = accum[question][tier]["total"]
            row[f"{tier}_avg"] = round(accum[question][tier]["wsum"] / t, 3) if t else None
            row[f"{tier}_total"] = t
        result.append(row)
    return result


def _expected_score(counts: dict) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return sum(RATING_VALUES.get(r, 0) * c for r, c in counts.items()) / total


def _entropy(counts: dict) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return -sum((c / total) * math.log(c / total) for c in counts.values() if c > 0)


def _n_bins_nonzero(counts: dict) -> int:
    return sum(1 for c in counts.values() if c > 0)


def _spearman_rho(x: list[float], y: list[float]) -> float | None:
    """Spearman rank correlation (no scipy dependency)."""
    n = len(x)
    if n < 3:
        return None

    def _rank(vals):
        idx = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and vals[idx[j + 1]] == vals[idx[j]]:
                j += 1
            avg_r = (i + j) / 2 + 1
            for k in range(i, j + 1):
                ranks[idx[k]] = avg_r
            i = j + 1
        return ranks

    rx, ry = _rank(x), _rank(y)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = math.sqrt(sum((rx[i] - mx) ** 2 for i in range(n)))
    dy = math.sqrt(sum((ry[i] - my) ** 2 for i in range(n)))
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def compute_model_robustness(data: list[dict]) -> list[dict]:
    """Per-model robustness scorecard: cross-Q volatility, entropy, pairwise rho."""
    cells = []
    for d in data:
        cells.append({
            "question": d["question"], "company": d["company"],
            "level": d["level"], "model": d["model"], "total": d["total"],
            "es": _expected_score(d["counts"]),
            "entropy": _entropy(d["counts"]),
            "n_bins": _n_bins_nonzero(d["counts"]),
        })

    model_cells: dict[str, list] = defaultdict(list)
    for c in cells:
        model_cells[c["model"]].append(c)

    cl_vec: dict[tuple, dict[str, dict[str, float]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for c in cells:
        cl_vec[(c["company"], c["level"])][c["model"]][c["question"]] = c["es"]

    model_rhos: dict[str, list[float]] = defaultdict(list)
    for (_co, _lv), md in cl_vec.items():
        ms = sorted(md)
        for i in range(len(ms)):
            for j in range(i + 1, len(ms)):
                shared = sorted(set(md[ms[i]]) & set(md[ms[j]]))
                if len(shared) >= 3:
                    rho = _spearman_rho(
                        [md[ms[i]][q] for q in shared],
                        [md[ms[j]][q] for q in shared],
                    )
                    if rho is not None:
                        model_rhos[ms[i]].append(rho)
                        model_rhos[ms[j]].append(rho)

    result = []
    for model in sorted(model_cells):
        mc = model_cells[model]
        scores = [c["es"] for c in mc]
        n = len(scores)
        mean_es = sum(scores) / n
        sd = math.sqrt(sum((s - mean_es) ** 2 for s in scores) / n) if n > 1 else 0.0
        es_range = max(scores) - min(scores) if scores else 0.0
        mean_ent = sum(c["entropy"] for c in mc) / n
        mean_nb = sum(c["n_bins"] for c in mc) / n
        rhos = model_rhos.get(model, [])
        mean_rho = sum(rhos) / len(rhos) if rhos else None
        result.append({
            "model": model, "n_cells": n,
            "total_samples": sum(c["total"] for c in mc),
            "mean_es": round(mean_es, 3),
            "cross_q_sd": round(sd, 3),
            "cross_q_range": round(es_range, 2),
            "mean_entropy": round(mean_ent, 3),
            "mean_n_bins": round(mean_nb, 2),
            "mean_pairwise_rho": round(mean_rho, 3) if mean_rho is not None else None,
        })
    return result


def _select_opts(values: list[str]) -> str:
    """Generate <option> elements for a select."""
    return "".join(f'<option value="{v.replace(chr(34), "&quot;")}">{v}</option>' for v in values)


def _color(rating: str) -> str:
    return {
        "No Hire": "#dc2626",
        "Leaning No Hire": "#f97316",
        "Leaning Hire": "#eab308",
        "Hire": "#22c55e",
        "Strong Hire": "#16a34a",
    }.get(rating, "#64748b")


def _heat(val: float, lo: float, hi: float, *, invert: bool = False) -> str:
    """Heatmap background: green (good) -> amber -> red (concern)."""
    if hi <= lo:
        return ""
    t = max(0.0, min(1.0, (val - lo) / (hi - lo)))
    if invert:
        t = 1.0 - t
    if t < 0.5:
        s = t * 2
        r, g, b = int(34 + 211 * s), int(197 - 39 * s), int(94 - 83 * s)
    else:
        s = (t - 0.5) * 2
        r, g, b = int(245 - 6 * s), int(158 - 90 * s), int(11 + 57 * s)
    return f"background:rgba({r},{g},{b},0.22)"


def emit_html(data: list[dict], tier_data: list[dict],
              robustness_data: list[dict], out_path: Path) -> None:
    """Generate standalone HTML with filter dropdowns and table."""
    # Unique values for filters
    questions = sorted({d["question"] for d in data})
    companies = sorted({d["company"] for d in data})
    levels = sorted({d["level"] for d in data})
    models = sorted({d["model"] for d in data})

    rows_html = []
    for d in data:
        labels = list(RATING_ORDER)
        counts = [d["counts"][r] for r in labels]
        pcts = [d["pct"][r] for r in labels]
        bar_html = "".join(
            f'<div class="bar-cell"><div class="bar" style="width:{p}%;background:{_color(r)}" title="{r}: {c} ({p}%)"></div><span class="bar-label">{c}</span></div>'
            for r, c, p in zip(labels, counts, pcts)
        )
        q_esc = d["question"].replace('"', "&quot;")
        rows_html.append(f"""
        <tr data-question="{q_esc}" data-company="{d["company"]}" data-level="{d["level"]}" data-model="{d["model"]}">
            <td class="q-cell">{d["question"]}</td>
            <td>{d["company"]}</td>
            <td>{d["level"]}</td>
            <td>{d["model"]}</td>
            <td class="bar-row">{bar_html}</td>
            <td class="total">{d["total"]}</td>
        </tr>
        """)

    # ---- Build tier comparison rows ----
    tier_rows_html = []
    for td in tier_data:
        q_short = td["question"][:55] + ("\u2026" if len(td["question"]) > 55 else "")
        q_esc_t = td["question"].replace('"', "&quot;")
        f_avg_s = f'{td["flagship_avg"]:.2f}' if td["flagship_avg"] is not None else "\u2014"
        l_avg_s = f'{td["lightweight_avg"]:.2f}' if td["lightweight_avg"] is not None else "\u2014"
        f_w = (td["flagship_avg"] - 1) / 4 * 100 if td["flagship_avg"] is not None else 0
        l_w = (td["lightweight_avg"] - 1) / 4 * 100 if td["lightweight_avg"] is not None else 0
        diff_s = ""
        if td["flagship_avg"] is not None and td["lightweight_avg"] is not None:
            diff_s = f'{td["flagship_avg"] - td["lightweight_avg"]:+.2f}'
        tier_rows_html.append(
            f'<tr>'
            f'<td class="q-cell" title="{q_esc_t}">{q_short}</td>'
            f'<td class="tier-bars"><div class="tier-row">'
            f'<div class="tier-bar flagship-bar" style="width:{f_w:.1f}%">'
            f'<span class="tier-val">{f_avg_s}</span></div>'
            f'<div class="tier-bar lightweight-bar" style="width:{l_w:.1f}%">'
            f'<span class="tier-val">{l_avg_s}</span></div>'
            f'</div></td>'
            f'<td class="num">{f_avg_s}</td>'
            f'<td class="num">{td["flagship_total"]}</td>'
            f'<td class="num">{l_avg_s}</td>'
            f'<td class="num">{td["lightweight_total"]}</td>'
            f'<td class="num diff">{diff_s}</td>'
            f'</tr>'
        )
    tier_table_html = "\n".join(tier_rows_html)

    # ---- Build robustness scorecard rows ----
    rob = robustness_data
    sd_vals = [r["cross_q_sd"] for r in rob]
    rng_vals = [r["cross_q_range"] for r in rob]
    ent_vals = [r["mean_entropy"] for r in rob]
    rho_vals = [r["mean_pairwise_rho"] for r in rob if r["mean_pairwise_rho"] is not None]
    sd_lo, sd_hi = min(sd_vals), max(sd_vals)
    rng_lo, rng_hi = min(rng_vals), max(rng_vals)
    ent_lo, ent_hi = min(ent_vals), max(ent_vals)
    rho_lo, rho_hi = (min(rho_vals), max(rho_vals)) if rho_vals else (0, 1)
    rob_rows = []
    for r in rob:
        rho_s = f'{r["mean_pairwise_rho"]:.3f}' if r["mean_pairwise_rho"] is not None else "\u2014"
        rho_st = _heat(r["mean_pairwise_rho"], rho_lo, rho_hi, invert=True) if r["mean_pairwise_rho"] is not None else ""
        rob_rows.append(
            f'<tr>'
            f'<td>{r["model"]}</td>'
            f'<td class="num">{r["n_cells"]}</td>'
            f'<td class="num">{r["total_samples"]}</td>'
            f'<td class="num">{r["mean_es"]:.3f}</td>'
            f'<td class="num" style="{_heat(r["cross_q_sd"], sd_lo, sd_hi)}">{r["cross_q_sd"]:.3f}</td>'
            f'<td class="num" style="{_heat(r["cross_q_range"], rng_lo, rng_hi)}">{r["cross_q_range"]:.2f}</td>'
            f'<td class="num" style="{_heat(r["mean_entropy"], ent_lo, ent_hi)}">{r["mean_entropy"]:.3f}</td>'
            f'<td class="num">{r["mean_n_bins"]:.2f}</td>'
            f'<td class="num" style="{rho_st}">{rho_s}</td>'
            f'</tr>'
        )
    rob_table_html = "\n".join(rob_rows)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BQ Rating Stats</title>
    <style>
        :root {{
            --bg: #0f172a;
            --card: #1e293b;
            --text: #e2e8f0;
            --muted: #94a3b8;
            --accent: #38bdf8;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 1.25rem;
            min-height: 100vh;
        }}
        h1 {{
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
            color: var(--accent);
        }}
        .sub {{
            color: var(--muted);
            font-size: 0.8rem;
            margin-bottom: 1rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.8rem;
        }}
        th, td {{
            padding: 0.5rem 0.75rem;
            text-align: left;
            border-bottom: 1px solid #334155;
        }}
        th {{
            color: var(--muted);
            font-weight: 500;
        }}
        .q-cell {{
            max-width: 280px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .bar-row {{
            min-width: 200px;
        }}
        .bar-cell {{
            display: inline-block;
            width: 36px;
            margin-right: 2px;
            text-align: center;
            vertical-align: middle;
        }}
        .bar-cell .bar {{
            height: 12px;
            border-radius: 2px;
            display: block;
            min-width: 2px;
        }}
        .bar-cell .bar-label {{
            font-size: 0.65rem;
            color: var(--muted);
        }}
        .total {{
            font-weight: 600;
            color: var(--accent);
        }}
        .legend {{
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            margin-bottom: 0.75rem;
            font-size: 0.7rem;
            color: var(--muted);
        }}
        .legend span {{
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
        }}
        .legend .swatch {{
            width: 8px;
            height: 8px;
            border-radius: 1px;
        }}
        .filters {{
            display: flex;
            gap: 0.5rem 1rem;
            flex-wrap: wrap;
            align-items: center;
            margin-bottom: 0.75rem;
            font-size: 0.8rem;
        }}
        .filters label {{
            color: var(--muted);
            display: flex;
            align-items: center;
            gap: 0.35rem;
        }}
        .filters select {{
            background: var(--card);
            color: var(--text);
            border: 1px solid #334155;
            border-radius: 4px;
            padding: 0.25rem 0.5rem;
            font-size: 0.75rem;
            min-width: 140px;
        }}
        .filters select:focus {{
            outline: none;
            border-color: var(--accent);
        }}
        tr.hidden {{ display: none; }}
        /* tabs */
        .tab-nav {{ display: flex; gap: 0; margin-bottom: 1rem; border-bottom: 2px solid #334155; }}
        .tab-btn {{
            padding: 0.5rem 1.25rem; background: transparent; border: none;
            color: var(--muted); font-family: inherit; font-size: 0.85rem;
            cursor: pointer; border-bottom: 2px solid transparent;
            margin-bottom: -2px; transition: color 0.2s, border-color 0.2s;
        }}
        .tab-btn:hover {{ color: var(--text); }}
        .tab-btn.active {{ color: var(--accent); border-bottom-color: var(--accent); }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        /* tier comparison */
        .tier-desc {{ color: var(--muted); font-size: 0.75rem; margin-bottom: 1rem; line-height: 1.6; }}
        .tier-desc code {{ background: var(--card); padding: 0.15rem 0.4rem; border-radius: 3px; font-size: 0.72rem; }}
        .tier-bars {{ width: 380px; padding: 4px 0; }}
        .tier-row {{ display: flex; flex-direction: column; gap: 3px; }}
        .tier-bar {{
            height: 20px; border-radius: 3px; display: flex; align-items: center;
            padding: 0 8px; min-width: 44px; transition: width 0.3s ease;
        }}
        .flagship-bar {{ background: linear-gradient(90deg, #0ea5e9, #38bdf8); }}
        .lightweight-bar {{ background: linear-gradient(90deg, #f59e0b, #fbbf24); }}
        .tier-val {{ font-size: 0.7rem; font-weight: 600; color: #0f172a; white-space: nowrap; }}
        .num {{ font-variant-numeric: tabular-nums; text-align: right; }}
        .diff {{ color: var(--muted); }}
        .tier-legend {{ display: flex; gap: 1.5rem; margin-bottom: 1rem; font-size: 0.75rem; color: var(--muted); }}
        .tier-legend span {{ display: inline-flex; align-items: center; gap: 0.3rem; }}
        .tier-legend .tswatch {{ width: 14px; height: 10px; border-radius: 2px; }}
    </style>
</head>
<body>
    <h1>BQ Rating Stats</h1>
    <p class="sub">question × company × level × model</p>
    <div class="tab-nav">
        <button class="tab-btn active" data-tab="detail">Detail Table</button>
        <button class="tab-btn" data-tab="tier">Flagship vs Lightweight</button>
        <button class="tab-btn" data-tab="robust">Model Robustness</button>
    </div>
    <div id="tab-detail" class="tab-content active">
    <div class="filters">
        <label>Question <select id="fq"><option value="">— all —</option>{_select_opts(questions)}</select></label>
        <label>Company <select id="fc"><option value="">— all —</option>{_select_opts(companies)}</select></label>
        <label>Level <select id="fl"><option value="">— all —</option>{_select_opts(levels)}</select></label>
        <label>Model <select id="fm"><option value="">— all —</option>{_select_opts(models)}</select></label>
    </div>
    <div class="legend">
        <span><span class="swatch" style="background:#dc2626"></span> No Hire</span>
        <span><span class="swatch" style="background:#f97316"></span> Leaning No Hire</span>
        <span><span class="swatch" style="background:#eab308"></span> Leaning Hire</span>
        <span><span class="swatch" style="background:#22c55e"></span> Hire</span>
        <span><span class="swatch" style="background:#16a34a"></span> Strong Hire</span>
    </div>
    <table>
            <thead>
                <tr>
                    <th>Question</th>
                    <th>Company</th>
                    <th>Level</th>
                    <th>Model</th>
                    <th>Rating</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
                {"".join(rows_html)}
            </tbody>
        </table>
    </div>
    <div id="tab-tier" class="tab-content">
        <p class="tier-desc">
            Weighted-average rating per question &mdash; <b>Flagship</b> vs <b>Lightweight</b> models.<br>
            <b>Flagship:</b> <code>gpt-5.4-pro</code> &middot; <code>claude-opus-4-6</code> &middot; <code>gemini/gemini-3.1-pro-preview</code><br>
            <b>Lightweight:</b> all other models<br>
            Scale: No&nbsp;Hire&nbsp;=&nbsp;1 &rarr; Strong&nbsp;Hire&nbsp;=&nbsp;5
        </p>
        <div class="tier-legend">
            <span><span class="tswatch" style="background:linear-gradient(90deg,#0ea5e9,#38bdf8)"></span> Flagship</span>
            <span><span class="tswatch" style="background:linear-gradient(90deg,#f59e0b,#fbbf24)"></span> Lightweight</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Question</th>
                    <th>Rating Bar (1&ndash;5)</th>
                    <th>Flagship Avg</th>
                    <th>Flagship N</th>
                    <th>Lightweight Avg</th>
                    <th>Lightweight N</th>
                    <th>Diff (F&minus;L)</th>
                </tr>
            </thead>
            <tbody>
                {tier_table_html}
            </tbody>
        </table>
    </div>
    <div id="tab-robust" class="tab-content">
        <p class="tier-desc">
            Per-model robustness scorecard &mdash; each metric aggregated across all (question &times; company &times; level) cells.<br>
            <b>Cross-Q SD / Range</b>: expected-score volatility across questions &mdash; <em>lower = more stable</em>.<br>
            <b>Mean Entropy</b>: Shannon entropy of rating distribution &mdash; <em>lower = more deterministic</em>.<br>
            <b>Mean &rho;</b>: average Spearman rank-correlation with every other model &mdash; <em>higher = more consensus</em>.<br>
            Cells heatmap: <span style="color:#22c55e">green</span> = robust, <span style="color:#ef4444">red</span> = needs attention.
        </p>
        <table>
            <thead>
                <tr>
                    <th>Model</th>
                    <th>Cells</th>
                    <th>Samples</th>
                    <th>Mean Score</th>
                    <th>Cross-Q SD &darr;</th>
                    <th>Cross-Q Range &darr;</th>
                    <th>Mean Entropy &darr;</th>
                    <th>Mean #Bins</th>
                    <th>Mean &rho; &uarr;</th>
                </tr>
            </thead>
            <tbody>
                {rob_table_html}
            </tbody>
        </table>
    </div>
    <script>
        (function() {{
            var rows = document.querySelectorAll('#tab-detail tbody tr');
            function filter() {{
                var q = document.getElementById('fq').value;
                var c = document.getElementById('fc').value;
                var l = document.getElementById('fl').value;
                var m = document.getElementById('fm').value;
                rows.forEach(function(tr) {{
                    var ok = (!q || tr.dataset.question === q) && (!c || tr.dataset.company === c) && (!l || tr.dataset.level === l) && (!m || tr.dataset.model === m);
                    tr.classList.toggle('hidden', !ok);
                }});
            }}
            ['fq','fc','fl','fm'].forEach(function(id) {{ document.getElementById(id).addEventListener('change', filter); }});
            document.querySelectorAll('.tab-btn').forEach(function(btn) {{
                btn.addEventListener('click', function() {{
                    document.querySelectorAll('.tab-btn').forEach(function(b) {{ b.classList.remove('active'); }});
                    document.querySelectorAll('.tab-content').forEach(function(c) {{ c.classList.remove('active'); }});
                    btn.classList.add('active');
                    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
                }});
            }});
        }})();
    </script>
</body>
</html>
"""
    out_path.write_text(html, encoding="utf-8")


def emit_summary_table(data: list[dict], out_path: Path) -> None:
    """One CSV row per group; utf-8-sig for Excel. Columns: ids, total, n/pct per rating."""
    hdr = (
        "question",
        "company",
        "level",
        "model",
        "total",
        *[f"n_{r}" for r in RATING_ORDER],
        *[f"pct_{r}" for r in RATING_ORDER],
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    key = lambda d: (d["question"], d["company"], d["level"], d["model"])
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(hdr)
        for d in sorted(data, key=key):
            w.writerow(
                [
                    d["question"],
                    d["company"],
                    d["level"],
                    d["model"],
                    d["total"],
                    *[d["counts"][r] for r in RATING_ORDER],
                    *[d["pct"][r] for r in RATING_ORDER],
                ]
            )


def emit_tier_summary_csv(tier_data: list[dict], out_path: Path) -> None:
    """Write per-question flagship vs lightweight weighted averages to CSV."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["question", "flagship_avg", "flagship_n",
                     "lightweight_avg", "lightweight_n", "diff"])
        for td in tier_data:
            f_avg = td["flagship_avg"]
            l_avg = td["lightweight_avg"]
            diff = round(f_avg - l_avg, 3) if f_avg is not None and l_avg is not None else None
            w.writerow([
                td["question"], f_avg, td["flagship_total"],
                l_avg, td["lightweight_total"], diff,
            ])


def emit_robustness_csv(robustness_data: list[dict], out_path: Path) -> None:
    """Write per-model robustness scorecard to CSV."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "model", "n_cells", "total_samples", "mean_expected_score",
            "cross_q_sd", "cross_q_range", "mean_entropy",
            "mean_n_bins", "mean_pairwise_rho",
        ])
        for r in robustness_data:
            w.writerow([
                r["model"], r["n_cells"], r["total_samples"],
                r["mean_es"], r["cross_q_sd"], r["cross_q_range"],
                r["mean_entropy"], r["mean_n_bins"], r["mean_pairwise_rho"],
            ])


def main() -> None:
    ap = argparse.ArgumentParser(description="Visualize BQ rating stats from rows.jsonl")
    ap.add_argument(
        "rows",
        type=Path,
        nargs="?",
        default=Path(__file__).parent / "results" / "latest" / "rows.jsonl",
        help="Path to rows.jsonl",
    )
    ap.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output HTML path (default: same dir as rows, viz_rating_stats.html)",
    )
    ap.add_argument(
        "--open",
        action="store_true",
        dest="open_browser",
        help="Open generated HTML in default browser",
    )
    args = ap.parse_args()

    rows = load_rows(args.rows)
    stats = aggregate_stats(rows)
    data = stats_to_chart_data(stats)

    out = args.output
    if out is None:
        out = args.rows.parent / "viz_rating_stats.html"

    tier_data = compute_question_tier_averages(data)
    robustness_data = compute_model_robustness(data)

    emit_html(data, tier_data, robustness_data, out)
    print(f"Wrote {len(data)} aggregations to {out}")

    summary_path = out.parent / "viz_rating_stats_summary.csv"
    emit_summary_table(data, summary_path)
    print(f"Wrote group summary table ({len(data)} rows) to {summary_path}")

    tier_csv_path = out.parent / "viz_tier_comparison.csv"
    emit_tier_summary_csv(tier_data, tier_csv_path)
    print(f"Wrote tier comparison ({len(tier_data)} questions) to {tier_csv_path}")

    rob_csv_path = out.parent / "viz_model_robustness.csv"
    emit_robustness_csv(robustness_data, rob_csv_path)
    print(f"Wrote model robustness ({len(robustness_data)} models) to {rob_csv_path}")

    if args.open_browser:
        webbrowser.open(out.as_uri())


if __name__ == "__main__":
    main()
