import os
import sys
import asyncio
from pathlib import Path

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from interview_analyzer import InterviewAnalyzer
from prompts import BQQuestions, BQAnswer, BQFeedback
from utils import Colors
from advance.self_improve import StorySelfImprove

example_dir = Path(os.path.dirname(os.path.abspath(__file__)))
root_dir = example_dir.parent
feedback_file = root_dir / "feedbacks" / "20251129-Leaning_No_Hire.md"


async def story_improve():
    with open(feedback_file, "r", encoding="utf-8") as f:
        feedback_full_content = f.read()

    analyzer = InterviewAnalyzer()
    prompt = BQFeedback.extract_question(feedback_full_content)
    result = await analyzer.customized_analyze(prompt, stream=True)
    print("=" * 80)
    print("Question:")
    question = await Colors.stream_and_print(result)

    prompt = BQFeedback.extract_answer(feedback_full_content)
    result = await analyzer.customized_analyze(prompt, stream=True)
    print("=" * 80)
    print("Original Answer:")
    answer = await Colors.stream_and_print(result)

    prompt = BQAnswer.improve_story(feedback_full_content)
    result = await analyzer.customized_analyze(prompt, stream=True)
    print("=" * 80)
    print("Improved Answer:")
    improved_answer = await Colors.stream_and_print(result)

    prompt = BQQuestions.real_interview(question, improved_answer, "Junior-Mid") + BQQuestions.bar_raiser()
    result = await analyzer.customized_analyze(prompt, stream=True)
    feedback = await Colors.stream_and_print(result)

    red_flag_prompt = BQQuestions.red_flag(question, improved_answer, "Junior-Mid") + BQQuestions.bar_raiser()
    red_flag_result = await analyzer.customized_analyze(red_flag_prompt, stream=True)
    red_flag_feedback = await Colors.stream_and_print(red_flag_result)


async def story_improve_with_feedback():
    self_improve = StorySelfImprove(feedback_file=feedback_file)
    print("=" * 80)
    print("Question:")
    print(await self_improve.question())
    print("=" * 80)
    print("Original Answer:")
    print(await self_improve.answer())
    await self_improve.run()
    print("=" * 80)
    print("Improved Answer:")
    print(await self_improve.improved_answer())
    print("=" * 80)
    print("Feedback:")
    print(await self_improve.feedback())
    print("=" * 80)
    print("Red Flag Feedback:")
    print(await self_improve.red_flag_feedback())
    print("=" * 80)
    print("iterate times:")
    print(self_improve.iterate_times)



async def main():
    await story_improve()
    # await story_improve_with_feedback()

if __name__ == "__main__":
    asyncio.run(main())