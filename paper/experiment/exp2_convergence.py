#!/usr/bin/env python3
"""
Experiment 2 - Convergence Analysis (Paired Design)

Tests whether CoT prompting converges quickly by running both treatments
on the same answers and tracking rating at each iteration.

Design:
- Paired: Same 50 answers undergo both treatments
- Early stopping: Stop after rating unchanged for 3 consecutive iterations
- Max iterations: 10 (safety cap)

Hypothesis:
- Both methods converge quickly (within 2-3 iterations)
- Automated converges at a lower ceiling
- Human-in-loop converges at a higher ceiling
- More iterations don't help - the limitation is context, not compute
"""

import os
import sys
import asyncio
import json
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add project root to path
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from interview_analyzer import InterviewAnalyzer
from prompts import BQQuestions, BQAnswer, BQFeedback
from utils import FeedbackRecorder, FeedbackParser, StreamProcessor

# Set random seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Constants
RATING_SCORES = {
    'No Hire': 0, 'Leaning No Hire': 1, 'No-Pass': 1,
    'Borderline': 2, 'Leaning Hire': 2, 'Weak Hire': 2,
    'Hire': 3, 'Pass': 3, 'Strong Hire': 4,
}

# Convergence settings
MAX_ITERATIONS = 10
CONVERGENCE_THRESHOLD = 3  # Stop after rating unchanged for this many iterations


def get_rating_score(rating: str) -> int:
    """Convert rating string to numeric score."""
    if not rating:
        return -1
    rating_lower = rating.strip().lower()
    rating_map = {
        'strong hire': 4, 'hire': 3, 'weak hire': 2,
        'leaning hire': 2, 'borderline': 2,
        'leaning no hire': 1, 'no hire': 0,
        'no-pass': 1, 'no pass': 1, 'pass': 3,
    }
    if rating in RATING_SCORES:
        return RATING_SCORES[rating]
    return rating_map.get(rating_lower, -1)


def normalize_rating(rating: str) -> str:
    """Normalize rating to standard names."""
    rating_map = {
        'strong hire': 'Strong Hire', 'hire': 'Hire', 'weak hire': 'Weak Hire',
        'leaning hire': 'Leaning Hire', 'borderline': 'Borderline',
        'leaning no hire': 'Leaning No Hire', 'no hire': 'No Hire',
        'no-pass': 'No-Pass', 'no pass': 'No-Pass', 'pass': 'Pass',
    }
    return rating_map.get(rating.strip().lower(), rating.strip())


def extract_rating(feedback_text: str) -> str:
    """Extract and normalize rating from feedback text."""
    rating = FeedbackParser.extract_rating(feedback_text)
    if rating:
        return normalize_rating(rating)
    return 'Unknown'


class ConvergenceTracker:
    """Tracks convergence during iterative improvement."""

    def __init__(self, max_iterations: int = MAX_ITERATIONS, threshold: int = CONVERGENCE_THRESHOLD):
        self.max_iterations = max_iterations
        self.threshold = threshold
        self.rating_history: List[str] = []
        self.rating_score_history: List[int] = []
        self.unchanged_count = 0
        self.converged = False
        self.convergence_iteration: Optional[int] = None

    def add_rating(self, rating: str) -> bool:
        """
        Add a rating to history and check for convergence.
        Returns True if should continue, False if converged or max reached.
        """
        score = get_rating_score(rating)
        self.rating_history.append(rating)
        self.rating_score_history.append(score)

        # Check for convergence (rating unchanged)
        if len(self.rating_score_history) >= 2:
            if self.rating_score_history[-1] == self.rating_score_history[-2]:
                self.unchanged_count += 1
            else:
                self.unchanged_count = 0

        # Check if converged
        if self.unchanged_count >= self.threshold:
            self.converged = True
            # Convergence iteration is when rating first stabilized
            # Index 0 = initial rating, Index 1 = after iteration 1, etc.
            # Example: [LNH, Hire, Hire, Hire, Hire] len=5 → 5-3-1=1 (first Hire at iter 1)
            # Example: [LNH, LNH, LNH, Hire, Hire, Hire, Hire] len=7 → 7-3-1=3 (first Hire at iter 3)
            self.convergence_iteration = len(self.rating_history) - self.threshold - 1
            return False  # Stop

        # Check max iterations
        if len(self.rating_history) >= self.max_iterations:
            return False  # Stop

        return True  # Continue

    def get_summary(self) -> Dict:
        """Get convergence summary."""
        return {
            'rating_history': self.rating_history,
            'rating_score_history': self.rating_score_history,
            'converged': self.converged,
            'convergence_iteration': self.convergence_iteration,
            'total_iterations': len(self.rating_history),
            'final_rating': self.rating_history[-1] if self.rating_history else None,
            'final_rating_score': self.rating_score_history[-1] if self.rating_score_history else None,
        }


async def run_automated_with_tracking(
    feedback_file: Path,
    initial_rating: str,
    level: str = "Junior-Mid"
) -> Dict:
    """
    Run automated improvement with per-iteration tracking.
    Uses early stopping when rating converges.
    """
    analyzer = InterviewAnalyzer()
    tracker = ConvergenceTracker()

    # Read initial feedback
    with open(feedback_file, 'r', encoding='utf-8') as f:
        feedback_content = f.read()

    # Extract question and initial answer
    question_prompt = BQFeedback.extract_question(feedback_content)
    question_result = await analyzer.customized_analyze(question_prompt, stream=True)
    question = await StreamProcessor.get_text(question_result)

    answer_prompt = BQFeedback.extract_answer(feedback_content)
    answer_result = await analyzer.customized_analyze(answer_prompt, stream=True)
    current_answer = await StreamProcessor.get_text(answer_result)

    initial_answer = current_answer

    # Add initial rating
    tracker.add_rating(initial_rating)

    current_feedback_content = feedback_content
    current_rating = initial_rating
    current_rating_score = get_rating_score(initial_rating)

    # Iterate with early stopping
    while tracker.add_rating(current_rating) if len(tracker.rating_history) > 1 else True:
        if len(tracker.rating_history) > MAX_ITERATIONS:
            break

        # Generate improved answer
        improve_prompt = BQAnswer.improve_story(current_feedback_content)
        improve_result = await analyzer.customized_analyze(improve_prompt, stream=True)
        improved_answer = await StreamProcessor.get_text(improve_result)

        # Evaluate improved answer
        eval_prompt = BQQuestions.real_interview(question, improved_answer, level) + BQQuestions.bar_raiser(level)
        eval_result = await analyzer.customized_analyze(eval_prompt, stream=True)
        new_feedback = await StreamProcessor.get_text(eval_result)

        new_rating = extract_rating(new_feedback)
        new_rating_score = get_rating_score(new_rating)

        # Rating protection: only update if rating improved or stayed same
        if new_rating_score >= current_rating_score and new_rating_score >= 0:
            current_answer = improved_answer
            current_feedback_content = new_feedback
            current_rating = new_rating
            current_rating_score = new_rating_score

        # Add to tracker (use the protected rating)
        if not tracker.add_rating(current_rating):
            break

    summary = tracker.get_summary()
    summary['initial_answer'] = initial_answer
    summary['final_answer'] = current_answer
    summary['question'] = question

    return summary


async def run_human_in_loop_with_tracking(
    feedback_file: Path,
    initial_rating: str,
    human_answers: List[str],
    level: str = "Junior-Mid"
) -> Dict:
    """
    Run human-in-loop improvement with per-iteration tracking.
    Uses early stopping when rating converges.
    """
    analyzer = InterviewAnalyzer()
    tracker = ConvergenceTracker()

    # Read initial feedback
    with open(feedback_file, 'r', encoding='utf-8') as f:
        feedback_content = f.read()

    # Extract question and initial answer
    question_prompt = BQFeedback.extract_question(feedback_content)
    question_result = await analyzer.customized_analyze(question_prompt, stream=True)
    question = await StreamProcessor.get_text(question_result)

    answer_prompt = BQFeedback.extract_answer(feedback_content)
    answer_result = await analyzer.customized_analyze(answer_prompt, stream=True)
    current_answer = await StreamProcessor.get_text(answer_result)

    initial_answer = current_answer

    # Add initial rating
    tracker.add_rating(initial_rating)

    current_feedback_content = feedback_content
    current_rating = initial_rating
    current_rating_score = get_rating_score(initial_rating)

    # Get probing questions
    probing_questions = FeedbackParser.extract_probing_questions(feedback_content)

    # Build probing Q&A pairs (use 'q' and 'a' keys as expected by prompts.py)
    probing_qa = []
    for i, q in enumerate(probing_questions):
        if i < len(human_answers) and human_answers[i]:
            probing_qa.append({'q': q, 'a': human_answers[i]})

    # Iterate with early stopping
    while tracker.add_rating(current_rating) if len(tracker.rating_history) > 1 else True:
        if len(tracker.rating_history) > MAX_ITERATIONS:
            break

        # Generate improved answer with human context
        improve_prompt = BQAnswer.improve_with_probing_answers(
            current_answer, current_feedback_content, probing_qa
        )
        improve_result = await analyzer.customized_analyze(improve_prompt, stream=True)
        improved_answer = await StreamProcessor.get_text(improve_result)

        # Evaluate improved answer
        eval_prompt = BQQuestions.real_interview(question, improved_answer, level) + BQQuestions.bar_raiser(level)
        eval_result = await analyzer.customized_analyze(eval_prompt, stream=True)
        new_feedback = await StreamProcessor.get_text(eval_result)

        new_rating = extract_rating(new_feedback)
        new_rating_score = get_rating_score(new_rating)

        # Rating protection: only update if rating improved or stayed same
        if new_rating_score >= current_rating_score and new_rating_score >= 0:
            current_answer = improved_answer
            current_feedback_content = new_feedback
            current_rating = new_rating
            current_rating_score = new_rating_score

        # Add to tracker (use the protected rating)
        if not tracker.add_rating(current_rating):
            break

    summary = tracker.get_summary()
    summary['initial_answer'] = initial_answer
    summary['final_answer'] = current_answer
    summary['question'] = question
    summary['probing_qa'] = probing_qa

    return summary


async def process_paired_convergence(
    feedback_file: Path,
    qa_id: int,
    initial_rating: str,
    human_answers: List[str],
    level: str = "Junior-Mid"
) -> Dict:
    """
    Process a single answer with both treatments for convergence analysis.
    """
    start_time = time.time()

    result = {
        'qa_id': qa_id,
        'initial_rating': initial_rating,
        'initial_rating_score': get_rating_score(initial_rating),
        'level': level,
    }

    try:
        # Run automated with tracking
        auto_result = await run_automated_with_tracking(
            feedback_file, initial_rating, level
        )
        result['automated'] = auto_result

        # Run human-in-loop with tracking
        human_result = await run_human_in_loop_with_tracking(
            feedback_file, initial_rating, human_answers, level
        )
        result['human_in_loop'] = human_result

        # Compare convergence
        result['comparison'] = {
            'auto_convergence_iter': auto_result.get('convergence_iteration'),
            'human_convergence_iter': human_result.get('convergence_iteration'),
            'auto_final_rating': auto_result.get('final_rating'),
            'human_final_rating': human_result.get('final_rating'),
            'auto_final_score': auto_result.get('final_rating_score'),
            'human_final_score': human_result.get('final_rating_score'),
            'ceiling_difference': (human_result.get('final_rating_score', 0) or 0) -
                                 (auto_result.get('final_rating_score', 0) or 0),
        }

    except Exception as e:
        print(f"Error processing Q&A {qa_id}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        result['error'] = str(e)

    result['elapsed_time_seconds'] = time.time() - start_time
    result['timestamp'] = datetime.now().isoformat()

    return result


def load_human_input(human_input_file: Path) -> dict:
    """Load human-provided answers grouped by qa_id."""
    if not human_input_file.exists():
        return {}

    with open(human_input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    grouped = {}
    for item in data:
        qa_id = item['qa_id']
        if qa_id not in grouped:
            grouped[qa_id] = []
        grouped[qa_id].append(item)

    return grouped


async def run_convergence_experiment(
    stratified_file: Path,
    feedback_dir: Path,
    human_input_file: Path,
    output_dir: Path,
    level: str = "Junior-Mid"
):
    """
    Run convergence experiment on all answers using paired design.
    """
    # Load stratified groups
    with open(stratified_file, 'r', encoding='utf-8') as f:
        stratified = json.load(f)

    # Collect all answers
    all_answers = []
    all_answers.extend(stratified.get('leaning_no_hire', []))
    all_answers.extend(stratified.get('hire', []))
    all_answers.extend(stratified.get('strong_hire', []))
    all_answers.extend(stratified.get('other', []))

    # Filter out errors
    all_answers = [a for a in all_answers if a.get('rating') not in ['Error', 'Unknown']]

    print(f"Total answers to process: {len(all_answers)}")

    # Load human input
    human_inputs = load_human_input(human_input_file)
    print(f"Loaded human input for {len(human_inputs)} Q&A pairs")

    # Process each answer
    semaphore = asyncio.Semaphore(4)  # Limit concurrent processing (lower for convergence test)

    async def process_with_progress(item, index, total):
        qa_id = item['qa_id']
        initial_rating = normalize_rating(item['rating'])
        feedback_file = feedback_dir / f"{qa_id}-{item['rating']}.md"

        if not feedback_file.exists():
            print(f"Warning: Feedback file not found for Q&A {qa_id}, skipping")
            return None

        # Get human answers
        qa_human_inputs = human_inputs.get(qa_id, [])
        human_answers = []
        if qa_human_inputs:
            human_answers = qa_human_inputs[0].get('participant_answers', [])

        async with semaphore:
            print(f"\n[{index}/{total}] Processing Q&A {qa_id} (initial: {initial_rating})...")
            result = await process_paired_convergence(
                feedback_file, qa_id, initial_rating, human_answers, level
            )

            # Print progress
            if 'error' in result:
                print(f"  [{index}/{total}] Q&A {qa_id}: Error - {result['error']}")
            else:
                auto_conv = result.get('comparison', {}).get('auto_convergence_iter', '?')
                human_conv = result.get('comparison', {}).get('human_convergence_iter', '?')
                auto_final = result.get('comparison', {}).get('auto_final_rating', '?')
                human_final = result.get('comparison', {}).get('human_final_rating', '?')
                print(f"  [{index}/{total}] Q&A {qa_id}: Auto conv@{auto_conv}→{auto_final}, Human conv@{human_conv}→{human_final}")

            return result

    tasks = [
        process_with_progress(item, i+1, len(all_answers))
        for i, item in enumerate(all_answers)
    ]
    results = await asyncio.gather(*tasks)
    results = [r for r in results if r is not None]

    # Save results
    output_file = output_dir / 'exp2_convergence_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"Convergence experiment complete!")
    print(f"Results saved to: {output_file}")
    print(f"Total answers processed: {len(results)}")
    print(f"{'='*80}")

    # Print summary statistics
    successful = [r for r in results if 'error' not in r]
    if successful:
        auto_conv_iters = [r['comparison']['auto_convergence_iter'] for r in successful
                          if r['comparison'].get('auto_convergence_iter') is not None]
        human_conv_iters = [r['comparison']['human_convergence_iter'] for r in successful
                           if r['comparison'].get('human_convergence_iter') is not None]
        ceiling_diffs = [r['comparison']['ceiling_difference'] for r in successful]

        print("\nSummary Statistics:")
        print(f"  Successful: {len(successful)}/{len(results)}")

        if auto_conv_iters:
            print(f"\n  Automated Convergence:")
            print(f"    Mean iteration: {sum(auto_conv_iters)/len(auto_conv_iters):.2f}")
            print(f"    Converged: {len(auto_conv_iters)}/{len(successful)} ({100*len(auto_conv_iters)/len(successful):.1f}%)")

        if human_conv_iters:
            print(f"\n  Human-in-Loop Convergence:")
            print(f"    Mean iteration: {sum(human_conv_iters)/len(human_conv_iters):.2f}")
            print(f"    Converged: {len(human_conv_iters)}/{len(successful)} ({100*len(human_conv_iters)/len(successful):.1f}%)")

        print(f"\n  Ceiling Comparison:")
        print(f"    Mean difference (Human - Auto): {sum(ceiling_diffs)/len(ceiling_diffs):.2f}")
        print(f"    Human higher: {sum(1 for d in ceiling_diffs if d > 0)}")
        print(f"    Auto higher: {sum(1 for d in ceiling_diffs if d < 0)}")
        print(f"    Same: {sum(1 for d in ceiling_diffs if d == 0)}")

    return results


async def main():
    """Main function."""
    script_dir = Path(__file__).parent
    results_dir = script_dir / 'exp1_results'  # Reuse exp1 data
    stratified_file = results_dir / 'exp1_stratified_groups.json'
    feedback_dir = results_dir / 'initial_feedbacks'
    human_input_file = results_dir / 'exp1_human_input_template.json'

    # Create exp2 output directory
    exp2_output_dir = script_dir / 'exp2_results'
    exp2_output_dir.mkdir(exist_ok=True)

    if not stratified_file.exists():
        print(f"Error: {stratified_file} not found!")
        print("Please run exp1_prepare_dataset.py first.")
        return

    if not feedback_dir.exists():
        print(f"Error: {feedback_dir} not found!")
        print("Please run exp1_prepare_dataset.py first.")
        return

    print("="*80)
    print("EXPERIMENT 2 - CONVERGENCE ANALYSIS (PAIRED DESIGN)")
    print("="*80)
    print(f"Random seed: {RANDOM_SEED}")
    print(f"Max iterations: {MAX_ITERATIONS}")
    print(f"Convergence threshold: {CONVERGENCE_THRESHOLD} consecutive same ratings")
    print("Design: Paired - same answers undergo both treatments")
    print("="*80)

    results = await run_convergence_experiment(
        stratified_file,
        feedback_dir,
        human_input_file,
        exp2_output_dir,
        level="Junior-Mid"
    )


if __name__ == '__main__':
    asyncio.run(main())
