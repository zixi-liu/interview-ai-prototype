# Experimental Plan for Paper Revision

> Comprehensive experimental plan to address review feedback and strengthen empirical validation

**Based on:** Review feedback from `paper/review_feedbacks/feedback-20251224.md`  
**Goal:** Add quantitative experiments, human evaluation, and statistical analysis to support all three findings  
**Timeline:** 4-6 months for comprehensive experiments

---

## Overview

This plan addresses the critical gaps identified in the review:
1. **Finding 1**: Quantitative comparison of Human-in-the-Loop vs Automated
2. **Finding 2**: Convergence analysis with statistical evidence
3. **Finding 3**: Adversarial challenging validation with human evaluators

---

## Experiment 1: Finding 1 - Human-in-the-Loop Effectiveness

### 1.1 Objective
Quantitatively compare `StorySelfImprove` (automated CoT) vs `HumanInLoopImprove` (CoT + human input) to explore the mechanisms, value propositions, and trade-offs of human-in-the-loop approaches. The experiment investigates whether and under what conditions human-in-the-loop provides advantages in training effectiveness and customization, with effectiveness potentially depending on participant quality and context.

### 1.2 Experimental Design

#### Dataset
- **Source**: `awesome-behavioral-interviews/answers.toml` (50 Q&A pairs)
- **Selection**: 
  - Use all 50 answers as initial dataset
  - Stratify by initial rating: ~20 "Leaning No Hire", ~20 "Hire", ~10 "Strong Hire"
  - Ensure diversity across question types (conflict, failure, leadership, etc.)

#### Experimental Groups
1. **Group A (Automated)**: `StorySelfImprove` - pure CoT, no human input
2. **Group B (Human-in-Loop)**: `HumanInLoopImprove` - CoT + human-provided probing answers

#### Procedure
1. **Initial Evaluation**: Evaluate all 50 answers using `BQQuestions.real_interview()` + `bar_raiser()`
2. **Group A Processing**:
   - Run `StorySelfImprove.run()` on each answer
   - Record: iterations, final rating, improved answer
3. **Group B Processing**:
   - For each answer, extract probing questions from initial feedback
   - **Human Input Collection**: Recruit 20-30 participants (actual candidates or volunteers)
   - Each participant answers probing questions for 2-3 answers
   - Run `HumanInLoopImprove.run_with_predefined_answers()` with human-provided answers
   - Record: iterations, final rating, improved answer, probing Q&A pairs

#### Metrics
1. **Rating Improvement**:
   - Rating score change (0-4 scale: No Hire=0, Leaning No Hire=1, Leaning Hire=2, Hire=3, Strong Hire=4)
   - Percentage reaching "Strong Hire"
   - Average rating improvement

2. **Training Effectiveness** (for Group B only):
   - Pre/post survey: self-reported confidence (1-5 scale)
   - Recall test: Can candidate recall improved answer details after 1 week?
   - Authenticity score: Self-reported authenticity (1-5 scale)

3. **Customization**:
   - Answer uniqueness: Compare improved answers across participants for same original answer
   - Personal detail integration: Count of personal experiences/metrics added

4. **Efficiency**:
   - Iterations to reach "Strong Hire"
   - Time to complete improvement process

### 1.3 Implementation Steps

#### Step 1: Prepare Dataset
```python
# File: paper/experiment/exp1_prepare_dataset.py
# - Load answers.toml
# - Initial evaluation of all 50 answers
# - Save initial ratings and feedback
# - Stratify by rating for balanced groups
```

#### Step 2: Run Automated Group
```python
# File: paper/experiment/exp1_automated.py
# - For each answer in Group A:
#   - Initialize StorySelfImprove
#   - Run improvement (max 5 iterations)
#   - Record: iterations, ratings at each iteration, final answer
# - Save results to exp1_automated_results.json
```

#### Step 3: Collect Human Input
```python
# File: paper/experiment/exp1_collect_human_input.py
# - Extract probing questions for each answer
# - Create survey/interface for participants
# - Collect answers to probing questions
# - Save to exp1_human_input.json
```

#### Step 4: Run Human-in-Loop Group
```python
# File: paper/experiment/exp1_human_in_loop.py
# - For each answer in Group B:
#   - Load human-provided probing answers
#   - Run HumanInLoopImprove.run_with_predefined_answers()
#   - Record: iterations, ratings, final answer
# - Save results to exp1_human_in_loop_results.json
```

#### Step 5: Analysis
```python
# File: paper/experiment/exp1_analysis.py
# - Compare rating improvements (t-test, effect size)
# - Compare iterations to convergence
# - Analyze training effectiveness metrics
# - Generate comparison tables and visualizations
```

### 1.4 Expected Outputs
- **Table 1**: Rating improvement comparison (Group A vs Group B)
- **Table 2**: Training effectiveness metrics (Group B)
- **Figure 1**: Rating improvement distribution
- **Statistical tests**: t-test, effect size (Cohen's d)

### 1.5 Success Criteria (Tiered)

**Tier 1 (Ideal - if results support hypothesis):**
- **Statistically significant** difference in rating improvement (p < 0.05)
- **Effect size** ≥ 0.5 (medium effect)
- **Training effectiveness**: ≥70% participants report improved confidence
- **Customization**: ≥80% answers show unique personal details

**Tier 2 (Acceptable - if results are directionally consistent):**
- Directionally consistent difference (p < 0.10) OR no significant difference but effect size ≥ 0.3
- **Effect size** ≥ 0.3 (small to medium effect)
- **Training effectiveness**: ≥50% participants report improved confidence
- **Customization**: ≥60% answers show unique personal details
- Qualitative evidence supports value proposition

**Tier 3 (Exploratory - if results differ from hypothesis):**
- No significant difference or opposite direction, but:
  - Mechanism analysis reveals valuable insights
  - Trade-offs and value propositions are clearly identified
  - Case studies demonstrate context-dependent effectiveness
  - Results inform when to use each approach

**Interpretation Strategy:**
- If Tier 1: Report full quantitative evidence supporting human-in-the-loop advantages
- If Tier 2: Report quantitative evidence with emphasis on mechanisms and value dimensions
- If Tier 3: Shift focus to mechanism analysis, trade-offs, and context-dependent recommendations

**Note:** All outcomes are valuable. The experiment aims to understand mechanisms and trade-offs, not just prove superiority.

### 1.6 Risk Mitigation and Contingency Plans

**Major Risks:**
1. **Participant Quality Variability**: Human participants may provide varying quality of input, affecting Group B results
2. **Non-Significant Results**: Results may not show statistically significant differences between groups
3. **Opposite Results**: Automated approach may outperform human-in-the-loop in rating improvement
4. **Sample Size Limitations**: 50 answers may not provide sufficient statistical power for all comparisons

**Mitigation Strategies:**
1. **Participant Screening**: 
   - Require participants with interview experience or relevant background
   - Set quality thresholds for participant responses
   - Provide training and guidance on providing detailed, authentic answers

2. **Quality Control**:
   - Score each response for quality (detail level, authenticity, specificity)
   - Exclude obviously low-quality responses from analysis
   - Implement multi-round validation for critical responses

3. **Sample Size Management**:
   - Conduct pilot study first (10 answers, 5-10 participants)
   - Adjust sample size based on pilot results and power analysis
   - Use power analysis to determine required sample size for desired effect size

4. **Result Interpretation Strategy**:
   - **If significant (Tier 1)**: Report full quantitative evidence supporting human-in-the-loop advantages
   - **If directionally consistent but not significant (Tier 2)**: Report effect size, confidence intervals, and qualitative analysis; discuss sample size limitations
   - **If opposite or no difference (Tier 3)**: 
     - Analyze reasons (participant quality, answer types, etc.)
     - Discuss limitations honestly
     - Emphasize mechanism insights and value dimensions beyond rating improvement
     - Provide context-dependent recommendations
   - **All outcomes provide valuable contributions** to understanding mechanisms, trade-offs, and when to use each approach

---

## Experiment 2: Finding 2 - Convergence Analysis

### 2.1 Objective
Quantitatively demonstrate that CoT prompting converges rapidly in interview scenarios, with minimal improvement beyond the first iteration.

### 2.2 Experimental Design

#### Dataset
- **Source**: `awesome-behavioral-interviews/answers.toml` (50 Q&A pairs)
- **Selection**: All 50 answers, stratified by initial rating

#### Convergence Definition
- **Primary Metric**: Rating stability
  - Convergence = rating remains unchanged for 3 consecutive iterations
- **Secondary Metrics**:
  - Rating score change per iteration (should approach 0)
  - Answer quality metrics (if available)

#### Procedure
1. **Extended Iteration Test**:
   - Run `StorySelfImprove.run()` with max_iterations = 100 (modify class to allow this)
   - For each answer, record:
     - Rating at each iteration (1, 2, 3, ..., 100)
     - Answer text at each iteration
     - Convergence iteration (when rating stabilizes)

2. **Statistical Analysis**:
   - Compare rating at iteration 1 vs iteration 100 (paired t-test)
   - Analyze convergence iteration distribution
   - Test if iteration 1 ≈ iteration 100 (equivalence test)

3. **Cross-Level Analysis**:
   - Analyze convergence behavior across:
     - Different initial ratings (Leaning No Hire vs Hire)
     - Different question types
     - Different answer lengths

### 2.3 Implementation Steps

#### Step 1: Modify StorySelfImprove for Extended Iterations
```python
# Modify advance/self_improve.py
# - Add parameter: max_iterations (default 5, allow up to 100)
# - Add logging: record rating at each iteration
# - Save iteration history
```

#### Step 2: Run Extended Iterations
```python
# File: paper/experiment/exp2_convergence.py
# - For each of 50 answers:
#   - Run StorySelfImprove with max_iterations=100
#   - Record rating at iterations: 1, 2, 3, 5, 10, 20, 50, 100
#   - Detect convergence iteration
# - Save to exp2_convergence_results.json
```

#### Step 3: Statistical Analysis
```python
# File: paper/experiment/exp2_analysis.py
# - Paired t-test: iteration 1 vs iteration 100 ratings
# - Equivalence test: test if difference < threshold
# - Convergence iteration analysis (mean, median, distribution)
# - Subgroup analysis (by initial rating, question type)
```

#### Step 4: Visualization
```python
# File: paper/experiment/exp2_visualization.py
# - Convergence curves: rating over iterations (line plot)
# - Convergence iteration distribution (histogram)
# - Box plot: rating change from iteration 1 to 100
```

### 2.4 Expected Outputs
- **Figure 2**: Convergence curves (rating over iterations, multiple answers)
- **Figure 3**: Convergence iteration distribution
- **Table 3**: Statistical comparison (iteration 1 vs 100)
- **Table 4**: Convergence by initial rating/question type

### 2.5 Success Criteria
- **No significant difference** between iteration 1 and 100 (p > 0.05)
- **Mean convergence iteration** ≤ 2
- **≥90% answers** converge within 3 iterations
- **Equivalence test** confirms iteration 1 ≈ iteration 100

---

## Experiment 3: Finding 3 - Adversarial Challenging Validation

### 3.1 Objective
Quantitatively validate that `bar_raiser()` (adversarial challenging) is necessary for realistic evaluation that matches real interviewer behavior.

### 3.2 Experimental Design

#### Dataset
- **Source**: `awesome-behavioral-interviews/answers.toml` (50 Q&A pairs)
- **Human Evaluators**: Recruit 5-10 FAANG interviewers or experienced interviewers

#### Experimental Conditions
1. **Condition A (Without bar_raiser)**: `BQQuestions.real_interview()` only
2. **Condition B (With bar_raiser)**: `BQQuestions.real_interview()` + `bar_raiser()`
3. **Condition C (Human Evaluators)**: Real FAANG interviewers evaluate same answers

#### Procedure
1. **LLM Evaluation**:
   - Evaluate all 50 answers under Condition A (no bar_raiser)
   - Evaluate all 50 answers under Condition B (with bar_raiser)
   - Record ratings and detailed feedback

2. **Human Evaluation**:
   - Each human evaluator evaluates 10-15 answers (randomly assigned)
   - Use same evaluation rubric (FAANG standards)
   - Record ratings and feedback
   - Ensure inter-evaluator agreement (each answer evaluated by 2-3 evaluators)

3. **Ablation Study**:
   - Test each `bar_raiser()` component separately:
     - Negativity Bias only
     - Ownership Tracing only
     - Scope Validation only
     - Data-Driven Requirement only
     - Industry Context only
   - Evaluate subset of answers (20 answers) with each component

4. **Comparison Analysis**:
   - Compare Condition A vs Condition B (LLM with/without bar_raiser)
   - Compare Condition B vs Condition C (LLM with bar_raiser vs Human)
   - Measure agreement (Cohen's kappa, correlation)

### 3.3 Implementation Steps

#### Step 1: LLM Evaluation (With/Without bar_raiser)
```python
# File: paper/experiment/exp3_llm_evaluation.py
# - Condition A: Evaluate all 50 answers without bar_raiser()
# - Condition B: Evaluate all 50 answers with bar_raiser()
# - Save ratings and feedback to exp3_llm_results.json
```

#### Step 2: Ablation Study
```python
# File: paper/experiment/exp3_ablation.py
# - Create modified bar_raiser() functions (one component at a time)
# - Evaluate 20 answers with each variant
# - Save to exp3_ablation_results.json
```

#### Step 3: Human Evaluation Collection
```python
# File: paper/experiment/exp3_human_evaluation.py
# - Create evaluation interface/survey
# - Assign answers to evaluators (random, balanced)
# - Collect ratings and feedback
# - Save to exp3_human_results.json
```

#### Step 4: Analysis
```python
# File: paper/experiment/exp3_analysis.py
# - Compare Condition A vs B (t-test, rating distribution)
# - Compare Condition B vs C (agreement: Cohen's kappa, correlation)
# - Ablation analysis: which components matter most?
# - Rating distribution analysis
```

### 3.4 Metrics

1. **Rating Distribution**:
   - Distribution of ratings (No Hire to Strong Hire)
   - Compare: without bar_raiser (should be optimistic) vs with bar_raiser vs human

2. **Agreement Metrics**:
   - Cohen's kappa: LLM (with bar_raiser) vs Human evaluators
   - Pearson correlation: rating scores
   - Inter-evaluator agreement (for human evaluators)

3. **Realism Metrics**:
   - Rating distribution similarity (KL divergence)
   - Mean rating difference
   - Percentage of "Strong Hire" (should be lower with bar_raiser)

4. **Ablation Metrics**:
   - Component importance: rating change when component removed
   - Statistical significance of each component

### 3.5 Expected Outputs
- **Table 5**: Rating distribution comparison (A vs B vs C)
- **Table 6**: Agreement metrics (LLM vs Human)
- **Table 7**: Ablation study results
- **Figure 4**: Rating distribution histograms
- **Figure 5**: Agreement scatter plots

### 3.6 Success Criteria
- **Significant difference** between Condition A and B (p < 0.05)
- **High agreement** between Condition B and C (kappa ≥ 0.6, correlation ≥ 0.7)
- **Ablation shows** all components contribute significantly
- **Rating distribution** with bar_raiser matches human evaluators better

---

## Experiment 4: Additional Supporting Experiments

### 4.1 Dataset Description and Statistics

#### Objective
Provide comprehensive dataset description for reproducibility.

#### Procedure
1. **Dataset Statistics**:
   - Total answers: 50
   - Question types distribution
   - Answer length distribution
   - Initial rating distribution
   - Level distribution (Junior-Mid, Senior, Staff)

2. **Data Collection Details**:
   - Source: `awesome-behavioral-interviews/answers.toml`
   - Collection method: Extracted from public repository
   - Preprocessing: None (used as-is)

#### Output
- **Table 8**: Dataset statistics
- **Figure 6**: Dataset distribution visualizations

### 4.2 Model and Hyperparameter Specifications

#### Objective
Document all implementation details for reproducibility.

#### Information to Document
1. **LLM Model**:
   - Model: GPT-4o-mini (or specify actual model)
   - API: OpenAI API
   - Temperature: 0.3 (for evaluation), 0.7 (for generation)
   - Max tokens: (specify)

2. **System Configuration**:
   - Python version
   - Dependencies (requirements.txt)
   - Random seeds: (if applicable, set to fixed value)

3. **Evaluation Parameters**:
   - Level: "Junior-Mid" (or specify)
   - Max iterations: 5 (default), 100 (for convergence test)
   - Evaluation prompt: `BQQuestions.real_interview()` + `bar_raiser()`

#### Output
- **Section in Methodology**: Detailed implementation specifications

### 4.3 Error Analysis

#### Objective
Analyze failure cases and common error patterns.

#### Procedure
1. **Identify Failure Cases**:
   - Answers that don't improve after iterations
   - Answers with inconsistent ratings
   - Answers where human-in-loop fails

2. **Error Pattern Analysis**:
   - Common weaknesses in answers
   - Evaluation inconsistencies
   - Improvement failures

#### Output
- **Section in Results**: Error analysis with examples

---

## Implementation Timeline

### Phase 1: Setup and Preparation (Week 1-2)
- [ ] Set up experiment infrastructure
- [ ] Prepare dataset and initial evaluations
- [ ] Modify code for extended iterations
- [ ] Create data collection interfaces

### Phase 2: Experiment 1 - Human-in-the-Loop (Week 3-6)
- [ ] Run automated group (Group A)
- [ ] Recruit participants and collect human input
- [ ] Run human-in-loop group (Group B)
- [ ] Analyze results

### Phase 3: Experiment 2 - Convergence (Week 7-8)
- [ ] Run extended iteration experiments (100 iterations)
- [ ] Statistical analysis
- [ ] Generate convergence visualizations

### Phase 4: Experiment 3 - Adversarial Challenging (Week 9-12)
- [ ] LLM evaluation (with/without bar_raiser)
- [ ] Ablation study
- [ ] Recruit human evaluators
- [ ] Collect human evaluations
- [ ] Analysis and agreement metrics

### Phase 5: Additional Experiments (Week 13-14)
- [ ] Dataset statistics
- [ ] Error analysis
- [ ] Documentation of implementation details

### Phase 6: Paper Revision (Week 15-16)
- [ ] Integrate results into paper
- [ ] Create figures and tables
- [ ] Write methodology section
- [ ] Update findings section with quantitative evidence

---

## Required Resources

### Computational
- OpenAI API access (for LLM calls)
- Estimated cost: ~$50-100 for all experiments
- Storage: ~1GB for results and logs

### Human Resources
- **Participants for Human-in-Loop**: 20-30 people (candidates or volunteers)
- **Human Evaluators**: 5-10 FAANG interviewers or experienced interviewers
- **Time commitment**: 
  - Participants: ~30 minutes each
  - Evaluators: ~2-3 hours each

### Tools and Infrastructure
- Python environment with dependencies
- Data collection platform (survey tool or custom interface)
- Statistical analysis tools (Python: scipy, statsmodels)

---

## Code Structure

```
paper/experiment/
├── plan.md (this file)
├── exp1_prepare_dataset.py
├── exp1_automated.py
├── exp1_collect_human_input.py
├── exp1_human_in_loop.py
├── exp1_analysis.py
├── exp2_convergence.py
├── exp2_analysis.py
├── exp2_visualization.py
├── exp3_llm_evaluation.py
├── exp3_ablation.py
├── exp3_human_evaluation.py
├── exp3_analysis.py
├── utils/
│   ├── data_loader.py
│   ├── evaluator.py
│   └── statistics.py
└── results/
    ├── exp1_automated_results.json
    ├── exp1_human_in_loop_results.json
    ├── exp2_convergence_results.json
    ├── exp3_llm_results.json
    ├── exp3_ablation_results.json
    └── exp3_human_results.json
```

---

## Success Metrics Summary

### Experiment 1 (Human-in-the-Loop)

**Primary Metrics (to be determined by results):**
- **Statistical significance**: p-value from independent t-test (target: p < 0.05, but accept p < 0.10 if directionally consistent)
- **Effect size**: Cohen's d (report regardless of significance; target: ≥ 0.5, acceptable: ≥ 0.3)
- **Training effectiveness**: % participants reporting improved confidence (target: ≥70%, acceptable: ≥50%)
- **Customization**: % answers showing unique personal details (target: ≥80%, acceptable: ≥60%)

**Interpretation:**
- Results will determine whether findings support, partially support, or differ from initial hypothesis
- All outcomes (including non-significant or opposite results) provide valuable insights into mechanisms and trade-offs
- Focus on understanding **when and why** each approach is effective, not just proving superiority

### Experiment 2 (Convergence)
- ✅ No significant difference iteration 1 vs 100 (p > 0.05)
- ✅ Mean convergence iteration ≤ 2
- ✅ ≥90% answers converge within 3 iterations

### Experiment 3 (Adversarial Challenging)
- ✅ Significant difference with/without bar_raiser (p < 0.05)
- ✅ High agreement with human evaluators (kappa ≥ 0.6)
- ✅ All ablation components show significant contribution

---

## Notes

1. **IRB Approval**: May be needed for human participant studies (check institutional requirements)

2. **Data Privacy**: Ensure participant data is anonymized and stored securely

3. **Reproducibility**: 
   - Set random seeds where applicable
   - Document all hyperparameters
   - Save all intermediate results

4. **Quality Control**:
   - Validate human input quality
   - Check for outliers in results
   - Ensure inter-evaluator agreement is acceptable

5. **Iterative Refinement**:
   - Start with pilot studies (smaller N)
   - Refine procedures based on initial results
   - Scale up to full experiments

---

## Next Steps

1. **Review this plan** with co-authors
2. **Set up experiment infrastructure**
3. **Begin Phase 1** (Setup and Preparation)
4. **Recruit participants and evaluators** early (can be done in parallel with setup)
5. **Run pilot studies** before full experiments

---

**Last Updated:** 2025-12-24  
**Status:** Planning Phase  
**Next Review:** After Phase 1 completion

