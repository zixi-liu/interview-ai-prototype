"""
BQ Interview Analyzer using LiteLLM
Analyzes behavioral questions and self-introductions for FAANG interviews
"""

import base64
from typing import AsyncIterator, List, Dict, Any
from dotenv import load_dotenv
from litellm import acompletion
from prompts import (
    SystemMessage,
    IntroductionPrompt,
    BQQuestions,
    ConversationalInterview,
)

load_dotenv()

# Audio-related constants
AUDIO_MODEL = "gpt-4o-audio-preview"
AUDIO_MODEL_MINI = "gpt-4o-mini-audio-preview"
AUDIO_TARGET_FORMAT = "wav"
AUDIO_PLACEHOLDER = "[Audio input - analyzing spoken content]"
TRANSCRIPTION_PROMPT = "Please transcribe the following audio exactly as spoken:"


class InterviewAnalyzer:
    """BQ Interview Analyzer for FAANG standards"""

    def __init__(self, model: str = "gpt-4o-mini", audio_model: str = AUDIO_MODEL_MINI):
        self.model = model
        self.audio_model = audio_model

    @staticmethod
    def _build_audio_messages(
        system_content: str, 
        text_prompt: str, 
        audio_b64: str, 
        audio_format: str
    ) -> List[Dict[str, Any]]:
        """Build messages with audio input for LLM API."""
        return [
            {"role": "system", "content": system_content},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text_prompt},
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": audio_b64,
                            "format": audio_format
                        }
                    }
                ]
            }
        ]

    @staticmethod
    async def _extract_stream_chunks(response_stream: AsyncIterator) -> AsyncIterator[str]:
        """Extract content chunks from streaming response."""
        async for chunk in response_stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    yield delta.content

    async def analyze_introduction(
        self, 
        introduction: str, 
        role: str, 
        company: str, 
        stream: bool = False
    ):
        """
        Analyze self-introduction (1-2 minutes) and provide FAANG-standard feedback.

        Args:
            introduction: Self-introduction text (1-2 minutes worth)
            role: Job role being interviewed for
            company: Target company name
            stream: Whether to stream the response

        Returns:
            If stream=False: Complete feedback string
            If stream=True: Async iterator yielding text chunks
        """
        prompt = IntroductionPrompt.analyze(introduction, role, company)
        messages = [
            {"role": "system", "content": SystemMessage.INTRODUCTION},
            {"role": "user", "content": prompt}
        ]
        
        response = await acompletion(
            model=self.model,
            messages=messages,
            temperature=0.3,
            stream=stream
        )

        if stream:
            return self._extract_stream_chunks(response)
        else:
            return response.choices[0].message.content

    async def transcribe_audio(
        self, 
        audio_content: bytes, 
        audio_format: str = AUDIO_TARGET_FORMAT
    ) -> str:
        """
        Transcribe audio using GPT-4o audio model asynchronously via LiteLLM.
        
        Args:
            audio_content: Audio bytes in WAV format
            audio_format: Audio format (should be "wav")
            
        Returns:
            Transcribed text
        """
        audio_b64 = base64.b64encode(audio_content).decode()
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": TRANSCRIPTION_PROMPT},
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": audio_b64,
                            "format": audio_format
                        }
                    }
                ]
            }
        ]
        
        response = await acompletion(
            model=AUDIO_MODEL,  # Use full audio model for reliable transcription
            messages=messages,
            modalities=["text"]
        )

        return response.choices[0].message.content

    async def analyze_audio(
        self, 
        audio_content: bytes, 
        audio_format: str, 
        role: str, 
        company: str, 
        stream: bool = False
    ):
        """
        Analyze audio directly using gpt-4o-audio-preview which supports text+audio mixed input.
        
        Args:
            audio_content: Audio bytes in WAV format
            audio_format: Audio format (should be "wav")
            role: Job role
            company: Company name
            stream: Whether to stream the response
            
        Returns:
            If stream=False: Complete analysis feedback string
            If stream=True: Async iterator yielding text chunks
        """
        audio_b64 = base64.b64encode(audio_content).decode()
        text_prompt = IntroductionPrompt.analyze(
            introduction=AUDIO_PLACEHOLDER,
            role=role,
            company=company
        )
        messages = self._build_audio_messages(
            SystemMessage.INTRODUCTION,
            text_prompt,
            audio_b64,
            audio_format
        )
        
        # Use full audio model for streaming, mini for non-streaming
        model = AUDIO_MODEL if stream else self.audio_model
        
        response = await acompletion(
            model=model,
            messages=messages,
            temperature=0.3,
            stream=stream,
            modalities=["text"]
        )

        if stream:
            return self._extract_stream_chunks(response)
        else:
            return response.choices[0].message.content

    async def analyze_bq_question(
        self, 
        question: str, 
        answer: str, 
        role: str = "Software Engineer",
        stream: bool = False
    ):
        """
        Analyze a specific BQ question answer following FAANG standards.
        
        Args:
            question: The BQ question asked (e.g., "Tell me about your most challenging project")
            answer: The candidate's answer
            role: Job role being interviewed for
            stream: Whether to stream the response
            
        Returns:
            If stream=False: Complete feedback string
            If stream=True: Async iterator yielding text chunks
        """
        bq_questions = BQQuestions()
        prompt = bq_questions.get_prompt(question, answer, role)
        messages = [
            {"role": "system", "content": SystemMessage.BQ_QUESTION},
            {"role": "user", "content": prompt}
        ]

        response = await acompletion(
            model=self.model,
            messages=messages,
            temperature=0.3,
            stream=stream
        )

        if stream:
            return self._extract_stream_chunks(response)
        else:
            return response.choices[0].message.content

    async def customized_analyze(
        self,
        prompt: str,
        stream: bool = False
    ):
        """
        Customized analyze using a custom prompt

        Args:
            prompt: Custom prompt
            stream: Whether to stream the response

        Returns:
            If stream=False: Complete feedback string
            If stream=True: Async iterator yielding text chunks
        """
        messages = [
            {"role": "user", "content": prompt}
        ]

        response = await acompletion(
            model=self.model,
            messages=messages,
            temperature=0.3,
            stream=stream
        )

        if stream:
            return self._extract_stream_chunks(response)
        else:
            return response.choices[0].message.content


class ConversationalInterviewer:
    """
    Manages a conversational follow-up interview using plan-then-execute approach.

    Step 1: Plan - Select top 3 questions to probe (JSON output)
    Step 2: Execute - Probe each question one at a time (max 5 rounds each)

    Full conversation history is maintained across all questions so LLM can
    reference earlier answers (e.g., "You mentioned X earlier...").
    """

    SATISFIED_MARKER = "[SATISFIED]"

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.max_rounds = ConversationalInterview.MAX_ROUNDS_PER_QUESTION
        self.num_questions = ConversationalInterview.NUM_QUESTIONS

        # Planning state
        self.planned_questions: List[Dict[str, str]] = []

        # Execution state (per question)
        self.current_question_idx = 0
        self.current_round = 0
        self.current_satisfied = False
        self._current_probe = ""
        self._level = "Senior"  # Store level for system prompt updates

        # Conversation history (maintained across ALL questions)
        self.messages: List[Dict[str, str]] = []
        self._initialized = False

        # Overall state
        self.all_qa_pairs: List[tuple] = []  # All (probe_q, user_answer) pairs
        self.current_question_qa: List[tuple] = []  # Q&A for CURRENT question only (for signal checking)
        self.question_answers: List[Dict] = []  # Per-question summary

    async def plan_questions(
        self,
        feedback: str,
        probing_questions: list
    ) -> List[Dict[str, str]]:
        """
        Step 1: Plan which 3 questions to probe.

        Returns:
            List of dicts with 'question' and 'reason' keys
        """
        import json

        prompt = ConversationalInterview.planning_prompt(feedback, probing_questions)
        messages = [{"role": "user", "content": prompt}]

        response = await acompletion(
            model=self.model,
            messages=messages,
            temperature=0.2,  # Low temp for consistent JSON
            response_format={"type": "json_object"}
        )

        result = response.choices[0].message.content
        try:
            parsed = json.loads(result)
            self.planned_questions = parsed.get("questions", [])[:self.num_questions]
        except json.JSONDecodeError:
            # Fallback: use first 3 probing questions
            self.planned_questions = [
                {"id": i+1, "question": q, "reason": "Selected from list"}
                for i, q in enumerate(probing_questions[:self.num_questions])
            ]

        return self.planned_questions

    def start_question(
        self,
        original_question: str,
        original_answer: str,
        level: str = "Senior"
    ):
        """
        Start probing the current planned question.

        On first call: initializes conversation with system prompt and context.
        On subsequent calls: appends new question directive to existing history.
        """
        if self.current_question_idx >= len(self.planned_questions):
            return

        self._level = level  # Store level for system prompt updates
        planned = self.planned_questions[self.current_question_idx]
        probing_q = planned.get("question", "")

        if not self._initialized:
            # First question: set up system prompt and full context
            self.messages = [
                {
                    "role": "system",
                    "content": ConversationalInterview.probe_system_prompt(level)
                },
                {
                    "role": "user",
                    "content": ConversationalInterview.probe_context(
                        original_question,
                        original_answer,
                        probing_q,
                        self.current_question_idx + 1,
                        len(self.planned_questions)
                    )
                }
            ]
            self._initialized = True
        else:
            # Subsequent questions: append new question directive to history
            # LLM can see all previous Q&A exchanges
            self.messages.append({
                "role": "user",
                "content": f"=== MOVING TO PROBING QUESTION {self.current_question_idx + 1}/{len(self.planned_questions)} ===\n{probing_q}\n\nAsk this question now. You can reference the candidate's earlier answers if relevant."
            })

        self.current_round = 0
        self.current_satisfied = False
        self._current_probe = ""
        self.current_question_qa = []  # Reset for new question

    async def get_probe(self) -> str:
        """Get the next probe question/hint from the interviewer."""
        # Update system prompt with CURRENT question's Q&A only (for signal checking)
        # LLM still sees full conversation in self.messages
        current_qa_history = self._format_current_question_history()
        self.messages[0] = {
            "role": "system",
            "content": ConversationalInterview.probe_system_prompt(self._level, current_qa_history)
        }

        response = await acompletion(
            model=self.model,
            messages=self.messages,
            temperature=0.4,
            stream=False
        )

        full_response = response.choices[0].message.content
        self._process_response(full_response)
        return self._current_probe

    def _process_response(self, response: str):
        """Process the LLM response, check for satisfied marker."""
        self.messages.append({"role": "assistant", "content": response})

        if self.SATISFIED_MARKER in response:
            self.current_satisfied = True
            # Remove marker from display
            self._current_probe = response.replace(self.SATISFIED_MARKER, "").strip()
        else:
            self._current_probe = response.strip()

        self.current_round += 1

    def add_user_response(self, user_answer: str):
        """Add user's answer to the conversation."""
        if self._current_probe:
            self.all_qa_pairs.append((self._current_probe, user_answer))
            self.current_question_qa.append((self._current_probe, user_answer))
        self.messages.append({"role": "user", "content": user_answer})

    def _format_current_question_history(self) -> str:
        """Format current question's Q&A for signal checking."""
        if not self.current_question_qa:
            return ""
        lines = []
        for i, (q, a) in enumerate(self.current_question_qa, 1):
            lines.append(f"Q{i}: {q}")
            lines.append(f"A{i}: {a}")
        return "\n".join(lines)

    def should_continue_question(self) -> bool:
        """Check if we should continue probing the current question."""
        if self.current_satisfied:
            return False
        if self.current_round >= self.max_rounds:
            return False
        return True

    def finish_current_question(self):
        """Mark current question as done and prepare for next."""
        if self.current_question_idx < len(self.planned_questions):
            planned = self.planned_questions[self.current_question_idx]
            self.question_answers.append({
                "question": planned.get("question", ""),
                "rounds": self.current_round,
                "satisfied": self.current_satisfied
            })
        self.current_question_idx += 1

    def has_more_questions(self) -> bool:
        """Check if there are more planned questions to probe."""
        return self.current_question_idx < len(self.planned_questions)

    def get_current_question_info(self) -> Dict[str, Any]:
        """Get info about the current question being probed."""
        if self.current_question_idx < len(self.planned_questions):
            planned = self.planned_questions[self.current_question_idx]
            return {
                "num": self.current_question_idx + 1,
                "total": len(self.planned_questions),
                "question": planned.get("question", ""),
                "reason": planned.get("reason", ""),
                "round": self.current_round,
                "max_rounds": self.max_rounds
            }
        return {}

    def get_all_qa_pairs(self) -> List[tuple]:
        """Get all question-answer pairs from the session."""
        return self.all_qa_pairs

    def get_conversation_summary(self) -> str:
        """Get a formatted summary of the conversation."""
        if not self.all_qa_pairs:
            return ""

        summary = "=== FOLLOW-UP Q&A ===\n"
        for i, (q, a) in enumerate(self.all_qa_pairs, 1):
            summary += f"\nQ{i}: {q}\nA{i}: {a}\n"

        return summary