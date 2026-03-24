# paper_2_eval — BQ multi-model hiring ratings

End-to-end script to evaluate `awesome-behavioral-interviews/answers.toml` with **four judge models** across **Google / Meta / Amazon**, with **up to 5 repetitions** and **per-(company, model) early stopping**.

## Layout

| File | Role |
|------|------|
| `litellm_client.py` | **Only** place that calls `litellm.acompletion` |
| `bq_rating_prompt_schema.py` | Prompt + JSON/regex parsing |
| `bq_stage_runner.py` | Async concurrency, retries, timeouts |
| `bq_early_stop.py` | Histogram + JS divergence + stop rule |
| `run_bq_experiment.py` | CLI: load TOML → run reps → append JSONL |
| `viz_rating_stats.py` | Aggregate and visualize ratings from rows.jsonl |

## Setup

1. From repo root, install deps: `pip install -r requirements.txt`
2. Provide API keys in either place (or mix: empty / omitted entries fall back to `.env`):
   - **`.env`** (repo root): copy `.env.example` → `.env` ([LiteLLM providers](https://docs.litellm.ai/docs/providers)).
   - **`run_config.json`**: optional `"api_keys"` with the **same variable names** as `.env` (e.g. `OPENAI_API_KEY`). Non-empty values are set on `os.environ` after `load_dotenv`, so they override `.env` for matching names. **Do not commit real secrets**; appended `run_meta.jsonl` lines redact `api_keys` to `***`.

## Run

```bash
# Copy and edit model IDs to match your LiteLLM version
python paper_2_eval/run_bq_experiment.py --config paper_2_eval/run_config.example.json
```

Dry run (no API; counts tasks):

```bash
python paper_2_eval/run_bq_experiment.py --dry-run
```

Quick test (first 2 Q&A only):

```bash
python paper_2_eval/run_bq_experiment.py --config paper_2_eval/run_config.example.json --limit-samples 2
```

Answer subset (same mechanism for 10 / 30 / full 50 — `answers.toml` is ordered; omit limit or use `null` in config for all rows):

| Goal | CLI | Or in `run_config.json` under `data` |
|------|-----|--------------------------------------|
| First 10 | `--limit-samples 10` | `"max_answer_samples": 10` |
| First 30 | `--limit-samples 30` | `"max_answer_samples": 30` |
| All rows (~50) | omit flag | `"max_answer_samples": null` |

`--limit-samples` overrides `data.max_answer_samples` when both are set.

Override level (default in config is `senior`):

```bash
python paper_2_eval/run_bq_experiment.py --config paper_2_eval/run_config.example.json --level senior
```

## Rating visualization

After a run, visualize ratings by question × company × level × model:

```bash
python paper_2_eval/viz_rating_stats.py paper_2_eval/results/latest/rows.jsonl -o paper_2_eval/results/latest/viz_rating_stats.html
# Open in browser:
python paper_2_eval/viz_rating_stats.py paper_2_eval/results/latest/rows.jsonl --open
```

The script outputs an HTML dashboard with stacked bar chart and table showing rating distribution (No Hire → Strong Hire) per dimension.

## Outputs

Under `output_dir` (see config), filenames are **fixed** (no timestamp in the name); each run **appends**:

- `rows.jsonl` (default; override with `output.rows_jsonl`) — one JSON object per API attempt. Each line includes `run_id` (UTC timestamp string) so you can group rows by invocation.
- `run_meta.jsonl` (default; override with `output.runs_meta_jsonl`) — one JSON object per **completed** run (config snapshot, paths, `finished_at`, `total_task_slots_counted`). Dry runs do not append. A crashed run leaves no new meta line.

## `runner.parallel_reps`

`true` submits every rep in one batch (faster wall time); **early_stop is off** (always run `max_replicates`). Default is `false` (sequential reps + early stop).

## Config merge vs defaults

`run_config.json` is merged with built-in defaults. **Exception:** if you set `"models": { ... }`, that object **replaces** the default model map entirely (no leftover provider slots). Other nested objects like `runner`, `early_stop`, or `output` still merge shallowly with defaults so you can override single fields.

## Model names (verify on your account + LiteLLM version)

Defaults follow **LiteLLM provider docs** (not vendor marketing names alone). Re-check after any `pip install -U litellm`:

| Slot | Default `model` string | Notes |
|------|------------------------|--------|
| OpenAI | `gpt-5.4-pro` | Docs also list dated pins, e.g. `gpt-5.4-pro-2026-03-05`. Older `gpt-4.1` still valid if you need compatibility. |
| Google | `gemini/gemini-3-pro-preview` | Requires `GEMINI_API_KEY` and a model your project can access; `gemini-2.5-*` previews are alternatives. |
| Anthropic | `claude-sonnet-4-5-20250929` | Newer lines in docs include `claude-sonnet-4-6`; Opus tier is `claude-opus-4-*` if you want top capability. |
| xAI | `xai/grok-4-1-fast-reasoning` | Docs highlight Grok **4.1** over `xai/grok-3`; use `...-non-reasoning` for cheaper/latency. |

Pin exact strings in `run_config` for the paper; if a call 404s, match the [LiteLLM provider page](https://docs.litellm.ai/docs/providers/) for your installed version.
