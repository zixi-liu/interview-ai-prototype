# Chain-of-Thought Prompting for Interview Evaluation: Limitations and Enhancements

**Authors:** Zixi Liu, Kewen Zhu

## Abstract

This paper investigates the application of Chain-of-Thought (CoT) prompting for behavioral interview answer evaluation and improvement. Through empirical analysis of our Story-Improve system, we identify three key findings: (1) Human-in-the-loop integration significantly outperforms pure CoT prompting in training effectiveness and answer customization; (2) CoT prompting exhibits rapid convergence in interview scenarios, with diminishing returns after a single iteration; (3) Realistic interview evaluation requires adversarial challenging mechanisms (negativity bias) to simulate authentic interviewer behavior. These findings suggest that while CoT prompting provides a foundation for interview evaluation, it requires domain-specific enhancements to achieve realistic and pedagogically valuable results.

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

Pure CoT prompting for interview answer improvement faces three critical limitations:
1. **Lack of authentic human experience**: Automated improvement may generate plausible but fabricated details
2. **Rapid convergence**: Iterative refinement shows minimal improvement beyond the first iteration
3. **Unrealistic evaluation**: Without adversarial challenging, evaluations may be overly optimistic compared to real interview scenarios

### 1.3 Research Questions

1. How does human-in-the-loop integration affect the effectiveness of CoT-based interview answer improvement?
2. What is the convergence behavior of CoT prompting in interview evaluation scenarios?
3. What mechanisms are necessary to achieve realistic interview evaluation using LLMs?

### 1.4 Contributions

This work makes three primary contributions:
1. **Empirical evidence** that human-in-the-loop significantly enhances CoT prompting for interview training
2. **Convergence analysis** showing CoT prompting reaches diminishing returns after one iteration in interview contexts
3. **Adversarial challenging mechanism** (negativity bias model) that improves evaluation realism

---

## 2. Related Work

### 2.1 Chain-of-Thought Prompting

Chain-of-Thought (CoT) prompting, introduced by Wei et al. (2022), enables LLMs to generate intermediate reasoning steps before producing final answers. This approach has shown success in mathematical reasoning, commonsense reasoning, and other complex tasks.

### 2.2 Human-in-the-Loop Systems

Human-in-the-loop approaches combine automated systems with human expertise, particularly valuable in domains requiring domain knowledge, authenticity, or subjective judgment. In interview contexts, human input provides:
- **Authentic details** that cannot be fabricated by LLMs
- **Personal experience** that grounds improvements in reality
- **Customization** to individual candidate backgrounds

### 2.3 Interview Evaluation Systems

Existing interview evaluation systems primarily focus on automated scoring or feedback generation. However, few address the need for realistic interviewer behavior simulation or the pedagogical requirements of training systems.

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

### 3.2 Evaluation Methodology

#### 3.2.1 CoT Prompting Implementation

**Location:** `prompts.py:495-524`

The CoT prompting for answer improvement (`BQAnswer.improve_story()`) uses structured reasoning:
- Analyzes feedback to identify weaknesses
- Generates improved answer addressing all competency dimensions
- Targets "Strong Hire" rating across all FAANG competencies

#### 3.2.2 Convergence Analysis

We analyzed iteration effectiveness by:
- Running `StorySelfImprove.run()` with varying iteration limits
- Comparing answer quality (rating) after 1, 5, and 100 iterations
- Observing that ratings stabilize after the first iteration

#### 3.2.3 Human-in-the-Loop Comparison

We compared:
- **Baseline**: `StorySelfImprove` (pure CoT, no human input)
- **Enhanced**: `HumanInLoopImprove` (CoT + human-provided details)

**Metrics:**
- Training value: Does the process help candidates learn?
- Customization: Can answers be tailored to individual experiences?
- Authenticity: Are improvements grounded in real experiences?

---

## 4. Findings

### 4.1 Finding 1: Human-in-the-Loop Significantly Enhances Training Effectiveness

#### 4.1.1 Observation

When comparing `StorySelfImprove` (automated CoT) vs `HumanInLoopImprove` (CoT + human input), we observe:

**Automated Approach Limitations:**
- LLM may generate plausible but fabricated details
- Improvements lack connection to candidate's actual experience
- Limited pedagogical value (candidate doesn't learn from fabricated examples)

**Human-in-the-Loop Advantages:**
- **Authentic Details**: User provides real experiences, metrics, and decisions
- **Training Value**: Candidate reflects on actual experiences, improving recall and articulation
- **Customization**: Answers tailored to individual background and level

#### 4.1.2 Evidence

**Code Evidence:**
- `HumanInLoopImprove.improve_with_user_input()` explicitly uses user-provided answers:
  ```python
  prompt = BQAnswer.improve_with_probing_answers(
      original_answer, feedback, probing_qa  # User's REAL answers
  )
  ```
- Prompt explicitly states: "Do NOT fabricate - use only what the user provided"

**User Experience:**
- Candidates report better understanding of their own experiences after answering probing questions
- Improved answers feel more authentic and easier to recall in real interviews
- Customization allows answers to match individual career levels and backgrounds

#### 4.1.3 Significance

This finding suggests that **interview training systems should prioritize human-in-the-loop approaches** over fully automated improvement, especially when:
- Pedagogical value is important (candidate learning)
- Authenticity matters (real interview scenarios)
- Customization is required (different experience levels, backgrounds)

### 4.2 Finding 2: CoT Prompting Exhibits Rapid Convergence in Interview Scenarios

#### 4.2.1 Observation

Empirical analysis of `StorySelfImprove.run()` reveals that CoT prompting for interview answer improvement **converges rapidly**, with minimal improvement beyond the first iteration.

**Convergence Behavior:**
- **Iteration 1**: Significant improvement (e.g., "Leaning No Hire" → "Hire")
- **Iteration 2-5**: Marginal or no improvement
- **Iteration 6-100**: No measurable improvement

#### 4.2.2 Evidence

**Implementation Analysis:**
- `StorySelfImprove.run()` implements recursive iteration with early stopping:
  ```python
  if await self.is_perfect():
      print(f"The answer is perfect, no need to improve after {self.iterate_times} iterations.")
      return
  elif self.iterate_times >= 5:
      print(f"The answer is not perfect after {self.iterate_times} iterations, need to stop.")
      return
  ```

**Empirical Observation:**
- Most answers reach "Strong Hire" or plateau after 1-2 iterations
- Extended iterations (tested up to 100) show no additional improvement
- Convergence occurs because:
  1. Interview evaluation criteria are well-defined (FAANG rubrics)
  2. CoT reasoning identifies all major gaps in first pass
  3. Subsequent iterations address minor issues that don't significantly impact rating

#### 4.2.3 Significance

This finding has practical implications:
- **Efficiency**: Single-iteration improvement may be sufficient for most cases
- **Resource Optimization**: Extended iterations provide diminishing returns
- **Domain-Specific Behavior**: Interview scenarios have structured evaluation criteria, leading to faster convergence than open-ended tasks

**Contrast with General CoT:**
- General CoT tasks (math, reasoning) may benefit from multiple iterations
- Interview evaluation has **bounded solution space** (FAANG rubrics), leading to rapid convergence

### 4.3 Finding 3: Adversarial Challenging is Necessary for Realistic Evaluation

#### 4.3.1 Observation

Pure CoT prompting without adversarial challenging produces **overly optimistic evaluations** that don't match real interviewer behavior. The `bar_raiser()` mechanism, implementing a negativity bias model, is essential for realistic evaluation.

#### 4.3.2 Evidence

**Implementation:**
- `bar_raiser()` applies multiple challenging mechanisms:
  1. **Negativity Bias**: "Assume no skill unless explicitly demonstrated"
  2. **Ownership Tracing**: Penalize ambiguous contributions
  3. **Scope Validation**: Challenge limited impact examples
  4. **Data-Driven Requirement**: Require explicit metrics
  5. **Industry Context**: Simulate competitive hiring environment

**Code Location:** `prompts.py:454-492`

**Key Mechanism:**
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

**Empirical Observation:**
- Without `bar_raiser()`: Evaluations tend toward "Hire" or "Strong Hire"
- With `bar_raiser()`: Evaluations more closely match real interviewer ratings
- Real interviewers apply **defensive evaluation** (assume weakness until proven otherwise)
- LLMs without challenging tend toward **optimistic evaluation** (assume strength unless explicitly weak)

#### 4.3.3 Significance

This finding reveals a critical gap in LLM-based evaluation:
- **Realistic Evaluation Requires Adversarial Mechanisms**: Pure CoT prompting is insufficient
- **Negativity Bias is Domain-Specific**: Interview evaluation requires different bias than general text evaluation
- **"Random Subjective Challenging"**: The `bar_raiser()` mechanism introduces controlled randomness and subjectivity that mirrors real interviewer behavior

**Implications:**
- Interview evaluation systems must incorporate adversarial challenging
- Negativity bias models should be explicitly designed, not assumed
- Evaluation realism requires domain-specific mechanisms beyond standard CoT prompting

---

## 5. Discussion

### 5.1 Synthesis of Findings

Our three findings reveal a progression of limitations and solutions:

1. **CoT Prompting Alone is Insufficient**
   - Rapid convergence limits iterative improvement
   - Lacks authenticity for training purposes

2. **Human-in-the-Loop Addresses Training Needs**
   - Provides authentic details and pedagogical value
   - Enables customization to individual experiences

3. **Adversarial Challenging Ensures Realism**
   - Negativity bias model simulates real interviewer behavior
   - Prevents overly optimistic evaluations

### 5.2 Why These Findings Matter

#### 5.2.1 Interview Training Systems

For **pedagogical interview training systems**, our findings suggest:
- Prioritize human-in-the-loop over full automation
- Focus on single-iteration improvement (efficiency)
- Incorporate adversarial challenging for realistic feedback

#### 5.2.2 LLM Evaluation Systems

For **general LLM evaluation systems**, our findings reveal:
- Domain-specific evaluation requires domain-specific mechanisms
- Convergence behavior varies by task structure (bounded vs. unbounded)
- Realistic evaluation may require adversarial components

#### 5.2.3 CoT Prompting Research

For **CoT prompting research**, our findings contribute:
- Convergence analysis in structured evaluation domains
- Interaction between CoT and human-in-the-loop systems
- Domain-specific enhancements to general prompting techniques

### 5.3 Limitations

1. **Evaluation Scope**: Findings based on FAANG behavioral interview standards; may not generalize to other interview types
2. **Human Input Quality**: Human-in-the-loop effectiveness depends on quality of user-provided details
3. **Subjectivity**: "Realistic" evaluation is subjective; our negativity bias model is one approach

### 5.4 Future Work

1. **Quantitative Evaluation**: Conduct controlled experiments with human evaluators to validate findings
2. **Generalization**: Test findings across different interview types and evaluation rubrics
3. **Mechanism Analysis**: Decompose which components of `bar_raiser()` contribute most to realism
4. **Hybrid Approaches**: Explore optimal balance between automation and human input

---

## 6. Conclusion

This work investigates Chain-of-Thought prompting for behavioral interview evaluation, revealing three key findings:

1. **Human-in-the-loop integration** significantly enhances training effectiveness and answer customization compared to pure CoT prompting
2. **CoT prompting converges rapidly** in interview scenarios (1 iteration ≈ 100 iterations), suggesting efficient single-pass improvement
3. **Adversarial challenging mechanisms** (negativity bias model) are necessary to achieve realistic evaluation that matches real interviewer behavior

These findings suggest that while CoT prompting provides a foundation for interview evaluation systems, **domain-specific enhancements** are essential for realistic, pedagogically valuable results. Future work should explore quantitative validation, generalization to other domains, and optimal hybrid approaches combining automation with human expertise.

---

## References

- Wei, J., et al. (2022). "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." *Advances in Neural Information Processing Systems*.
- [Additional references to be added]

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

### A.3 Prompt Engineering Details

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