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


class IntroductionPrompt:
    @staticmethod
    def analyze(introduction: str, role: str, company: str) -> str:
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
- Generate 3–6 targeted probing questions based on the specific weaknesses identified above
- ORDER BY PRIORITY (most critical first):
    * Competencies rated Concern(❌) → highest priority
    * Competencies rated Below(🤔) → high priority
    * Gaps in "Areas for Improvement" (section 4) → medium priority
- Questions MUST be:
    * Specific to THIS answer (not generic templates)
    * Targeting the actual gaps found in sections 4 & 5
    * Designed to clarify personal contribution vs team effort
    * Aligned with LEVEL expectations (Junior-Mid/Senior/Staff)
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
        DEPRECATED: Use blind_calibration() instead for unbiased evaluation.
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

    @staticmethod
    def blind_calibration(
        question: str,
        answer_a: str,
        rating_a: str,
        answer_b: str,
        rating_b: str
    ) -> str:
        """
        Blind calibration prompt - compares two answers without revealing which is 'improved'.
        Used after both answers have been evaluated independently.

        Args:
            question: The BQ question
            answer_a: First answer (original)
            rating_a: Rating for first answer
            answer_b: Second answer (after follow-up)
            rating_b: Rating for second answer
        """
        return f"""You are calibrating interview ratings for two answers to the same behavioral question.

QUESTION: {question}

ANSWER A:
{answer_a}

RATING A: {rating_a}

---

ANSWER B:
{answer_b}

RATING B: {rating_b}

---

CALIBRATION TASK:
Compare the two answers and explain why the ratings are different (or the same).

Evaluate:
1. What specific details does Answer B have that Answer A lacks? (or vice versa)
2. Is the rating difference justified based on actual content differences?
3. Are both ratings accurate, or should either be adjusted?

OUTPUT FORMAT:
============================================================
Rating Calibration

**Answer A Rating:** {rating_a}
**Answer B Rating:** {rating_b}
**Rating Changed:** Yes / No

**Calibration Reason:**
[2-3 sentences explaining why the ratings differ or are the same.
Reference specific content differences that justify the rating change,
or explain why no change is warranted despite any superficial differences.]

**Key Differences:**
- [Bullet points of substantive differences between answers]
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


class ProbingAgent:
    """
    Agentic probing using Value of Information (VoI) framework.

    KEY DESIGN PRINCIPLE:
    We do NOT manually define competency rubrics - the LLM already knows
    FAANG interview standards from its training data. Instead, we:
    1. Define the ACTION SPACE (ASK/STOP)
    2. Define the VoI FORMULA (cost-benefit)
    3. Let LLM infer competency assessments from its knowledge

    Decision Rule:
        if max(VoI) > 0: ASK(argmax(VoI))
        else: STOP

    Based on:
    - "Active Information Gathering for Long-Horizon Navigation Under
       Uncertainty by Learning the Value of Information" (Arnob & Stein, 2024)
    """

    # Cost parameters (the ONLY hardcoded values)
    BASE_COST = 0.15          # Minimum cost per probe (user time/fatigue)
    FATIGUE_FACTOR = 0.05     # Additional cost per turn
    MAX_TURNS = 8             # Hard cap on probing

    @staticmethod
    def initial_assessment(
        question: str,
        answer: str,
        level: str = "Senior"
    ) -> str:
        """
        Initial assessment prompt - LLM identifies gaps using its FAANG knowledge.
        No hardcoded dimensions - LLM decides what matters for this level.
        """
        return f"""You are a FAANG behavioral interviewer assessing an answer to identify probing opportunities.

LEVEL: {level}
QUESTION: {question}
ANSWER: {answer}

Using your knowledge of {level}-level FAANG interview standards, assess this answer.

For each competency gap you identify:
1. Name the gap (e.g., "ownership", "metrics", "tradeoffs", "depth", "reflection")
2. Assess its severity for {level} level (critical/important/minor)
3. Rate your confidence in the assessment (0-100%)
4. Estimate probe value: would probing likely yield useful info? (high/medium/low)

IMPORTANT: Only list gaps that are RELEVANT to {level} level.
- Junior-Mid: Focus on clarity, specifics, basic ownership
- Senior: Focus on ownership, cross-team impact, decision-making, metrics
- Staff: Focus on strategic thinking, org-wide influence, tradeoffs, leadership

OUTPUT (JSON only):
{{
  "gaps": [
    {{
      "name": "<gap name>",
      "severity": "<critical|important|minor>",
      "confidence": <0-100>,
      "probe_value": "<high|medium|low>",
      "evidence": "<brief observation from answer>",
      "suggested_probe": "<example question to ask>"
    }}
  ],
  "overall_confidence": <0-100>,
  "initial_impression": "<1-2 sentence summary>",
  "recommendation": "<ready_to_evaluate|needs_probing>"
}}"""

    @staticmethod
    def decide_action(
        question: str,
        original_answer: str,
        conversation_history: list[tuple[str, str]],
        current_assessment: str,
        turn_count: int,
        level: str = "Senior"
    ) -> str:
        """
        Core decision prompt: ASK or STOP?

        LLM computes VoI implicitly using its FAANG knowledge.
        We provide the formula; LLM provides the competency understanding.
        """
        history_text = "\n".join([
            f"PROBE: {q}\nRESPONSE: {a}\n" for q, a in conversation_history
        ]) if conversation_history else "None yet"

        cost = ProbingAgent.BASE_COST + ProbingAgent.FATIGUE_FACTOR * turn_count
        remaining_budget = ProbingAgent.MAX_TURNS - turn_count

        return f"""You are a FAANG interviewer deciding whether to probe further.

=== CONTEXT ===
Level: {level}
Question: {question}
Turn: {turn_count + 1}/{ProbingAgent.MAX_TURNS}
Current cost per probe: {cost:.2f}
Remaining budget: {remaining_budget} probes

=== ORIGINAL ANSWER ===
{original_answer}

=== PROBING SO FAR ===
{history_text}

=== CURRENT ASSESSMENT ===
{current_assessment}

=== DECISION FRAMEWORK (Value of Information) ===

For each potential probe, compute:
  VoI = (severity × probe_value × uncertainty) - cost

Where:
- severity: How critical is this gap for {level}? (0.0-1.0)
- probe_value: How likely will probing reveal useful info? (0.0-1.0)
- uncertainty: How uncertain are you about this dimension? (0.0-1.0)
- cost: {cost:.2f} (fixed, increases with fatigue)

DECISION RULE:
- If max(VoI) > 0 → ASK the highest-VoI gap
- If max(VoI) ≤ 0 → STOP (no probe is worth the cost)
- If overall_confidence >= 80% → STOP (enough info gathered)

STOP CONDITIONS (any one triggers STOP):
1. All gaps have VoI ≤ 0
2. Overall confidence >= 80%
3. Last 2 responses showed diminishing returns (same info repeated)
4. User showed inability to provide more detail on a gap

OUTPUT (JSON only):
{{
  "voi_analysis": [
    {{"gap": "<name>", "severity": <0-1>, "probe_value": <0-1>, "uncertainty": <0-1>, "voi": <computed>}}
  ],
  "max_voi": <highest VoI>,
  "action": "ASK" or "STOP",
  "target_gap": "<if ASK: which gap>",
  "probe_question": "<if ASK: natural question to ask>",
  "reasoning": "<1-2 sentences>",
  "updated_confidence": <0-100>
}}"""

    # Response Type Ontology
    # These are FEATURES for the policy to reason over, not hardcoded rules
    # Includes OTHER as escape hatch for ontology discovery
    RESPONSE_TYPES = {
        "ANSWER_GOOD": "User provided a strong, specific answer with concrete details, metrics, or examples",
        "ANSWER_VAGUE": "User answered but response lacks specifics, depth, or concrete examples",
        "ANSWER_PARTIAL": "User addressed only part of the question, leaving key aspects unanswered",
        "ASKS_QUESTION": "User asks for clarification about the probe or has a follow-up question",
        "SAYS_IDK": "User explicitly admits they don't know, can't remember, or don't have that info",
        "OFF_TOPIC": "User's response doesn't relate to the probe at all",
        "NEW_INFO": "User reveals new information not in original answer that changes assessment",
        "PUSHBACK": "User disagrees with the premise, challenges the question, or pushes back",
        "OTHER": "None of the above types fit well - describe what you observe",
    }

    # Policy hints (not hardcoded behavior - just guidance for LLM)
    POLICY_HINTS = {
        "ANSWER_GOOD": "Mark gap as resolved, move to next critical gap or STOP",
        "ANSWER_VAGUE": "Either re-probe same gap with more specific question, or move on",
        "ANSWER_PARTIAL": "Follow up on the missing part, or accept and move on",
        "ASKS_QUESTION": "Answer their question, then re-ask the probe or rephrase",
        "SAYS_IDK": "Mark gap as unresolvable, move to next gap",
        "OFF_TOPIC": "Acknowledge briefly, redirect to the probe",
        "NEW_INFO": "Update assessment, may reveal new gaps to probe",
        "PUSHBACK": "Acknowledge their perspective, adjust approach or move on",
        "OTHER": "Use best judgment based on the specific situation",
    }

    @staticmethod
    def step_prompt(
        question: str,
        original_answer: str,
        evaluation_summary: dict,
        conversation_history: list[tuple[str, str]],
        remaining_probes: list[str],
        turn_count: int,
        max_turns: int,
        level: str = "Senior"
    ) -> str:
        """
        Combined step prompt: classify response → apply policy → generate output.
        ONE LLM call per turn.

        The response type ontology provides a discrete representation of user behavior
        that a policy can reason over. This is aligned with RL principles:
        - Define a small feature space (response types)
        - Let the model learn the mapping from text to types
        - Let the model learn optimal policy for each type
        """
        history_text = "\n".join([
            f"Q{i+1}: {q}\nA{i+1}: {a}\n" for i, (q, a) in enumerate(conversation_history)
        ]) if conversation_history else "None yet"

        last_qa = conversation_history[-1] if conversation_history else None
        last_probe = last_qa[0] if last_qa else ""
        last_response = last_qa[1] if last_qa else ""

        remaining_text = "\n".join([f"- {q}" for q in remaining_probes[:3]]) if remaining_probes else "None"

        weak_comps = ", ".join(evaluation_summary.get("weak_competencies", [])) or "None identified"
        areas = "\n".join([f"- {a}" for a in evaluation_summary.get("areas_for_improvement", [])]) or "None"

        # Format response types for prompt
        response_types_text = "\n".join([
            f"  - {k}: {v}" for k, v in ProbingAgent.RESPONSE_TYPES.items()
        ])
        policy_hints_text = "\n".join([
            f"  - {k}: {v}" for k, v in ProbingAgent.POLICY_HINTS.items()
        ])

        return f"""You are a FAANG interviewer having a natural follow-up conversation.

=== CONTEXT ===
Level: {level}
Original Question: {question}
Turn: {turn_count}/{max_turns}

=== WEAK AREAS TO PROBE ===
Weak Competencies: {weak_comps}
Areas for Improvement:
{areas}

=== CONVERSATION SO FAR ===
{history_text}

=== LAST EXCHANGE ===
Your question: {last_probe}
Their response: {last_response}

=== STEP 1: CLASSIFY THE RESPONSE ===
Classify the user's response into ONE of these types:
{response_types_text}

Classification guidelines:
- Pick the BEST fitting type
- If unsure between two types, pick the more specific one
- If none fit well, use OTHER and describe what you observe
- Report your confidence and the runner-up type (for ontology refinement)

=== STEP 2: APPLY POLICY ===
Based on the response type, decide your action. Policy guidance:
{policy_hints_text}

=== STEP 3: GENERATE OUTPUT ===
Based on your classification and policy decision, generate your response.

CRITICAL CONVERSATION RULES:
- Be CONVERSATIONAL - speak naturally like a real interviewer
- NEVER repeat the exact same question - always rephrase or build on what they said
- If they asked for clarification (ASKS_QUESTION), answer briefly then ask a DIFFERENT follow-up
- Reference what they just said: "You mentioned X... can you tell me more about Y?"
- If their answer was vague, ask for SPECIFIC details: metrics, names, dates, outcomes

Good: "That's helpful. You mentioned working with the team - what was YOUR specific role in making those decisions?"
Bad: "Can you describe a specific instance?" (repeated verbatim)

Remaining pre-generated probes (use as inspiration, don't copy verbatim):
{remaining_text}

OUTPUT (JSON only):
{{
  "classification": {{
    "response_type": "<ANSWER_GOOD | ANSWER_VAGUE | ANSWER_PARTIAL | ASKS_QUESTION | SAYS_IDK | OFF_TOPIC | NEW_INFO | PUSHBACK | OTHER>",
    "confidence": "<HIGH | MEDIUM | LOW>",
    "runner_up_type": "<second best type, or null if clearly one type>",
    "other_description": "<if OTHER: describe what you observe, else null>"
  }},
  "response_analysis": "<brief analysis of what user said>",
  "action": "<PROBE_NEXT | PROBE_SAME | ANSWER_USER | REDIRECT | STOP>",
  "agent_message": "<your response to the user - question, answer, or closing>",
  "target_gap": "<which gap this targets, if probing>",
  "reasoning": "<1-2 sentences explaining your decision>",
  "state_update": {{
    "gaps_resolved": ["<gaps now addressed>"],
    "gaps_unresolvable": ["<gaps user can't answer>"],
    "gaps_remaining": ["<gaps still to probe>"],
    "new_gaps": ["<any new gaps discovered>"]
  }}
}}"""

    @staticmethod
    def extract_gaps_from_evaluation(
        question: str,
        answer: str,
        evaluation: str,
        level: str = "Senior"
    ) -> str:
        """
        Extract gaps from an existing real_interview() evaluation.

        This is more efficient than running initial_assessment() separately,
        and ensures VoI decisions are based on the same evaluation the user sees.

        Args:
            question: The BQ question
            answer: Candidate's answer
            evaluation: Full evaluation from real_interview() + bar_raiser()
            level: Interview level
        """
        return f"""Extract probing gaps from this existing interview evaluation.

LEVEL: {level}
QUESTION: {question}
ANSWER: {answer}

=== EXISTING EVALUATION ===
{evaluation}
=== END EVALUATION ===

From the evaluation above, extract:
1. Competencies rated Below(🤔) or Concern(❌) → these are CRITICAL gaps
2. Areas for Improvement mentioned → these are IMPORTANT gaps
3. Any probing questions already suggested → use these as starting points

For each gap, assess:
- severity: critical (rated Below/Concern) | important (in Areas for Improvement) | minor
- confidence: How certain is the evaluation? (0-100%)
- probe_value: Would probing likely yield useful info? (high/medium/low)

OUTPUT (JSON only):
{{
  "gaps": [
    {{
      "name": "<gap name: ownership/metrics/tradeoffs/depth/reflection/etc>",
      "severity": "<critical|important|minor>",
      "confidence": <0-100>,
      "probe_value": "<high|medium|low>",
      "source": "<competency rating | area for improvement | suggested probe>",
      "suggested_probe": "<question to ask, from evaluation or generated>"
    }}
  ],
  "competency_summary": {{
    "strong": ["<competencies rated Strong/Meets+>"],
    "weak": ["<competencies rated Below/Concern>"]
  }},
  "overall_confidence": <0-100>,
  "recommendation": "<ready_to_evaluate|needs_probing>"
}}"""

    @staticmethod
    def update_assessment(
        original_answer: str,
        probe: str,
        response: str,
        previous_assessment: str,
        level: str = "Senior"
    ) -> str:
        """
        Update assessment after receiving probe response.
        LLM decides how much the response improved each gap.
        """
        return f"""Update your assessment based on the new probe response.

LEVEL: {level}

ORIGINAL ANSWER:
{original_answer}

PREVIOUS ASSESSMENT:
{previous_assessment}

NEW PROBE: {probe}
USER RESPONSE: {response}

Evaluate the response quality:
1. Did it ADD new information? (specifics, metrics, decisions, timelines)
2. Did it CLARIFY ownership? (I vs we, personal contribution)
3. Did it REVEAL depth? (reasoning, tradeoffs, learnings)
4. Was it CREDIBLE? (consistent, authentic, not rehearsed)

Update gaps based on what was learned. A gap is resolved if:
- Confidence >= 80% AND severity addressed

OUTPUT (JSON only):
{{
  "response_quality": {{
    "added_value": <1-5>,
    "ownership_clarity": <1-5>,
    "depth_revealed": <1-5>,
    "credibility": <1-5>
  }},
  "gaps_updated": [
    {{
      "name": "<gap>",
      "old_confidence": <0-100>,
      "new_confidence": <0-100>,
      "resolved": <true|false>,
      "what_learned": "<brief note>"
    }}
  ],
  "remaining_gaps": [
    {{
      "name": "<gap>",
      "severity": "<critical|important|minor>",
      "confidence": <0-100>,
      "probe_value": "<high|medium|low>"
    }}
  ],
  "overall_confidence": <0-100>,
  "diminishing_returns": <true|false>
}}"""

    # ===== LEGACY METHODS (for backward compatibility with test_voi.py) =====

    # Gap types that can be probed (maps to STAR dimensions)
    GAP_TYPES = [
        "situation_context",   # Background, timeline, stakeholders
        "task_ownership",      # Why was it YOUR responsibility?
        "action_specifics",    # What exactly did you do?
        "action_tradeoffs",    # What alternatives did you consider?
        "result_metrics",      # Quantified impact?
        "result_learnings",    # What did you learn?
    ]

    # Competency criticality by level (how important each dimension is)
    # NOTE: These are kept for backward compatibility but the new approach
    # lets LLM determine criticality from its training knowledge
    CRITICALITY_MATRIX = {
        "Junior-Mid": {
            "situation_context": 0.4,
            "task_ownership": 0.6,
            "action_specifics": 0.9,
            "action_tradeoffs": 0.5,
            "result_metrics": 0.7,
            "result_learnings": 0.4,
        },
        "Senior": {
            "situation_context": 0.4,
            "task_ownership": 1.0,
            "action_specifics": 0.7,
            "action_tradeoffs": 0.85,
            "result_metrics": 0.9,
            "result_learnings": 0.6,
        },
        "Staff": {
            "situation_context": 0.5,
            "task_ownership": 1.0,
            "action_specifics": 0.6,
            "action_tradeoffs": 0.95,
            "result_metrics": 0.9,
            "result_learnings": 0.75,
        },
    }

    STATUS_SEVERITY = {
        "missing": 1.0,
        "weak": 0.7,
        "adequate": 0.3,
        "strong": 0.0,
    }

    CONFIDENCE_THRESHOLDS = {
        "Junior-Mid": 70,
        "Senior": 80,
        "Staff": 85,
    }

    @staticmethod
    def compute_voi(
        gap: str,
        status: str,
        confidence: int,
        level: str,
        turn_count: int
    ) -> float:
        """Legacy VoI computation for backward compatibility."""
        severity = ProbingAgent.STATUS_SEVERITY.get(status, 0.5)
        criticality = ProbingAgent.CRITICALITY_MATRIX.get(level, {}).get(gap, 0.5)
        uncertainty = (100 - confidence) / 100
        cost = ProbingAgent.BASE_COST + ProbingAgent.FATIGUE_FACTOR * turn_count
        voi = (severity * criticality * uncertainty) - cost
        return round(voi, 3)

    @staticmethod
    def rank_gaps_by_voi(
        dimensions: dict,
        level: str,
        turn_count: int
    ) -> list[tuple[str, float]]:
        """Legacy gap ranking for backward compatibility."""
        voi_scores = []
        for gap, dim in dimensions.items():
            voi = ProbingAgent.compute_voi(
                gap=gap,
                status=dim.get("status", "adequate"),
                confidence=dim.get("confidence", 50),
                level=level,
                turn_count=turn_count
            )
            voi_scores.append((gap, voi))
        return sorted(voi_scores, key=lambda x: -x[1])

    @staticmethod
    def decide_action_by_voi(
        dimensions: dict,
        level: str,
        turn_count: int
    ) -> tuple[str, str | None, str]:
        """Legacy VoI decision for backward compatibility."""
        ranked = ProbingAgent.rank_gaps_by_voi(dimensions, level, turn_count)
        if not ranked:
            return ("STOP", None, "No dimensions to evaluate")
        best_gap, best_voi = ranked[0]
        if best_voi > 0:
            return ("ASK", best_gap, f"VoI({best_gap}) = {best_voi:.3f} > 0, worth probing")
        else:
            return ("STOP", None, f"max VoI = {best_voi:.3f} ≤ 0, no probe is worth the cost")

    @staticmethod
    def parse_decision(json_str: str) -> dict:
        """Parse the decision JSON."""
        import json
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback: try to extract action from text
            if "STOP" in json_str.upper():
                return {"action": "STOP", "reasoning": "Parse failed, defaulting to STOP"}
            return {"action": "STOP", "reasoning": "Parse failed", "error": json_str}


class ProcessRewardModel:
    """
    Lightweight reward models for RL-based interview training.

    Two levels:
    1. AnswerPRM: Scores a complete answer (used for final eval)
    2. StepPRM: Scores each probe response (used during conversation)

    These are separate from the full Teacher prompt (real_interview + bar_raiser)
    which generates rich human-readable feedback.
    """

    # Competency dimensions (same as BQQuestions.COMPETENCIES)
    DIMENSIONS = [
        "ownership",
        "problem_solving",
        "execution",
        "collaboration",
        "communication",
        "leadership",
        "culture_fit",
    ]

    @staticmethod
    def answer_prm(
        question: str,
        answer: str,
        level: str = "Senior"
    ) -> str:
        """
        Lightweight PRM for scoring a complete BQ answer.
        Returns JSON-only output for RL/programmatic use.

        Use this instead of real_interview() when you only need scores,
        not the full human-readable feedback.
        """
        return f"""Score this behavioral interview answer. Output ONLY valid JSON, no other text.

LEVEL: {level}
QUESTION: {question}
ANSWER: {answer}

SCORING RULES (apply {level}-level expectations):
- 1 = Concern (❌) - Missing, problematic, or red flag
- 2 = Below (🤔) - Insufficient for {level} level
- 3 = Meets (👌) - Acceptable, meets minimum bar
- 4 = Meets+ (👍) - Good, solid demonstration
- 5 = Strong (🌟) - Exceptional, exceeds expectations

DECISION RULES:
- Any score = 1 → no_hire
- Any score = 2 → leaning_no_hire or worse
- Average < 3 → leaning_no_hire
- Average >= 4 → hire or strong_hire
- All scores >= 4 with majority 5 → strong_hire

{{
  "scores": {{
    "ownership": <1-5>,
    "problem_solving": <1-5>,
    "execution": <1-5>,
    "collaboration": <1-5>,
    "communication": <1-5>,
    "leadership": <1-5>,
    "culture_fit": <1-5>
  }},
  "total": <sum of all scores>,
  "average": <average score to 2 decimal places>,
  "decision": "<strong_hire|hire|leaning_hire|leaning_no_hire|no_hire>",
  "weakest": "<lowest scoring dimension>",
  "strongest": "<highest scoring dimension>",
  "rationale": "<1 sentence explaining the decision>"
}}"""

    @staticmethod
    def step_prm(
        original_answer: str,
        probe_question: str,
        probe_response: str,
        conversation_history: str = "",
        level: str = "Senior"
    ) -> str:
        """
        Step-level PRM for scoring individual probe responses.
        Used during conversational probing to get per-turn rewards.

        This enables:
        - Credit assignment (which response improved what)
        - Early stopping (satisfied = enough info gathered)
        - Next probe selection (what weakness to target next)
        """
        history_section = f"""
CONVERSATION HISTORY:
{conversation_history}
""" if conversation_history else ""

        return f"""Score this single follow-up response in a behavioral interview. Output ONLY valid JSON.

LEVEL: {level}

ORIGINAL ANSWER:
{original_answer}
{history_section}
PROBE QUESTION: {probe_question}

CANDIDATE'S RESPONSE: {probe_response}

SCORING DIMENSIONS (1-5 scale):

1. ADDED_VALUE: Did this response add NEW information?
   - 1: Just repeated original answer, no new details
   - 3: Added some new context but nothing substantial
   - 5: Added significant new details (names, numbers, decisions, timelines)

2. OWNERSHIP: Did they demonstrate personal contribution?
   - 1: Only "we" language, deflected to team, no personal ownership
   - 3: Mixed "we/I", some personal actions but unclear scope
   - 5: Clear "I decided/built/proposed" with specific personal actions

3. SPECIFICITY: Were concrete details provided?
   - 1: Vague, generic, no specifics
   - 3: Some details but missing key specifics (metrics, names, timelines)
   - 5: Precise metrics, names, dates, technical details

4. DEPTH: Did they explain WHY, not just WHAT?
   - 1: Surface-level description only
   - 3: Some reasoning but incomplete
   - 5: Clear tradeoffs, decision rationale, lessons learned

5. CREDIBILITY: Does it sound authentic?
   - 1: Sounds rehearsed, inconsistent, possibly fabricated
   - 3: Plausible but lacks conviction
   - 5: Natural, consistent with original, authentic details

6. COMPOSURE: How well did they handle the probe?
   - 1: Defensive, confused, evasive, or flustered
   - 3: Adequate but showed some hesitation
   - 5: Confident, direct, thoughtful, welcomed the challenge

SATISFACTION CHECK:
- Set "satisfied" = true ONLY if this response provided enough new information
  to address the probe's intent (usually scores >= 4 on added_value + specificity)
- Set "satisfied" = false if more probing would likely yield useful information

NEXT PROBE SELECTION:
- Based on remaining weaknesses, suggest what to probe next
- Options: ownership, metrics, depth, reflection, scope, collaboration, none

{{
  "scores": {{
    "added_value": <1-5>,
    "ownership": <1-5>,
    "specificity": <1-5>,
    "depth": <1-5>,
    "credibility": <1-5>,
    "composure": <1-5>
  }},
  "total": <sum>,
  "average": <average to 2 decimal>,
  "satisfied": <true|false>,
  "next_probe": "<ownership|metrics|depth|reflection|scope|collaboration|none>",
  "rationale": "<1 sentence on what this response did well or poorly>"
}}"""

    @staticmethod
    def batch_step_prm(
        original_answer: str,
        qa_pairs: list[tuple[str, str]],  # [(probe1, response1), (probe2, response2), ...]
        level: str = "Senior"
    ) -> str:
        """
        Batch scoring of ALL probe responses in one call.

        Call this ONCE at end of session instead of per-turn.
        Much more efficient - single API call for entire conversation.

        Args:
            original_answer: The candidate's original BQ answer
            qa_pairs: List of (probe_question, user_response) tuples
            level: Interview level

        Returns:
            Prompt that outputs JSON array of scores
        """
        # Format Q&A pairs
        qa_text = ""
        for i, (probe, response) in enumerate(qa_pairs, 1):
            qa_text += f"""
--- TURN {i} ---
PROBE: {probe}
RESPONSE: {response}
"""

        return f"""Score ALL follow-up responses in this behavioral interview. Output ONLY valid JSON.

LEVEL: {level}

ORIGINAL ANSWER:
{original_answer}

FOLLOW-UP CONVERSATION:
{qa_text}

For EACH turn, score these dimensions (1-5):
- added_value: New info vs repetition (5 = significant new details)
- ownership: Personal "I" actions vs "we" deflection (5 = clear ownership)
- specificity: Concrete details, metrics, names (5 = precise specifics)
- depth: WHY not just WHAT (5 = clear reasoning/tradeoffs)
- credibility: Authentic vs rehearsed (5 = natural, consistent)
- composure: Handled pressure well (5 = confident, direct)

Also identify:
- improvement_trajectory: Did responses get better over turns?
- key_turn: Which turn added the most value?
- remaining_gaps: What's still missing after all probing?

{{
  "turns": [
    {{
      "turn": 1,
      "scores": {{
        "added_value": <1-5>,
        "ownership": <1-5>,
        "specificity": <1-5>,
        "depth": <1-5>,
        "credibility": <1-5>,
        "composure": <1-5>
      }},
      "total": <sum>,
      "rationale": "<what this turn contributed>"
    }},
    // ... one object per turn
  ],
  "summary": {{
    "total_turns": {len(qa_pairs)},
    "average_score": <average across all turns>,
    "improvement_trajectory": "<improving|stable|declining>",
    "key_turn": <turn number that added most value>,
    "remaining_gaps": ["<gap1>", "<gap2>"],
    "overall_probing_result": "<successful|partial|unsuccessful>"
  }}
}}"""

    @staticmethod
    def parse_step_reward(json_str: str) -> dict:
        """Parse StepPRM JSON output into reward dict."""
        import json
        try:
            data = json.loads(json_str)
            return {
                "scores": data.get("scores", {}),
                "total": data.get("total", 0),
                "average": data.get("average", 0.0),
                "satisfied": data.get("satisfied", False),
                "next_probe": data.get("next_probe", "none"),
                "rationale": data.get("rationale", ""),
            }
        except json.JSONDecodeError:
            return {"error": "Failed to parse PRM output", "raw": json_str}

    @staticmethod
    def parse_batch_reward(json_str: str) -> dict:
        """Parse batched StepPRM JSON output."""
        import json
        try:
            data = json.loads(json_str)
            return {
                "turns": data.get("turns", []),
                "summary": data.get("summary", {}),
            }
        except json.JSONDecodeError:
            return {"error": "Failed to parse batch PRM output", "raw": json_str}

    @staticmethod
    def compute_reward(scores: dict) -> float:
        """
        Compute scalar reward from StepPRM scores.

        Returns a value in [-1, 1] range for RL.
        - Negative: Poor response, made things worse
        - Zero: Neutral, no progress
        - Positive: Good response, added value
        """
        if not scores or "scores" in scores and not scores["scores"]:
            return 0.0

        s = scores.get("scores", scores)

        # Weighted average (ownership and specificity matter most)
        weights = {
            "added_value": 1.5,
            "ownership": 2.0,
            "specificity": 1.5,
            "depth": 1.0,
            "credibility": 1.0,
            "composure": 0.5,
        }

        total_weight = sum(weights.values())
        weighted_sum = sum(s.get(k, 3) * w for k, w in weights.items())

        # Normalize to [-1, 1] range
        # Score range is 1-5, midpoint is 3
        # (weighted_avg - 3) / 2 maps [1,5] to [-1,1]
        weighted_avg = weighted_sum / total_weight
        reward = (weighted_avg - 3) / 2

        return round(reward, 3)


class AutoCompletion:
    """Prompts for auto-completion of self-introduction and BQ answers"""

    @staticmethod
    def self_intro_completion(partial_text: str, role: str = "Software Engineer", company: str = "FAANG") -> str:
        """Generate completion suggestions for self-introduction"""
        return f"""You are an expert FAANG behavioral interviewer helping a candidate complete their self-introduction.

SCENARIO: Self-introduction for {role} position at {company}
CANDIDATE'S PARTIAL INPUT:
{partial_text}

TASK:
1. FIRST, check if the last sentence clearly indicates the introduction has ENDED.
   - Look for closing phrases like: "Thank you", "I'm looking forward to...", "That's all", "I'm excited to...", or sentences that clearly conclude the introduction
   - If the last sentence is a clear ending/closing statement, the introduction is STRUCTURALLY COMPLETE
   - If structurally complete, output: {{"is_complete": true, "message": "Your self-introduction is structurally complete. Consider evaluating it to ensure all key elements are covered."}}
   - DO NOT provide completions if the introduction has a clear ending.

2. If the last sentence does NOT indicate an ending, evaluate content completeness:
   - A complete self-intro SHOULD cover these elements:
     * Background: Who you are and your experience level
     * Relevant experience: What you've worked on
     * Key achievements: Specific accomplishments with metrics if possible
     * Motivation: Why you're interested in this role/company
     * Connection: How you align with the role/company
   - If ALL elements are present and well-structured (1-2 minutes when spoken), output: {{"is_complete": true, "message": "Your self-introduction is already complete and strong."}}
   - DO NOT provide completions if the introduction is already complete.
   
3. ONLY if NOT complete, analyze what's missing and generate the TOP 3 most recommended completion options.
   - GENERATION PROCESS (think through this implicitly before generating each option):
     Step 1: Deeply analyze the partial input's QUALITY and CURRENT LEVEL:
       * Assess the partial input's strength level: Is it weak/vague, solid, or already strong?
       * Identify what STRONG elements already exist in partial_text:
         - Clear ownership statements? (I led, I designed, I implemented)
         - Quantified metrics/impact? (numbers, percentages, scale)
         - Technical depth? (specific technologies, architectures, solutions)
         - Cross-functional impact? (collaboration, influence beyond own team)
         - Clear connection to role/company? (why this role matters)
       * Identify CRITICAL GAPS that prevent Strong Hire rating:
         - Missing ownership (too vague, "we" instead of "I")
         - No metrics or quantifiable impact
         - Lacks technical depth or specificity
         - Missing connection to target role/company
         - Insufficient demonstration of impact or scope
       * Note the writing style and quality level to match in completions
       * Identify the last character(s): punctuation, space, or mid-word
       * Determine if the last sentence is complete or incomplete
       * Note the grammatical structure and context at the end
     
     Step 2: Design each completion to ELEVATE to Strong Hire level:
       * Base completions on the gaps identified in Step 1
       * If partial_text is weak/vague: Generate completions that ADD strong elements (ownership, metrics, technical depth)
       * If partial_text is already solid: Generate completions that ADD missing Strong Hire elements (specific metrics, cross-functional impact, clear connection)
       * If partial_text is already strong: Generate completions that REINFORCE and AMPLIFY existing strengths
       * Each completion should address at least ONE critical gap that would prevent Strong Hire
       * Match the quality and style of existing content - don't create jarring quality jumps
       * Prioritize completions that add the MOST VALUE toward Strong Hire rating
     
     Step 3: For each potential completion option, think about fluency AND Strong Hire impact BEFORE finalizing:
       * Mentally combine the partial input with each potential completion (partial_input + " " + completion)
       * Read the combined text aloud in your mind to check naturalness and flow
       * Verify grammatical correctness of the combined sentence/paragraph
       * Ensure proper punctuation, capitalization, spacing, and word flow
       * Check for awkward transitions, redundant words, or grammatical errors
       * EVALUATE: Would the combined text meet Strong Hire criteria?
         - Does it show clear ownership? (I statements, personal impact)
         - Does it include quantifiable metrics/impact? (numbers, scale, measurable outcomes)
         - Does it demonstrate technical depth? (specific tech, architecture, solutions)
         - Does it connect to the target role/company? (clear alignment, motivation)
         - Does it show appropriate scope/impact for the role level?
       * If the combined text reads awkwardly OR doesn't strengthen toward Strong Hire, revise the completion
       * Only proceed with completions that create seamless, fluent combined text AND elevate toward Strong Hire
     
     Step 4: Finalize only options that pass BOTH fluency test AND Strong Hire enhancement test:
       * Each completion MUST create fluent, natural-sounding text when appended to partial input
       * Each completion MUST add value that moves the combined text toward Strong Hire rating
       * Prioritize options that seamlessly integrate AND address critical Strong Hire gaps
       * Reject or revise any option that would create awkward text OR doesn't strengthen the answer
       * Ensure the combined text reads as if written as one continuous, coherent paragraph that demonstrates Strong Hire qualities

   - STRONG HIRE COMPLETION STRATEGY: Each completion option should be designed to help achieve Strong Hire rating by:
     * Adding specific, quantifiable metrics and impact (e.g., "reducing latency by 40%", "serving 10M+ users", "improving team velocity by 25%")
     * Demonstrating clear ownership with "I" statements and personal impact (e.g., "I led", "I designed and implemented", "I owned the end-to-end")
     * Showing technical depth and specificity (e.g., "using microservices architecture", "implementing Redis caching layer", "building event-driven systems")
     * Connecting explicitly to the target role/company (e.g., "I'm excited about Meta's scale", "aligns with Google's focus on", "leverages Amazon's infrastructure")
     * Demonstrating appropriate scope for {role} level (cross-functional impact for Senior+, strategic thinking for Staff)
     * Maintaining consistency with partial_text's quality level and style
   
   - COMPLETION LENGTH CONSTRAINT: Each completion option MUST be ≤ 1 complete sentence.
     * If the last sentence in partial_text is incomplete: Complete that sentence only (do not start a new sentence)
     * If the last sentence in partial_text is complete: Generate exactly 1 complete sentence that adds the next logical element
     * DO NOT generate multiple sentences or paragraph-length completions
     * Keep completions concise and focused on adding one key Strong Hire element per option
   
   - Each option should be a natural continuation that:
     * Completes the current incomplete sentence if the last sentence is incomplete (finish within that one sentence), OR
     * Adds exactly 1 complete sentence with the next logical missing element if the last sentence is complete, prioritizing elements that move toward Strong Hire
   
   - CRITICAL FLUENCY REQUIREMENT: Each completion MUST create a grammatically correct and fluent sentence when appended to the partial input.
     * Analyze the LAST CHARACTER of the partial input to determine how to start the completion:
       - If it ends with a period (.), exclamation (!), or question mark (?): Start the completion with a space and capital letter to begin a new sentence (e.g., ". I have..." or ". With over...")
       - If it ends with a comma (,), semicolon (;), or colon (:): Continue the sentence naturally after the punctuation (e.g., ", specializing in..." or "; I've worked on...")
       - If it ends with a space or no punctuation but the sentence is complete: Start with a period and space, then continue (e.g., ". I have..." or ". With...")
       - If it ends mid-word or mid-sentence (no punctuation, sentence clearly incomplete): Continue seamlessly without adding punctuation (e.g., if input is "I am a software engin", complete as "eer with...")
     * ALWAYS mentally verify the combined text (partial_input + " " + completion) reads as ONE fluent, grammatically correct paragraph before finalizing
     * Example GOOD: Input "I am a software engineer" → Completion " with over five years of experience building scalable systems that serve millions of users..." (fluent AND adds Strong Hire elements: experience, scale, impact)
     * Example GOOD: Input "I am a software engineer," → Completion " and I've led multiple projects that reduced system latency by 40%..." (fluent AND adds ownership + metrics)
     * Example BAD: Input "I am a software engineer" → Completion "I have over five years..." (would create "I am a software engineer I have..." - grammatically incorrect! REJECT)
     * Example BAD: Input "I am a software engineer" → Completion " and I like coding" (grammatically correct but too vague/weak - doesn't move toward Strong Hire! REJECT)
   
   - Options should follow FAANG Strong Hire interview best practices:
     * Be specific and concrete with quantifiable impact (avoid vague statements like "worked on", "helped", "involved in")
     * Show clear ownership and personal impact (use "I" statements, demonstrate direct contribution)
     * Demonstrate technical depth and specificity (name technologies, architectures, design decisions)
     * Include metrics and measurable outcomes (numbers, percentages, scale, user impact)
     * Connect explicitly to the target role/company (show understanding and alignment)
     * Demonstrate appropriate scope for {role} level (technical leadership, cross-functional work, strategic impact)
     * Be concise, professional, and authentic
   - Output format:
     {{
       "is_complete": true/false,
       "reason": "why the introduction is completed or not",
       "confidence": "[0-100%]",
       "completions": [
         {{
           "text": "completion option 1",
           "reason": "why this is recommended",
           "confidence": "[0-100%]",
           "fluency": "[0-100%]",
           "red_flag": "N/A or specific red flag"
         }},
         {{
           "text": "completion option 2",
           "reason": "why this is recommended",
           "confidence": "[0-100%]",
           "fluency": "[0-100%]",
           "red_flag": "N/A or specific red flag"
         }},
         {{
           "text": "completion option 3",
           "reason": "why this is recommended",
           "confidence": "[0-100%]",
           "fluency": "[0-100%]",
           "red_flag": "N/A or specific red flag"
         }}
       ]
     }}

CRITICAL RULES:
- PRIORITY 1: If the last sentence clearly ends the introduction (closing statement), return is_complete: true immediately
- PRIORITY 2: If all content elements are present, return is_complete: true
- Only generate completions if the introduction is NOT structurally complete (no clear ending) AND missing content
- STRONG HIRE FOCUS: All completions must be designed to elevate the combined text toward Strong Hire rating
  * Analyze partial_text quality first, then generate completions that fill critical gaps
  * Prioritize completions that add ownership, metrics, technical depth, and role connection
  * Ensure completions match and enhance the quality level of existing content
- LENGTH CONSTRAINT: Each completion MUST be ≤ 1 complete sentence (never multiple sentences or paragraphs)
- All completions must be realistic, authentic, and follow FAANG Strong Hire standards
- Output ONLY valid JSON, no additional text"""

    @staticmethod
    def bq_answer_completion(
        partial_text: str,
        question: str,
        role: str = "Software Engineer",
        level: str = "Senior"
    ) -> str:
        """Generate completion suggestions for BQ answer"""
        return f"""You are an expert FAANG behavioral interviewer helping a candidate complete their behavioral question answer.

SCENARIO: Behavioral question answer for {role} position (Level: {level})
QUESTION: {question}
CANDIDATE'S PARTIAL ANSWER:
{partial_text}

TASK:
1. FIRST, check if the last sentence clearly indicates the answer has ENDED.
   - Look for closing phrases like: "That's how I...", "In conclusion", "Overall", "The key takeaway", or sentences that clearly conclude the story/answer
   - If the last sentence is a clear ending/closing statement, the answer is STRUCTURALLY COMPLETE
   - If structurally complete, output: {{"is_complete": true, "message": "Your answer is structurally complete. Consider evaluating it to ensure all STAR elements and {level}-level requirements are covered."}}
   - DO NOT provide completions if the answer has a clear ending.

2. If the last sentence does NOT indicate an ending, evaluate content completeness:
   - A complete BQ answer SHOULD have ALL of these STAR elements:
     * Situation: Clear context and background
     * Task: Specific challenge or goal
     * Action: Detailed actions taken (with clear ownership)
     * Result: Measurable outcomes and impact
   - For {level} level, also require:
     * Clear ownership and personal contribution (not just "we")
     * Cross-functional impact (for Senior+)
     * Specific metrics and quantifiable results
     * Reflection/learnings (when appropriate)
   - If ALL required elements are present and well-structured, output: {{"is_complete": true, "message": "Your answer is already complete and follows STAR format well."}}
   - DO NOT provide completions if the answer is already complete.
   
3. ONLY if NOT complete, analyze what's missing and generate the TOP 3 most recommended completion options.
   - GENERATION PROCESS (think through this implicitly before generating each option):
     Step 1: Deeply analyze the partial input's QUALITY and CURRENT LEVEL:
       * Assess the partial input's strength level: Is it weak/vague (Leaning No Hire), solid (Hire), or already strong (Strong Hire)?
       * Identify what STRONG elements already exist in partial_text:
         - Clear STAR structure? (Situation, Task, Action, Result)
         - Unambiguous ownership? (I led, I designed, I decided - not "we did")
         - Quantified metrics/impact? (numbers, percentages, scale, measurable outcomes)
         - Technical depth and specificity? (specific technologies, architectures, solutions, trade-offs)
         - Cross-functional impact? (for Senior+: collaboration, influence beyond own team)
         - Problem-solving and decision-making? (how decisions were made, why, trade-offs considered)
         - Reflection/learnings? (what was learned, how it improved future work)
       * Identify CRITICAL GAPS that prevent Strong Hire rating:
         - Missing or weak STAR elements (which sections are incomplete/weak?)
         - Lack of ownership (too vague, "we" instead of "I", executor-style contributions)
         - No metrics or quantifiable impact (missing numbers, scale, measurable outcomes)
         - Lacks technical depth or specificity (vague descriptions, no trade-offs)
         - Missing {level}-level scope (insufficient cross-functional impact for Senior+, no strategic thinking for Staff)
         - No reflection or learnings (missing meta-cognition)
       * Note the writing style and quality level to match in completions
       * Identify the last character(s): punctuation, space, or mid-word
       * Determine if the last sentence is complete or incomplete
       * Note the grammatical structure and context at the end
     
     Step 2: Design each completion to ELEVATE to Strong Hire level:
       * Base completions on the gaps identified in Step 1
       * If partial_text is weak/vague (Leaning No Hire level): Generate completions that ADD strong STAR elements, ownership, metrics, technical depth
       * If partial_text is solid (Hire level): Generate completions that ADD missing Strong Hire elements (specific metrics, cross-functional impact, reflection, {level}-appropriate scope)
       * If partial_text is already strong (Strong Hire level): Generate completions that REINFORCE and AMPLIFY existing strengths
       * Each completion should address at least ONE critical gap that would prevent Strong Hire
       * Match the quality and style of existing content - don't create jarring quality jumps
       * Prioritize completions that add the MOST VALUE toward Strong Hire rating for {level} level
     
     Step 3: For each potential completion option, think about fluency AND Strong Hire impact BEFORE finalizing:
       * Mentally combine the partial input with each potential completion (partial_input + " " + completion)
       * Read the combined text aloud in your mind to check naturalness and flow
       * Verify grammatical correctness of the combined sentence/paragraph
       * Ensure proper punctuation, capitalization, spacing, and word flow
       * Check for awkward transitions, redundant words, or grammatical errors
       * EVALUATE: Would the combined text meet Strong Hire criteria for {level} level?
         - Does it have complete STAR structure? (all sections present and well-developed)
         - Does it show unambiguous ownership? (I statements, personal decisions, direct impact - not facilitator/executor style)
         - Does it include quantifiable metrics/impact? (specific numbers, percentages, scale, measurable outcomes)
         - Does it demonstrate technical depth? (specific tech, architecture, design decisions, trade-offs)
         - Does it show {level}-appropriate scope? (cross-functional for Senior+, strategic for Staff)
         - Does it show problem-solving and decision-making? (how/why decisions were made)
         - Does it include reflection/learnings? (meta-cognition, improvement)
       * If the combined text reads awkwardly OR doesn't strengthen toward Strong Hire, revise the completion
       * Only proceed with completions that create seamless, fluent combined text AND elevate toward Strong Hire
     
     Step 4: Finalize only options that pass BOTH fluency test AND Strong Hire enhancement test:
       * Each completion MUST create fluent, natural-sounding text when appended to partial input
       * Each completion MUST add value that moves the combined text toward Strong Hire rating for {level} level
       * Prioritize options that seamlessly integrate AND address critical Strong Hire gaps
       * Reject or revise any option that would create awkward text OR doesn't strengthen the answer
       * Ensure the combined text reads as if written as one continuous, coherent STAR-formatted answer that demonstrates Strong Hire qualities

   - STRONG HIRE COMPLETION STRATEGY: Each completion option should be designed to help achieve Strong Hire rating for {level} level by:
     * Adding specific, quantifiable metrics and impact (e.g., "reduced latency by 40%", "served 10M+ users", "improved team velocity by 25%", "decreased error rate from 2% to 0.1%")
     * Demonstrating clear ownership with "I" statements and personal impact (e.g., "I led the design", "I decided to", "I owned the end-to-end", "I made the trade-off to")
     * Showing technical depth and specificity (e.g., "using microservices architecture", "implementing Redis caching layer", "chose X over Y because", "considered trade-offs between")
     * Demonstrating {level}-appropriate scope (for Senior+: cross-functional collaboration, influence beyond own team; for Staff: strategic thinking, multi-team impact)
     * Including problem-solving and decision-making reasoning (e.g., "I analyzed", "I considered", "The key trade-off was", "I decided because")
     * Adding reflection/learnings when appropriate (e.g., "This taught me", "The key takeaway was", "I learned that")
     * Completing STAR elements that are missing or weak (ensure all STAR sections are well-developed)
     * Maintaining consistency with partial_text's quality level and style
   
   - COMPLETION LENGTH CONSTRAINT: Each completion option MUST be ≤ 1 complete sentence.
     * If the last sentence in partial_text is incomplete: Complete that sentence only (do not start a new sentence)
     * If the last sentence in partial_text is complete: Generate exactly 1 complete sentence that adds the next logical STAR element or Strong Hire component
     * DO NOT generate multiple sentences or paragraph-length completions
     * Keep completions concise and focused on adding one key Strong Hire element per option
   
   - Each option should be a natural continuation that:
     * Completes the current incomplete sentence if the last sentence is incomplete (finish within that one sentence), OR
     * Moves to the next logical STAR section with exactly 1 complete sentence if current section is complete, OR
     * Adds exactly 1 complete sentence with missing critical Strong Hire elements (metrics, ownership, impact, reflection, {level}-appropriate scope), prioritizing elements that move toward Strong Hire
   
   - CRITICAL FLUENCY REQUIREMENT: Each completion MUST create a grammatically correct and fluent sentence when appended to the partial input.
     * Analyze the LAST CHARACTER of the partial input to determine how to start the completion:
       - If it ends with a period (.), exclamation (!), or question mark (?): Start the completion with a space and capital letter to begin a new sentence (e.g., ". This resulted in..." or ". The key takeaway...")
       - If it ends with a comma (,), semicolon (;), or colon (:): Continue the sentence naturally after the punctuation (e.g., ", which led to..." or "; I decided to...")
       - If it ends with a space or no punctuation but the sentence is complete: Start with a period and space, then continue (e.g., ". I then..." or ". The outcome...")
       - If it ends mid-word or mid-sentence (no punctuation, sentence clearly incomplete): Continue seamlessly without adding punctuation
     * ALWAYS mentally verify the combined text (partial_input + " " + completion) reads as ONE fluent, grammatically correct paragraph before finalizing
     * Example GOOD: Input "I was working on a project" → Completion ". My task was to reduce system latency, and I implemented a caching layer using Redis that decreased response time by 40%..." (fluent AND adds Strong Hire elements: task clarity, ownership, technical depth, metrics)
     * Example GOOD: Input "I led the team," → Completion " and I made the decision to use microservices architecture, which improved our deployment frequency by 3x..." (fluent AND adds ownership + decision-making + metrics)
     * Example BAD: Input "I was working on a project" → Completion "My task was to..." (would create "I was working on a project My task was to..." - grammatically incorrect! REJECT)
     * Example BAD: Input "I was working on a project" → Completion " and it went well" (grammatically correct but too vague/weak - doesn't move toward Strong Hire! REJECT)
   
   - Options should follow FAANG Strong Hire interview best practices for {level} level:
     * Use complete STAR method structure with all sections well-developed
     * Show unambiguous ownership and personal contribution (use "I" statements, avoid "we", demonstrate direct impact, not facilitator/executor style)
     * Include specific metrics and quantifiable results (numbers, percentages, scale, measurable outcomes - required for Strong Hire)
     * Demonstrate {level}-level scope and impact (for Senior+: cross-functional collaboration; for Staff: strategic, multi-team influence)
     * Show problem-solving and decision-making (explain how decisions were made, trade-offs considered, reasoning)
     * Include reflection/learnings when appropriate (meta-cognition, what was learned, how it improved future work)
     * Demonstrate technical depth and specificity (name technologies, architectures, design decisions, trade-offs)
     * Be concise, professional, and authentic
   - Output format:
     {{
       "is_complete": true/false,
       "reason": "why the introduction is completed or not",
       "confidence": "[0-100%]",
       "completions": [
         {{
           "text": "completion option 1",
           "reason": "why this is recommended",
           "confidence": "[0-100%]"
         }},
         {{
           "text": "completion option 2",
           "reason": "why this is recommended",
           "confidence": "[0-100%]"
         }},
         {{
           "text": "completion option 3",
           "reason": "why this is recommended",
           "confidence": "[0-100%]"
         }}
       ]
     }}

CRITICAL RULES:
- PRIORITY 1: If the last sentence clearly ends the answer (closing statement), return is_complete: true immediately
- PRIORITY 2: If all STAR elements are present, return is_complete: true
- Only generate completions if the answer is NOT structurally complete (no clear ending) AND missing STAR elements
- STRONG HIRE FOCUS: All completions must be designed to elevate the combined text toward Strong Hire rating for {level} level
  * Analyze partial_text quality first (assess current rating level: Leaning No Hire, Hire, or Strong Hire)
  * Identify existing strong elements and critical gaps that prevent Strong Hire
  * Generate completions that fill critical gaps (ownership, metrics, technical depth, {level}-appropriate scope, reflection)
  * Prioritize completions that add the most value toward Strong Hire rating
  * Ensure completions match and enhance the quality level of existing content
- LENGTH CONSTRAINT: Each completion MUST be ≤ 1 complete sentence (never multiple sentences or paragraphs)
- All completions must be realistic, authentic, and demonstrate {level}-level competency that meets Strong Hire standards
- Output ONLY valid JSON, no additional text"""

    @staticmethod
    def check_fluency(partial_text: str, completion: str) -> str:
        """Check if the completion is fluent and natural-sounding"""
        return f"""You are a FAANG interviewer checking the fluency of the sentence.

        INPUT:
        - SENTENCE: {partial_text}{completion}

        OUTPUT (follow this structure exactly):
        {{
            "is_fluent": true/false,
            "reason": "why the completion is fluent or not",
            "confidence": "[0-100%]"
        }}"""