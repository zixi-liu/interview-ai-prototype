#!/usr/bin/env python3
"""
Bootstrap Training Data Generator for Stop Policy.

Phase 1: Generate synthetic sessions + parse YouTube transcripts
to bootstrap the learned stop policy.

Usage:
    python bootstrap_training.py --synthetic 100
    python bootstrap_training.py --youtube transcript.txt
    python bootstrap_training.py --train
"""

import asyncio
import json
import os
import random
import argparse
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
from litellm import acompletion

load_dotenv()

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from policy.stop_policy import (
    StateFeatures,
    SessionLog,
    RewardSignals,
    StopPolicyTeacher,
    LearnedStopPolicy,
)


# ============================================================
# SYNTHETIC DATA TEMPLATES
# ============================================================

def load_bq_questions_from_taxonomy() -> List[str]:
    """Load BQ questions from the taxonomy CSV."""
    import csv
    taxonomy_path = os.path.join(
        os.path.dirname(POLICY_DIR),
        "promptbase", "bq", "taxonomy.csv"
    )
    questions = []
    try:
        with open(taxonomy_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                q = row.get("typical_question", "").strip()
                if q:
                    questions.append(q)
    except FileNotFoundError:
        # Fallback to hardcoded if CSV not found
        questions = [
            "Tell me about a time you faced a challenging project.",
            "Tell me about a time you disagreed with your manager.",
        ]
    return questions

# Will be loaded when needed
BQ_QUESTIONS = None

def get_bq_questions() -> List[str]:
    """Get BQ questions, loading from taxonomy if needed."""
    global BQ_QUESTIONS
    if BQ_QUESTIONS is None:
        BQ_QUESTIONS = load_bq_questions_from_taxonomy()
        print(f"Loaded {len(BQ_QUESTIONS)} questions from taxonomy")
    return BQ_QUESTIONS

# Templates for each response type - LLM will expand these
RESPONSE_TEMPLATES = {
    "ANSWER_GOOD": [
        "Specific metrics: reduced latency by X%, saved $Y, improved Z by N%",
        "Clear ownership: 'I personally decided...', 'I led the effort to...'",
        "Concrete examples with names, dates, technologies",
        "STAR format: clear Situation, Task, Action, Result",
    ],
    "ANSWER_VAGUE": [
        "Generic statements: 'We improved things', 'It was successful'",
        "No metrics or specifics",
        "Passive voice: 'It was decided', 'The team worked on'",
        "Missing personal contribution",
    ],
    "ANSWER_PARTIAL": [
        "Answers only part of the question",
        "Good on situation/task, weak on action/result",
        "Mentions what happened but not their role",
        "Starts strong but trails off",
    ],
    "ASKS_QUESTION": [
        "Clarification: 'What do you mean by X?'",
        "Scope: 'Are you asking about technical or people challenges?'",
        "Context: 'Do you want a recent example or from earlier in my career?'",
    ],
    "SAYS_IDK": [
        "Explicit: 'I don't have a good example for that'",
        "Deflection: 'I can't think of one right now'",
        "Admission: 'I haven't faced that situation'",
    ],
    "OFF_TOPIC": [
        "Answers a different question entirely",
        "Goes on tangent about unrelated project",
        "Misunderstands the question",
    ],
    "PUSHBACK": [
        "Challenges premise: 'I don't think that's a fair question'",
        "Redirects: 'I'd rather talk about X instead'",
        "Defensive: 'Why are you asking that?'",
    ],
    "NEW_INFO": [
        "Reveals something not in original answer",
        "Adds important context that changes assessment",
        "Mentions key detail they forgot initially",
    ],
}

# Scenario distributions for realistic sessions
SCENARIO_DISTRIBUTIONS = {
    "strong_candidate": {
        "ANSWER_GOOD": 0.5,
        "ANSWER_PARTIAL": 0.25,
        "ANSWER_VAGUE": 0.1,
        "ASKS_QUESTION": 0.1,
        "NEW_INFO": 0.05,
    },
    "average_candidate": {
        "ANSWER_GOOD": 0.2,
        "ANSWER_PARTIAL": 0.3,
        "ANSWER_VAGUE": 0.25,
        "ASKS_QUESTION": 0.15,
        "SAYS_IDK": 0.05,
        "OFF_TOPIC": 0.05,
    },
    "weak_candidate": {
        "ANSWER_VAGUE": 0.35,
        "ANSWER_PARTIAL": 0.2,
        "SAYS_IDK": 0.2,
        "OFF_TOPIC": 0.1,
        "PUSHBACK": 0.1,
        "ASKS_QUESTION": 0.05,
    },
    "friction_heavy": {
        "SAYS_IDK": 0.3,
        "PUSHBACK": 0.25,
        "OFF_TOPIC": 0.2,
        "ANSWER_VAGUE": 0.15,
        "ANSWER_PARTIAL": 0.1,
    },
}


@dataclass
class SyntheticResponse:
    """A synthetic candidate response."""
    response_type: str
    response_text: str
    quality_score: float  # 0-1, how good the response is


class SyntheticSessionGenerator:
    """
    Generate synthetic interview sessions for training.

    Uses the ACTUAL production system (real_interview + AgenticInterviewer)
    with LLM-simulated candidate responses.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    async def generate_initial_answer(
        self,
        question: str,
        candidate_type: str = "average_candidate",
        level: str = "Senior"
    ) -> str:
        """Generate a realistic initial BQ answer."""

        prompt = f"""Generate a realistic behavioral interview answer for a {level}-level candidate.

Question: {question}
Candidate type: {candidate_type}

The answer should:
- Be 100-200 words
- {"Have clear gaps (missing metrics, vague ownership)" if candidate_type != "strong_candidate" else "Be strong but still have 1-2 minor gaps to probe"}
- Sound natural, not scripted

Just output the answer text, nothing else."""

        response = await acompletion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        return response.choices[0].message.content

    async def generate_response(
        self,
        question: str,
        original_answer: str,
        probe: str,
        target_type: str,
        conversation_history: List[Tuple[str, str]] = None
    ) -> SyntheticResponse:
        """Generate a synthetic response of a specific type."""

        templates = RESPONSE_TEMPLATES.get(target_type, RESPONSE_TEMPLATES["ANSWER_VAGUE"])
        template_hint = random.choice(templates)

        history_text = ""
        if conversation_history:
            for q, a in conversation_history[-3:]:
                history_text += f"Q: {q}\nA: {a}\n\n"

        prompt = f"""Generate a realistic candidate response to an interview probe.

Original question: {question}
Original answer: {original_answer}

{f"Previous exchanges:{chr(10)}{history_text}" if history_text else ""}

Current probe: {probe}

Generate a response that is clearly type: {target_type}
Hint: {template_hint}

The response should:
- Be 30-100 words
- Sound natural
- Clearly match the {target_type} pattern

OUTPUT JSON:
{{
    "response": "the candidate's response",
    "quality_score": 0.0-1.0
}}"""

        response = await acompletion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return SyntheticResponse(
            response_type=target_type,
            response_text=result["response"],
            quality_score=result.get("quality_score", 0.5)
        )

    def sample_response_type(self, scenario: str, turn: int) -> str:
        """Sample a response type based on scenario distribution."""
        dist = SCENARIO_DISTRIBUTIONS.get(scenario, SCENARIO_DISTRIBUTIONS["average_candidate"])

        # Adjust distribution based on turn (more friction later)
        if turn > 4:
            # Increase friction probability after turn 4
            adjusted = dist.copy()
            friction_boost = 0.1 * (turn - 4)
            for key in ["SAYS_IDK", "PUSHBACK", "ANSWER_VAGUE"]:
                if key in adjusted:
                    adjusted[key] = min(0.4, adjusted.get(key, 0) + friction_boost / 3)
            # Normalize
            total = sum(adjusted.values())
            adjusted = {k: v/total for k, v in adjusted.items()}
            dist = adjusted

        types = list(dist.keys())
        weights = list(dist.values())
        return random.choices(types, weights=weights, k=1)[0]

    async def generate_session(
        self,
        scenario: str = "average_candidate",
        max_turns: int = 8,
        level: str = "Senior"
    ) -> SessionLog:
        """
        Generate a complete synthetic session using the PRODUCTION system.

        Flow:
        1. Generate synthetic answer
        2. Run real_interview() to get evaluation (production)
        3. Initialize AgenticInterviewer with evaluation (production)
        4. Simulate candidate responses and run step() (production)
        """
        from interview_analyzer import AgenticInterviewer
        from prompts import BQQuestions

        # Step 1: Generate synthetic answer
        question = random.choice(get_bq_questions())
        answer = await self.generate_initial_answer(question, scenario, level)

        # Step 2: Run PRODUCTION real_interview() to get evaluation
        print(f"    Running real_interview()...")
        prompt = BQQuestions.real_interview(question=question, answer=answer, level=level)

        response = await acompletion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        evaluation = response.choices[0].message.content

        # Step 3: Initialize PRODUCTION AgenticInterviewer
        interviewer = AgenticInterviewer(model=self.model, max_turns=max_turns)
        init_result = interviewer.initialize(
            question=question,
            answer=answer,
            evaluation=evaluation,
            level=level
        )

        if init_result["action"] == "STOP":
            # No probing needed - skip this session (not useful for training)
            print(f"    Skipping: No probing needed (rating: {interviewer.parsed_eval.recommendation})")
            return None

        # Step 4: Run probing loop with simulated responses
        print(f"    Probing loop (scenario: {scenario})...")
        turn = 0
        while interviewer.should_continue() and turn < max_turns:
            probe = interviewer.get_current_probe()
            if not probe:
                break

            # Generate simulated response based on scenario
            response_type = self.sample_response_type(scenario, turn)
            response = await self.generate_response(
                question=question,
                original_answer=answer,
                probe=probe,
                target_type=response_type,
                conversation_history=interviewer.qa_pairs
            )

            # Run PRODUCTION step()
            decision = await interviewer.step(response.response_text)

            if decision.get("action") == "STOP":
                break

            turn += 1

        # Finalize session
        interviewer.finalize_session()
        return interviewer.session_log



class SessionLabeler:
    """Label sessions with optimal stopping points using LLM."""

    def __init__(self, model: str = "gpt-4o"):
        self.model = model

    async def label_session(self, session: SessionLog) -> Dict:
        """Use LLM to determine optimal stopping point."""
        prompt = StopPolicyTeacher.retro_label_prompt(session)

        response = await acompletion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        session.optimal_stop_turn = result.get("optimal_stop_turn")
        session.teacher_feedback = result.get("reasoning")

        return result


class YouTubeTranscriptParser:
    """Parse YouTube mock interview transcripts for few-shot examples."""

    @staticmethod
    def parse_transcript(transcript: str) -> List[Dict]:
        """
        Parse a transcript into Q&A exchanges.

        Expected format (flexible):
        - Lines starting with "Interviewer:" or "I:" are questions
        - Lines starting with "Candidate:" or "C:" are answers
        """
        exchanges = []
        current_q = None
        current_a = []

        for line in transcript.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Detect interviewer line
            if any(line.lower().startswith(p) for p in ["interviewer:", "i:", "q:"]):
                # Save previous exchange
                if current_q and current_a:
                    exchanges.append({
                        "question": current_q,
                        "answer": " ".join(current_a)
                    })
                current_q = line.split(":", 1)[1].strip() if ":" in line else line
                current_a = []

            # Detect candidate line
            elif any(line.lower().startswith(p) for p in ["candidate:", "c:", "a:"]):
                answer_text = line.split(":", 1)[1].strip() if ":" in line else line
                current_a.append(answer_text)

            # Continuation of previous speaker
            elif current_a is not None:
                current_a.append(line)

        # Save last exchange
        if current_q and current_a:
            exchanges.append({
                "question": current_q,
                "answer": " ".join(current_a)
            })

        return exchanges

    @staticmethod
    async def classify_exchanges(
        exchanges: List[Dict],
        model: str = "gpt-4o-mini"
    ) -> List[Dict]:
        """Classify each exchange with response type."""

        prompt = f"""Classify each candidate response in these interview exchanges.

EXCHANGES:
{json.dumps(exchanges, indent=2)}

For each exchange, determine:
1. response_type: ANSWER_GOOD, ANSWER_VAGUE, ANSWER_PARTIAL, ASKS_QUESTION, SAYS_IDK, OFF_TOPIC, PUSHBACK, NEW_INFO
2. quality_notes: Why this classification

OUTPUT JSON:
{{
    "classified": [
        {{"question": "...", "answer": "...", "response_type": "...", "quality_notes": "..."}},
        ...
    ]
}}"""

        response = await acompletion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result.get("classified", [])


POLICY_DIR = os.path.dirname(os.path.abspath(__file__))


async def evaluate_llm_zero_shot(states: List, model: str = "gpt-4o") -> List[int]:
    """
    Evaluate LLM zero-shot stop policy on a list of states.
    Returns list of predictions (1=STOP, 0=CONTINUE).
    """
    from policy.stop_policy import StateFeatures

    predictions = []

    for state in states:
        prompt = f"""You are an experienced FAANG interviewer conducting a behavioral interview. You need to decide whether to STOP probing (move to next question) or CONTINUE probing the current question.

## Interview Context
- **Candidate Level**: {state.level} ({"expect strategic leadership examples" if state.level == "Staff" else "expect solid execution examples" if state.level == "Senior" else "expect learning and growth examples"})
- **Current Turn**: {state.turn_count} of {state.max_turns} maximum

## Gaps Analysis
- **Initial gaps identified**: {state.gaps_remaining + state.gaps_resolved}
- **Gaps resolved through probing**: {state.gaps_resolved}
- **Gaps still remaining**: {state.gaps_remaining}

## Candidate Response Quality
- **Good substantive responses**: {state.good_responses} (specific examples, metrics, clear ownership)
- **Vague/generic responses**: {state.vague_responses} (lacking specifics)
- **"I don't know" responses**: {state.idk_count}
- **Pushback/deflection**: {state.pushback_count}
- **Friction ratio**: {state.friction_ratio:.1%} (proportion of unproductive responses)

## Decision Guidelines
STOP probing when:
- All significant gaps have been resolved
- Candidate shows consistent inability to provide more details (high IDK/vague)
- Friction is high (>50%) - continuing wastes time
- You've gathered enough signal to make a fair assessment
- Candidate has given 2+ good substantive responses

CONTINUE probing when:
- Critical gaps remain unaddressed
- Candidate is being responsive and providing new information
- Early in the conversation with low friction
- Need more evidence for hire/no-hire decision

Based on this context, should you STOP or CONTINUE?

Answer with ONLY one word: STOP or CONTINUE"""

        response = await acompletion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=10
        )

        answer = response.choices[0].message.content.strip().upper()
        predictions.append(1 if "STOP" in answer else 0)

    return predictions

async def generate_synthetic_sessions(
    n_sessions: int = 100,
    output_dir: str = None
) -> List[str]:
    """Generate N synthetic sessions and save them."""
    if output_dir is None:
        output_dir = os.path.join(POLICY_DIR, "session_logs")
    os.makedirs(output_dir, exist_ok=True)

    generator = SyntheticSessionGenerator()
    labeler = SessionLabeler()

    scenarios = list(SCENARIO_DISTRIBUTIONS.keys())
    levels = ["Junior-Mid", "Senior", "Staff"]

    saved_paths = []

    for i in range(n_sessions):
        scenario = random.choice(scenarios)
        level = random.choice(levels)

        print(f"[{i+1}/{n_sessions}] Generating {scenario} session at {level} level...")

        session = await generator.generate_session(
            scenario=scenario,
            level=level
        )

        # Label with optimal stop
        print(f"  Labeling optimal stop point...")
        label = await labeler.label_session(session)
        print(f"  Optimal stop: turn {label.get('optimal_stop_turn')} ({label.get('actual_stop_assessment')})")

        # Save
        path = f"{output_dir}/{session.session_id}.json"
        session.save(path)
        saved_paths.append(path)

        print(f"  Saved: {path}")

    return saved_paths


async def process_youtube_transcript(
    transcript_path: str,
    output_path: str = "youtube_examples.json"
) -> List[Dict]:
    """Process a YouTube transcript into classified examples."""

    with open(transcript_path, "r") as f:
        transcript = f.read()

    parser = YouTubeTranscriptParser()
    exchanges = parser.parse_transcript(transcript)

    print(f"Found {len(exchanges)} exchanges in transcript")

    classified = await parser.classify_exchanges(exchanges)

    with open(output_path, "w") as f:
        json.dump(classified, f, indent=2)

    print(f"Saved classified examples to {output_path}")

    # Print summary
    type_counts = {}
    for ex in classified:
        rt = ex.get("response_type", "UNKNOWN")
        type_counts[rt] = type_counts.get(rt, 0) + 1

    print("\nResponse type distribution:")
    for rt, count in sorted(type_counts.items()):
        print(f"  {rt}: {count}")

    return classified


def train_classifier(session_dir: str = None):
    """Train the stop policy classifier on labeled sessions."""
    if session_dir is None:
        session_dir = os.path.join(POLICY_DIR, "session_logs")

    # Load all sessions
    sessions = []
    for filename in os.listdir(session_dir):
        if filename.endswith(".json"):
            with open(os.path.join(session_dir, filename), "r") as f:
                data = json.load(f)
                sessions.append(data)

    print(f"Loaded {len(sessions)} sessions")

    # Extract training data: (state_features, should_stop)
    X = []  # Feature vectors
    y = []  # Labels (1 = should stop, 0 = should continue)

    for session in sessions:
        optimal_stop = session.get("optimal_stop_turn")
        if optimal_stop is None:
            continue

        for step in session.get("trajectory", []):
            turn = step.get("turn", 0)
            state = step.get("state", {})

            # Extract features
            features = [
                state.get("gaps_remaining", 0),
                state.get("gaps_resolved", 0),
                state.get("turn_count", 0),
                state.get("good_responses", 0),
                state.get("vague_responses", 0),
                state.get("idk_count", 0),
                state.get("pushback_count", 0),
                state.get("friction_ratio", 0),
                1 if state.get("level") == "Senior" else 0,
                1 if state.get("level") == "Staff" else 0,
            ]

            # Label: should we have stopped at this turn?
            should_stop = 1 if turn >= optimal_stop else 0

            X.append(features)
            y.append(should_stop)

    print(f"Training samples: {len(X)}")
    print(f"Stop labels: {sum(y)} / {len(y)}")

    # Train simple logistic regression
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, classification_report
        import pickle

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        clf = LogisticRegression(max_iter=1000)
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)
        print(f"\n=== LEARNED POLICY ===")
        print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=["Continue", "Stop"]))

        # Compare to heuristic baseline
        print(f"\n=== HEURISTIC BASELINE ===")
        from policy.stop_policy import ZeroShotStopPolicy, StateFeatures
        y_heuristic = []
        test_states = []  # Save for LLM baseline
        for i, features in enumerate([X_test[j] for j in range(len(X_test))]):
            state = StateFeatures(
                gaps_remaining=int(features[0]),
                gaps_resolved=int(features[1]),
                turn_count=int(features[2]),
                good_responses=int(features[3]),
                vague_responses=int(features[4]),
                idk_count=int(features[5]),
                pushback_count=int(features[6]),
                friction_ratio=features[7],
                level="Senior" if features[8] else ("Staff" if features[9] else "Junior-Mid"),
                max_turns=8
            )
            test_states.append(state)
            decision, _ = ZeroShotStopPolicy.should_stop(state)
            y_heuristic.append(1 if decision.value == "STOP" else 0)

        print(f"Accuracy: {accuracy_score(y_test, y_heuristic):.2f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_heuristic, target_names=["Continue", "Stop"]))

        # LLM zero-shot baseline (optional, slower)
        print(f"\n=== LLM ZERO-SHOT BASELINE ===")
        print("Running LLM predictions on test set...")
        import nest_asyncio
        nest_asyncio.apply()
        import asyncio
        y_llm = asyncio.get_event_loop().run_until_complete(evaluate_llm_zero_shot(test_states))
        print(f"Accuracy: {accuracy_score(y_test, y_llm):.2f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_llm, target_names=["Continue", "Stop"]))

        # Save model
        model_path = os.path.join(POLICY_DIR, "stop_policy_model.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(clf, f)
        print(f"\nModel saved to {model_path}")

        # Print feature importances
        feature_names = [
            "gaps_remaining", "gaps_resolved", "turn_count",
            "good_responses", "vague_responses", "idk_count",
            "pushback_count", "friction_ratio", "is_senior", "is_staff"
        ]
        print("\nFeature importances:")
        for name, coef in sorted(zip(feature_names, clf.coef_[0]), key=lambda x: abs(x[1]), reverse=True):
            print(f"  {name}: {coef:.3f}")

    except ImportError:
        print("\nInstall scikit-learn to train classifier: pip install scikit-learn")


async def relabel_sessions(session_dir: str = None, output_dir: str = None):
    """Re-label all sessions with gpt-4o for better optimal_stop_turn labels."""
    if session_dir is None:
        session_dir = os.path.join(POLICY_DIR, "session_logs")
    if output_dir is None:
        output_dir = os.path.join(POLICY_DIR, "session_logs_relabeled")

    os.makedirs(output_dir, exist_ok=True)

    labeler = SessionLabeler(model="gpt-4o")

    files = [f for f in os.listdir(session_dir) if f.endswith(".json")]
    print(f"Re-labeling {len(files)} sessions with gpt-4o...")
    print(f"  Input:  {session_dir}")
    print(f"  Output: {output_dir}")

    for i, filename in enumerate(files):
        path = os.path.join(session_dir, filename)
        with open(path, "r") as f:
            data = json.load(f)

        # Reconstruct SessionLog
        session = SessionLog(
            session_id=data["session_id"],
            question=data["question"],
            original_answer=data["original_answer"],
            level=data["level"],
            initial_gaps=data["initial_gaps"],
            initial_weak_competencies=data["initial_weak_competencies"],
        )
        session.trajectory = data.get("trajectory", [])
        session.final_qa_pairs = data.get("final_qa_pairs", [])
        session.initial_rating = data.get("initial_rating")
        session.final_rating = data.get("final_rating")

        # Re-label
        old_stop = data.get("optimal_stop_turn")
        result = await labeler.label_session(session)
        new_stop = result.get("optimal_stop_turn")

        print(f"  [{i+1}/{len(files)}] {filename}: turn {old_stop} -> {new_stop}")

        # Save to new folder
        output_path = os.path.join(output_dir, filename)
        session.save(output_path)

    print(f"\nDone! Relabeled files saved to: {output_dir}")
    print(f"To use: mv {output_dir}/* {session_dir}/")


async def main():
    parser = argparse.ArgumentParser(description="Bootstrap training data generator")
    parser.add_argument("--synthetic", type=int, help="Generate N synthetic sessions")
    parser.add_argument("--youtube", type=str, help="Path to YouTube transcript file")
    parser.add_argument("--train", action="store_true", help="Train classifier on session_logs/")
    parser.add_argument("--relabel", action="store_true", help="Re-label all sessions with gpt-4o")

    args = parser.parse_args()

    if args.relabel:
        await relabel_sessions()

    if args.synthetic:
        await generate_synthetic_sessions(n_sessions=args.synthetic)

    if args.youtube:
        await process_youtube_transcript(args.youtube)

    if args.train:
        train_classifier()

    if not any([args.synthetic, args.youtube, args.train]):
        parser.print_help()
        print("\nExamples:")
        print("  python bootstrap_training.py --synthetic 50")
        print("  python bootstrap_training.py --youtube mock_interview.txt")
        print("  python bootstrap_training.py --train")


if __name__ == "__main__":
    asyncio.run(main())
