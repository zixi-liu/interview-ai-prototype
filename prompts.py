"""
Prompt templates for BQ Interview Analyzer
"""

# System messages
class SystemMessage:
    INTRODUCTION = (
        "You are an expert FAANG behavioral interviewer with deep knowledge of hiring standards "
        "at Google, Amazon, Apple, Netflix, and Meta. Provide honest, constructive, and detailed "
        "feedback following FAANG evaluation criteria."
    )
    BQ_QUESTION = (
        "You are an expert FAANG behavioral interviewer. You evaluate answers using the STAR method "
        "(Situation, Task, Action, Result) and FAANG hiring standards. Provide detailed, actionable feedback."
    )


def get_introduction_prompt(introduction: str, role: str, company: str) -> str:
    """
    Generate prompt for self-introduction analysis

    Args:
        introduction: Self-introduction text
        role: Job role being interviewed for
        company: Target company name

    Returns:
        Formatted prompt string
    """

    return f"""Analyze the following self-introduction for a {role} position at {company}.
Provide a comprehensive evaluation following FAANG standards.

SELF-INTRODUCTION:
{introduction}

Please provide your analysis in the following structured format:

## Overall Rating
[no hire / weak hire / hire / strong hire]
(Note: Rating should be based on FAANG standards)

## Checkpoints Evaluation

### 1. Clarity & Conciseness
**Result:** [Pass / No-Pass]
**Reason:** [Detailed explanation]

### 2. Relevance to Job
**Result:** [Pass / No-Pass]
**Reason:** [Detailed explanation]

### 3. Technical Depth Preview
**Result:** [Pass / No-Pass]
**Reason:** [Detailed explanation]

### 4. Ownership
**Result:** [Pass / No-Pass]
**Reason:** [Detailed explanation]

### 5. Motivation & Career Narrative
**Result:** [Pass / No-Pass]
**Reason:** [Detailed explanation]

### 6. Confidence & Professionalism
**Result:** [Pass / No-Pass]
**Reason:** [Detailed explanation]

## Feedback & Improvement Suggestions
(Prioritized by importance, most critical first)

1. [Most important feedback]
2. [Second priority feedback]
3. [Additional suggestions...]
"""


class BQQuestions:
    # FAANG competency dimensions used for evaluation
    COMPETENCIES = [
        "Ownership",
        "Problem Solving",
        "Execution",
        "Collaboration",
        "Communication",
        "Leadership / Influence",
        "Culture Fit",
    ]

    MOST_CHALLENGING_PROJECT = """
    Tell me about your most challenging project.
    """
    SOLVED_CONFLICT = """
    Tell me about a time you solved a conflict.
    """
    BIGGEST_MISTAKE = """
    Tell me about the biggest mistake you made at work.
    """
    NEGATIVE_FEEDBACK = """
    Tell me about a time when you received a negative feedback.
    """
    WORKED_OUTSIDE_COMFORT_ZONE = """
    Tell me about a time you worked outside your comfort zone.
    """
    MET_TIGHT_DEADLINE = """
    Tell me about a time you had to meet a tight deadline.
    """
    DIVE_DEEP_TO_UNDERSTAND_PROBLEM = """
    Tell me about a time you had to dive deep to understand a problem.
    """

    def get_prompt(self, question: str, answer: str, role: str) -> str:
        return f"""Analyze the following behavioral question answer for a {role} position at FAANG companies.
Evaluate the answer following FAANG behavioral interview standards.

QUESTION:
{question}

CANDIDATE'S ANSWER:
{answer}

Please provide your analysis in the following structured format:

## Overall Result
[Pass / No-Pass / Borderline]
(Note: Based on FAANG standards for this specific behavioral question)

## Key Checkpoints Evaluation

### STAR Method Structure
**Result:** [Pass / No-Pass]
**Reason:** [Did the answer follow Situation, Task, Action, Result structure?]

### Specificity & Details
**Result:** [Pass / No-Pass]
**Reason:** [Were concrete examples, metrics, and specific details provided?]

### Impact & Results
**Result:** [Pass / No-Pass]
**Reason:** [Were measurable outcomes and impact clearly demonstrated?]

### Leadership & Ownership
**Result:** [Pass / No-Pass]
**Reason:** [Did the candidate show clear ownership and leadership?]

### Problem-Solving & Decision Making
**Result:** [Pass / No-Pass]
**Reason:** [Were problem-solving approach and decision-making process clear?]

### Communication & Clarity
**Result:** [Pass / No-Pass]
**Reason:** [Was the answer well-structured and easy to follow?]

## Detailed Feedback
(Prioritized by importance)

1. [Most critical feedback]
2. [Second priority feedback]
3. [Additional suggestions...]

## Strengths
- [Key strength 1]
- [Key strength 2]
- [Additional strengths...]

## Areas for Improvement
- [Area 1]
- [Area 2]
- [Additional areas...]
"""

    def real_interview(question: str, answer: str, level: str = "Junior-Mid", include_probing: bool = True) -> str:
        """
        Generate prompt for real interview evaluation

        Args:
            question: Behavioral question
            answer: Candidate's answer
            level: Level of the candidate (Junior-Mid, Senior, Staff)
            include_probing: Whether to include probing questions section (default True)

        Returns:
            Formatted prompt string
        """
        probing_section = """
============================================================
7. Probing Follow-up Questions
- Generate 3–6 targeted probing questions based on the weaknesses identified above
- Questions MUST specifically target:
    * Competencies rated Below(🤔) or Concern(❌) in section 5
    * Gaps identified in "Areas for Improvement" (section 4)
    * Any ambiguity about candidate's personal contribution vs team effort
- Include at least one question from each category:
    * Ownership: "What was YOUR specific decision that changed the outcome?"
    * Reflection: "What mistake did you make, and what would you do differently?"
    * Metrics: "What specific numbers can you share about YOUR contribution?"
- MUST align with the LEVEL (Junior, Senior, Staff)
    * Junior-Mid: clarity, correctness, thinking process
    * Senior: ownership, cross-team alignment, decision-making
    * Staff: strategy, multi-team scope, org-level influence
- Questions should elicit AUTHENTIC details that can't be fabricated
============================================================
""" if include_probing else ""

        return f"""You are a FAANG-level behavioral interview examiner.
Your task is to evaluate the candidate EXACTLY as a real interviewer would, based on the LEVEL they are interviewing for.

You MUST follow the internal evaluation style, tone, rubric, and structure used in actual Meta/Google/Amazon interview feedback systems.

===================
INPUT:
- LEVEL: {level}
- BEHAVIORAL QUESTION: {question}
- CANDIDATE ANSWER: {answer}
===================

OUTPUT (Follow this structure EXACTLY):

============================================================
1. Real-Time Raw Notes (Interviewer's scratch notes)
- Bullet points only
- Short fragments, keywords, abbreviations
- No full sentences
- Simulate EXACTLY how FAANG interviewers type quick notes
============================================================

============================================================
2. Formal Interview Summary (for hiring committee)
- 4–7 sentences
- Objective, concise, professional
- Summarize the scenario, actions, tradeoffs, results
- LEVEL-appropriate expectations must be reflected
============================================================

============================================================
3. Strengths (Interviewer perspective)
- Bullet points
- Must reflect the LEVEL
    * Junior-Mid: clarity, reliability, structured thinking
    * Senior: ownership, cross-functional collaboration, execution
    * Staff: influence, multi-team strategy, systemic thinking
============================================================

============================================================
4. Areas for Improvement
- Bullet points
- Every candidate must have 1–2 realistic improvement points
- Must match LEVEL expectations (e.g., Staff has higher bar)
============================================================

============================================================
5. Competency Ratings (use FAANG rubric)
Use:
Strong(🌟) / Meets+(👍) / Meets(👌) / Below(🤔) / Concern(❌)

Dimensions:
- Ownership
- Problem Solving
- Execution
- Collaboration
- Communication
- Leadership / Influence (LEVEL-dependent definition)
- Culture Fit
============================================================

============================================================
6. Final Overall Recommendation
Choose:
- 🌟 Strong Hire
- 👍Hire
- 🤔 Leaning Hire
- 🤨 Leaning No Hire
- ❌ No Hire

STRICT RATING RULES (MUST follow):
- If ANY competency is Concern(❌): rating MUST be No Hire
- If ANY competency is Below(🤔): rating MUST be Leaning No Hire or worse
- For Staff level: if Leadership/Influence is not Strong(🌟) or Meets+(👍), rating MUST be Leaning No Hire or worse
- For Senior level: if Ownership is Below(🤔), rating MUST be Leaning No Hire or worse

Include a short justification (1–3 sentences)
aligned with real FAANG interviewer tone,
and LEVEL-appropriate reasoning.
============================================================
{probing_section}
IMPORTANT:
- Do NOT give coaching, advice, or rewrite answers.
- Only evaluate.
"""

    def red_flag(question: str, answer: str, level: str = "Junior-Mid") -> str:
        """
        Generate prompt for red flag evaluation

        Args:
            question: Behavioral question
            answer: Candidate's answer
            level: Level of the candidate (Junior-Mid, Senior, Staff)

        Returns:
            Formatted prompt string
        """
        return f"""You are a FAANG-level behavioral interview examiner.  
Your task is to evaluate ONLY whether the candidate’s behavioral answer contains Red Flags.  
Your judgment must strictly match actual Meta/Google/Amazon interviewer standards.

=====================
INPUT
- LEVEL: {level}
- QUESTION: {question}
- ANSWER: {answer}
=====================

OUTPUT (follow this structure exactly):

=====================
1. Red Flag Detection
- If no Red Flags → Output: “Red Flags: None”
- If Red Flags exist → List each specific Red Flag
- Use precise wording FAANG interviewers use (e.g., "blames others", "no ownership", "fabrication risk", "communication breakdown", "lack of reflection", "ambiguity avoidance", “overclaiming contribution”, etc.)
=====================

=====================
2. Red Flag Severity Rating
For EACH Red Flag, rate severity using:
★☆☆☆☆ = very minor, unlikely to impact hire
★★☆☆☆ = mild concern
★★★☆☆ = moderate concern (can block hire depending on other signals)
★★★★☆ = major concern, likely No Hire
★★★★★ = critical red flag, immediate No Hire

Use realistic FAANG standards.
If no Red Flags → Output: “N/A”
=====================

=====================
3. Short Justification (Interviewer Tone)
- 1–3 bullet points maximum
- Extremely concise, objective, professional
- Written as if for hiring committee
=====================

=====================
4. Improvement Suggestions (very concise)
- Give 2–3 **specific & actionable** suggestions
- No fluff, no coaching tone
- MUST be ≤ 5 bullet points
- Tailored to LEVEL
=====================

IMPORTANT:
- Do NOT rewrite the candidate’s answer.
- Do NOT provide general behavioral advice.
- Only evaluate Red Flags and give precise, compact improvement points.
- Tone must match FAANG interviewer feedback: objective, unemotional, concise.
"""

    def followup_calibration(original_rating: str) -> str:
        """
        Additional prompt to calibrate rating based on follow-up Q&A responses
        Append this after bar_raiser() when evaluating with follow-ups

        Args:
            original_rating: The rating from the initial evaluation (e.g., "Leaning No Hire")
        """
        return f"""
--- FOLLOW-UP CALIBRATION ---
The candidate has answered follow-up probing questions after their initial answer.
The ORIGINAL rating (before follow-ups) was: {original_rating}

IMPORTANT: The "7. Final Overall Recommendation" section above MUST reflect the CALIBRATED rating after considering follow-up responses, NOT the original rating.

Add this section AFTER section 7:

============================================================
8. Follow-up Assessment

**Follow-up Result:** Pass / No-Pass

Evaluate EACH follow-up response against these criteria:
- Specificity: Did they provide NEW concrete details (names, numbers, timelines, metrics) not in the original answer?
- Depth: Did they explain the WHY behind decisions, not just repeat WHAT happened?
- Consistency: Were there any contradictions or gaps compared to the original story?
- Ownership: Did they clearly own their actions or deflect to "we" / blame others?
- Self-awareness: Did they acknowledge tradeoffs, limitations, or learnings?

Pass ONLY if:
- Majority of follow-up responses add meaningful new information
- No contradictions or red flags introduced
- Demonstrates genuine understanding, not rehearsed/vague responses

No-Pass if:
- Responses are vague, repetitive, or lack new details
- Candidate struggles to answer or contradicts original story
- Shows shallow understanding when probed deeper

**Follow-up Feedback:**
- 2-3 specific bullet points on follow-up performance
- Reference specific Q&A that was strong or weak

**Rating Calibration:**
- Original Rating: {original_rating}
- Final Rating: [the calibrated rating from section 7]
- Reason: [1-2 sentences explaining upgrade/downgrade/no change]
============================================================
"""

    def bar_raiser(level: str = "Senior") -> str:
        return f"""
--- STRICT BAR ENFORCEMENT ---
Evaluate strictly for {level} level. If the example does not clearly demonstrate
{level}-level ownership, scope, and impact, downgrade the rating aggressively.

--- OWNERSHIP TRACING ---
Perform ownership tracing on every step of the answer.
Reward only the actions clearly driven by the candidate.
Penalize any ambiguity or executor-style contribution.

--- SCOPE VALIDATION ---
Challenge the scope of the example.
If the impact is limited to the candidate's immediate task or small surface area,
mark the competency as Below or Concern.

--- NEGATIVITY BIAS MODEL ---
Apply realistic FAANG interviewer negativity bias:
Assume no skill unless explicitly demonstrated.
Penalize vagueness, assumptions, or unsupported claims harshly.

--- DATA-DRIVEN REQUIREMENT ---
Check for explicit data-driven decision making.
If impact or decisions lack metrics, measurements, profiling data, or quantifiable reasoning,
downgrade ratings by one level.

--- CURRENT INDUSTRY CONTEXT (IMPORTANT) ---
Assume the interview is taking place in late 2025, where:
- SWE/SDE hiring is extremely competitive
- HC is minimal
- interviewers are explicitly instructed to raise the hiring bar
- only clearly exceptional, immediately productive candidates should pass

As a result:
- Treat borderline answers as Leaning No Hire or No Hire
- Require clear, unambiguous {level}-level ownership, scope, and impact
- Penalize vagueness, missing metrics, unclear scope, or executor-style contributions
- Do not give the benefit of the doubt unless explicitly demonstrated
"""


class BQAnswer:
    def improve_story(feedback_full_content: str) -> str:
        return f"""You are a FAANG-level behavioral interview answer optimizer.

Your task:
Using ONLY the content inside INPUT: section, extract the candidate's original answer
and rewrite it into a significantly stronger version that meets the highest bar for a FAANG Senior-level behavioral interview.

MANDATORY REQUIREMENTS:
- Output ONLY the improved answer (no analysis, no explanation, no bullet points).
- The improved answer MUST:
    • Achieve Solid Strong on ALL FAANG behavioral competencies:
        - Ownership
        - Problem Solving
        - Execution
        - Collaboration
        - Communication
        - Leadership / Influence
        - Culture Fit
    • Achieve a Solid Strong Hire final recommendation.
    • Fix every weakness mentioned in the MD feedback.
    • Eliminate every Red Flag with high-confidence "no red flags".
    • Demonstrate unambiguous ownership, senior-level scope, and cross-team influence.
    • Include measurable impact, metrics, trade-offs, decision reasoning.
    • Remain realistic and credible for a FAANG Senior Engineer.

INPUT:
{feedback_full_content}

Now produce ONLY the improved answer."""

    def improve_with_probing_answers(
        original_answer: str,
        feedback: str,
        probing_qa: list[dict]
    ) -> str:
        """
        Generate prompt to improve answer using user's real answers to probing questions.

        Args:
            original_answer: The candidate's original answer
            feedback: The feedback received from evaluation
            probing_qa: List of dicts with 'q' (question) and 'a' (user's answer)

        Returns:
            Formatted prompt string
        """
        qa_text = "\n".join([f"Q: {qa['q']}\nA: {qa['a']}\n" for qa in probing_qa])

        return f"""You are a FAANG-level behavioral interview answer optimizer.

Your task:
Rewrite the original answer into a Strong Hire version by using the USER'S REAL ANSWERS
to fix every weakness in the FEEDBACK. Do NOT fabricate - use only what the user provided.

MANDATORY REQUIREMENTS:
- Output ONLY the improved answer (no analysis, no explanation, no bullet points).
- The improved answer MUST:
    • Achieve Solid Strong on ALL FAANG behavioral competencies:
        - Ownership
        - Problem Solving
        - Execution
        - Collaboration
        - Communication
        - Leadership / Influence
        - Culture Fit
    • Achieve a Solid Strong Hire final recommendation.
    • Fix every weakness mentioned in the FEEDBACK using the user's real details.
    • Eliminate every Red Flag using the user's authentic reflections and specifics.
    • Demonstrate unambiguous ownership using the user's specific decisions and actions.
    • Include the exact metrics and numbers the user provided.
    • Include the user's real mistakes and lessons learned for genuine reflection.
    • Remain realistic and credible - the user's real experience is the foundation.

INPUT:

=== ORIGINAL ANSWER ===
{original_answer}

=== FEEDBACK (WEAKNESSES TO FIX) ===
{feedback}

=== USER'S PROBING ANSWERS (USE THESE TO FIX WEAKNESSES) ===
{qa_text}

Now produce ONLY the improved answer."""


class BQFeedback:
    """LLM prompts and regex helpers for extracting content from feedback markdown files"""

    def extract_question(feedback_full_content: str) -> str:
        """LLM prompt to extract question"""
        return f"""Extract only the content under the "## Question" section from the markdown input below.
Output only the question text, nothing else.

Input:
{feedback_full_content}"""

    def extract_answer(feedback_full_content: str) -> str:
        """LLM prompt to extract answer"""
        return f"""Extract only the content under the "## Answer" section from the markdown input below.
Output only the answer text, nothing else.

Input:
{feedback_full_content}"""

    def is_perfect(content: str) -> str:
        """LLM prompt to check if Strong Hire with no red flags"""
        return f"""Read the content inside INPUT: section and evaluate two conditions:

(1) The Final Overall Recommendation must be "Strong Hire".
(2) The Red Flag section must indicate that there are no red flags.

If and only if BOTH conditions are met, output: True
Otherwise output: False

Output ONLY True or False, with no explanation.

Input:
{content}"""


class StoryBuilder:
    """Prompts for building initial BQ stories from scratch"""

    def generate_draft(
        category: str,
        sub_scenario: str,
        question: str,
        user_responses: list[dict],
        level: str = "Senior"
    ) -> str:
        """Generate initial STAR draft from user's core responses"""
        qa_text = "\n".join([f"Q: {r['q']}\nA: {r['a']}\n" for r in user_responses])

        competencies = "\n".join(f"- {c}" for c in BQQuestions.COMPETENCIES)

        return f"""Create a STAR-format behavioral interview answer.

QUESTION: "{question}"
SCENARIO: {category} / {sub_scenario}

USER'S INPUT:
{qa_text}

The answer will be evaluated on these FAANG competencies:
{competencies}

REQUIREMENTS:
- Use ONLY the user's real details - do NOT fabricate
- Emphasize personal ownership and specific actions
- Include metrics/numbers where user provided them

Output ONLY the story."""