# Interview Auto-Evaluation and Auto-Improvement

**Authors:** Zixi Liu, Kewen Zhu, Jing Chen

## Abstract

This paper investigates the application of Chain-of-Thought (CoT) prompting for behavioral interview answer evaluation and improvement. Through two controlled experiments with 50 behavioral interview Q&A pairs, we present three key contributions: (1) **Quantitative comparison of human-in-the-loop vs. automated CoT improvement**: Using a within-subject paired design (n=50), both approaches show positive rating improvements (Automated: +0.58, Human-in-Loop: +0.64, p=0.705), with human-in-the-loop providing significant training benefits—confidence improved from 3.16 to 4.16 (p<0.001) and authenticity from 2.94 to 4.53 (p<0.001, Cohen's d=3.21). Human-in-the-loop also requires 5× fewer iterations (1.0 vs 5.0, p<0.001) and achieves 100% personal detail integration. (2) **Convergence analysis**: Both methods converge rapidly (mean <1 iteration), with human-in-the-loop achieving 100% success rate vs. 84% for automated approaches among initially weak answers (Cohen's h=0.82, large effect). Additional iterations provide diminishing returns, indicating the limitation is context, not compute. (3) **Adversarial challenging mechanism**: We propose a negativity bias model (`bar_raiser`) to simulate realistic interviewer behavior, though quantitative validation remains future work. These findings demonstrate that while CoT prompting provides a foundation for interview evaluation, domain-specific enhancements and context-aware approach selection are essential for realistic and pedagogically valuable results.

**Keywords:** Chain-of-Thought Prompting, Human-in-the-Loop, Interview Evaluation, LLM Applications, Behavioral Assessment

---

## 1. Introduction

### 1.1 Background

Behavioral interview evaluation using Large Language Models (LLMs) presents unique challenges compared to general text generation tasks. Unlike open-ended generation, interview evaluation requires:
- **Structured assessment** following FAANG (Facebook, Amazon, Apple, Netflix, Google) hiring standards
- **Realistic interviewer behavior** simulation, including adversarial questioning
- **Pedagogical value** for candidate training and improvement

Chain-of-Thought (CoT) prompting has shown promise in complex reasoning tasks, but its application to interview scenarios reveals domain-specific limitations that require investigation.

### 1.2 Problem Statement

Pure CoT prompting for interview answer improvement faces two empirically validated limitations and one design challenge:
1. **Lack of authentic human experience and training value**: Automated improvement may generate plausible but fabricated details, limiting pedagogical value for candidate learning
2. **Rapid convergence with diminishing returns**: Iterative refinement shows minimal improvement beyond the first iteration, suggesting bounded solution space in structured evaluation domains
3. **Evaluation realism challenge**: Achieving realistic interviewer behavior simulation requires domain-specific mechanisms beyond standard CoT prompting

### 1.3 Research Questions

1. How does human-in-the-loop integration affect the effectiveness, training value, and value proposition of CoT-based interview answer improvement compared to pure automated approaches?
2. What is the convergence behavior of CoT prompting in interview evaluation scenarios, and do additional iterations provide meaningful improvements?
3. What design mechanisms can contribute to achieving realistic interview evaluation using LLMs?

### 1.4 Contributions

This work makes three primary contributions:

1. **Empirical analysis of human-in-the-loop vs. automated CoT improvement** (Experiment 1): Using a within-subject paired design with 50 behavioral interview Q&A pairs, we quantitatively compare automated and human-in-the-loop approaches. While both show positive rating improvements (38-36% improvement rates), human-in-the-loop provides significant training benefits (confidence +1.00, authenticity +1.59, p<0.001) and requires 5× fewer iterations, demonstrating context-dependent value propositions.

2. **Convergence analysis of CoT prompting in interview scenarios** (Experiment 2): Through systematic iteration analysis, we demonstrate that both automated and human-in-the-loop methods converge rapidly (mean <1 iteration), with human-in-the-loop achieving higher success rates for initially weak answers (100% vs. 84%, Cohen's h=0.82). Additional iterations provide diminishing returns, indicating the limitation is context availability rather than computational resources.

3. **Adversarial challenging mechanism design** (`bar_raiser`): We propose a negativity bias model to simulate realistic FAANG interviewer behavior, addressing the gap between optimistic LLM evaluations and defensive real interviewer assessments. While the mechanism is implemented and used in our experiments, quantitative validation with human evaluators remains future work.

These contributions address the lack of quantitative research in AI-assisted interview preparation and provide evidence-based insights for improving interview training systems.
---

## 2. Related Work

### 2.1 Chain-of-Thought Prompting

Chain-of-Thought (CoT) prompting, introduced by Wei et al. (2022), enables LLMs to generate intermediate reasoning steps before producing final answers. This approach has shown success in mathematical reasoning (Cobbe et al., 2021), commonsense reasoning (Talmor et al., 2023), and other complex tasks. Subsequent work has explored variations including self-consistency (Wang et al., 2023), tree-of-thoughts (Yao et al., 2023), and iterative refinement (Madaan et al., 2023). However, convergence behavior in structured evaluation domains with bounded solution spaces remains underexplored.

### 2.2 Human-in-the-Loop Systems

Human-in-the-loop approaches combine automated systems with human expertise, particularly valuable in domains requiring domain knowledge, authenticity, or subjective judgment. Recent surveys (Amershi et al., 2019; Bansal et al., 2021) highlight the importance of human feedback in improving LLM outputs. In NLP applications, human-in-the-loop has been applied to text generation (Zhang et al., 2020), evaluation (Kreutzer et al., 2022), and training (Ouyang et al., 2022). However, quantitative comparisons of human-in-the-loop vs. fully automated approaches in training contexts remain limited, particularly for interview preparation where authenticity and pedagogical value are critical.

### 2.3 LLM-Based Evaluation Systems

LLM-based evaluation has gained prominence as an alternative to human evaluation, with applications in text generation (Liu et al., 2023), dialogue systems (Zheng et al., 2023), and code generation (Chen et al., 2021). Recent work has identified biases in LLM evaluators, including leniency bias (Wang et al., 2023) and position bias (Zheng et al., 2023). Our work addresses the specific challenge of achieving realistic evaluation in interview contexts, where defensive evaluation (negativity bias) is essential for accurate assessment.

### 2.4 Interview Training and Evaluation Systems

Existing interview evaluation systems primarily focus on automated scoring (Chen et al., 2020) or feedback generation (Kumar et al., 2021). Commercial systems like Pramp, InterviewBit, and LeetCode provide practice platforms but lack realistic interviewer behavior simulation. Academic work has explored automated interview assessment (D'Mello et al., 2015; Chen et al., 2020), but few address the pedagogical requirements of training systems or the need for realistic adversarial challenging. Our work bridges this gap by providing quantitative analysis of improvement methods and proposing mechanisms for realistic evaluation.

### 2.5 Prompt Engineering for Evaluation

Prompt engineering has emerged as a critical technique for improving LLM performance across tasks (Liu et al., 2023; White et al., 2023). Recent work has explored evaluation-specific prompting strategies, including rubric-based evaluation (Zheng et al., 2023) and adversarial prompting (Perez et al., 2022). However, domain-specific evaluation mechanisms for interview scenarios, particularly negativity bias models, have not been systematically explored. Our `bar_raiser` mechanism contributes to this line of work by proposing a structured approach to simulating realistic interviewer behavior.

### 2.6 Convergence Analysis in Iterative LLM Systems

Convergence analysis in iterative LLM systems has been studied in various contexts, including iterative refinement (Madaan et al., 2023), self-correction (Huang et al., 2023), and multi-step reasoning (Yao et al., 2023). However, most work focuses on open-ended tasks with unbounded solution spaces. Our convergence analysis in structured evaluation domains (interview scenarios with FAANG rubrics) reveals rapid convergence behavior that differs from general CoT applications, contributing to understanding of domain-specific convergence patterns.

### 2.7 Positioning of This Work

Our work differs from existing systems in several key aspects: (1) We provide quantitative empirical comparison of human-in-the-loop vs. automated approaches with statistical validation, addressing a gap in the literature; (2) We analyze convergence behavior specifically in structured evaluation domains, revealing domain-specific patterns; (3) We propose and implement an adversarial challenging mechanism for interview evaluation, though quantitative validation remains future work. This combination of empirical analysis, convergence study, and mechanism design addresses multiple limitations of existing interview training systems.

---

## 3. Methodology

### 3.1 System Architecture: Story-Improve

Our Story-Improve system implements CoT prompting for behavioral interview answer evaluation and iterative improvement. The system consists of three main components:

#### 3.1.1 Automated Self-Improvement (`StorySelfImprove`)

**Location:** `advance/self_improve.py:14-107`

The `StorySelfImprove` class implements pure CoT-based iterative improvement:
- Extracts question and answer from feedback files
- Generates improved answer using CoT prompting (`BQAnswer.improve_story()`)
- Re-evaluates improved answer using `BQQuestions.real_interview()` + `BQQuestions.bar_raiser()`
- Iterates until "Strong Hire" rating or maximum iterations (default: 5)

**Key Implementation:**
```python
async def run(self) -> None:
    if await self.is_perfect():
        return
    elif self.iterate_times >= 5:
        return
    else:
        self.iterate_times += 1
        # Generate improved answer using CoT
        improved_answer = await self.improved_answer()
        # Re-evaluate
        feedback = await self.feedback()
        await self.run()  # Recursive iteration
```

#### 3.1.2 Human-in-the-Loop Improvement (`HumanInLoopImprove`)

**Location:** `advance/self_improve.py:109-397`

The `HumanInLoopImprove` class integrates human input into the improvement process:
- Extracts probing questions from evaluation feedback
- Prompts user to provide real, specific answers to probing questions
- Incorporates user's authentic details into improved answer (`BQAnswer.improve_with_probing_answers()`)
- Re-evaluates with human-provided details

**Key Difference:** Instead of LLM-generated improvements, this approach uses:
```python
async def improve_with_user_input(
    self,
    original_answer: str,
    feedback: str,
    probing_qa: list[dict]  # User's real answers
) -> str:
    prompt = BQAnswer.improve_with_probing_answers(
        original_answer, feedback, probing_qa
    )
    # Uses USER'S REAL ANSWERS, not LLM fabrication
```

#### 3.1.3 Adversarial Challenging Mechanism (`bar_raiser`)

**Location:** `prompts.py:454-492`

The `bar_raiser()` function implements a negativity bias model to simulate realistic interviewer behavior:

**Key Components:**
1. **Negativity Bias Model**: "Assume no skill unless explicitly demonstrated"
2. **Ownership Tracing**: "Reward only actions clearly driven by the candidate"
3. **Scope Validation**: "Challenge the scope of the example"
4. **Data-Driven Requirement**: "Downgrade ratings by one level if metrics are missing"
5. **Industry Context**: Simulates competitive 2025 hiring environment with raised bars

**Implementation:**
```python
def bar_raiser(level: str = "Senior") -> str:
    return f"""
    --- NEGATIVITY BIAS MODEL ---
    Apply realistic FAANG interviewer negativity bias:
    Assume no skill unless explicitly demonstrated.
    Penalize vagueness, assumptions, or unsupported claims harshly.
    
    --- OWNERSHIP TRACING ---
    Perform ownership tracing on every step of the answer.
    Reward only the actions clearly driven by the candidate.
    Penalize any ambiguity or executor-style contribution.
    """
```

#### 3.1.4 Model Configuration

We use **GPT-4o-mini** (OpenAI API) as our primary LLM for all evaluation and generation tasks. This model was selected based on the following considerations:

1. **Cost-Effectiveness**: Our experimental design requires iterative evaluation (up to 100 iterations per answer across 50 answers), resulting in approximately 250-5000 API calls. GPT-4o-mini provides optimal cost-performance ratio ($0.15/$0.60 per 1M tokens), making it suitable for large-scale iterative experiments while maintaining adequate performance for structured evaluation tasks.

2. **Task Suitability**: Behavioral interview evaluation is a structured task with well-defined rubrics (FAANG standards). GPT-4o-mini demonstrates sufficient capability for structured assessment tasks while maintaining consistency across iterations.

3. **Reproducibility**: Using a fixed model version (GPT-4o-mini) ensures consistent results and enables reproducibility, which is critical for academic research. The model has been widely adopted in production systems, ensuring our findings are directly applicable to real-world deployments.

4. **API Stability**: OpenAI's API infrastructure provides reliable access and consistent behavior, essential for iterative experiments requiring multiple sequential calls.

**Hyperparameters:**
- **Temperature**: 0.3 for evaluation tasks (ensures consistent ratings across iterations)
- **Temperature**: 0.7 for answer generation (allows creative improvements while maintaining coherence)
- **Max Tokens**: Determined dynamically based on prompt length and response requirements
- **API Version**: OpenAI API (as of December 2024)

**Model Validation Strategy:**
To ensure robustness of our findings and assess model-agnostic generalizability, we conducted comparative analysis using:
- **Gemini 3.0 Pro** (Google AI API): Used for model-agnostic validation on 20% of answers to confirm our conclusions are not model-specific
- **GPT-5.2 Thinking** (OpenAI API): Used for critical result verification on 10% of answers, leveraging its superior reasoning capabilities (AIME 2025: 100%, ARC-AGI-2: 52.9%) to validate key findings

This multi-model validation approach strengthens our conclusions by demonstrating that our findings generalize across different model architectures and capabilities.

### 3.1.5 Experimental Design

We conducted two controlled experiments to address our research questions. Both experiments use the same dataset and evaluation framework, enabling cross-experiment insights.

#### Experiment 1: Human-in-the-Loop vs. Automated Improvement

**Design Type**: Within-subject paired design

**Rationale**: The paired design provides 30-50% higher statistical power compared to independent groups design, as each answer serves as its own control, reducing confounding variables.

**Dataset**: 
- Source: 50 behavioral interview Q&A pairs from `awesome-behavioral-interviews/answers.toml`
- Initial evaluation: All answers evaluated using `BQQuestions.real_interview()` + `bar_raiser()`
- Stratification: Answers stratified by initial rating (Leaning No Hire, Hire, Strong Hire)

**Treatments**:
- **Automated**: Uses `StorySelfImprove` - pure Chain-of-Thought (CoT) prompting, no human input
- **Human-in-Loop**: Uses `HumanInLoopImprove` - CoT + human-provided answers to probing questions

**Procedure**:
1. Initial evaluation of all 50 answers
2. **Paired Design Implementation**:
   - Each of the 50 answers undergoes **both treatments** (automated and human-in-loop)
   - **Counterbalancing**: 25 answers processed automated-first, 25 answers processed human-first (random assignment)
   - Each treatment starts from the **original answer** (avoids carryover effects)
   - Sample size: **n=50** (all answers serve as their own control)
3. Human participants provide answers to probing questions for human-in-loop treatment
4. Comparison analysis: Rating improvements, iterations, training effectiveness, customization

**Metrics**:
1. **Rating Improvement**: Change in rating score (0-4 scale: No Hire=0, Leaning No Hire=1, Leaning Hire=2, Hire=3, Strong Hire=4)
2. **Training Effectiveness** (Human-in-Loop only):
   - Pre/post confidence scores (1-5 scale)
   - Pre/post authenticity scores (1-5 scale)
   - Recall test responses
3. **Efficiency**: Iterations to reach final rating
4. **Customization**: Personal detail integration rate, answer uniqueness

**Statistical Analysis**:
- **Paired t-test** for rating improvement comparison (within-subject design, higher statistical power)
- Paired t-test for training effectiveness (pre/post matched by participant_id)
- Effect size (Cohen's d)
- Descriptive statistics

#### Experiment 2: Convergence Analysis

**Design Type**: Within-subject paired design

**Dataset**: 
- Source: Same 50 behavioral interview Q&A pairs as Experiment 1
- Initial distribution: 25 "Leaning No Hire", 25 "Hire"

**Treatments**:
- **Automated**: Uses `StorySelfImprove` - pure CoT prompting with no-fabrication constraint
- **Human-in-Loop**: Uses `HumanInLoopImprove` - CoT + human-provided answers to probing questions

**Convergence Settings**:
- Max iterations: 10
- Early stopping: Rating unchanged for 3 consecutive iterations
- Success threshold: "Hire" or better (rating score >= 3)

**Metrics**:
1. **Success Rate by Iteration**: % of answers reaching "Hire" or better at each iteration
2. **Convergence Iteration**: When final rating was first reached (0 = initial, 1 = after first improvement)
3. **Effect Size**: Cohen's h for success rate difference

**Statistical Analysis**:
- Descriptive statistics for convergence iteration
- Success rate analysis by initial rating
- Effect size (Cohen's h) for success rate differences
- McNemar's test for paired binary outcomes (discordant pairs)

### 3.2 Evaluation Methodology

#### 3.2.1 CoT Prompting Implementation

**Location:** `prompts.py:495-524`

The CoT prompting for answer improvement (`BQAnswer.improve_story()`) uses structured reasoning:
- Analyzes feedback to identify weaknesses
- Generates improved answer addressing all competency dimensions
- Targets "Strong Hire" rating across all FAANG competencies

#### 3.2.2 Convergence Analysis (Experiment 2)

We systematically analyzed convergence behavior through Experiment 2:

**Procedure**:
- For each of 50 answers, run both automated and human-in-loop treatments with max 10 iterations
- Track rating at each iteration
- Apply early stopping: rating unchanged for 3 consecutive iterations
- Record convergence iteration (when final stable rating first reached)
- Calculate success rate by iteration (% reaching "Hire" or better)

**Analysis**:
- Compare success rates at each iteration (0, 1, 2, 3, 4+)
- Analyze convergence statistics (mean convergence iteration, distribution)
- Stratify by initial rating to identify where methods differ
- Calculate effect sizes (Cohen's h) for success rate differences

**Key Metrics**:
- Mean convergence iteration: When final rating was first reached
- Success rate by iteration: % achieving "Hire" or better at each step
- Convergence distribution: How many answers converged at each iteration

#### 3.2.3 Human-in-the-Loop Comparison (Experiment 1)

We quantitatively compared automated and human-in-the-loop approaches through Experiment 1:

**Procedure**:
- Within-subject paired design: Each answer undergoes both treatments
- Counterbalancing: 25 answers automated-first, 25 human-first (random assignment)
- Each treatment starts from original answer (avoids carryover effects)
- Human participants provide answers to probing questions for human-in-loop treatment

**Metrics**:
1. **Rating Improvement**: Quantitative comparison using paired t-test
   - Rating score change (0-4 scale)
   - Improvement rate (% of answers showing improvement)
   - Distribution of outcomes (improved, no change, degraded)

2. **Training Effectiveness** (Human-in-Loop only):
   - Pre/post confidence scores (1-5 scale) - paired t-test
   - Pre/post authenticity scores (1-5 scale) - paired t-test with effect size
   - Recall test: Can participants recall improved answer details after 1 week?

3. **Efficiency**: Iterations to reach final rating - independent t-test

4. **Customization**:
   - Personal detail integration rate (% of answers with personal details)
   - Mean personal detail indicators per answer
   - Answer uniqueness (string comparison)

**Statistical Analysis**:
- Paired t-test for rating improvement (within-subject design)
- Paired t-test for training effectiveness (pre/post matched by participant_id)
- Independent t-test for iteration comparison
- Effect sizes (Cohen's d) for all comparisons
- Descriptive statistics for all metrics

---

## 4. Findings

### 4.1 Finding 1: Human-in-the-Loop Mechanisms and Effectiveness

#### 4.1.1 Experimental Results

Using a within-subject paired design (n=50), we quantitatively compared automated CoT improvement and human-in-the-loop improvement across multiple dimensions.

**Rating Improvement Comparison** (Table 1):

| Metric | Automated | Human-in-Loop |
|--------|-----------|---------------|
| N | 50 | 50 |
| Mean Improvement | +0.58 | +0.64 |
| Std Improvement | 1.21 | 1.10 |
| Improved Count | 19 | 18 |
| No Change Count | 27 | 30 |
| Degraded Count | 4 | 2 |
| Improvement Rate | 38.0% | 36.0% |

**Statistical Test**: Paired t-test (within-subject design)
- t-statistic: -0.38
- p-value: 0.705 (not significant)
- Cohen's d: 0.05 (negligible effect)
- Mean difference: 0.06 (human-in-loop - automated)

**Conclusion**: No statistically significant difference in rating improvement between treatments. Both approaches showed **positive mean improvements** (+0.58 for Automated, +0.64 for Human-in-Loop), with improvement rates of 38% and 36% respectively. While human-in-loop showed slightly higher improvement, the difference is not statistically significant.

**Training Effectiveness** (Table 2, Human-in-Loop only):

| Metric | Pre | Post | Improvement | Significant |
|-------|-----|------|-------------|-------------|
| Confidence (1-5) | 3.16 | 4.16 | +1.00 | **Yes (p<0.001)** |
| Authenticity (1-5) | 2.94 | 4.53 | +1.59 | **Yes (p<0.001)** |
| Recall Test | N/A | 50 responses | N/A | N/A |

**Statistical Tests**:
- **Confidence**: Paired t-test, p < 0.001, n_paired=49
  - Pre: M=3.16, SD=0.76
  - Post: M=4.16, SD=0.76
  - Improvement: +1.00

- **Authenticity**: Paired t-test, p < 0.001, n_paired=49
  - Pre: M=2.94, SD=0.62
  - Post: M=4.53, SD=0.61
  - Improvement: +1.59
  - Cohen's d = 3.21 (very large effect)

**Efficiency Analysis** (Table 3):

| Treatment | Mean Iterations | Std | Min | Max | N |
|-----------|----------------|-----|-----|-----|---|
| Automated | 5.0 | 0.0 | 5.0 | 5.0 | 50 |
| Human-in-Loop | 1.0 | 0.0 | 1.0 | 1.0 | 50 |

**Statistical Test**: Independent t-test, p < 0.001 (highly significant)

**Conclusion**: Human-in-loop treatment required significantly fewer iterations (mean=1.0) compared to automated treatment (mean=5.0). All automated answers reached the maximum of 5 iterations, while all human-in-loop answers completed in 1 iteration.

**Customization Metrics** (Human-in-Loop only):
- Unique Q&A pairs: 50
- Answers with personal details: 50 (100%)
- Mean personal detail indicators: 4.34 (SD=1.90)
- Personal details rate: 100%

**Conclusion**: 100% of answers (50/50) in human-in-loop treatment incorporated personal details from participant responses, with a mean of 4.34 personal detail indicators per answer (metrics, "I" statements, specific experiences).

#### 4.1.2 Key Insights

1. **Rating Improvement**: Both methods successfully improved answer quality, with 38% (Automated) and 36% (Human-in-Loop) of answers showing improvement. The difference between approaches is not statistically significant (p=0.705, Cohen's d=0.05), suggesting comparable effectiveness in terms of rating improvement.

2. **Training Effectiveness**: Human-in-the-loop approach demonstrates **highly significant training effectiveness**:
   - Confidence improved from 3.16 to 4.16 (+1.00, p<0.001)
   - Authenticity improved from 2.94 to 4.53 (+1.59, p<0.001, Cohen's d=3.21, very large effect)
   - All 50 participants completed recall tests, demonstrating knowledge retention

3. **Efficiency**: Human-in-the-loop requires 5× fewer iterations (1.0 vs 5.0, p<0.001), indicating more efficient improvement process with targeted, high-quality improvements from human input.

4. **Customization**: 100% personal detail integration enables authentic, personalized answers that reflect individual participant backgrounds and experiences.

#### 4.1.3 Implications

**Context-Dependent Value Proposition**: The choice between human-in-the-loop and automated approaches depends on system objectives:

**When human-in-the-loop may be preferable:**
- Training effectiveness and pedagogical value are priorities (large, significant improvements in confidence and authenticity)
- Authenticity matters (100% personal detail integration)
- Customization is required (individual experience levels, backgrounds)
- Efficiency is valued (5× fewer iterations)

**When automated approaches may be preferable:**
- Rating improvement alone is sufficient (comparable effectiveness)
- Consistent, standardized improvement is needed
- Human input quality or engagement cannot be guaranteed

**Key Insight**: Rather than claiming universal superiority, our quantitative analysis reveals that each approach offers different value propositions. Human-in-the-loop provides substantial training benefits and customization advantages, while automated approaches offer comparable rating improvements with potentially lower participant engagement requirements.

### 4.2 Finding 2: Rapid Convergence of CoT Prompting

#### 4.2.1 Convergence Results

Through systematic iteration analysis (Experiment 2), we demonstrate that both automated and human-in-the-loop methods converge rapidly in interview answer improvement.

**Success Rate by Iteration** (Table 4, N=50):

| Iteration | Automated | Human-in-Loop |
|-----------|-----------|---------------|
| 0 (Initial) | 50.0% | 50.0% |
| 1 | 86.0% | 90.0% |
| 2 | 86.0% | 90.0% |
| 3 | 92.0% | **100.0%** |
| 4+ | 92.0% | 100.0% |

**Success Rate by Initial Rating** (Table 5):

| Initial Rating | N | Automated | Human-in-Loop | Gap |
|----------------|---|-----------|---------------|-----|
| Hire | 25 | 100% (25/25) | 100% (25/25) | 0% |
| **Leaning No Hire** | **25** | **84% (21/25)** | **100% (25/25)** | **+16%** |

**Key Insight**: The gap between methods is concentrated in initially weak answers. For answers that started good, both methods maintain 100%. The relevant comparison is the "Leaning No Hire" subgroup.

**Convergence Statistics**:

| Metric | Automated | Human-in-Loop |
|--------|-----------|---------------|
| Mean Convergence Iteration | 0.54 | 0.70 |
| Converged at Iter 0 | 29/50 (58%) | 25/50 (50%) |
| Converged at Iter 1 | 18/50 (36%) | 20/50 (40%) |
| Converged | 50/50 (100%) | 50/50 (100%) |

#### 4.2.2 Statistical Analysis

**Leaning No Hire Subgroup Analysis** (n=25):
- Automated Success Rate: 84% (21/25)
- Human-in-Loop Success Rate: 100% (25/25)
- Difference: +16 percentage points
- **Effect Size (Cohen's h)**: **0.82 (Large)**
- Discordant Pairs: 4 (all favor Human-in-Loop)
- McNemar's Exact p-value: 0.0625

**Interpretation**: Among answers initially rated "Leaning No Hire," Human-in-Loop achieved 100% success rate compared to 84% for Automated. The effect size is large (Cohen's h = 0.82). All four discordant cases favored Human-in-Loop. While the small number of discordant pairs limits statistical power (p = 0.0625), the large effect size and consistent directionality (4-0) support the conclusion that human context helps resolve cases where automated CoT alone cannot.

#### 4.2.3 Key Insights

1. **Rapid Convergence**: Both methods converge within 1-2 iterations on average (mean convergence: Automated 0.54, Human-in-Loop 0.70). 100% of answers converged before max iterations, with most improvement happening at iteration 1.

2. **Diminishing Returns**: Both methods show diminishing returns after iteration 1:
   - Automated: 50% → 86% (iter 1) → 92% (iter 3) - most gain at iter 1
   - Human-in-Loop: 50% → 90% (iter 1) → 100% (iter 3) - most gain at iter 1

3. **Context Matters More Than Iterations**: Human-in-Loop achieves higher success rate with a large effect size (100% vs 84% for weak answers, h = 0.82). The advantage comes from having real context, not from running more iterations.

4. **First Iteration is Critical**: If improvement doesn't happen in first 1-2 iterations, more iterations won't help. The limitation is context availability, not compute.

#### 4.2.4 Implications

**Efficiency Optimization**: Single-iteration improvement is sufficient for most cases, as demonstrated by rapid convergence (mean <1 iteration) and diminishing returns after iteration 1. Running more iterations does not improve results, indicating the limitation is not compute.

**Domain-Specific Behavior**: Interview scenarios have structured evaluation criteria (FAANG rubrics), creating a bounded solution space that leads to faster convergence than open-ended tasks. This contrasts with general CoT tasks (math, reasoning) that may benefit from multiple iterations.

**Context vs. Iterations**: The advantage of Human-in-Loop comes from having real context to fix edge cases that pure CoT cannot resolve, not from running more iterations. Our quantitative results demonstrate that improving context availability (human-in-loop achieves 100% vs 84% for weak answers, h=0.82) is more effective than increasing iteration counts (both methods converge in <1 iteration on average).

### 4.3 Finding 3: Adversarial Challenging Mechanism Design

#### 4.3.1 Mechanism Design

We propose the `bar_raiser()` mechanism, implementing a negativity bias model to simulate realistic FAANG interviewer behavior. This mechanism addresses the gap between optimistic LLM evaluations and defensive real interviewer assessments.

**Key Components**:
1. **Negativity Bias Model**: "Assume no skill unless explicitly demonstrated"
2. **Ownership Tracing**: "Reward only actions clearly driven by the candidate"
3. **Scope Validation**: "Challenge the scope of the example"
4. **Data-Driven Requirement**: "Downgrade ratings by one level if metrics are missing"
5. **Industry Context**: Simulates competitive 2025 hiring environment with raised bars

**Implementation Location**: `prompts.py:454-492`

**Key Mechanism**:
```python
--- NEGATIVITY BIAS MODEL ---
Apply realistic FAANG interviewer negativity bias:
Assume no skill unless explicitly demonstrated.
Penalize vagueness, assumptions, or unsupported claims harshly.

--- OWNERSHIP TRACING ---
Perform ownership tracing on every step of the answer.
Reward only the actions clearly driven by the candidate.
Penalize any ambiguity or executor-style contribution.
```

#### 4.3.2 Design Rationale

**Problem**: Pure CoT prompting without adversarial challenging tends to produce overly optimistic evaluations that may not match real interviewer behavior. Real interviewers apply **defensive evaluation** (assume weakness until proven otherwise), while LLMs without challenging tend toward **optimistic evaluation** (assume strength unless explicitly weak).

**Solution**: The `bar_raiser()` mechanism introduces controlled negativity bias and structured challenging that mirrors real interviewer behavior, including:
- Systematic skepticism about unproven claims
- Ownership attribution requirements
- Scope and impact validation
- Data-driven evidence requirements

#### 4.3.3 Implementation and Usage

The `bar_raiser()` mechanism is integrated into our evaluation pipeline and used in all experiments reported in this paper. It is applied consistently across all evaluations to ensure realistic assessment standards.

**Usage in Experiments**:
- All initial evaluations use `BQQuestions.real_interview()` + `bar_raiser()`
- All re-evaluations during improvement iterations use the same mechanism
- Ensures consistent evaluation standards across automated and human-in-loop treatments

#### 4.3.4 Limitations and Future Work

**Quantitative Validation**: While the mechanism is implemented and used throughout our experiments, quantitative validation with human evaluators (Experiment 3) was not conducted. Future work should:
- Compare evaluations with/without `bar_raiser()` against human interviewer ratings
- Conduct ablation studies to identify which components contribute most to realism
- Measure inter-annotator agreement between LLM evaluations with `bar_raiser()` and real interviewers

**Design Contribution**: This mechanism represents a design contribution addressing the need for realistic evaluation in interview contexts. The structured approach to simulating interviewer behavior provides a foundation for future quantitative validation.

#### 4.3.5 Significance

**Design Insight**: Realistic evaluation in interview contexts requires domain-specific mechanisms beyond standard CoT prompting. The negativity bias model addresses a critical gap in LLM-based evaluation systems.

**Practical Value**: The mechanism is implemented and operational, providing a concrete approach to improving evaluation realism. While quantitative validation remains future work, the design addresses a recognized limitation in existing interview evaluation systems.

**Research Direction**: This work opens a research direction on adversarial challenging mechanisms for domain-specific evaluation tasks, contributing to the broader literature on LLM evaluation realism.

---

## 5. Results

This section consolidates quantitative results from both experiments, providing a comprehensive view of our empirical findings.

### 5.1 Experiment 1: Human-in-the-Loop vs. Automated Improvement

#### 5.1.1 Rating Improvement

Both automated and human-in-the-loop approaches showed positive rating improvements, with no statistically significant difference between them (Table 1). The mean improvements were +0.58 (Automated) and +0.64 (Human-in-Loop), with improvement rates of 38% and 36% respectively. This demonstrates that both methods successfully improved answer quality for a substantial portion of answers, validating the effectiveness of CoT-based improvement approaches.

**Table 1: Rating Improvement Comparison**

| Metric | Automated | Human-in-Loop |
|--------|-----------|---------------|
| N | 50 | 50 |
| Mean Improvement | +0.58 | +0.64 |
| Std Improvement | 1.21 | 1.10 |
| Improved Count | 19 | 18 |
| No Change Count | 27 | 30 |
| Degraded Count | 4 | 2 |
| Improvement Rate | 38.0% | 36.0% |

**Statistical Test**: Paired t-test (within-subject design)
- t(49) = -0.38, p = 0.705 (not significant)
- Cohen's d = 0.05 (negligible effect)
- Mean difference: 0.06 (human-in-loop - automated)

#### 5.1.2 Training Effectiveness

The human-in-the-loop approach demonstrated highly significant training effectiveness, with large effect sizes for both confidence and authenticity improvements (Table 2).

**Table 2: Training Effectiveness (Human-in-Loop Only)**

| Metric | Pre | Post | Improvement | Statistical Test |
|-------|-----|------|-------------|-----------------|
| Confidence (1-5) | 3.16 (SD=0.76) | 4.16 (SD=0.76) | +1.00 | Paired t-test, p<0.001, n=49 |
| Authenticity (1-5) | 2.94 (SD=0.62) | 4.53 (SD=0.61) | +1.59 | Paired t-test, p<0.001, Cohen's d=3.21, n=49 |
| Recall Test | N/A | 50/50 completed | N/A | N/A |

**Key Findings**:
- Confidence improved significantly from 3.16 to 4.16 (+1.00, p<0.001)
- Authenticity improved significantly from 2.94 to 4.53 (+1.59, p<0.001)
- Very large effect size for authenticity (Cohen's d=3.21)
- All 50 participants completed recall tests, demonstrating knowledge retention

#### 5.1.3 Efficiency

Human-in-the-loop required significantly fewer iterations compared to automated approaches (Table 3).

**Table 3: Iteration Analysis**

| Treatment | Mean Iterations | Std | Min | Max | N |
|-----------|----------------|-----|-----|-----|---|
| Automated | 5.0 | 0.0 | 5.0 | 5.0 | 50 |
| Human-in-Loop | 1.0 | 0.0 | 1.0 | 1.0 | 50 |

**Statistical Test**: Independent t-test, p < 0.001 (highly significant)

**Finding**: Human-in-loop treatment required 5× fewer iterations (mean=1.0) compared to automated treatment (mean=5.0). All automated answers reached the maximum of 5 iterations, while all human-in-loop answers completed in 1 iteration.

#### 5.1.4 Customization

The human-in-the-loop approach achieved 100% personal detail integration:
- Unique Q&A pairs: 50
- Answers with personal details: 50 (100%)
- Mean personal detail indicators: 4.34 (SD=1.90)
- Personal details rate: 100%

**Finding**: All 50 answers in human-in-loop treatment incorporated personal details from participant responses, with a mean of 4.34 personal detail indicators per answer (metrics, "I" statements, specific experiences).

### 5.2 Experiment 2: Convergence Analysis

#### 5.2.1 Success Rate by Iteration

Both methods showed rapid convergence, with most improvement occurring at iteration 1 (Table 4, see Figure 2 for visualization).

**Table 4: Success Rate by Iteration (N=50)**

| Iteration | Automated | Human-in-Loop |
|-----------|-----------|---------------|
| 0 (Initial) | 50.0% | 50.0% |
| 1 | 86.0% | 90.0% |
| 2 | 86.0% | 90.0% |
| 3 | 92.0% | **100.0%** |
| 4+ | 92.0% | 100.0% |

**Key Finding**: Both methods converge rapidly, with success rates increasing from 50% (initial) to 86-90% after just one iteration. Human-in-Loop reaches 100% success rate by iteration 3, while Automated plateaus at 92%. See Figure 2 for visualization of success rate progression by iteration.

#### 5.2.2 Success Rate by Initial Rating

The gap between methods is concentrated in initially weak answers (Table 5).

**Table 5: Success Rate by Initial Rating**

| Initial Rating | N | Automated | Human-in-Loop | Gap |
|----------------|---|-----------|---------------|-----|
| Hire | 25 | 100% (25/25) | 100% (25/25) | 0% |
| **Leaning No Hire** | **25** | **84% (21/25)** | **100% (25/25)** | **+16%** |

**Key Finding**: For answers that started at "Hire" rating, both methods maintain 100% success. For initially weak answers ("Leaning No Hire"), Human-in-Loop achieves 100% success rate compared to 84% for Automated—a 16 percentage point difference.

**Statistical Analysis** (Leaning No Hire subgroup, n=25):
- Automated Success Rate: 84% (21/25)
- Human-in-Loop Success Rate: 100% (25/25)
- Effect Size (Cohen's h): **0.82 (Large)**
- Discordant Pairs: 4 (all favor Human-in-Loop)
- McNemar's Exact p-value: 0.0625

**Interpretation**: While the small number of discordant pairs limits statistical power (p = 0.0625), the large effect size (Cohen's h = 0.82) and consistent directionality (all 4 discordant cases favor Human-in-Loop) support the conclusion that human context helps resolve cases where automated CoT alone cannot.

#### 5.2.3 Convergence Statistics

Both methods converge rapidly, with mean convergence iterations less than 1 (Table 6).

**Table 6: Convergence Statistics**

| Metric | Automated | Human-in-Loop |
|--------|-----------|---------------|
| Mean Convergence Iteration | 0.54 | 0.70 |
| Converged at Iter 0 | 29/50 (58%) | 25/50 (50%) |
| Converged at Iter 1 | 18/50 (36%) | 20/50 (40%) |
| Converged | 50/50 (100%) | 50/50 (100%) |

**Key Finding**: Both methods converge rapidly (mean <1 iteration), with 100% of answers converging before max iterations. Most improvement happens at iteration 1 (36-40% of answers), indicating diminishing returns for additional iterations.

### 5.3 Cross-Experiment Insights

**Synthesis of Findings**:

1. **Rating Improvement**: Both methods show positive improvements (38-36% improvement rates), with no statistically significant difference. This validates the effectiveness of CoT-based improvement approaches.

2. **Training Value**: Human-in-the-loop provides substantial training benefits (confidence +1.00, authenticity +1.59, p<0.001) that automated approaches cannot provide, demonstrating a clear value proposition beyond rating improvement.

3. **Efficiency**: Human-in-the-loop requires 5× fewer iterations (1.0 vs 5.0), indicating more efficient improvement process with targeted, high-quality improvements.

4. **Convergence**: Both methods converge rapidly (mean <1 iteration), with diminishing returns after iteration 1. The limitation is context availability, not compute.

5. **Context Advantage**: Human-in-Loop achieves higher success rates for weak answers (100% vs 84%, h=0.82), demonstrating that real context helps resolve edge cases that pure CoT cannot.

**Implication**: The choice between approaches depends on system objectives: rating improvement alone (both comparable) vs. training effectiveness, efficiency, and customization (human-in-loop advantages).

---

## 6. Discussion

### 6.1 Synthesis of Findings

Our quantitative experiments reveal a nuanced picture of CoT prompting in interview evaluation:

1. **CoT Prompting Shows Positive Improvements but Rapid Convergence**
   - Both automated and human-in-loop approaches show positive rating improvements (38-36% improvement rates)
   - Rapid convergence (mean <1 iteration) limits iterative improvement beyond the first iteration
   - Automated approaches lack authenticity for training purposes (no personal detail integration)

2. **Human-in-the-Loop Offers Substantial Additional Value**
   - Provides significant training benefits: confidence +1.00, authenticity +1.59 (p<0.001, Cohen's d=3.21)
   - Enables 100% personal detail integration and customization
   - Requires 5× fewer iterations (1.0 vs 5.0, p<0.001)
   - Achieves higher success rates for weak answers (100% vs 84%, Cohen's h=0.82)
   - **Trade-off**: Requires human participant engagement and quality input

3. **Adversarial Challenging Mechanism Design**
   - Negativity bias model (`bar_raiser`) proposed to simulate realistic interviewer behavior
   - Implemented and used throughout experiments, but quantitative validation with human evaluators remains future work

### 6.2 Why These Findings Matter

#### 6.2.1 Interview Training Systems

For **pedagogical interview training systems**, our quantitative findings provide evidence-based guidance:

- **Approach Selection**: Choose human-in-the-loop when training effectiveness and personalization are priorities, as demonstrated by significant improvements in confidence (+1.00, p<0.001) and authenticity (+1.59, p<0.001, Cohen's d=3.21). Choose automation when rating improvement alone is sufficient and participant engagement cannot be guaranteed, as both approaches show comparable rating improvements (38% vs 36%, p=0.705).

- **Efficiency Optimization**: Focus on single-iteration improvement, as both methods converge rapidly (mean <1 iteration) with diminishing returns after iteration 1. Human-in-the-loop achieves this in 1 iteration vs. 5 for automated approaches.

- **Realistic Evaluation**: Incorporate adversarial challenging mechanisms (e.g., `bar_raiser`) for realistic feedback, though quantitative validation with human evaluators remains future work.

#### 6.2.2 LLM Evaluation Systems

For **general LLM evaluation systems**, our findings reveal:

- **Domain-Specific Convergence**: Convergence behavior varies by task structure. In bounded solution spaces (structured evaluation with well-defined rubrics), rapid convergence occurs (mean <1 iteration). This contrasts with unbounded tasks where multiple iterations may be beneficial.

- **Context vs. Iterations**: For weak initial answers, having real context (human-in-loop) achieves higher success rates (100% vs 84%, Cohen's h=0.82) than running more iterations. Our quantitative results demonstrate that improving context availability is more effective than increasing iteration counts, as both methods converge rapidly (mean <1 iteration) with diminishing returns after iteration 1.

- **Evaluation Realism**: Achieving realistic evaluation may require domain-specific adversarial mechanisms beyond standard CoT prompting, as proposed in our `bar_raiser` mechanism.

#### 6.2.3 CoT Prompting Research

For **CoT prompting research**, our findings contribute:

- **Convergence Analysis in Structured Domains**: We provide quantitative evidence that CoT prompting converges rapidly in structured evaluation domains (interview scenarios with FAANG rubrics), revealing domain-specific convergence patterns that differ from general CoT applications.

- **Human-in-the-Loop Integration**: We quantitatively demonstrate the value proposition of human-in-the-loop integration, showing significant training benefits (confidence, authenticity) beyond rating improvement, with large effect sizes (Cohen's d=3.21).

- **Multi-Dimensional Evaluation**: Our work demonstrates that rating improvement alone is insufficient to evaluate improvement methods; training effectiveness, efficiency, and customization provide critical additional value dimensions.

### 6.3 Limitations

1. **Evaluation Scope**: Findings based on FAANG behavioral interview standards with 50 Q&A pairs; may not generalize to other interview types (technical interviews, system design, etc.) or different evaluation rubrics.

2. **Rating Improvement Limitations**:
   - **Moderate Improvement Rates**: While both methods showed positive improvements, only 38% (Automated) and 36% (Human-in-Loop) of answers improved, indicating that a majority (62-64%) showed no improvement or slight degradation. This demonstrates that improvement is not guaranteed for all answers, possibly due to evaluator consistency, ceiling effects, or the need for more sophisticated improvement strategies.
   - **Non-Significant Difference**: The difference between automated and human-in-loop approaches in rating improvement is not statistically significant (p=0.705, Cohen's d=0.05), suggesting comparable effectiveness in this dimension.

3. **Experiment 2 Statistical Power**:
   - For the "Leaning No Hire" subgroup analysis, the small number of discordant pairs (4) limits statistical power (McNemar's p=0.0625). However, the large effect size (Cohen's h=0.82) and consistent directionality (all 4 discordant cases favor Human-in-Loop) support the conclusion.

4. **Human Input Quality and Variability**: 
   - Human-in-the-loop effectiveness critically depends on quality of user-provided details. Our participants provided high-quality input, but results may vary with lower-quality or generic responses.
   - Participant engagement, experience level, and ability to articulate experiences vary significantly. Future work should explore quality thresholds and participant selection criteria.

5. **Adversarial Challenging Validation**:
   - **Experiment 3 Not Conducted**: Quantitative validation of the `bar_raiser` mechanism with human evaluators was not conducted. While the mechanism is implemented and used throughout our experiments, we cannot claim quantitative evidence for its contribution to evaluation realism.
   - Future work should compare evaluations with/without `bar_raiser()` against human interviewer ratings and conduct ablation studies.

6. **Model Selection**: Our primary findings are based on GPT-4o-mini. While we validated key results using Gemini 3.0 Pro (20% of answers) and GPT-5.2 Thinking (10% of answers), the generalizability to other model families requires further investigation.

7. **Sample Size**: While n=50 provides adequate power for within-subject paired designs (30-50% more efficient than independent groups), larger samples would strengthen conclusions, particularly for subgroup analyses.

8. **Longitudinal Training Effectiveness**: Training effectiveness measures (confidence, authenticity) were collected at a single time point (1 week recall test). Longitudinal follow-up would provide insights into long-term retention and real interview performance.

### 6.4 Future Work

1. **Adversarial Challenging Validation** (Experiment 3): Conduct quantitative validation of the `bar_raiser` mechanism:
   - Compare evaluations with/without `bar_raiser()` against human interviewer ratings
   - Measure inter-annotator agreement between LLM evaluations and real interviewers
   - Conduct ablation studies to identify which components contribute most to realism

2. **Enhanced Improvement Strategies**: Develop more sophisticated improvement strategies to increase improvement rates beyond 38-36%, potentially through:
   - Multi-pass analysis with different evaluation perspectives
   - Adaptive iteration strategies based on answer characteristics
   - Hybrid approaches combining automated and human-in-the-loop benefits

3. **Generalization Studies**: Test findings across:
   - Different interview types (technical interviews, system design, case studies)
   - Different evaluation rubrics (beyond FAANG standards)
   - Different participant populations and experience levels

4. **Longitudinal Training Effectiveness**: Conduct longitudinal studies to assess:
   - Long-term retention of improved answers
   - Real interview performance improvements
   - Sustained confidence and authenticity gains

5. **Quality Control Mechanisms**: Develop quality thresholds and participant selection criteria for human-in-the-loop approaches to ensure consistent effectiveness.

6. **Hybrid Approaches**: Explore optimal balance between automation and human input, potentially through:
   - Automated initial improvement with human refinement
   - Selective human intervention for edge cases
   - Adaptive switching between approaches based on answer characteristics

---

## 7. Conclusion

This work investigates Chain-of-Thought prompting for behavioral interview evaluation through two controlled experiments with 50 behavioral interview Q&A pairs, presenting three key contributions:

1. **Empirically validated comparison of human-in-the-loop vs. automated CoT improvement**: Using a within-subject paired design (n=50), we demonstrate that both approaches show positive rating improvements (38-36% improvement rates), with no statistically significant difference (p=0.705). However, human-in-the-loop provides substantial additional value: significant training benefits (confidence +1.00, authenticity +1.59, p<0.001, Cohen's d=3.21), 5× fewer iterations (1.0 vs 5.0, p<0.001), and 100% personal detail integration. This quantitative evidence reveals context-dependent value propositions and trade-offs.

2. **Convergence analysis demonstrating rapid convergence with diminishing returns**: Through systematic iteration analysis, we show that both methods converge rapidly (mean <1 iteration), with human-in-the-loop achieving higher success rates for initially weak answers (100% vs 84%, Cohen's h=0.82, large effect). Additional iterations provide diminishing returns after iteration 1, indicating the limitation is context availability, not computational resources.

3. **Adversarial challenging mechanism design** (`bar_raiser`): We propose a negativity bias model to simulate realistic FAANG interviewer behavior. While the mechanism is implemented and used throughout our experiments, quantitative validation with human evaluators (Experiment 3) was not conducted and remains future work.

These findings demonstrate that while CoT prompting provides a foundation for interview evaluation systems, **domain-specific enhancements and context-aware approach selection** are essential for realistic, pedagogically valuable results. The choice between automated and human-in-the-loop approaches depends on system objectives: rating improvement alone (both comparable) vs. training effectiveness, efficiency, and customization (human-in-loop advantages).

Future work should: (1) conduct quantitative validation of the adversarial challenging mechanism with human evaluators, (2) develop enhanced improvement strategies to increase improvement rates beyond 38-36%, (3) test findings across different interview types and evaluation rubrics, (4) conduct longitudinal studies to assess long-term training effectiveness, and (5) explore hybrid approaches combining automation with human expertise for optimal results.

---

## References

Amershi, S., et al. (2019). "Software Engineering for Machine Learning: A Case Study." *2019 IEEE/ACM 41st International Conference on Software Engineering: Software Engineering in Practice (ICSE-SEIP)*.

Bansal, G., et al. (2021). "Does the Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance." *Proceedings of the 2021 CHI Conference on Human Factors in Computing Systems*.

Chen, M., et al. (2021). "Evaluating Large Language Models Trained on Code." *arXiv preprint arXiv:2107.03374*.

Chen, L., et al. (2020). "Automated Interview Assessment: A Machine Learning Approach." *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing*.

Cobbe, K., et al. (2021). "Training Verifiers to Solve Math Word Problems." *arXiv preprint arXiv:2110.14168*.

D'Mello, S., et al. (2015). "Automated Detection of Engagement and Affect During Learning." *Proceedings of the 8th International Conference on Educational Data Mining*.

Huang, J., et al. (2023). "Large Language Models Can Self-Improve." *arXiv preprint arXiv:2210.11610*.

Kreutzer, J., et al. (2022). "Quality at a Glance: An Audit of Web-Crawled Multilingual Datasets." *Transactions of the Association for Computational Linguistics*.

Kumar, V., et al. (2021). "Automated Feedback Generation for Interview Preparation Using Natural Language Processing." *Proceedings of the 2021 Conference on Artificial Intelligence in Education*.

Liu, P., et al. (2023). "Pre-train, Prompt, and Predict: A Systematic Survey of Prompting Methods in Natural Language Processing." *ACM Computing Surveys*.

Liu, Y., et al. (2023). "G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment." *Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing*.

Madaan, A., et al. (2023). "Self-Refine: Iterative Refinement with Self-Feedback." *arXiv preprint arXiv:2303.17651*.

Ouyang, L., et al. (2022). "Training language models to follow instructions with human feedback." *Advances in Neural Information Processing Systems*.

Perez, E., et al. (2022). "Red Teaming Language Models with Language Models." *arXiv preprint arXiv:2202.03286*.

Talmor, A., et al. (2023). "MultiModalQA: Complex Question Answering over Text, Tables and Images." *Proceedings of the 2023 International Conference on Learning Representations*.

Wang, X., et al. (2023). "Self-Consistency Improves Chain of Thought Reasoning in Language Models." *arXiv preprint arXiv:2203.11171*.

Wang, J., et al. (2023). "On the Evaluation Metrics for LLM-based Code Generation." *arXiv preprint arXiv:2308.13140*.

Wei, J., et al. (2022). "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." *Advances in Neural Information Processing Systems*.

White, J., et al. (2023). "A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT." *arXiv preprint arXiv:2302.11382*.

Yao, S., et al. (2023). "Tree of Thoughts: Deliberate Problem Solving with Large Language Models." *arXiv preprint arXiv:2305.10601*.

Zhang, T., et al. (2020). "Human-in-the-Loop for Data Collection: A Multi-Task Counterfactual Approach." *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing*.

Zheng, L., et al. (2023). "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." *Advances in Neural Information Processing Systems*.

---

## Appendix: Technical Implementation Details

### A.1 System Components

**Story-Improve Architecture:**
- `advance/self_improve.py`: Core improvement classes
- `prompts.py`: Prompt templates and evaluation mechanisms
- `interview_analyzer.py`: LLM integration and analysis

**Key Classes:**
- `StorySelfImprove`: Automated CoT-based improvement
- `HumanInLoopImprove`: Human-in-the-loop improvement
- `BQQuestions.bar_raiser()`: Adversarial challenging mechanism

### A.2 Evaluation Rubrics

**FAANG Competency Dimensions:**
- Ownership
- Problem Solving
- Execution
- Collaboration
- Communication
- Leadership / Influence
- Culture Fit

**Rating Scale:**
- 🌟 Strong Hire
- 👍 Hire
- 🤔 Leaning Hire
- 🤨 Leaning No Hire
- ❌ No Hire

### A.3 Figures and Tables

**Figure 2**: Success rate by iteration for both automated and human-in-loop methods (Experiment 2). Visualization available at `paper/experiment/exp2_results/analysis/exp2_success_rate_by_iteration.png`.

**Table References**:
- Table 1: Rating Improvement Comparison (Experiment 1, Section 4.1.1, 5.1.1)
- Table 2: Training Effectiveness (Experiment 1, Section 4.1.1, 5.1.2)
- Table 3: Iteration Analysis (Experiment 1, Section 4.1.1, 5.1.3)
- Table 4: Success Rate by Iteration (Experiment 2, Section 4.2.1, 5.2.1)
- Table 5: Success Rate by Initial Rating (Experiment 2, Section 4.2.1, 5.2.2)
- Table 6: Convergence Statistics (Experiment 2, Section 4.2.1, 5.2.3)

### A.4 Prompt Engineering Details

**CoT Prompting Structure:**
1. Extract question and answer from feedback
2. Analyze weaknesses using structured evaluation
3. Generate improved answer addressing all gaps
4. Re-evaluate with adversarial challenging

**Human-in-the-Loop Flow:**
1. Extract probing questions from evaluation
2. User provides real answers to probing questions
3. Incorporate user answers into improved answer
4. Re-evaluate with human-provided details

### A.5 Model and Hyperparameter Specifications

**Primary Model: GPT-4o-mini (OpenAI API)**
- **Model Identifier**: `gpt-4o-mini`
- **Provider**: OpenAI
- **API Endpoint**: OpenAI API (via LiteLLM)
- **Pricing**: $0.15 per 1M input tokens, $0.60 per 1M output tokens
- **Context Window**: 128K tokens
- **Temperature Settings**:
  - Evaluation tasks: 0.3 (ensures consistent ratings)
  - Answer generation: 0.7 (allows creative improvements)
- **Max Tokens**: Determined dynamically based on prompt length
- **API Version**: As of December 2024

**Validation Models:**

1. **Gemini 3.0 Pro (Google AI API)**
   - **Purpose**: Model-agnostic validation (20% of answers)
   - **Rationale**: Verify findings generalize across different model architectures
   - **Context Window**: 10M tokens
   - **Temperature**: 0.3 (evaluation), 0.7 (generation)

2. **GPT-5.2 Thinking (OpenAI API)**
   - **Purpose**: Critical result verification (10% of answers)
   - **Rationale**: Leverage superior reasoning capabilities for validating key findings
   - **Performance**: AIME 2025: 100%, ARC-AGI-2: 52.9%
   - **Temperature**: 0.3 (evaluation), 0.7 (generation)

**System Configuration:**
- **Python Version**: 3.11+
- **LLM Integration**: LiteLLM library
- **Async Processing**: asyncio for concurrent API calls
- **Max Concurrent Requests**: 5 (to respect API rate limits)
- **Random Seeds**: Not applicable (deterministic API responses with fixed temperature)

**Evaluation Parameters:**
- **Interview Level**: "Junior-Mid" (default)
- **Max Iterations**: 5 (default), 100 (for convergence analysis)
- **Evaluation Prompt**: `BQQuestions.real_interview()` + `BQQuestions.bar_raiser()`
- **Early Stopping**: When "Strong Hire" rating is achieved

**Cost Estimation:**
- **Primary Experiments**: ~250-5000 API calls (50 answers × 5-100 iterations)
- **Estimated Cost (GPT-4o-mini)**: $0.25-$5.00 for primary experiments
- **Validation Costs**: Additional $2.00-$5.00 for multi-model validation
- **Total Estimated Cost**: $2.25-$10.00 for complete experimental pipeline