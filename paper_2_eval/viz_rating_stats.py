"""
Visualize BQ rating statistics from rows.jsonl.

Aggregates ratings by (question, company, level, model) and generates
an interactive HTML dashboard for browser viewing.
"""

from __future__ import annotations

import argparse
import json
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
        lvl = r.get("level", "").strip()
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


def emit_html(data: list[dict], out_path: Path) -> None:
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
    </style>
</head>
<body>
    <h1>BQ Rating Stats</h1>
    <p class="sub">question × company × level × model</p>
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
    <script>
        (function() {{
            var rows = document.querySelectorAll('tbody tr');
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
        }})();
    </script>
</body>
</html>
"""
    out_path.write_text(html, encoding="utf-8")


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

    emit_html(data, out)
    print(f"Wrote {len(data)} aggregations to {out}")
    if args.open_browser:
        webbrowser.open(out.as_uri())


if __name__ == "__main__":
    main()
