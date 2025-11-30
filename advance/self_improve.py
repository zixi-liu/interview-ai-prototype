import os
import sys
from pathlib import Path

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from interview_analyzer import InterviewAnalyzer
from prompts import BQQuestions, BQAnswer, BQFeedback
from utils import FeedbackRecorder, FeedbackParser, StreamProcessor


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
            prompt = BQQuestions.real_interview(await self.question(), await self.improved_answer(), self.level) + BQQuestions.bar_raiser(self.level)
            result = await self.analyzer.customized_analyze(prompt, stream=True)
            self._feedback = await StreamProcessor.get_text(result)
        return self._feedback

    async def red_flag_feedback(self) -> str | None:
        if not self._red_flag_feedback:
            prompt = BQQuestions.red_flag(await self.question(), await self.improved_answer(), self.level) + BQQuestions.bar_raiser(self.level)
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
                answer=await self.improved_answer(),
                feedback=await self.feedback(),
                red_flag=await self.red_flag_feedback()
            )
            self.feedback_file = Path(feedback_filepath)
            # Reset cached values for next iteration
            self._feedback_full_content = None
            self._answer = None
            self._improved_answer = None
            self._feedback = None
            self._red_flag_feedback = None
            await self.run()


class HumanInLoopImprove:
    """
    Self-improvement with human in the loop.
    Uses probing questions to gather real details from user,
    then incorporates those details into the improved answer.
    """

    def __init__(
        self,
        feedback_file: Path | None = None,
        feedback_full_content: str | None = None,
        level: str = "Junior-Mid",
        max_iterations: int = 3,
    ):
        self.analyzer = InterviewAnalyzer()
        self.feedback_file = feedback_file
        self._feedback_full_content = feedback_full_content
        self.level = level
        self.max_iterations = max_iterations
        self.iterate_times = 0

        # Cached values
        self._question = None
        self._answer = None
        self._feedback = None
        self._red_flag_feedback = None
        self._probing_questions = None

    @property
    def feedback_full_content(self) -> str:
        if not self._feedback_full_content and self.feedback_file:
            with open(self.feedback_file, "r", encoding="utf-8") as f:
                self._feedback_full_content = f.read()
        return self._feedback_full_content

    def _reset_cache(self):
        """Reset cached values for next iteration"""
        self._feedback_full_content = None
        self._answer = None
        self._feedback = None
        self._red_flag_feedback = None
        self._probing_questions = None

    async def question(self) -> str:
        if not self._question:
            prompt = BQFeedback.extract_question(self.feedback_full_content)
            result = await self.analyzer.customized_analyze(prompt, stream=True)
            self._question = await StreamProcessor.get_text(result)
        return self._question

    async def answer(self) -> str:
        if not self._answer:
            prompt = BQFeedback.extract_answer(self.feedback_full_content)
            result = await self.analyzer.customized_analyze(prompt, stream=True)
            self._answer = await StreamProcessor.get_text(result)
        return self._answer

    def probing_questions(self) -> list[str]:
        """Extract probing questions from feedback using regex (no LLM call)"""
        if not self._probing_questions:
            self._probing_questions = FeedbackParser.extract_probing_questions(
                self.feedback_full_content
            )
        return self._probing_questions

    async def evaluate(self, answer: str) -> str:
        """Evaluate an answer and return feedback"""
        prompt = (
            BQQuestions.real_interview(await self.question(), answer, self.level)
            + BQQuestions.bar_raiser(self.level)
        )
        result = await self.analyzer.customized_analyze(prompt, stream=True)
        return await StreamProcessor.get_text(result)

    async def evaluate_red_flag(self, answer: str) -> str:
        """Evaluate an answer for red flags"""
        prompt = (
            BQQuestions.red_flag(await self.question(), answer, self.level)
            + BQQuestions.bar_raiser(self.level)
        )
        result = await self.analyzer.customized_analyze(prompt, stream=True)
        return await StreamProcessor.get_text(result)

    async def is_strong_hire(self, feedback: str, red_flag: str) -> bool:
        """Check if feedback indicates Strong Hire with no red flags"""
        combined = f"{feedback}\n\n{red_flag}"
        prompt = BQFeedback.is_perfect(combined)
        result = await self.analyzer.customized_analyze(prompt, stream=True)
        is_perfect = await StreamProcessor.get_text(result)
        return is_perfect.strip() == "True"

    async def improve_with_user_input(
        self,
        original_answer: str,
        feedback: str,
        probing_qa: list[dict]
    ) -> str:
        """Generate improved answer using user's real answers to probing questions"""
        prompt = BQAnswer.improve_with_probing_answers(
            original_answer, feedback, probing_qa
        )
        result = await self.analyzer.customized_analyze(prompt, stream=True)
        return await StreamProcessor.get_text(result)

    async def run_interactive(self) -> dict:
        """
        Run interactive improvement loop.
        Returns dict with final answer, iterations, and history.
        """
        current_answer = await self.answer()
        question = await self.question()

        answer_history = [current_answer]
        feedback_history = []

        for i in range(self.max_iterations):
            self.iterate_times = i + 1
            print(f"\n{'='*60}")
            print(f"Iteration {self.iterate_times}")
            print(f"{'='*60}")

            # Evaluate current answer
            print("\nEvaluating answer...")
            feedback = await self.evaluate(current_answer)
            red_flag = await self.evaluate_red_flag(current_answer)
            feedback_history.append({"feedback": feedback, "red_flag": red_flag})

            # Check if we've reached Strong Hire
            if await self.is_strong_hire(feedback, red_flag):
                print("\n✅ Strong Hire achieved!")
                return {
                    "status": "strong_hire",
                    "final_answer": current_answer,
                    "iterations": self.iterate_times,
                    "answer_history": answer_history,
                    "feedback_history": feedback_history,
                }

            # Extract probing questions from feedback
            probing_qs = FeedbackParser.extract_probing_questions(feedback)

            if not probing_qs:
                print("\nNo probing questions found in feedback.")
                continue

            # Ask user to answer probing questions
            print("\n" + "-"*40)
            print("Please answer these probing questions to improve your answer:")
            print("-"*40)

            probing_qa = []
            for j, q in enumerate(probing_qs, 1):
                print(f"\nQ{j}: {q}")
                user_input = input("> ")
                if user_input.strip():
                    probing_qa.append({"q": q, "a": user_input})

            if not probing_qa:
                print("\nNo answers provided. Skipping improvement.")
                continue

            # Generate improved answer with user's real details
            print("\nGenerating improved answer with your details...")
            current_answer = await self.improve_with_user_input(
                current_answer, feedback, probing_qa
            )
            answer_history.append(current_answer)

            print(f"\n{'='*40}")
            print("Improved Answer:")
            print(f"{'='*40}")
            print(current_answer)

            # Save feedback for reference
            feedback_recorder = FeedbackRecorder()
            feedback_recorder.save_feedback(
                question=question,
                answer=current_answer,
                feedback=feedback,
                red_flag=red_flag
            )

        return {
            "status": "max_iterations",
            "final_answer": current_answer,
            "iterations": self.iterate_times,
            "answer_history": answer_history,
            "feedback_history": feedback_history,
        }

    async def run_with_predefined_answers(
        self,
        probing_answers: list[list[str]]
    ) -> dict:
        """
        Run improvement loop with predefined answers (for testing).

        Args:
            probing_answers: List of answer lists, one per iteration.
                            Each inner list contains answers to probing questions.
        """
        current_answer = await self.answer()
        question = await self.question()

        answer_history = [current_answer]
        feedback_history = []

        for i, answers in enumerate(probing_answers):
            self.iterate_times = i + 1
            print(f"\n{'='*60}")
            print(f"Iteration {self.iterate_times}")
            print(f"{'='*60}")

            # For iteration 1, use feedback from file; for later iterations, evaluate
            if i == 0:
                # Use existing feedback from file
                feedback = self.feedback_full_content
                rating = FeedbackParser.extract_rating(feedback)
                print(f"\nUsing feedback from file. Rating: {rating}")
            else:
                # Evaluate the improved answer
                print("\nEvaluating improved answer...")
                feedback = await self.evaluate(current_answer)
                red_flag = await self.evaluate_red_flag(current_answer)
                feedback_history.append({"feedback": feedback, "red_flag": red_flag})

                rating = FeedbackParser.extract_rating(feedback)
                print(f"\nCurrent Rating: {rating}")

                # Check if we've reached Strong Hire
                if await self.is_strong_hire(feedback, red_flag):
                    print("\n✅ Strong Hire achieved!")
                    return {
                        "status": "strong_hire",
                        "final_answer": current_answer,
                        "iterations": self.iterate_times,
                        "answer_history": answer_history,
                        "feedback_history": feedback_history,
                    }

            # Extract probing questions from feedback
            probing_qs = FeedbackParser.extract_probing_questions(feedback)

            # Build Q&A pairs
            probing_qa = []
            for j, (q, a) in enumerate(zip(probing_qs, answers)):
                print(f"\nQ{j+1}: {q}")
                print(f"A{j+1}: {a}")
                probing_qa.append({"q": q, "a": a})

            # Generate improved answer
            print("\nGenerating improved answer...")
            current_answer = await self.improve_with_user_input(
                current_answer, feedback, probing_qa
            )
            answer_history.append(current_answer)

            print(f"\n{'='*40}")
            print("Improved Answer:")
            print(f"{'='*40}")
            print(current_answer)

            # Save feedback
            feedback_recorder = FeedbackRecorder()
            feedback_recorder.save_feedback(
                question=question,
                answer=current_answer,
                feedback=feedback,
                red_flag=FeedbackParser.extract_rating(feedback)  # Just save rating for iteration 1
            )

        # Final evaluation
        print(f"\n{'='*60}")
        print("Final Evaluation")
        print(f"{'='*60}")
        feedback = await self.evaluate(current_answer)
        red_flag = await self.evaluate_red_flag(current_answer)
        feedback_history.append({"feedback": feedback, "red_flag": red_flag})

        status = "strong_hire" if await self.is_strong_hire(feedback, red_flag) else "completed"

        return {
            "status": status,
            "final_answer": current_answer,
            "iterations": self.iterate_times,
            "answer_history": answer_history,
            "feedback_history": feedback_history,
        }
