"""
Auto-completion feature for self-introduction and BQ answers
Provides intelligent completion suggestions based on FAANG interview standards
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Literal, Dict, Any, Optional

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from interview_analyzer import InterviewAnalyzer
from prompts import AutoCompletion
from utils import StreamProcessor


class AutoCompletionEngine:
    """
    Auto-completion engine for interview answers.
    Supports two scenarios: "self-intro" and "bq answer"
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize the auto-completion engine.

        Args:
            model: LLM model to use for completion
        """
        self.analyzer = InterviewAnalyzer(model=model)

    async def complete(
        self,
        scenario: Literal["self-intro", "bq answer"],
        partial_text: str,
        role: str = "Software Engineer",
        company: str = "FAANG",
        question: Optional[str] = None,
        level: str = "Senior"
    ) -> Dict[str, Any]:
        """
        Generate completion suggestions for partial text.

        Args:
            scenario: Either "self-intro" or "bq answer"
            partial_text: The partial text input from user
            role: Job role (for context)
            company: Company name (for self-intro)
            question: BQ question (required for "bq answer" scenario)
            level: Candidate level (for BQ answers, default: "Senior")

        Returns:
            Parsed JSON object returned by the LLM.
            We do not enforce any specific schema here – whatever JSON the
            prompt defines, we just extract and return as-is.
        """
        if scenario == "self-intro":
            prompt = AutoCompletion.self_intro_completion(
                partial_text=partial_text,
                role=role,
                company=company
            )
        elif scenario == "bq answer":
            if not question:
                raise ValueError("question parameter is required for 'bq answer' scenario")
            prompt = AutoCompletion.bq_answer_completion(
                partial_text=partial_text,
                question=question,
                role=role,
                level=level
            )
        else:
            raise ValueError(f"Unknown scenario: {scenario}. Must be 'self-intro' or 'bq answer'")

        # Call LLM
        result = await self.analyzer.customized_analyze(prompt, stream=True)
        response_text = await StreamProcessor.get_text(result)

        # Parse JSON response (best-effort: extract the first JSON object the model outputs)
        try:
            response_text = response_text.strip()

            # Use regex to find the first {...} block, allowing newlines inside
            match = re.search(r"\{[\s\S]*\}", response_text)
            if match:
                json_str = match.group(0)
            else:
                # Fall back to treating the whole response as JSON
                json_str = response_text

            return json.loads(json_str)

        except json.JSONDecodeError as e:
            # If JSON parsing fails, return error info for debugging
            return {
                "is_complete": False,
                "error": f"Failed to parse LLM response as JSON: {str(e)}",
                "raw_response": response_text,
            }
        except Exception as e:
            return {
                "is_complete": False,
                "error": f"Error processing response: {str(e)}",
                "raw_response": response_text,
            }

    async def complete_self_intro(
        self,
        partial_text: str,
        role: str = "Software Engineer",
        company: str = "FAANG"
    ) -> Dict[str, Any]:
        """
        Convenience method for self-introduction completion.

        Args:
            partial_text: Partial self-introduction text
            role: Job role
            company: Company name

        Returns:
            Completion result dict (parsed JSON from LLM)
        """
        return await self.complete(
            scenario="self-intro",
            partial_text=partial_text,
            role=role,
            company=company
        )

    async def complete_bq_answer(
        self,
        partial_text: str,
        question: str,
        role: str = "Software Engineer",
        level: str = "Senior"
    ) -> Dict[str, Any]:
        """
        Convenience method for BQ answer completion.

        Args:
            partial_text: Partial BQ answer text
            question: The behavioral question
            role: Job role
            level: Candidate level

        Returns:
            Completion result dict (parsed JSON from LLM)
        """
        return await self.complete(
            scenario="bq answer",
            partial_text=partial_text,
            question=question,
            role=role,
            level=level
        )

    async def check_fluency(
        self,
        partial_text: str,
        completion: str
    ) -> Dict[str, Any]:
        """
        Check if the completion is fluent and natural-sounding

        Args:
            partial_text: Partial text input from user
            completion: Completion text to check

        Returns:
            Dict containing fluency information
            - is_fluent: True/False
            - reason: Reason for the fluency
            - confidence: Confidence in the fluency
        """
        prompt = AutoCompletion.check_fluency(
            partial_text=partial_text,
            completion=completion
        )
        result = await self.analyzer.customized_analyze(prompt, stream=True)
        response_text = await StreamProcessor.get_text(result)
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            return {
                "is_fluent": False,
                "reason": f"Failed to parse LLM response as JSON: {str(e)}",
                "confidence": 0
            }
        except Exception as e:
            return {
                "is_fluent": False,
                "reason": f"Error processing response: {str(e)}",
                "confidence": 0
            }

