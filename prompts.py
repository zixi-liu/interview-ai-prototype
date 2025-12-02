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


class ConversationalInterview:
    """Prompts for conversational follow-up using plan-then-execute approach.

    Step 1: Planning - LLM selects top 3 questions (JSON output)
    Step 2: Execution - Probe each question separately (max 5 rounds each)
    """

    MAX_ROUNDS_PER_QUESTION = 5
    NUM_QUESTIONS = 3

    @staticmethod
    def planning_prompt(feedback: str, probing_questions: list) -> str:
        """Prompt for planning which 3 questions to probe"""
        pq_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(probing_questions)])

        return f"""You are a FAANG interviewer planning follow-up probing questions.

EVALUATION FEEDBACK:
{feedback}

AVAILABLE PROBING QUESTIONS:
{pq_text}

YOUR TASK:
Select the 3 most critical questions to probe. Prioritize questions that target:
- Competencies rated Below (🤔) or Concern (❌)
- Areas where the candidate was vague or lacked specifics
- Ownership and metrics gaps

OUTPUT FORMAT (JSON only, no other text):
{{
  "questions": [
    {{"id": 1, "question": "exact question text", "reason": "why this is critical"}},
    {{"id": 2, "question": "exact question text", "reason": "why this is critical"}},
    {{"id": 3, "question": "exact question text", "reason": "why this is critical"}}
  ]
}}"""

    @staticmethod
    def probe_system_prompt(level: str = "Senior", conversation_history: str = "") -> str:
        """System prompt for probing a single question"""
        if conversation_history:
            history_check = f"""
=== FOLLOW-UP CONVERSATION (check signals HERE only) ===
{conversation_history}
=== END FOLLOW-UP CONVERSATION ===

CRITICAL RULE - CHECK FOLLOW-UP CONVERSATION ABOVE:
Scan ONLY the follow-up conversation above for these signals:
- Numbers/percentages (e.g., "50%", "200 tickets", "$2M", "3 months")
- Specific timeframes (e.g., "2 hours", "6 months", "Q3")
- Concrete metrics (e.g., "precision improved", "reduced errors by X")
- Personal actions with "I" (e.g., "I decided", "I proposed", "I built")

If ANY signal found → output ONLY: [SATISFIED]
Do NOT ask another question if they gave specifics."""
        else:
            history_check = """
No follow-up conversation yet. You MUST ask your probing question first."""

        return f"""You are a FAANG behavioral interviewer probing ONE specific question.

LEVEL: {level}
{history_check}

YOUR STYLE:
- Be conversational but professional
- Question ownership: if they say "we", ask what THEY did
- Challenge inconsistencies
- If user seems confused or asks for clarification, provide an example to guide them

FORMAT: [SATISFIED], a follow-up question, or answer to their question."""

    @staticmethod
    def probe_context(
        original_question: str,
        original_answer: str,
        probing_question: str,
        question_num: int,
        total_questions: int
    ) -> str:
        """Initial context for probing a single question"""
        return f"""=== CONTEXT ===
ORIGINAL BQ: {original_question}

CANDIDATE'S ANSWER:
{original_answer}

=== PROBING QUESTION {question_num}/{total_questions} ===
{probing_question}

Ask this question now. Be direct."""


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
   
2. ONLY if NOT complete, analyze what's missing and generate the TOP 3 most recommended completion options.
   - Each option should be a natural continuation that:
     * Completes the current incomplete sentence if the last sentence is incomplete, OR
     * Adds the next logical missing element if the last sentence is complete
   - Options should follow FAANG interview best practices:
     * Be specific and concrete (avoid vague statements)
     * Show ownership and impact
     * Demonstrate technical depth
     * Connect to the target role/company
     * Be concise and professional
   - Output format:
     {{
       "is_complete": false,
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
- PRIORITY 1: If the last sentence clearly ends the introduction (closing statement), return is_complete: true immediately
- PRIORITY 2: If all content elements are present, return is_complete: true
- Only generate completions if the introduction is NOT structurally complete (no clear ending) AND missing content
- All completions must be realistic, authentic, and follow FAANG standards
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
   
2. ONLY if NOT complete, analyze what's missing and generate the TOP 3 most recommended completion options.
   - Each option should be a natural continuation that:
     * Completes the current incomplete sentence if the last sentence is incomplete, OR
     * Moves to the next logical STAR section if current section is complete, OR
     * Adds missing critical elements (metrics, ownership, impact, reflection)
   - Options should follow FAANG interview best practices:
     * Use STAR method structure
     * Show unambiguous ownership and personal contribution
     * Include specific metrics and quantifiable results
     * Demonstrate {level}-level scope and impact
     * Show problem-solving and decision-making
     * Include reflection/learnings when appropriate
   - Output format:
     {{
       "is_complete": false,
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
- All completions must be realistic, authentic, and demonstrate {level}-level competency
- Output ONLY valid JSON, no additional text"""