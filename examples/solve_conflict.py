import os
import sys
import asyncio

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from interview_analyzer import InterviewAnalyzer
from prompts import BQQuestions
from utils import Colors, FeedbackRecorder

GOOD_ANSWER = """
    Certainly. In my previous role I found myself in the midst of a conflict 
    regarding resource allocation for two critical projects within our development team.

    The conflict arose when both the product development and infrastructure enhancement 
    teams were vying for the same limited resources for their respective projects. 
    I could empathise with both their perspectives but it seemed to me that many of 
    the people involved were basing their arguments on their "gut feeling" around what was "fair".

    Recognizing the potential disruption this conflict could cause, I organized a 
    collaborative discussion involving representatives from both teams, project managers, 
    and the leadership. During this discussion, we openly addressed the conflicting priorities 
    and resource needs of each project. I encouraged a transparent sharing of data and information 
    regarding the potential impact of both projects on the company's goals.

    This way we were able to base our discussion around the data, rather than around people's 
    subjective opinions and hunches.

    By presenting a data-driven analysis and illustrating how each project aligned with the 
    company's objectives, we were able to justify the resource allocation for both initiatives. 
    The infrastructure team ended up with slightly less than they were hoping for, 
    but presented with the data, they accepted that this was a fair distribution of resources. 
    In the end, both projects progressed effectively.

    Ultimately, this experience taught me how useful data can be in solving or avoiding these 
    types of conflicts. When people are using opinion, hunches and emotions to make decisions, 
    disagreements occur and they tend to feel more personal. But when the decision-making process 
    is data-driven there is less room for subjective opinion and it becomes easier to align 
    different stakeholders.
    """


async def solve_conflict():
    analyzer = InterviewAnalyzer()
    question = BQQuestions.SOLVED_CONFLICT
    print("=" * 80)
    print(f"Question: {question}")
    answer = GOOD_ANSWER

    print("=" * 80)
    print("Answer:")
    print(answer)

    prompt = BQQuestions.real_interview(question, answer, "Junior-Mid") + BQQuestions.bar_raiser()
    result = await analyzer.customized_analyze(prompt, stream=True)
    feedback = await Colors.stream_and_print(result)

    red_flag_prompt = BQQuestions.red_flag(question, answer, "Junior-Mid") + BQQuestions.bar_raiser()
    red_flag_result = await analyzer.customized_analyze(red_flag_prompt, stream=True)
    red_flag_feedback = await Colors.stream_and_print(red_flag_result)

    feedback_recorder = FeedbackRecorder()
    feedback_recorder.save_feedback(question, answer, feedback)
    feedback_recorder.save_red_flag(question, answer, red_flag_feedback)

async def main():
    await solve_conflict()

if __name__ == "__main__":
    asyncio.run(main())