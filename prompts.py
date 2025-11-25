"""
Prompt templates for BQ Interview Analyzer
"""

# System messages
SYSTEM_MESSAGE_INTRODUCTION = (
    "You are an expert FAANG behavioral interviewer with deep knowledge of hiring standards "
    "at Google, Amazon, Apple, Netflix, and Meta. Provide honest, constructive, and detailed "
    "feedback following FAANG evaluation criteria."
)

SYSTEM_MESSAGE_BQ_QUESTION = (
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
    MOST_CHALLENGING_PROJECT = """
    Tell me about your most challenging project.
    """
    TECHNICAL_PROBLEM_SOLVING = """
    Tell me about a time you faced a technical problem and how you solved it.
    """
    LEADERSHIP_EXPERIENCE = """
    Tell me about a time you led a team.
    """
    TEAM_COLLABORATION = """
    Tell me about a time you collaborated with a team.
    """
    PROBLEM_SOLVING = """
    Tell me about a time you faced a problem and how you solved it.
    """
    DECISION_MAKING = """
    Tell me about a time you faced a decision and how you made it.
    """
    COMMUNICATION = """
    Tell me about a time you communicated with a team.
    """
    LEARNING_EXPERIENCE = """
    Tell me about a time you learned something new.
    """
    TEAM_WORK = """
    Tell me about a time you worked with a team.
    """
    PROBLEM_SOLVING = """
    Tell me about a time you faced a problem and how you solved it.
    """
    DECISION_MAKING = """
    Tell me about a time you faced a decision and how you made it.
    """
    COMMUNICATION = """
    Tell me about a time you communicated with a team.
    """
    LEARNING_EXPERIENCE = """
    Tell me about a time you learned something new.
    """
    TEAM_WORK = """
    Tell me about a time you worked with a team.
    """
    PROBLEM_SOLVING = """
    Tell me about a time you faced a problem and how you solved it.
    """
    DECISION_MAKING = """
    Tell me about a time you faced a decision and how you made it.
    """
    COMMUNICATION = """
    Tell me about a time you communicated with a team.
    """
    LEARNING_EXPERIENCE = """
    Tell me about a time you learned something new.
    """
    TEAM_WORK = """
    Tell me about a time you worked with a team.
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

