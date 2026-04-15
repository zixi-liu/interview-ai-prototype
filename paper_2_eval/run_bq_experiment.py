#!/usr/bin/env python3
"""
BQ multi-model rating experiment: load answers.toml, cross companies × models,
repeat up to max_replicates with per-(company, model) early stopping.

Usage (from repo root):
  python paper_2_eval/run_bq_experiment.py --config paper_2_eval/run_config.example.json

Dry run (count tasks only):
  python paper_2_eval/run_bq_experiment.py --dry-run

Subset of answers (first N rows; full set is typically 50 in answers.toml):
  python paper_2_eval/run_bq_experiment.py --config ... --limit-samples 10
  # Or set "max_answer_samples": 30 in config data (CLI overrides).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

# Ensure local imports
_P2 = Path(__file__).resolve().parent
if str(_P2) not in sys.path:
    sys.path.insert(0, str(_P2))

from bq_early_stop import rating_histogram, should_stop_layer
from bq_rating_prompt_schema import build_bq_rating_prompt, parse_bq_rating_output
from bq_stage_runner import run_stage_tasks
from litellm_client import complete_text, provider_bucket_for_model
from viz_rating_stats import aggregate_stats, emit_html, load_rows, stats_to_chart_data

LOGGER = logging.getLogger("run_bq_experiment")

# Keys in api_keys must look like environment variable names (same strings as .env / LiteLLM).
_ENV_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,}$")


def load_questions_answers(toml_path: Path) -> list[dict[str, Any]]:
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)
    return [
        {
            "id": item.get("id"),
            "question": item.get("question", ""),
            "answer": item.get("answer", ""),
        }
        for item in data.get("questions", [])
    ]


def default_config() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[1]
    return {
        "level": "senior",
        "companies": ["Google", "Meta", "Amazon"],
        "models": {
            "openai": "gpt-5.4-pro",
            "google": "gemini/gemini-3-pro-preview",
            "anthropic": "claude-sonnet-4-5-20250929",
            "xai": "xai/grok-4-1-fast-reasoning",
        },
        "data": {
            "answers_toml": str(root / "awesome-behavioral-interviews" / "answers.toml"),
            # null = use all rows in answers.toml; or set e.g. 10 / 30 for quick runs
            "max_answer_samples": None,
        },
        "output_dir": str(_P2 / "results" / "latest"),
        "max_replicates": 5,
        "early_stop": {
            "min_rep_to_check": 3,
            "max_abs_bin_diff": 0.02,
            "js_divergence": 0.01,
            "consecutive_stable_pairs": 2,
        },
        "runner": {
            "max_concurrent_global": 8,
            "max_concurrent_per_provider": {
                "openai": 4,
                "google": 2,
                "anthropic": 2,
                "xai": 2,
            },
            "min_interval_sec_per_provider": {},
            "max_retries": 3,
            "request_timeout_sec": 120,
            "parallel_reps": False,  # all reps at once; no early_stop
        },
        # Optional: same names as in .env, e.g. OPENAI_API_KEY (non-empty → os.environ before run).
        # Redacted in appended run_meta lines; do not commit real secrets.
        "api_keys": {},
        # Fixed names under output_dir; new runs append rows and one meta line per completed run.
        "output": {
            "rows_jsonl": "rows.jsonl",
            "runs_meta_jsonl": "run_meta.jsonl",
        },
    }


def apply_api_keys_from_config(cfg: dict[str, Any]) -> None:
    """Apply cfg['api_keys'] to os.environ (overrides .env for the same names)."""
    block = cfg.get("api_keys")
    if not isinstance(block, dict):
        return
    for k, v in block.items():
        if not isinstance(v, str) or not v.strip():
            continue
        if not _ENV_NAME_RE.match(k):
            LOGGER.warning("api_keys: skip %r (use OPENAI_API_KEY-style names)", k)
            continue
        os.environ[k] = v


def redact_config_for_meta(cfg: dict[str, Any]) -> dict[str, Any]:
    out = json.loads(json.dumps(cfg))
    ak = out.get("api_keys")
    if isinstance(ak, dict):
        out["api_keys"] = {k: ("***" if isinstance(v, str) and v.strip() else v) for k, v in ak.items()}
    return out


def merge_config(base: dict[str, Any], override: dict[str, Any] | None) -> dict[str, Any]:
    """Merge defaults with a JSON config file.

    Top-level keys from the file replace or shallow-merge into defaults.
    Nested dicts are merged shallowly **except** ``models``: if the file
    defines ``models``, that object replaces defaults entirely (no union
    with default provider slots).
    """
    if not override:
        return json.loads(json.dumps(base))
    out = json.loads(json.dumps(base))
    for k, v in override.items():
        if k == "models" and isinstance(v, dict):
            out["models"] = json.loads(json.dumps(v))
            continue
        if isinstance(v, dict) and k in out and isinstance(out[k], dict):
            out[k] = {**out[k], **v}
        else:
            out[k] = v
    return out


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _resolve_sample_limit(cfg: dict[str, Any], cli_limit: int | None) -> int | None:
    """CLI --limit-samples overrides config data.max_answer_samples."""
    if cli_limit is not None:
        return cli_limit
    raw = cfg.get("data", {}).get("max_answer_samples")
    if raw is None:
        return None
    return int(raw)


def _resolve_output_paths(cfg: dict[str, Any], out_dir: Path) -> tuple[Path, Path]:
    block = cfg.get("output")
    if not isinstance(block, dict):
        block = {}
    rows_name = block.get("rows_jsonl") or "rows.jsonl"
    meta_name = block.get("runs_meta_jsonl") or "run_meta.jsonl"
    return out_dir / str(rows_name), out_dir / str(meta_name)


def _write_viz_from_rows(rows_path: Path) -> Path:
    """Generate/update HTML visualization from rows.jsonl."""
    viz_path = rows_path.parent / "viz_rating_stats.html"
    rows = load_rows(rows_path)
    stats = aggregate_stats(rows)
    data = stats_to_chart_data(stats)
    emit_html(data, viz_path)
    return viz_path


async def run_experiment(cfg: dict[str, Any], *, dry_run: bool, limit_samples: int | None) -> None:
    level = str(cfg["level"]).strip().lower()
    companies: list[str] = cfg["companies"]
    models: dict[str, str] = cfg["models"]
    max_reps = int(cfg["max_replicates"])
    es = cfg["early_stop"]
    runner_cfg = cfg["runner"]
    answers_path = Path(cfg["data"]["answers_toml"])
    if not answers_path.is_absolute():
        answers_path = (_P2 / answers_path).resolve()
    out_dir = Path(cfg["output_dir"])
    if not out_dir.is_absolute():
        out_dir = (_P2 / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    qas = load_questions_answers(answers_path)
    n = _resolve_sample_limit(cfg, limit_samples)
    if n is not None:
        qas = qas[:n]

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rows_path, runs_meta_path = _resolve_output_paths(cfg, out_dir)

    meta = {
        "run_id": run_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "config": redact_config_for_meta(cfg),
        "answers_toml": str(answers_path),
        "n_samples": len(qas),
        "max_answer_samples": n,
    }

    # (company, model_name) -> active
    model_items = list(models.items())
    active_layers: set[tuple[str, str]] = {(c, m) for c in companies for _, m in model_items}

    # Ratings collected per layer per rep (for early stop)
    layer_rep_ratings: dict[tuple[str, str], dict[int, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )

    to = float(runner_cfg.get("request_timeout_sec") or 120)

    def build_tasks(rep: int) -> list[tuple[str, str, Any]]:
        out: list[tuple[str, str, Any]] = []
        for qa in qas:
            qa_id = qa["id"]
            q = qa["question"]
            a = qa["answer"]
            for company in companies:
                for _mkey, model_name in model_items:
                    layer = (company, model_name)
                    if rep > 1 and layer not in active_layers:
                        continue
                    tid = f"id{qa_id}_{company}_{model_name}_r{rep}"

                    def make_factory(
                        *,
                        qa_id_=qa_id,
                        q_=q,
                        a_=a,
                        company_=company,
                        model_=model_name,
                        rep_=rep,
                    ):
                        async def _factory():
                            raw = await complete_text(
                                model_,
                                build_bq_rating_prompt(
                                    question=q_, answer=a_, company=company_, level=level
                                ),
                                timeout=to,
                            )
                            p = parse_bq_rating_output(raw)
                            return {
                                "sample_id": qa_id_,
                                "question": q_,
                                "answer": a_,
                                "company": company_,
                                "level": level,
                                "model_name": model_,
                                "replicate_id": rep_,
                                "stage": 1 if rep_ == 1 else 2,
                                "feedback": p.feedback,
                                "rating": p.rating,
                                "parse_error": p.parse_error,
                                "parse_note": p.error,
                                "raw_text": p.raw_text,
                            }

                        return _factory

                    out.append((tid, provider_bucket_for_model(model_name), make_factory()))
        return out

    def write_rows(outcomes: list[dict[str, Any]]) -> None:
        for o in outcomes:
            base = {
                "run_id": run_id,
                "task_id": o["task_id"],
                "ok": o["ok"],
                "latency_ms": o["latency_ms"],
                "attempts": o["attempts"],
                "error": o.get("error", ""),
                "replicate_id": o.get("replicate_id"),
                "stage": o.get("stage"),
            }
            if o["ok"] and isinstance(o.get("result"), dict):
                r = o["result"]
                append_jsonl(rows_path, {**base, **r})
                if r.get("rating"):
                    layer_rep_ratings[(r["company"], r["model_name"])][int(r["replicate_id"])].append(
                        str(r["rating"])
                    )
            else:
                append_jsonl(rows_path, {**base, "result": o.get("result")})

    rs = dict(
        max_concurrent_global=int(runner_cfg.get("max_concurrent_global", 8)),
        max_concurrent_per_provider=runner_cfg.get("max_concurrent_per_provider"),
        min_interval_sec_per_provider=runner_cfg.get("min_interval_sec_per_provider"),
        max_retries=int(runner_cfg.get("max_retries", 3)),
        request_timeout_sec=to,
    )

    parallel_reps = bool(runner_cfg.get("parallel_reps", False))
    total_tasks = 0

    if parallel_reps:
        tasks = [t for r in range(1, max_reps + 1) for t in build_tasks(r)]
        total_tasks = len(tasks)
        if dry_run:
            LOGGER.info("dry-run parallel_reps tasks=%s (early_stop off)", total_tasks)
        else:
            LOGGER.info("parallel_reps: %s tasks, %s reps (early_stop off)", total_tasks, max_reps)
            write_rows(await run_stage_tasks(tasks, replicate_id=None, stage=None, **rs))
    else:
        for rep in range(1, max_reps + 1):
            tasks = build_tasks(rep)
            total_tasks += len(tasks)
            if dry_run:
                LOGGER.info("dry-run rep=%s tasks=%s active_layers=%s", rep, len(tasks), len(active_layers))
                continue
            write_rows(
                await run_stage_tasks(
                    tasks, replicate_id=rep, stage=2 if rep > 1 else 1, **rs
                )
            )
            if rep > 1:
                to_remove: list[tuple[str, str]] = []
                for layer in list(active_layers):
                    hist_by_rep = {
                        r: rating_histogram(layer_rep_ratings[layer].get(r, []))
                        for r in range(1, rep + 1)
                    }
                    if should_stop_layer(
                        hist_by_rep,
                        min_rep_to_check=int(es["min_rep_to_check"]),
                        max_abs_bin_diff_threshold=float(es["max_abs_bin_diff"]),
                        js_threshold=float(es["js_divergence"]),
                        consecutive_stable_pairs=int(es["consecutive_stable_pairs"]),
                    ):
                        to_remove.append(layer)
                        LOGGER.info("early_stop layer=%s after rep=%s", layer, rep)
                for layer in to_remove:
                    active_layers.discard(layer)
            if rep > 1 and not active_layers:
                LOGGER.info("all layers stopped early after rep=%s", rep)
                break

    meta_final = {
        **meta,
        "status": "completed",
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "rows_jsonl": str(rows_path),
        "runs_meta_jsonl": str(runs_meta_path),
        "total_task_slots_counted": total_tasks,
    }
    if not dry_run:
        append_jsonl(runs_meta_path, meta_final)
        LOGGER.info("appended run to %s and rows to %s", runs_meta_path, rows_path)
        try:
            viz_path = _write_viz_from_rows(rows_path)
            LOGGER.info("updated visualization at %s", viz_path)
        except Exception:
            LOGGER.exception("failed to update visualization from %s", rows_path)
    else:
        LOGGER.info("dry-run total task slots ~ %s (sum over reps); no files written", total_tasks)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description="BQ rating experiment (paper_2_eval)")
    ap.add_argument("--config", type=Path, help="JSON config file")
    ap.add_argument("--dry-run", action="store_true", help="Count tasks; no API calls")
    ap.add_argument(
        "--limit-samples",
        type=int,
        default=None,
        metavar="N",
        help="Only first N Q/A rows (overrides config data.max_answer_samples; e.g. 10 / 30 / 50)",
    )
    ap.add_argument("--level", type=str, default=None, help="Override level (e.g. senior)")
    ap.add_argument("--max-replicates", type=int, default=None)
    args = ap.parse_args()

    cfg = default_config()
    if args.config:
        with open(args.config, encoding="utf-8") as f:
            cfg = merge_config(cfg, json.load(f))
    if args.level:
        cfg["level"] = args.level
    if args.max_replicates is not None:
        cfg["max_replicates"] = args.max_replicates

    # Normalize level to lowercase for stable output and grouping.
    cfg["level"] = str(cfg.get("level", "")).strip().lower()

    apply_api_keys_from_config(cfg)

    asyncio.run(run_experiment(cfg, dry_run=args.dry_run, limit_samples=args.limit_samples))


if __name__ == "__main__":
    main()
