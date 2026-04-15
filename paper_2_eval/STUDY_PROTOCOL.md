# Human Interviewer Ground Truth — Pilot Study Protocol

> Optional but strongly recommended supplement for the paper.
> Adds calibration anchor for Finding 5 (Expectation Gap) and enables R5 of the reliability checklist.

---

## 1. Objective

Collect human interviewer ratings for the same 10 behavioral interview answers used in the LLM benchmark, enabling:
- Direct human-LLM agreement measurement
- Calibration of LLM rating distributions against human judgment
- Disambiguation of the Expectation Gap (Finding 5): are the answers genuinely below "Hire," or are LLMs systematically harsh?

## 2. Participants

### 2.1 Recruitment Criteria

| Criterion | Requirement |
|-----------|-------------|
| Interview experience | >= 50 behavioral interviews conducted |
| Company tier | Current or former FAANG / Big Tech engineer |
| Level | >= Senior (L5+ at Google, E5+ at Meta, L6+ at Amazon) |
| Recency | Active interviewing within last 12 months |

### 2.2 Sample Size

- **Minimum**: 3 raters (sufficient for pilot ICC computation)
- **Recommended**: 5 raters (enables cross-rater subgroup analysis)
- **Ideal**: 8–10 raters (matches psychometric standards for inter-rater reliability)

### 2.3 Compensation

- $100–150 per rater (estimated 60–90 minutes total)
- IRB exempt if no identifiable candidate data is used (answers are from public GitHub repo)

## 3. Materials

### 3.1 Answer Stimuli

The same 10 behavioral Q&A pairs from [awesome-behavioral-interviews](https://github.com/ashishps1/awesome-behavioral-interviews):

| # | Question (abridged) | Category |
|---|---------------------|----------|
| 1 | Tell me about yourself | Introduction |
| 2 | Led a team — what was the outcome? | Leadership |
| 3 | Difficult decision | Leadership |
| 4 | Above and beyond for a project | Initiative |
| 5 | Conflict with a teammate | Vulnerability |
| 6 | Disagreement with your manager | Vulnerability |
| 7 | Time you failed | Vulnerability |
| 8 | Worked well under pressure | Vulnerability |
| 9 | Received tough or critical feedback | Vulnerability |
| 10 | Handle not knowing the answer | Epistemic |

### 3.2 Rating Scale

Identical 5-point scale used in the LLM experiment:

| Rating | Score | Definition |
|--------|-------|------------|
| No Hire | 1 | Clearly does not meet the bar |
| Leaning No Hire | 2 | More concerns than positives; would not advocate for hire |
| Leaning Hire | 3 | Some positives but insufficient evidence; borderline |
| Hire | 4 | Solid evidence of competency; would advocate for hire |
| Strong Hire | 5 | Exceptional; exceeds expectations significantly |

### 3.3 Evaluation Instructions

Same prompt frame as the LLM experiment:

> Imagine you are interviewing a candidate for a Senior Software Engineer role at Google. Read the question and the candidate's answer below. Rate the answer on the 5-point scale. Provide brief feedback (2–3 sentences) explaining your rating.
>
> Focus on: ownership, problem solving, execution, collaboration, communication, leadership, and impact. Be strict and evidence-based. Do not give the benefit of the doubt when details are missing.

## 4. Procedure

### 4.1 Pre-Calibration (10 minutes)

1. Raters read the evaluation instructions and rating scale definitions
2. Raters complete 2 practice ratings (not from the 10 stimuli) with feedback
3. Brief discussion of any questions about the scale

### 4.2 Rating Phase (45–60 minutes)

1. Each rater independently rates all 10 answers
2. Randomized presentation order (different for each rater to avoid order effects)
3. For each answer, raters provide:
   - Rating (1–5)
   - Confidence in their rating (1–5)
   - Brief feedback (2–3 sentences)
4. No communication between raters during rating

### 4.3 Debrief (10 minutes)

1. Raters reflect on any answers they found difficult to rate
2. Collect qualitative feedback on the scale and instructions
3. Ask: "Were any answers clearly 'Hire' or better?"

## 5. Analysis Plan

### 5.1 Primary Analyses

| Analysis | Method | Purpose |
|----------|--------|---------|
| Inter-rater reliability | ICC(2,k) two-way random | Do human raters agree with each other? |
| Human-LLM agreement | Spearman rho, weighted kappa | Do LLM ratings correlate with human ratings? |
| Expectation gap calibration | Paired comparison | Are community answers below Hire per humans too? |
| Scale utilization | Distribution analysis | Do humans use more of the 5-point scale than LLMs? |

### 5.2 Key Comparisons

For each question, compute:
- `human_mean`: Mean rating across human raters
- `llm_flagship_mean`: Mean rating across flagship LLM models
- `llm_lightweight_mean`: Mean rating across lightweight LLM models
- `human_llm_diff`: human_mean - llm_flagship_mean

### 5.3 Interpretation Framework

| Scenario | Finding | Implication |
|----------|---------|-------------|
| Humans rate >= 4.0, LLMs rate < 4.0 | LLMs too harsh | Calibration needed |
| Humans rate < 4.0, LLMs rate < 4.0 | Both agree: answers below Hire | Community materials genuinely weak |
| Humans disagree (high ICC < 0.40) | Behavioral rating inherently noisy | LLM disagreement partially mirrors human |
| Humans agree (ICC >= 0.75), LLMs disagree | LLMs add noise beyond human baseline | LLM reliability is a genuine concern |

## 6. Expected Outcomes

Based on the LLM benchmark results, we predict:

1. **Human scale utilization will be broader** — humans are likely to use 3–4 bins vs. LLMs' effective 2 bins
2. **Humans will rate some answers at or above "Hire"** — the top 2–3 questions (handling unknowns, difficult decision) likely meet Hire threshold for humans even if not for LLMs
3. **Human inter-rater reliability will be moderate** (ICC ~0.50–0.70) — behavioral interview ratings are inherently somewhat subjective
4. **Human-LLM agreement will be low-moderate** (rho ~0.40–0.60) — LLMs capture general trends but add systematic harshness

## 7. Timeline

| Phase | Duration | Dependencies |
|-------|----------|-------------|
| Recruit raters | 1 week | Network outreach |
| Prepare materials | 2 days | Materials from Section 3 |
| Rating collection | 1 week | Raters' availability |
| Analysis | 2 days | After all ratings collected |
| Integration into paper | 1 day | After analysis |
| **Total** | **~2.5 weeks** | |

## 8. Ethical Considerations

- **No real candidates**: All answers are from a public GitHub repository. No identifiable candidate data is involved.
- **Rater privacy**: Rater identities are anonymized in reporting (Rater A, B, C...).
- **Informed consent**: Raters are informed this is for academic research and consent to anonymized data use.
- **IRB**: Likely exempt (no human subjects in the traditional sense — raters are providing expert opinions on public text, not undergoing experimentation). Confirm with institutional IRB if submitting to a venue that requires IRB documentation.

## 9. Data Format

### 9.1 Output Schema

```json
{
  "rater_id": "A",
  "question_index": 1,
  "question": "Tell me about yourself.",
  "rating": 2,
  "confidence": 4,
  "feedback": "The answer lacks specific technical depth...",
  "timestamp": "2026-04-15T10:30:00Z"
}
```

### 9.2 Output File

Append to `paper_2_eval/results/latest/human_ratings.jsonl` for integration with existing analysis pipeline.

## 10. Integration with Paper

### 10.1 New Section

Add **Section 4.6: Human Ground Truth Calibration** to the paper:
- Present human rating distribution
- Compare human vs. LLM distributions (per question and overall)
- Report ICC for human raters
- Report human-LLM agreement metrics

### 10.2 Updated Reliability Checklist

R5 (calibration validity) can be evaluated if human ground truth is available:
- Compute Spearman rho between human-mean and each model's expected scores
- Models passing R5 threshold (rho >= 0.60) earn checkmark

### 10.3 Updated Finding 5

Disambiguate the Expectation Gap:
- If humans also rate below Hire: emphasize "community materials are genuinely below interview standard"
- If humans rate at/above Hire: emphasize "LLMs are systematically miscalibrated"
- If mixed: nuanced interpretation with per-question breakdown
