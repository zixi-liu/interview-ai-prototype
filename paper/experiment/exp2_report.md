# Experiment 2 Report: Convergence Analysis

**Date**: 2025-12-26
**Experiment Type**: Convergence Analysis
**Status**: Completed

---

## Executive Summary

This experiment analyzes whether CoT prompting converges quickly in interview answer improvement, and whether more iterations help. Using a within-subject paired design with 50 behavioral interview Q&A pairs, we tracked success rate by iteration for both automated and human-in-loop methods.

**Key Finding**: Both methods converge rapidly (mean <1 iteration). Human-in-Loop reaches 100% success by iteration 3, while Automated plateaus at 92%. The limitation is context, not iterations - more iterations don't close the gap.

**Conclusion**: Additional iterations provide diminishing returns. The advantage of Human-in-Loop comes from having real context, not from running more iterations.

---

## 1. Methodology

### 1.1 Experimental Design

**Design Type**: Within-subject paired design

**Treatments**:
- **Automated**: Uses `StorySelfImprove` - pure CoT prompting with no-fabrication constraint
- **Human-in-Loop**: Uses `HumanInLoopImprove` - CoT + human-provided answers to probing questions

**Convergence Settings**:
- Max iterations: 10
- Early stopping: Rating unchanged for 3 consecutive iterations
- Success threshold: "Hire" or better (rating score >= 3)

**Dataset**:
- Source: 50 behavioral interview Q&A pairs (same as Exp 1)
- Initial distribution: 25 "Leaning No Hire", 25 "Hire"

### 1.2 Metrics

**Primary Metrics**:
1. **Success Rate by Iteration**: % of answers reaching "Hire" or better at each iteration
2. **Convergence Iteration**: When rating first stabilized (0 = initial, 1 = after first improvement)
3. **Ceiling Comparison**: Final rating comparison between methods

---

## 2. Results

### 2.1 Success Rate by Iteration

| Iteration | Automated | Human-in-Loop |
|-----------|-----------|---------------|
| 0 (Initial) | 50.0% | 50.0% |
| 1 | 86.0% | 90.0% |
| 2 | 86.0% | 90.0% |
| 3 | 92.0% | **100.0%** |
| 4+ | 92.0% | 100.0% |

**Key Observations**:
- Both methods improve significantly at iteration 1
- Human-in-Loop reaches 100% success by iteration 3
- Automated plateaus at 92%
- Both flatten quickly - more iterations don't help

### 2.2 Convergence Statistics

| Metric | Automated | Human-in-Loop |
|--------|-----------|---------------|
| Mean Convergence Iteration | 0.54 | 0.70 |
| Converged | 50/50 (100%) | 50/50 (100%) |

**Statistical Tests**:
- Paired t-test: t=1.84, p=0.071 (not significant)
- Both methods converge very quickly (mean <1 iteration)

### 2.3 Ceiling Comparison

| Outcome | Count |
|---------|-------|
| Human-in-Loop higher | 4 |
| Automated higher | 0 |
| Same final rating | 46 |

Human-in-Loop never performs worse than Automated, and outperforms in 4 cases.

---

## 3. Key Findings

### 3.1 Rapid Convergence

**Finding**: Both methods converge within 1-2 iterations on average.

**Evidence**:
- Mean convergence: Automated 0.54, Human-in-Loop 0.70
- 100% of answers converged before max iterations

**Implication**: Running more iterations does not improve results. The limitation is not compute.

### 3.2 Context Matters More Than Iterations

**Finding**: Human-in-Loop reaches higher success rate (100% vs 92%) despite similar convergence speed.

**Evidence**:
- At iteration 1: Human-in-Loop 90% vs Automated 86%
- At iteration 3+: Human-in-Loop 100% vs Automated 92%
- Gap persists regardless of iterations

**Implication**: The advantage comes from having real context (hidden details), not from running more iterations.

### 3.3 Diminishing Returns

**Finding**: Both methods show diminishing returns after iteration 1.

**Evidence**:
- Automated: 50% → 86% (iter 1) → 92% (iter 3) - most gain at iter 1
- Human-in-Loop: 50% → 90% (iter 1) → 100% (iter 3) - most gain at iter 1

**Implication**: If improvement doesn't happen in first 1-2 iterations, more iterations won't help.

---

## 4. Conclusions

1. **Both methods converge rapidly** - mean <1 iteration, 100% converged
2. **Human-in-Loop reaches higher ceiling** - 100% vs 92% success rate
3. **More iterations don't close the gap** - limitation is context, not compute
4. **First iteration is critical** - most improvement happens at iteration 1

---

## Appendix

### A. Files

- Results: `exp2_results/exp2_convergence_results.json`
- Figure: `exp2_results/analysis/exp2_success_rate_by_iteration.png`
- Table: `exp2_results/analysis/exp2_table1_convergence.md`

### B. Code

- Experiment: `exp2_convergence.py`
- Visualization: `exp2_visualization.py`

---

**Report Generated**: 2025-12-26
**Experiment Status**: Completed
