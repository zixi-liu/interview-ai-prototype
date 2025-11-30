import os
import sys
import asyncio
from pathlib import Path

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from interview_analyzer import InterviewAnalyzer
from prompts import BQQuestions
from utils import FeedbackParser
from utils import Colors
from storage import LocalStorage

# Path to feedback file
FEEDBACK_FILE = Path(_project_root) / "feedbacks" / "20251129-Leaning_No_Hire.md"

# Sample follow-up answers (you need to write these based on the probing questions)
FOLLOWUP_ANSWERS = [
    # Q1: Can you elaborate on the specific data you used?
    """I gathered three key data points: First, I pulled revenue impact projections from
    our product team showing the feature would drive $2M ARR if launched in Q1. Second,
    I got infrastructure metrics showing our current system was at 78% capacity with
    projected failures at 85%. Third, I calculated engineering velocity data showing
    we could deliver 60% of both projects' scope with a hybrid allocation. I presented
    these in a simple spreadsheet comparing scenarios.""",

    # Q2: How did you ensure all voices were heard?
    """I structured the meeting in three phases. First, I gave each team lead 10 uninterrupted
    minutes to present their case. Second, I created a shared doc where everyone could add
    concerns anonymously before the meeting. Third, I specifically called on quieter team
    members to share their views. The infrastructure junior engineer actually raised a
    critical dependency we'd missed, which changed our timeline estimates.""",

    # Q3: What metrics did you track post-allocation?
    """We tracked three metrics weekly: sprint velocity for both teams, the revenue
    pipeline from the product feature, and system uptime for infrastructure. After
    8 weeks, product had shipped their MVP generating $800K in pipeline, and infrastructure
    had improved system capacity to handle 40% more load. Both teams hit their adjusted
    milestones within 2 weeks of the original timeline.""",
]


def parse_feedback_file(filepath: Path) -> dict:
    """Parse the feedback markdown file"""
    with open(filepath, "r") as f:
        content = f.read()

    return {
        "rating": FeedbackParser.extract_rating(content),
        "question": FeedbackParser.extract_question(content),
        "answer": FeedbackParser.extract_answer(content),
        "probing_questions": FeedbackParser.extract_probing_questions(content),
    }


async def test_followup_evaluation():
    """Test follow-up evaluation by parsing existing feedback file"""
    analyzer = InterviewAnalyzer()
    storage = LocalStorage()

    print("=" * 80)
    print("TESTING FOLLOW-UP QUESTIONS EVALUATION")
    print("=" * 80)

    # Parse the feedback file
    print(f"\nParsing: {FEEDBACK_FILE}")
    data = parse_feedback_file(FEEDBACK_FILE)

    question = data.get("question", "")
    answer = data.get("answer", "")
    original_rating = data.get("rating", "Unknown")
    probing_questions = data.get("probing_questions", [])

    print(f"\nQuestion: {question}")
    print(f"\nOriginal Rating: {original_rating}")
    print(f"\nFound {len(probing_questions)} probing questions:")
    for i, q in enumerate(probing_questions, 1):
        print(f"  {i}. {q}")

    # Build follow-up Q&A pairs
    followup_qa = list(zip(probing_questions[:len(FOLLOWUP_ANSWERS)], FOLLOWUP_ANSWERS))

    print("\n" + "-" * 40)
    print("Follow-up Q&A:")
    for i, (q, a) in enumerate(followup_qa, 1):
        print(f"\nQ{i}: {q}")
        print(f"A{i}: {a}")

    # Format combined answer with follow-ups
    followup_text = ""
    for i, (fq, fa) in enumerate(followup_qa, 1):
        followup_text += f"\n--- Follow-up Q{i}: {fq}\n--- Answer: {fa}\n"

    combined_answer = f"{answer}\n\n=== FOLLOW-UP Q&A ==={followup_text}"

    # Generate follow-up evaluation
    print("\n" + "=" * 80)
    print("Generating follow-up evaluation...")
    print("=" * 80 + "\n")

    prompt = (
        BQQuestions.real_interview(question, combined_answer, "Junior-Mid", include_probing=False)
        + BQQuestions.bar_raiser()
        + BQQuestions.followup_calibration(original_rating)
    )

    result = await analyzer.customized_analyze(prompt, stream=True)
    feedback_followup = await Colors.stream_and_print(result)

    # Extract new rating
    new_rating = FeedbackParser.extract_rating(feedback_followup) or "Unknown"

    print("\n" + "=" * 80)
    print(f"RESULT: {original_rating} -> {new_rating}")
    print("=" * 80)

    return feedback_followup


async def main():
    await test_followup_evaluation()


if __name__ == "__main__":
    asyncio.run(main())
