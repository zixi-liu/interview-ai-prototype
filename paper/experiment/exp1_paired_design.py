#!/usr/bin/env python3
"""
Experiment 1 - Paired Design Implementation

Implements within-subject paired design where each answer (n=50) undergoes both treatments:
- Automated improvement (StorySelfImprove)
- Human-in-loop improvement (HumanInLoopImprove)

Uses counterbalancing to control for order effects:
- 25 answers: Automated first, then Human-in-loop
- 25 answers: Human-in-loop first, then Automated

Each treatment starts from the original answer to avoid carryover effects.
"""

import os
import sys
import asyncio
import json
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add project root to path
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from advance.self_improve import StorySelfImprove, HumanInLoopImprove
from utils import FeedbackParser

# Set random seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Constants
RATING_SCORES = {
    'No Hire': 0, 'Leaning No Hire': 1, 'No-Pass': 1,
    'Borderline': 2, 'Leaning Hire': 2, 'Weak Hire': 2,
    'Hire': 3, 'Pass': 3, 'Strong Hire': 4,
}


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


def load_human_input(human_input_file: Path) -> dict:
    """
    Load human-provided answers.
    
    Expected format: List of dicts with:
    - qa_id
    - participant_answers: List of answers to probing questions
    - pre_survey, post_survey (optional)
    """
    if not human_input_file.exists():
        print(f"Warning: {human_input_file} not found!")
        return {}
    
    with open(human_input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Group by qa_id (multiple participants may answer same Q&A)
    grouped = {}
    for item in data:
        qa_id = item['qa_id']
        if qa_id not in grouped:
            grouped[qa_id] = []
        grouped[qa_id].append(item)
    
    return grouped


async def process_automated_improvement(
    feedback_file: Path,
    qa_id: int,
    initial_rating: str,
    level: str = "Junior-Mid"
) -> Dict:
    """
    Process a single answer using StorySelfImprove (automated).
    Always starts from the original answer.
    
    Args:
        feedback_file: Path to initial feedback file
        qa_id: Question-answer ID
        initial_rating: Initial rating from exp1_stratified_groups.json (not extracted from feedback content)
        level: Interview level
    """
    start_time = time.time()
    
    try:
        # Initialize StorySelfImprove (uses original answer from feedback file)
        self_improve = StorySelfImprove(
            feedback_file=feedback_file,
            level=level
        )
        
        # Get initial state
        initial_question = await self_improve.question()
        initial_answer = await self_improve.answer()
        initial_feedback = self_improve.feedback_full_content
        # Use initial_rating from stratified_groups, not extracted from feedback content
        # This ensures consistency with exp1_stratified_groups.json
        
        # Run improvement
        await self_improve.run()
        
        # Get final results
        # Use answer() to get the protected answer saved during iterations, not improved_answer() which generates a new answer
        final_answer = await self_improve.answer()
        final_feedback = await self_improve.feedback()
        final_rating = extract_rating(final_feedback)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        return {
            'qa_id': qa_id,
            'question': initial_question,
            'initial_answer': initial_answer,
            'initial_rating': initial_rating,
            'initial_rating_score': RATING_SCORES.get(initial_rating, -1),
            'final_answer': final_answer,
            'final_rating': final_rating,
            'final_rating_score': RATING_SCORES.get(final_rating, -1),
            'rating_improvement': RATING_SCORES.get(final_rating, -1) - RATING_SCORES.get(initial_rating, -1),
            'iterations': self_improve.iterate_times,
            'reached_strong_hire': final_rating == 'Strong Hire',
            'elapsed_time_seconds': elapsed_time,
            'level': level,
            'timestamp': datetime.now().isoformat(),
        }
        
    except Exception as e:
        print(f"Error processing automated improvement for Q&A {qa_id}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return {
            'qa_id': qa_id,
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
        }


async def process_human_in_loop_improvement(
    feedback_file: Path,
    qa_id: int,
    human_inputs: List[Dict],
    initial_rating: str,
    level: str = "Junior-Mid",
    max_iterations: int = 5
) -> Dict:
    """
    Process a single answer using HumanInLoopImprove.
    Always starts from the original answer.
    Uses the first participant's input if multiple available.
    
    Args:
        feedback_file: Path to initial feedback file
        qa_id: Question-answer ID
        human_inputs: List of human input dicts
        initial_rating: Initial rating from exp1_stratified_groups.json (not extracted from feedback content)
        level: Interview level
        max_iterations: Maximum number of improvement iterations
    """
    start_time = time.time()
    
    if not human_inputs:
        return {
            'qa_id': qa_id,
            'error': 'No human input available',
            'timestamp': datetime.now().isoformat(),
        }
    
    # Use first participant's input
    participant_data = human_inputs[0]
    participant_id = participant_data.get('participant_id', f'participant_{qa_id}')
    participant_answers = participant_data.get('participant_answers', [])
    
    if not participant_answers or all(a is None for a in participant_answers):
        return {
            'qa_id': qa_id,
            'error': 'No participant answers provided',
            'timestamp': datetime.now().isoformat(),
        }
    
    try:
        # Initialize HumanInLoopImprove (uses original answer from feedback file)
        human_improve = HumanInLoopImprove(
            feedback_file=feedback_file,
            level=level,
            max_iterations=max_iterations
        )
        
        # Get initial state
        initial_question = await human_improve.question()
        initial_answer = await human_improve.answer()
        initial_feedback = human_improve.feedback_full_content
        # Use initial_rating from stratified_groups, not extracted from feedback content
        # This ensures consistency with exp1_stratified_groups.json
        
        # Prepare probing answers
        probing_answers_per_iteration = [participant_answers]
        
        # Run improvement with human-provided answers
        result_dict = await human_improve.run_with_predefined_answers(
            probing_answers_per_iteration
        )
        
        # Extract final results
        final_answer = result_dict['final_answer']
        iterations = result_dict['iterations']
        status = result_dict['status']
        
        # Get final rating from feedback history
        final_rating = initial_rating  # Default
        if result_dict.get('feedback_history'):
            last_feedback = result_dict['feedback_history'][-1]
            if isinstance(last_feedback, dict):
                final_feedback_text = last_feedback.get('feedback', '')
            else:
                final_feedback_text = str(last_feedback)
            final_rating = extract_rating(final_feedback_text)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        return {
            'qa_id': qa_id,
            'participant_id': participant_id,
            'question': initial_question,
            'initial_answer': initial_answer,
            'initial_rating': initial_rating,
            'initial_rating_score': RATING_SCORES.get(initial_rating, -1),
            'final_answer': final_answer,
            'final_rating': final_rating,
            'final_rating_score': RATING_SCORES.get(final_rating, -1),
            'rating_improvement': RATING_SCORES.get(final_rating, -1) - RATING_SCORES.get(initial_rating, -1),
            'iterations': iterations,
            'status': status,
            'reached_strong_hire': status == 'strong_hire',
            'elapsed_time_seconds': elapsed_time,
            'probing_questions': participant_data.get('probing_questions', []),
            'participant_answers': participant_answers,
            'pre_survey': participant_data.get('pre_survey', {}),
            'post_survey': participant_data.get('post_survey', {}),
            'level': level,
            'timestamp': datetime.now().isoformat(),
        }
        
    except Exception as e:
        print(f"Error processing human-in-loop improvement for Q&A {qa_id}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return {
            'qa_id': qa_id,
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
        }


async def process_paired_answer(
    feedback_file: Path,
    qa_id: int,
    human_inputs: List[Dict],
    initial_rating: str,
    order: str,  # 'automated_first' or 'human_first'
    level: str = "Junior-Mid"
) -> Dict:
    """
    Process a single answer with both treatments in specified order.
    Each treatment starts from the original answer.
    
    Args:
        feedback_file: Path to initial feedback file (contains original answer)
        qa_id: Question-answer ID
        human_inputs: List of human input dicts
        initial_rating: Initial rating from exp1_stratified_groups.json
        order: Processing order ('automated_first' or 'human_first')
        level: Interview level
    
    Returns:
        Dict with results from both treatments
    """
    result = {
        'qa_id': qa_id,
        'order': order,
        'level': level,
    }
    
    if order == 'automated_first':
        # Process automated first
        automated_result = await process_automated_improvement(feedback_file, qa_id, initial_rating, level)
        result['automated'] = automated_result
        
        # Process human-in-loop second (still from original answer)
        human_result = await process_human_in_loop_improvement(feedback_file, qa_id, human_inputs, initial_rating, level)
        result['human_in_loop'] = human_result
    else:  # human_first
        # Process human-in-loop first
        human_result = await process_human_in_loop_improvement(feedback_file, qa_id, human_inputs, initial_rating, level)
        result['human_in_loop'] = human_result
        
        # Process automated second (still from original answer)
        automated_result = await process_automated_improvement(feedback_file, qa_id, initial_rating, level)
        result['automated'] = automated_result
    
    # Calculate paired difference (automated - human_in_loop)
    if 'error' not in result.get('automated', {}) and 'error' not in result.get('human_in_loop', {}):
        auto_improvement = result['automated'].get('rating_improvement', 0)
        human_improvement = result['human_in_loop'].get('rating_improvement', 0)
        result['paired_difference'] = auto_improvement - human_improvement
    
    result['timestamp'] = datetime.now().isoformat()
    
    return result


async def process_all_paired(
    stratified_file: Path,
    feedback_dir: Path,
    human_input_file: Path,
    output_dir: Path,
    level: str = "Junior-Mid"
):
    """
    Process all answers using paired design with counterbalancing.
    
    - All 50 answers undergo both treatments
    - Order is balanced: 25 automated-first, 25 human-first
    - Each treatment starts from original answer
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
    
    print(f"Total answers available: {len(all_answers)}")
    
    # Randomly assign order (counterbalancing)
    random.shuffle(all_answers)  # Shuffle for random assignment
    orders = ['automated_first'] * 25 + ['human_first'] * 25
    if len(all_answers) > 50:
        # If more than 50, randomly assign remaining
        orders.extend(random.choice(['automated_first', 'human_first']) 
                     for _ in range(len(all_answers) - 50))
    elif len(all_answers) < 50:
        # If less than 50, adjust proportionally
        n = len(all_answers)
        orders = ['automated_first'] * (n // 2) + ['human_first'] * (n - n // 2)
    
    random.shuffle(orders)  # Shuffle orders to randomize assignment
    
    # Load human input
    human_inputs = load_human_input(human_input_file)
    
    # Process each answer
    semaphore = asyncio.Semaphore(8)  # Limit concurrent processing
    
    async def process_with_progress(item, order, index, total):
        qa_id = item['qa_id']
        initial_rating = normalize_rating(item['rating'])  # Get and normalize initial_rating from stratified_groups
        feedback_file = feedback_dir / f"{qa_id}-{item['rating']}.md"  # Use original rating for filename
        
        if not feedback_file.exists():
            print(f"Warning: Feedback file not found for Q&A {qa_id}, skipping")
            return None
        
        qa_human_inputs = human_inputs.get(qa_id, [])
        
        async with semaphore:
            print(f"\n[{index}/{total}] Processing Q&A {qa_id} (order: {order}, initial_rating: {initial_rating})...")
            result = await process_paired_answer(
                feedback_file, qa_id, qa_human_inputs, initial_rating, order, level
            )
            
            # Print progress
            if result.get('automated', {}).get('error') or result.get('human_in_loop', {}).get('error'):
                print(f"  [{index}/{total}] Q&A {qa_id}: Errors occurred")
            else:
                auto_imp = result.get('automated', {}).get('rating_improvement', 0)
                human_imp = result.get('human_in_loop', {}).get('rating_improvement', 0)
                print(f"  [{index}/{total}] Q&A {qa_id}: Auto={auto_imp:+d}, Human={human_imp:+d}, Diff={result.get('paired_difference', 0):+d}")
            
            return result
    
    tasks = [
        process_with_progress(item, order, i+1, len(all_answers))
        for i, (item, order) in enumerate(zip(all_answers, orders))
    ]
    results = await asyncio.gather(*tasks)
    results = [r for r in results if r is not None]  # Filter out None
    
    # Save results
    output_file = output_dir / 'exp1_paired_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Also save in format compatible with existing analysis
    # Extract automated and human-in-loop results separately
    automated_results = []
    human_in_loop_results = []
    
    for result in results:
        if 'automated' in result and 'error' not in result['automated']:
            automated_results.append(result['automated'])
        if 'human_in_loop' in result and 'error' not in result['human_in_loop']:
            human_in_loop_results.append(result['human_in_loop'])
    
    # Save in old format for compatibility
    automated_file = output_dir / 'exp1_automated_results.json'
    with open(automated_file, 'w', encoding='utf-8') as f:
        json.dump(automated_results, f, indent=2, ensure_ascii=False)
    
    human_file = output_dir / 'exp1_human_in_loop_results.json'
    with open(human_file, 'w', encoding='utf-8') as f:
        json.dump(human_in_loop_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"Paired design processing complete!")
    print(f"Results saved to: {output_file}")
    print(f"Compatible format saved to:")
    print(f"  - {automated_file}")
    print(f"  - {human_file}")
    print(f"Total answers processed: {len(results)}")
    print(f"{'='*80}")
    
    # Print summary
    successful = [r for r in results if 'error' not in r.get('automated', {}) and 'error' not in r.get('human_in_loop', {})]
    if successful:
        auto_improvements = [r['automated']['rating_improvement'] for r in successful]
        human_improvements = [r['human_in_loop']['rating_improvement'] for r in successful]
        paired_diffs = [r.get('paired_difference', 0) for r in successful]
        
        print("\nSummary Statistics:")
        print(f"  Successful pairs: {len(successful)}/{len(results)}")
        print(f"  Automated mean improvement: {sum(auto_improvements)/len(auto_improvements):.2f}")
        print(f"  Human-in-loop mean improvement: {sum(human_improvements)/len(human_improvements):.2f}")
        print(f"  Mean paired difference (Auto - Human): {sum(paired_diffs)/len(paired_diffs):.2f}")
    
    return results


async def main():
    """Main function."""
    script_dir = Path(__file__).parent
    results_dir = script_dir / 'exp1_results'
    stratified_file = results_dir / 'exp1_stratified_groups.json'
    feedback_dir = results_dir / 'initial_feedbacks'
    human_input_file = results_dir / 'exp1_human_input_template.json'
    output_dir = results_dir
    
    if not stratified_file.exists():
        print(f"Error: {stratified_file} not found!")
        print("Please run exp1_prepare_dataset.py first.")
        return
    
    if not feedback_dir.exists():
        print(f"Error: {feedback_dir} not found!")
        print("Please run exp1_prepare_dataset.py first.")
        return
    
    print("="*80)
    print("EXPERIMENT 1 - PAIRED DESIGN IMPLEMENTATION")
    print("="*80)
    print(f"Random seed: {RANDOM_SEED}")
    print("Design: Within-subject paired design with counterbalancing")
    print("  - All answers undergo both treatments")
    print("  - Order balanced: 25 automated-first, 25 human-first")
    print("  - Each treatment starts from original answer")
    print("="*80)
    
    results = await process_all_paired(
        stratified_file,
        feedback_dir,
        human_input_file,
        output_dir,
        level="Junior-Mid"
    )


if __name__ == '__main__':
    asyncio.run(main())

