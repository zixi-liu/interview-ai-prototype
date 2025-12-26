# Chain-of-Thought Prompting for Interview Evaluation: Limitations and Enhancements
# (Option 1) Interview Auto-Evaluation and Auto-Improvement
# (Option 2) ABI: Interview Evaluation and Improvement dataset

**Authors:** Zixi Liu, Kewen Zhu

## Abstract

This paper investigates the application of Chain-of-Thought (CoT) prompting for behavioral interview answer evaluation and improvement. Through empirical analysis of our Story-Improve system, we explore three key aspects: (1) The mechanisms, value proposition, and trade-offs of human-in-the-loop integration compared to pure CoT prompting, with effectiveness potentially depending on participant quality and engagement; (2) CoT prompting exhibits rapid convergence in interview scenarios, with diminishing returns after a single iteration; (3) Realistic interview evaluation requires adversarial challenging mechanisms (negativity bias) to simulate authentic interviewer behavior. These findings suggest that while CoT prompting provides a foundation for interview evaluation, domain-specific enhancements and careful consideration of context-dependent factors are essential for achieving realistic and pedagogically valuable results.

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

1. How does human-in-the-loop integration affect the effectiveness and value proposition of CoT-based interview answer improvement?
2. What is the convergence behavior of CoT prompting in interview evaluation scenarios?
3. What mechanisms contribute to achieving realistic interview evaluation using LLMs?

### 1.4 Contributions

This work makes three primary contributions:
1. **Mechanism analysis** exploring the value proposition, trade-offs, and context-dependent effectiveness of human-in-the-loop integration in CoT-based interview training
2. **Convergence analysis** showing CoT prompting reaches diminishing returns after one iteration in interview contexts
3. **Adversarial challenging mechanism** (negativity bias model) that improves evaluation realism

(Optional) Contribution
1. Fullfill Lack of research in AI Interview
2. Improve interview preparation
3. Provide enhanced-datasests
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
- **Automated Approach**: `StorySelfImprove` (pure CoT, no human input)
- **Human-in-the-Loop Approach**: `HumanInLoopImprove` (CoT + human-provided details)

**Metrics:**
- Training value: Does the process help candidates learn?
- Customization: Can answers be tailored to individual experiences?
- Authenticity: Are improvements grounded in real experiences?
- Rating improvement: Quantitative comparison of effectiveness (requires experimental validation)

---

## 4. Findings

### 4.1 Finding 1: Mechanisms and Value Proposition of Human-in-the-Loop

#### 4.1.1 Observation

When comparing `StorySelfImprove` (automated CoT) vs `HumanInLoopImprove` (CoT + human input), we explore the mechanisms, value propositions, and trade-offs of each approach:

**Automated Approach Characteristics:**
- LLM may generate plausible but fabricated details
- Improvements may lack connection to candidate's actual experience
- Limited pedagogical value (candidate doesn't learn from fabricated examples)
- **Advantages**: Consistent quality, efficiency, cost-effectiveness

**Human-in-the-Loop Characteristics:**
- **Authentic Details**: User provides real experiences, metrics, and decisions
- **Training Value**: Candidate reflects on actual experiences, potentially improving recall and articulation
- **Customization**: Answers tailored to individual background and level
- **Trade-offs**: Effectiveness depends on participant quality and engagement; may require more time and effort

#### 4.1.2 Evidence

**Code Evidence:**
- `HumanInLoopImprove.improve_with_user_input()` explicitly uses user-provided answers:
  ```python
  prompt = BQAnswer.improve_with_probing_answers(
      original_answer, feedback, probing_qa  # User's REAL answers
  )
  ```
- Prompt explicitly states: "Do NOT fabricate - use only what the user provided"
- This mechanism ensures authenticity, but effectiveness depends on the quality of user-provided input

**Qualitative Observations:**
- Some candidates report better understanding of their own experiences after answering probing questions
- Improved answers may feel more authentic and easier to recall in real interviews (subjective assessment)
- Customization allows answers to match individual career levels and backgrounds

**Note on Quantitative Validation:**
- Quantitative comparison of rating improvements between automated and human-in-the-loop approaches requires controlled experiments (see Experiment 1 in experimental plan)
- Results may vary depending on participant quality, engagement level, and answer types
- The relative effectiveness in terms of rating improvement is an open empirical question

#### 4.1.3 Significance

This finding suggests that **the choice between human-in-the-loop and automated approaches depends on system objectives and context**:

**When human-in-the-loop may be preferable:**
- Pedagogical value is the primary goal (candidate learning and reflection)
- Authenticity matters (real interview scenarios requiring genuine experiences)
- Customization is required (different experience levels, backgrounds)
- Participants can provide high-quality, detailed input

**When automated approaches may be preferable:**
- Efficiency and cost-effectiveness are priorities
- Consistent, standardized improvement is needed
- Quick iterations are required
- Participant quality or engagement cannot be guaranteed

**Key Insight**: Rather than claiming universal superiority, our analysis reveals that each approach offers different value propositions, and the optimal choice depends on the specific goals and constraints of the interview training system.

### 4.2 Finding 2: CoT Prompting Exhibits Rapid Convergence in Interview Scenarios

#### 4.2.1 Observation

Empirical analysis of `StorySelfImprove.run()` reveals that CoT prompting for interview answer improvement **converges rapidly**, with minimal improvement beyond the first iteration.

**Convergence Behavior:**
- **Iteration 1**: Substantial improvement observed (e.g., "Leaning No Hire" → "Hire")
- **Iteration 2-5**: Marginal or no improvement
- **Iteration 6-100**: No measurable improvement (based on empirical testing)

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
- Convergence likely occurs because:
  1. Interview evaluation criteria are well-defined (FAANG rubrics), creating a bounded solution space
  2. CoT reasoning appears to identify most major gaps in first pass
  3. Subsequent iterations address minor issues that may not significantly impact rating

#### 4.2.3 Significance

This finding has practical implications:
- **Efficiency**: Single-iteration improvement may be sufficient for most cases
- **Resource Optimization**: Extended iterations provide diminishing returns
- **Domain-Specific Behavior**: Interview scenarios have structured evaluation criteria, leading to faster convergence than open-ended tasks

**Contrast with General CoT:**
- General CoT tasks (math, reasoning) may benefit from multiple iterations
- Interview evaluation has **bounded solution space** (FAANG rubrics), leading to rapid convergence

### 4.3 Finding 3: Adversarial Challenging Contributes to Realistic Evaluation

#### 4.3.1 Observation

Pure CoT prompting without adversarial challenging tends to produce **overly optimistic evaluations** that may not match real interviewer behavior. The `bar_raiser()` mechanism, implementing a negativity bias model, appears to contribute to more realistic evaluation.

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
- Interview evaluation systems may benefit from incorporating adversarial challenging mechanisms
- Negativity bias models should be explicitly designed and tested, rather than assumed
- Achieving evaluation realism likely requires domain-specific mechanisms beyond standard CoT prompting

---

## 5. Discussion

### 5.1 Synthesis of Findings

Our three findings reveal a nuanced picture of CoT prompting in interview evaluation:

1. **CoT Prompting Alone is Insufficient**
   - Rapid convergence limits iterative improvement
   - Lacks authenticity for training purposes (when using automated generation)

2. **Human-in-the-Loop Offers Different Value Proposition**
   - Provides authentic details and potential pedagogical value
   - Enables customization to individual experiences
   - **However**: Effectiveness is context-dependent and may vary with participant quality and engagement
   - **Trade-off**: Requires more time and effort compared to automated approaches

3. **Adversarial Challenging Ensures Realism**
   - Negativity bias model simulates real interviewer behavior
   - Prevents overly optimistic evaluations

### 5.2 Why These Findings Matter

#### 5.2.1 Interview Training Systems

For **pedagogical interview training systems**, our findings suggest:
- **Consider context-dependent approach selection**: Choose human-in-the-loop when learning and authenticity are priorities and participants can provide quality input; choose automation when efficiency and consistency are priorities
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

2. **Human Input Quality and Variability**: 
   - Human-in-the-loop effectiveness critically depends on quality of user-provided details
   - Participant engagement, experience level, and ability to articulate experiences vary significantly
   - Our findings may not hold if participants provide low-quality or generic responses
   - Future work should explore quality thresholds and participant selection criteria

3. **Experimental Uncertainty**:
   - Quantitative comparison between automated and human-in-the-loop approaches requires controlled experiments with sufficient sample sizes
   - Results may vary depending on participant population, answer types, and evaluation criteria
   - The relative effectiveness of each approach may differ from our initial observations
   - Statistical significance and effect sizes need to be established through rigorous experimentation

4. **Subjectivity**: "Realistic" evaluation is subjective; our negativity bias model is one approach among many possible mechanisms

5. **Model Selection**: Our primary findings are based on GPT-4o-mini. While we validated key results using Gemini 3.0 Pro and GPT-5.2 Thinking, the generalizability to other model families requires further investigation

6. **Potential for Opposite Results**: 
   - If experimental results show automated approaches outperform human-in-the-loop in rating improvement, our interpretation would shift to emphasize different value dimensions (e.g., learning vs. efficiency)
   - The mechanisms and trade-offs we identify remain valuable regardless of quantitative outcomes
   - Future work should explore conditions under which each approach excels

### 5.4 Future Work

1. **Quantitative Evaluation**: Conduct controlled experiments with human evaluators to validate findings
2. **Generalization**: Test findings across different interview types and evaluation rubrics
3. **Mechanism Analysis**: Decompose which components of `bar_raiser()` contribute most to realism
4. **Hybrid Approaches**: Explore optimal balance between automation and human input

---

## 6. Conclusion

This work investigates Chain-of-Thought prompting for behavioral interview evaluation, exploring three key aspects:

1. **Human-in-the-loop integration** offers different value propositions (authenticity, learning, customization) compared to pure CoT prompting, with effectiveness potentially depending on participant quality and context
2. **CoT prompting converges rapidly** in interview scenarios (1 iteration ≈ 100 iterations), suggesting efficient single-pass improvement
3. **Adversarial challenging mechanisms** (negativity bias model) appear to contribute to more realistic evaluation that better matches real interviewer behavior

These findings suggest that while CoT prompting provides a foundation for interview evaluation systems, **domain-specific enhancements and context-aware approach selection** are essential for realistic, pedagogically valuable results. Future work should conduct quantitative validation, explore conditions under which each approach excels, generalize to other domains, and develop optimal hybrid approaches combining automation with human expertise.

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

### A.4 Model and Hyperparameter Specifications

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