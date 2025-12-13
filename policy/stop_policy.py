"""
Stop/Continue Policy for Probing Agent.

This module implements a learned stopping policy trained via supervised learning
on synthetic interview sessions with GPT-4o teacher labels.

Training approach:
1. Generate synthetic sessions with bootstrap_training.py --synthetic N
2. Label optimal stop points with GPT-4o via --relabel
3. Train logistic regression on state features via --train

The policy learns: π_stop(state) → {STOP, CONTINUE}

State features (10 total):
- gaps_remaining: count of unresolved gaps
- gaps_resolved: count of resolved gaps
- turn_count: number of probes asked
- good_responses: count of ANSWER_GOOD
- vague_responses: count of ANSWER_VAGUE
- idk_count: count of SAYS_IDK
- pushback_count: count of PUSHBACK
- friction_ratio: friction_signals / total_responses
- is_senior: 1 if Senior level
- is_staff: 1 if Staff level

Model performance (30 sessions, 125 samples):
- Learned policy: 88% accuracy, 92% stop recall
- Heuristic baseline: 60% accuracy, 17% stop recall
- LLM zero-shot: 56% accuracy, 8% stop recall
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from enum import Enum
import json
import os


class StopDecision(Enum):
    STOP = "STOP"
    CONTINUE = "CONTINUE"


@dataclass
class StateFeatures:
    """
    State representation for the stop/continue policy.
    These are the features the policy will learn from.
    """
    # Gap tracking
    gaps_total: int = 0
    gaps_resolved: int = 0
    gaps_unresolvable: int = 0
    gaps_remaining: int = 0

    # Turn tracking
    turn_count: int = 0
    max_turns: int = 8

    # Response history (last 3)
    recent_response_types: List[str] = field(default_factory=list)

    # Quality signals
    good_responses: int = 0  # ANSWER_GOOD count
    vague_responses: int = 0  # ANSWER_VAGUE count
    partial_responses: int = 0  # ANSWER_PARTIAL count

    # Friction signals (negative indicators)
    idk_count: int = 0  # SAYS_IDK
    pushback_count: int = 0  # PUSHBACK
    off_topic_count: int = 0  # OFF_TOPIC
    question_count: int = 0  # ASKS_QUESTION

    # Derived features
    response_quality_trend: str = "stable"  # improving/stable/declining
    friction_ratio: float = 0.0  # friction_signals / total_responses

    # Context
    level: str = "Senior"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_session(cls, session_data: dict) -> "StateFeatures":
        """Build state features from session data."""
        decisions = session_data.get("decisions", [])
        level = session_data.get("level", "Senior")
        max_turns = session_data.get("max_turns", 8)

        # Count response types
        response_types = []
        good = vague = partial = 0
        idk = pushback = off_topic = questions = 0

        for d in decisions:
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

        # Count gaps
        state_update = decisions[-1].get("state_update", {}) if decisions else {}
        gaps_resolved = len(state_update.get("gaps_resolved", []))
        gaps_unresolvable = len(state_update.get("gaps_unresolvable", []))
        gaps_remaining = len(state_update.get("gaps_remaining", []))
        gaps_total = gaps_resolved + gaps_unresolvable + gaps_remaining

        # Calculate friction
        total_responses = len(decisions)
        friction_signals = idk + pushback + off_topic
        friction_ratio = friction_signals / max(total_responses, 1)

        # Determine trend (simple: compare first half vs second half)
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

        return cls(
            gaps_total=gaps_total,
            gaps_resolved=gaps_resolved,
            gaps_unresolvable=gaps_unresolvable,
            gaps_remaining=gaps_remaining,
            turn_count=len(decisions),
            max_turns=max_turns,
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
            level=level
        )


@dataclass
class SessionLog:
    """
    Complete session log for training the stop policy.
    """
    session_id: str
    question: str
    original_answer: str
    level: str

    # Initial state
    initial_gaps: List[str] = field(default_factory=list)
    initial_weak_competencies: List[str] = field(default_factory=list)

    # Trajectory: list of (state, action, response_type)
    trajectory: List[Dict[str, Any]] = field(default_factory=list)

    # Outcomes (filled after session)
    final_qa_pairs: List[tuple] = field(default_factory=list)
    initial_rating: Optional[str] = None
    final_rating: Optional[str] = None
    rating_improved: Optional[bool] = None

    # Retro labels (filled by teacher)
    optimal_stop_turn: Optional[int] = None
    teacher_feedback: Optional[str] = None

    def add_step(
        self,
        state: StateFeatures,
        action: str,
        response_type: str,
        classification: dict
    ):
        """Add a step to the trajectory."""
        self.trajectory.append({
            "turn": len(self.trajectory) + 1,
            "state": state.to_dict(),
            "action": action,
            "response_type": response_type,
            "classification": classification
        })

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


class StopPolicyTeacher:
    """
    LLM-based teacher that retro-labels sessions with optimal stopping points.
    """

    @staticmethod
    def retro_label_prompt(session: SessionLog) -> str:
        """Generate prompt for teacher to label optimal stopping point."""
        trajectory_text = ""
        for step in session.trajectory:
            turn = step["turn"]
            rt = step["response_type"]
            action = step["action"]
            trajectory_text += f"Turn {turn}: Response={rt}, Action={action}\n"

        qa_text = ""
        for i, (q, a) in enumerate(session.final_qa_pairs, 1):
            qa_text += f"Q{i}: {q}\nA{i}: {a[:200]}...\n\n"

        return f"""You are evaluating a probing session to determine the OPTIMAL stopping point.

=== CONTEXT ===
Level: {session.level}
Original Question: {session.question}
Initial Gaps: {session.initial_gaps}
Initial Rating: {session.initial_rating or "Unknown"}
Final Rating: {session.final_rating or "Unknown"}

=== TRAJECTORY ===
{trajectory_text}

=== Q&A TRANSCRIPT ===
{qa_text}

=== YOUR TASK ===
Analyze this session and determine:
1. What was the OPTIMAL turn to stop? (could be earlier or later than actual)
2. Why? Consider:
   - Was useful information still being gathered?
   - Were there signs of diminishing returns?
   - Was there unnecessary friction?
   - Were critical gaps addressed?

OUTPUT (JSON only):
{{
  "optimal_stop_turn": <turn number>,
  "reasoning": "<why this is the optimal stopping point>",
  "actual_stop_assessment": "<too_early | just_right | too_late>",
  "missed_opportunities": ["<gaps that could have been probed>"],
  "unnecessary_probes": ["<probes that didn't add value>"]
}}"""


class ZeroShotStopPolicy:
    """
    Current zero-shot stopping logic (baseline).
    Will be replaced/augmented by learned policy.
    """

    @staticmethod
    def should_stop(state: StateFeatures) -> tuple[StopDecision, str]:
        """
        Zero-shot heuristic for stopping.
        Returns (decision, reasoning).
        """
        # Hard stops
        if state.turn_count >= state.max_turns:
            return StopDecision.STOP, "Maximum turns reached"

        if state.gaps_remaining == 0:
            return StopDecision.STOP, "All gaps addressed"

        # Friction-based stop
        if state.friction_ratio > 0.5:
            return StopDecision.STOP, "High user friction detected"

        if state.idk_count >= 2:
            return StopDecision.STOP, "User unable to provide more info"

        # Diminishing returns
        if len(state.recent_response_types) >= 3:
            recent = state.recent_response_types[-3:]
            if all(r in ["ANSWER_VAGUE", "SAYS_IDK"] for r in recent):
                return StopDecision.STOP, "Diminishing returns - last 3 responses weak"

        # Quality threshold
        if state.good_responses >= 3 and state.gaps_resolved >= 2:
            return StopDecision.STOP, "Sufficient quality responses gathered"

        # Default: continue
        return StopDecision.CONTINUE, "Critical gaps remain"


class LearnedStopPolicy:
    """
    Learned stop policy using logistic regression on state features.
    Trained on SessionLog data with teacher labels.
    """

    # Default model path relative to this file
    DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "stop_policy_model.pkl")

    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.model_loaded = False

        # Try to load model from default path if not specified
        path = model_path or self.DEFAULT_MODEL_PATH
        if os.path.exists(path):
            self.load(path)

    def _extract_features(self, state: StateFeatures) -> list:
        """Extract feature vector from state."""
        return [
            state.gaps_remaining,
            state.gaps_resolved,
            state.turn_count,
            state.good_responses,
            state.vague_responses,
            state.idk_count,
            state.pushback_count,
            state.friction_ratio,
            1 if state.level == "Senior" else 0,
            1 if state.level == "Staff" else 0,
        ]

    def predict(self, state: StateFeatures) -> tuple[StopDecision, float]:
        """
        Predict stop/continue with confidence.
        Returns (decision, confidence).
        """
        if not self.model_loaded or self.model is None:
            # Fall back to zero-shot if no model
            decision, _ = ZeroShotStopPolicy.should_stop(state)
            return decision, 0.5  # Low confidence = use zero-shot

        features = [self._extract_features(state)]

        # Get prediction and probability
        pred = self.model.predict(features)[0]
        proba = self.model.predict_proba(features)[0]
        confidence = max(proba)  # Confidence is max probability

        decision = StopDecision.STOP if pred == 1 else StopDecision.CONTINUE
        return decision, confidence

    def save(self, path: str):
        """Save model to file."""
        import pickle
        with open(path, "wb") as f:
            pickle.dump(self.model, f)

    def load(self, path: str):
        """Load model from file."""
        import pickle
        try:
            with open(path, "rb") as f:
                self.model = pickle.load(f)
            self.model_loaded = True
        except Exception as e:
            print(f"Warning: Could not load stop policy model from {path}: {e}")
            self.model_loaded = False


class HybridStopPolicy:
    """
    Combines zero-shot and learned policy.
    Uses learned policy when confident, falls back to zero-shot otherwise.
    """

    def __init__(self, learned_policy: Optional[LearnedStopPolicy] = None):
        self.learned = learned_policy or LearnedStopPolicy()
        self.zero_shot = ZeroShotStopPolicy()
        self.confidence_threshold = 0.7

    def should_stop(self, state: StateFeatures) -> tuple[StopDecision, str, str]:
        """
        Returns (decision, reasoning, policy_used).
        """
        # Try learned policy first
        learned_decision, confidence = self.learned.predict(state)

        if confidence >= self.confidence_threshold:
            return (
                learned_decision,
                f"Learned policy (confidence: {confidence:.2f})",
                "learned"
            )

        # Fall back to zero-shot
        zs_decision, zs_reasoning = self.zero_shot.should_stop(state)
        return zs_decision, zs_reasoning, "zero_shot"
