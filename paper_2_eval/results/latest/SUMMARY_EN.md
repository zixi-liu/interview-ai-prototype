# BQ Interview LLM Rating Experiment — Results Summary

> Experiment dates: 2026-03-25 ~ 2026-03-27
> Coverage: 10 behavioral questions × 3 companies (Google/Meta/Amazon) × 2 levels × 11 models
> Scale: No Hire / Leaning No Hire / Leaning Hire / Hire / Strong Hire (ordinal 1–5)

---

## 1. Data Overview

| Dimension | Value |
|-----------|-------|
| Total rating cells (question × company × level × model) | 141 |
| Samples per cell | 10 or 50 |
| Model families | GPT-5.4 (3 variants), Claude (3 variants), Gemini (3 variants) |
| Test-retest runs | 27 |

---

## 2. High-Value Highlights

### H1: Scale Collapse — A 5-point scale used as a 2-point scale

- **"No Hire" appears in exactly 0 out of 141 cells**
- **"Strong Hire" appears only in a few claude-haiku-4-5 cells** (max 16%, i.e. 8/50)
- Most cells show **90–100% concentration in a single bin** (Leaning Hire or Leaning No Hire)
- Number of non-zero bins (`n_bins_nonzero`): majority = **1** (zero entropy, deterministic output)

> **Insight**: The 5-point scale degenerates into a de facto binary/ternary judgment under LLM evaluation. The top and bottom of the scale are never activated — there is **zero headroom to distinguish star candidates from mediocre ones**.

### H2: Cross-Question Volatility — Up to 9x difference in stability

| Model (Google senior) | Expected Score SD | Expected Score Range | Interpretation |
|-----------------------|-------------------|---------------------|----------------|
| gpt-5.4-mini | **0.075** | 0.30 | Ultra-stable, near-flat |
| gpt-5.4-pro | 0.441 | 1.00 | Moderate swing |
| gemini-3-flash-preview | **0.684** | **2.02** | Highly volatile, 2 full ordinal points |

> **Insight**: A model's mean score hides its stability profile. gpt-5.4-mini's cross-question SD is 0.075 while Gemini Flash's is 0.684 — a **9x gap**. Cross-question variance is a first-class metric that must be reported.

### H3: Inter-Model Rank Agreement — Swapping models ≈ swapping rubrics

| Model Pair (Google senior) | Spearman ρ | Interpretation |
|----------------------------|-----------|----------------|
| Gemini 3 Flash ↔ Gemini 3.1 Pro | **0.936** | Same-family, excellent |
| Claude Haiku ↔ Claude Sonnet | **0.890** | Same-family, excellent |
| Claude Haiku ↔ Gemini 3.1 Pro | 0.874 | Cross-family, good |
| Gemini 3 Flash ↔ gpt-5.4 | 0.522 | **Moderate only** |
| gpt-5.4 ↔ gpt-5.4-pro | **0.314** | **Same-brand, near-random** |
| gpt-5.4 ↔ gpt-5.4-pro (mid-level) | **0.249** | **Lowest — effectively random** |

> **Insight**: Same-brand variant agreement (ρ = 0.25–0.31) can be **worse** than cross-vendor agreement (ρ = 0.52–0.87). Swapping model checkpoints can reshuffle candidate rankings more than swapping entire scoring frameworks.

### H4: Test-Retest Reliability — Deterministic vs. coin-flip, 10x spread

| Model | Best Run Agreement | Worst Run Agreement | Worst pstdev |
|-------|--------------------|---------------------|-------------|
| gpt-5.4 | **1.00** (SD=0) | 0.80 | 0.08 |
| gpt-5.4-pro | 0.80 | 0.80 | 0.079 |
| gpt-5.4-mini | 0.80 | 0.60 | 0.147 |
| gemini-3.1-pro-preview | 0.90 | 0.60 | 0.20 |
| claude-haiku-4-5 | 0.50 | **0.10** | 0.421 |
| gemini-3-flash-preview | 0.20 | **0.20** | **0.369** |
| gemini-3.1-flash-lite | 0.30 | **0.10** | **0.381** |

> **Insight**: gpt-5.4 achieves 100% perfect agreement; Gemini Flash and Claude Haiku drop to 10–20% agreement with ordinal pstdev ~0.37–0.42 — nearly a full grade of jitter. **Repeatability must be benchmarked before deployment — otherwise single-shot scores are unreliable.**

### H5: "Tell me about yourself" — The universal harshest question

- Google senior: **8 out of 11 models rate 100% "Leaning No Hire"** (expected score = 2.0)
- Only gpt-5.4-mini (92% Leaning Hire) and claude-haiku (60%/40% split) deviate
- Compare: on "How do you handle not knowing the answer?", Gemini Flash gives **98% Hire** (expected = 4.02)

> **Insight**: For the same candidate response, the expected rating can differ by **2 full ordinal points** (2.0 vs 4.0) purely based on question type. Prompt family strongly governs LLM "harshness" — cross-question candidate comparison requires normalization or stratification.

### H6: Vulnerability questions — The biggest model-disagreement battlefield

- Vulnerability category (failure/conflict/pressure) shows the **highest cross-model stdev** in by_category (up to 0.58)
- Extreme contrast: gpt-5.4-pro rates "tough feedback" / "conflict" / "failure" / "pressure" at **100% Leaning No Hire** (expected = 2.0)
- While gpt-5.4-mini rates the exact same questions at **100% Leaning Hire** (expected = 3.0)
- Same brand, two versions, **one full ordinal grade apart**

> **Insight**: Behavioral questions involving failure and conflict are the most potent amplifiers of inter-model disagreement. They serve as the best litmus test for LLM interviewer calibration.

---

## 3. Quantitative Quick Reference

| Metric | Min | Max | Implication |
|--------|-----|-----|-------------|
| Cell entropy (nats) | 0 (62% of cells) | 1.09 | Most outputs are deterministic |
| Cross-question expected score SD | 0.046 (gpt-5.4-mini / Amazon) | 0.684 (Gemini Flash / Google) | 15x spread |
| Pairwise Spearman ρ | 0.249 | 0.936 | From near-random to highly aligned |
| Replicate agreement rate | 0.10 | 1.00 | 10x spread |
| Ordinal pstdev | 0 | 0.421 | Up to ~1 full grade of noise |

---

## 4. The Bottom Line

> **Three fatal flaws of LLM interview scoring:**
>
> 1. **Scale collapse** — A 5-point scale that only uses 2 points cannot distinguish excellence from mediocrity.
> 2. **Models are not interchangeable** — Same-brand variants (ρ = 0.25) can disagree more than cross-vendor pairs (ρ = 0.87).
> 3. **Repeatability varies by an order of magnitude** — The most stable model hits 100% agreement; the least stable hits 10%.
>
> **Conclusion: Any LLM-based interview scoring system that reports only point estimates without cross-question variance, inter-model rank correlation, and test-retest metrics is masking real noise with false precision.**
