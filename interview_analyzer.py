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
)
from policy.stop_policy import (
    StateFeatures,
    SessionLog,
    HybridStopPolicy,
    StopDecision,
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


class AgenticInterviewer:
    """
    Agentic probing interviewer - LLM decides ASK or STOP at each step.

    Key features:
    - Uses EvaluationParser to extract gaps from real_interview() output (no extra LLM call)
    - ONE LLM call per turn: evaluate response + decide + generate next probe
    - Stops when all critical gaps addressed or diminishing returns

    Flow:
    1. initialize(evaluation) → Parse gaps, get first probe (1 LLM call)
    2. step(user_response) → Evaluate + decide + next probe (1 LLM call per turn)
    3. Repeat until STOP
    """

    def __init__(self, model: str = "gpt-4o-mini", max_turns: int = 8):
        self.model = model
        self.max_turns = max_turns

        # State
        self.question = ""
        self.original_answer = ""
        self.level = "Senior"
        self.turn_count = 0

        # Parsed evaluation data (from EvaluationParser)
        self.parsed_eval = None
        self.probing_questions: List[str] = []  # Pre-generated from evaluation
        self.weak_competencies: List[str] = []

        # Conversation state
        self.qa_pairs: List[tuple] = []  # (probe, response)
        self.current_probe = ""  # Current question being asked
        self.decisions: List[Dict] = []

        # Final state
        self.stopped = False
        self.stop_reason = ""

        # Stop policy (learnable)
        self.stop_policy = HybridStopPolicy()
        self.session_log: SessionLog = None  # For training data collection

    def initialize(
        self,
        question: str,
        answer: str,
        evaluation: str,
        level: str = "Senior",
        session_id: str = None
    ) -> Dict:
        """
        Initialize with parsed evaluation. NO LLM call needed.

        Args:
            question: The BQ question
            answer: Candidate's answer
            evaluation: Markdown output from real_interview()
            level: Interview level
            session_id: Optional session ID for logging (auto-generated if None)

        Returns:
            Dict with gaps, probing_questions, and first probe
        """
        from utils import EvaluationParser
        import uuid

        self.question = question
        self.original_answer = answer
        self.level = level
        self.turn_count = 0
        self.qa_pairs = []
        self.decisions = []
        self.stopped = False

        # Parse evaluation - NO LLM CALL
        self.parsed_eval = EvaluationParser.parse(evaluation)
        self.probing_questions = self.parsed_eval.probing_questions.copy()
        self.weak_competencies = self.parsed_eval.weak_competencies.copy()

        # Initialize session log for training data collection
        self.session_log = SessionLog(
            session_id=session_id or str(uuid.uuid4())[:8],
            question=question,
            original_answer=answer,
            level=level,
            initial_gaps=self.parsed_eval.areas_for_improvement.copy(),
            initial_weak_competencies=self.weak_competencies.copy(),
            initial_rating=self.parsed_eval.recommendation
        )

        # Get first probe from pre-generated questions
        if self.probing_questions:
            self.current_probe = self.probing_questions.pop(0)
        else:
            self.stopped = True
            self.stop_reason = "No probing questions needed"
            self.current_probe = ""

        return {
            "weak_competencies": self.weak_competencies,
            "areas_for_improvement": self.parsed_eval.areas_for_improvement,
            "probing_questions": self.parsed_eval.probing_questions,
            "first_probe": self.current_probe,
            "action": "STOP" if self.stopped else "ASK"
        }

    async def step(self, user_response: str) -> Dict:
        """
        Process user response and decide next action. ONE LLM call.

        Flow:
        1. Classify response type (ANSWER_GOOD, ASKS_QUESTION, etc.)
        2. Apply policy based on type
        3. Consult stop policy for STOP/CONTINUE decision
        4. Generate appropriate output (probe, answer, redirect, etc.)

        Args:
            user_response: User's response to current probe

        Returns:
            Dict with response_type, action, agent_message, state_update
        """
        from prompts import ProbingAgent

        # Record Q&A
        self.qa_pairs.append((self.current_probe, user_response))
        self.turn_count += 1

        # Build state features for stop policy
        state = self._build_state_features()

        # Check stop policy (combines learned + zero-shot)
        stop_decision, stop_reasoning, policy_used = self.stop_policy.should_stop(state)

        if stop_decision == StopDecision.STOP:
            self.stopped = True
            self.stop_reason = stop_reasoning
            decision = {
                "response_type": "N/A",
                "action": "STOP",
                "agent_message": "Thank you for your responses. I have enough information now.",
                "reasoning": f"{stop_reasoning} (policy: {policy_used})",
                "policy_used": policy_used
            }
            self._log_step(state, decision)
            return decision

        # Single LLM call: classify → policy → generate
        prompt = ProbingAgent.step_prompt(
            question=self.question,
            original_answer=self.original_answer,
            evaluation_summary={
                "weak_competencies": self.weak_competencies,
                "areas_for_improvement": self.parsed_eval.areas_for_improvement,
            },
            conversation_history=self.qa_pairs,
            remaining_probes=self.probing_questions,
            turn_count=self.turn_count,
            max_turns=self.max_turns,
            level=self.level
        )

        response = await acompletion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        decision = ProbingAgent.parse_decision(response.choices[0].message.content)
        self.decisions.append(decision)

        # Build state AFTER decision is added so features reflect current turn
        state = self._build_state_features()

        # Log step for training data
        self._log_step(state, decision)

        # Handle different actions
        action = decision.get("action", "STOP")

        if action == "STOP":
            self.stopped = True
            self.stop_reason = decision.get("reasoning", "Sufficient information gathered")
            self.current_probe = ""

        elif action in ["PROBE_NEXT", "PROBE_SAME", "REDIRECT"]:
            # Agent is asking a question - update current probe
            self.current_probe = decision.get("agent_message", "")
            if not self.current_probe and self.probing_questions:
                self.current_probe = self.probing_questions.pop(0)

        elif action == "ANSWER_USER":
            # Agent is answering user's question
            # Current probe stays the same (will re-ask after answering)
            # agent_message contains the answer
            pass

        # Update state based on state_update
        state_update = decision.get("state_update", {})
        if state_update.get("gaps_resolved"):
            for gap in state_update["gaps_resolved"]:
                if gap in self.weak_competencies:
                    self.weak_competencies.remove(gap)

        return decision

    def _build_state_features(self) -> StateFeatures:
        """Build state features from current session state for stop policy."""
        # Count response types from decisions
        good = vague = partial = 0
        idk = pushback = off_topic = questions = 0
        response_types = []

        for d in self.decisions:
            classification = d.get("classification", {})
            rt = classification.get("response_type", d.get("response_type", ""))
            response_types.append(rt)

            if rt == "ANSWER_GOOD":
                good += 1
            elif rt == "ANSWER_VAGUE":
                vague += 1
            elif rt == "ANSWER_PARTIAL":
                partial += 1
            elif rt == "SAYS_IDK":
                idk += 1
            elif rt == "PUSHBACK":
                pushback += 1
            elif rt == "OFF_TOPIC":
                off_topic += 1
            elif rt == "ASKS_QUESTION":
                questions += 1

        # Count gaps from state updates
        gaps_resolved = 0
        gaps_unresolvable = 0
        for d in self.decisions:
            state_update = d.get("state_update", {})
            gaps_resolved += len(state_update.get("gaps_resolved", []))
            gaps_unresolvable += len(state_update.get("gaps_unresolvable", []))

        gaps_total = len(self.session_log.initial_gaps) if self.session_log else 0
        gaps_remaining = max(0, gaps_total - gaps_resolved - gaps_unresolvable)

        # Calculate friction
        total_responses = len(self.decisions)
        friction_signals = idk + pushback + off_topic
        friction_ratio = friction_signals / max(total_responses, 1)

        # Determine trend
        if len(response_types) >= 4:
            first_half = response_types[:len(response_types)//2]
            second_half = response_types[len(response_types)//2:]
            first_good = sum(1 for r in first_half if r == "ANSWER_GOOD")
            second_good = sum(1 for r in second_half if r == "ANSWER_GOOD")
            if second_good > first_good:
                trend = "improving"
            elif second_good < first_good:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return StateFeatures(
            gaps_total=gaps_total,
            gaps_resolved=gaps_resolved,
            gaps_unresolvable=gaps_unresolvable,
            gaps_remaining=gaps_remaining,
            turn_count=self.turn_count,
            max_turns=self.max_turns,
            recent_response_types=response_types[-3:],
            good_responses=good,
            vague_responses=vague,
            partial_responses=partial,
            idk_count=idk,
            pushback_count=pushback,
            off_topic_count=off_topic,
            question_count=questions,
            response_quality_trend=trend,
            friction_ratio=friction_ratio,
            level=self.level
        )

    def _log_step(self, state: StateFeatures, decision: Dict):
        """Log a step to the session log for training data collection."""
        if self.session_log is None:
            return

        classification = decision.get("classification", {})
        response_type = classification.get("response_type", decision.get("response_type", ""))

        self.session_log.add_step(
            state=state,
            action=decision.get("action", ""),
            response_type=response_type,
            classification=classification
        )

    def get_current_probe(self) -> str:
        """Get the current probe question to ask user."""
        return self.current_probe

    def should_continue(self) -> bool:
        """Check if probing should continue."""
        if self.stopped:
            return False
        if self.turn_count >= self.max_turns:
            self.stop_reason = "Maximum turns reached"
            return False
        return True

    def get_qa_pairs(self) -> List[tuple]:
        """Get all probe/response pairs."""
        return self.qa_pairs

    def get_decision_log(self) -> List[Dict]:
        """Get log of all decisions for analysis."""
        return self.decisions

    def get_summary(self) -> Dict:
        """Get summary of the probing session."""
        return {
            "question": self.question,
            "level": self.level,
            "turns": self.turn_count,
            "max_turns": self.max_turns,
            "stopped": self.stopped,
            "stop_reason": self.stop_reason,
            "qa_pairs": self.qa_pairs,
        }

    def finalize_session(self, final_rating: str = None) -> SessionLog:
        """
        Finalize the session log with outcomes.

        Call this after the session ends and you have the final rating
        (e.g., after re-evaluating with probing Q&A included).

        Args:
            final_rating: The rating after probing (e.g., "Hire", "No Hire")

        Returns:
            The completed SessionLog for training
        """
        if self.session_log is None:
            return None

        # Set final Q&A pairs
        self.session_log.final_qa_pairs = self.qa_pairs.copy()
        self.session_log.final_rating = final_rating

        # Determine if rating improved
        if self.session_log.initial_rating and final_rating:
            # Simple comparison - could be made more sophisticated
            rating_order = ["No Hire", "Leaning No Hire", "Leaning Hire", "Hire", "Strong Hire"]
            try:
                initial_idx = next(
                    i for i, r in enumerate(rating_order)
                    if r.lower() in self.session_log.initial_rating.lower()
                )
                final_idx = next(
                    i for i, r in enumerate(rating_order)
                    if r.lower() in final_rating.lower()
                )
                self.session_log.rating_improved = final_idx > initial_idx
            except StopIteration:
                self.session_log.rating_improved = None

        return self.session_log

    def save_session_log(self, path: str = None) -> str:
        """
        Save the session log to a JSON file for training data.

        Args:
            path: Optional file path. If None, auto-generates based on session_id.

        Returns:
            The file path where the log was saved.
        """
        if self.session_log is None:
            return None

        import os
        if path is None:
            os.makedirs("session_logs", exist_ok=True)
            path = f"session_logs/{self.session_log.session_id}.json"

        self.session_log.save(path)
        return path