import os
import sys
from pathlib import Path

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from interview_analyzer import InterviewAnalyzer
from prompts import BQQuestions, BQAnswer, BQFeedback
from utils import FeedbackRecorder, StreamProcessor


class StorySelfImprove:
    def __init__(
        self,
        feedback_file: Path | None = None,
        feedback_full_content: str | None = None,
        level: str = "Junior-Mid",
    ):
        self.analyzer = InterviewAnalyzer()
        self.feedback_file = feedback_file
        self._feedback_full_content = feedback_full_content
        self._question = None
        self._answer = None
        self._improved_answer = None
        self._feedback = None
        self._red_flag_feedback = None
        self.level = level
        # iterate times
        self.iterate_times = 0

    @property
    def feedback_full_content(self) -> str:
        if not self._feedback_full_content and self.feedback_file:
            with open(self.feedback_file, "r", encoding="utf-8") as f:
                self._feedback_full_content = f.read()
        return self._feedback_full_content

    async def question(self) -> str | None:
        if not self._question:
            prompt = BQFeedback.extract_question(self.feedback_full_content)
            result = await self.analyzer.customized_analyze(prompt, stream=True)
            self._question = await StreamProcessor.get_text(result)
        return self._question

    async def answer(self) -> str | None:
        if not self._answer:
            prompt = BQFeedback.extract_answer(self.feedback_full_content)
            result = await self.analyzer.customized_analyze(prompt, stream=True)
            self._answer = await StreamProcessor.get_text(result)
        return self._answer

    async def improved_answer(self) -> str | None:
        if not self._improved_answer:
            prompt = BQAnswer.improve_story(self.feedback_full_content)
            result = await self.analyzer.customized_analyze(prompt, stream=True)
            self._improved_answer = await StreamProcessor.get_text(result)
        return self._improved_answer

    async def feedback(self) -> str | None:
        if not self._feedback:
            prompt = BQQuestions.real_interview(await self.question(), await self.improved_answer(), self.level) + BQQuestions.bar_raiser()
            result = await self.analyzer.customized_analyze(prompt, stream=True)
            self._feedback = await StreamProcessor.get_text(result)
        return self._feedback

    async def red_flag_feedback(self) -> str | None:
        if not self._red_flag_feedback:
            prompt = BQQuestions.red_flag(await self.question(), await self.improved_answer(), self.level) + BQQuestions.bar_raiser()
            result = await self.analyzer.customized_analyze(prompt, stream=True)
            self._red_flag_feedback = await StreamProcessor.get_text(result)
        return self._red_flag_feedback

    async def is_perfect(self) -> bool:
        prompt = BQFeedback.is_perfect(self.feedback_full_content)
        result = await self.analyzer.customized_analyze(prompt, stream=True)
        is_perfect = await StreamProcessor.get_text(result)
        return is_perfect == "True"

    async def run(self) -> None:
        if await self.is_perfect():
            print(f"The answer is perfect, no need to improve after {self.iterate_times} iterations.")
            return
        elif self.iterate_times >= 5:
            print(f"The answer is not perfect after {self.iterate_times} iterations, need to stop.")
            return
        else:
            print("The answer is not perfect, need to improve.")
            self.iterate_times += 1
            feedback_recorder = FeedbackRecorder()
            feedback_filepath = feedback_recorder.save_feedback(
                question=await self.question(),
                answer=await self.answer(),
                feedback=await self.feedback(),
                red_flag=await self.red_flag_feedback()
            )
            self.feedback_file = Path(feedback_filepath)
            await self.run()
