#!/usr/bin/env python3
"""
Experiment 1 - Step 4: Run Human-in-Loop Group

For each answer in Group B:
- Load human-provided probing answers
- Run HumanInLoopImprove.run_with_predefined_answers()
- Record: iterations, ratings, final answer
- Save results to exp1_human_in_loop_results.json
"""

import os
import sys
import asyncio
import json
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from advance.self_improve import HumanInLoopImprove
from utils import FeedbackParser

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
        print("Using template structure. Please fill in actual participant responses.")
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


async def process_single_answer_with_human_input(
    feedback_file: Path,
    qa_id: int,
    human_inputs: list[dict],
    level: str = "Junior-Mid",
    max_iterations: int = 3
) -> dict:
    """
    Process a single answer using HumanInLoopImprove with human-provided answers.
    
    Args:
        feedback_file: Path to initial feedback file
        qa_id: Question-answer ID
        human_inputs: List of human input dicts (may have multiple participants)
        level: Interview level
        max_iterations: Maximum iterations for improvement
    
    Returns:
        Result dict with all participant results
    """
    results = []
    
    for participant_data in human_inputs:
        participant_id = participant_data.get('participant_id', f'participant_{qa_id}')
        participant_answers = participant_data.get('participant_answers', [])
        
        # Skip if no answers provided
        if not participant_answers or all(a is None for a in participant_answers):
            print(f"  Warning: No answers provided by {participant_id}, skipping")
            continue
        
        start_time = time.time()
        
        try:
            # Initialize HumanInLoopImprove
            human_improve = HumanInLoopImprove(
                feedback_file=feedback_file,
                level=level,
                max_iterations=max_iterations
            )
            
            # Get initial state
            initial_question = await human_improve.question()
            initial_answer = await human_improve.answer()
            initial_feedback = human_improve.feedback_full_content
            initial_rating = extract_rating(initial_feedback)
            
            # Prepare probing answers for run_with_predefined_answers
            # Format: list of lists, one list per iteration
            # For now, use answers for iteration 1 only
            # TODO: Support multiple iterations if needed
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
            
            result = {
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
                'answer_history': result_dict.get('answer_history', []),
                'probing_questions': participant_data.get('probing_questions', []),
                'participant_answers': participant_answers,
                'pre_survey': participant_data.get('pre_survey', {}),
                'post_survey': participant_data.get('post_survey', {}),
                'level': level,
                'timestamp': datetime.now().isoformat(),
            }
            
            results.append(result)
            
        except Exception as e:
            print(f"  Error processing Q&A {qa_id} for participant {participant_id}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            results.append({
                'qa_id': qa_id,
                'participant_id': participant_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
            })
    
    return results


async def process_group_b(
    stratified_file: Path,
    feedback_dir: Path,
    human_input_file: Path,
    output_dir: Path,
    level: str = "Junior-Mid"
):
    """
    Process Group B (Human-in-Loop).
    Use answers NOT in Group A, with human-provided probing answers.
    """
    # Load stratified groups
    with open(stratified_file, 'r', encoding='utf-8') as f:
        stratified = json.load(f)
    
    # Load Group A IDs (to exclude from Group B)
    automated_results_file = output_dir / 'exp1_automated_results.json'
    group_a_ids = set()
    if automated_results_file.exists():
        with open(automated_results_file, 'r', encoding='utf-8') as f:
            group_a_results = json.load(f)
            group_a_ids = {r['qa_id'] for r in group_a_results if 'qa_id' in r}
    
    # Select Group B: Remaining answers (not in Group A)
    all_answers = []
    all_answers.extend(stratified.get('leaning_no_hire', []))
    all_answers.extend(stratified.get('hire', []))
    all_answers.extend(stratified.get('strong_hire', []))
    all_answers.extend(stratified.get('other', []))
    
    group_b_answers = [a for a in all_answers if a['qa_id'] not in group_a_ids]
    
    print(f"Selected {len(group_b_answers)} answers for Group B (Human-in-Loop)")
    print(f"(Excluded {len(group_a_ids)} answers used in Group A)")
    
    # Load human input
    human_inputs = load_human_input(human_input_file)
    
    if not human_inputs:
        print("\nWARNING: No human input data found!")
        print("Please:")
        print("1. Run exp1_collect_human_input.py to create template")
        print("2. Collect participant responses")
        print("3. Save to exp1_human_input.json")
        print("\nFor now, creating empty results structure...")
        # Create empty results
        results = []
    else:
        print(f"Loaded human input for {len(human_inputs)} Q&A pairs")
        
        # Prepare tasks for concurrent processing
        tasks = []
        task_info = []  # Store (index, qa_id) for progress tracking
        
        for i, item in enumerate(group_b_answers, 1):
            qa_id = item['qa_id']
            feedback_file = feedback_dir / f"{qa_id}-{item['rating']}.md"
            
            if not feedback_file.exists():
                print(f"Warning: Feedback file not found for Q&A {qa_id}, skipping")
                continue
            
            # Get human inputs for this Q&A
            qa_human_inputs = human_inputs.get(qa_id, [])
            
            if not qa_human_inputs:
                print(f"[{i}/{len(group_b_answers)}] Q&A {qa_id}: No human input available, skipping")
                continue
            
            # Create task with progress info
            task = process_single_answer_with_human_input(
                feedback_file,
                qa_id,
                qa_human_inputs,
                level=level,
                max_iterations=3
            )
            tasks.append(task)
            task_info.append((i, qa_id, len(qa_human_inputs)))
        
        # Process all tasks concurrently
        print(f"\nProcessing {len(tasks)} Q&A pairs concurrently...")
        all_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect and print results
        results = []
        processed_count = 0
        
        for (i, qa_id, num_participants), qa_results in zip(task_info, all_results):
            if isinstance(qa_results, Exception):
                print(f"\n[{i}/{len(group_b_answers)}] Q&A {qa_id}: Error - {qa_results}")
                continue
            
            print(f"\n[{i}/{len(group_b_answers)}] Q&A {qa_id} "
                  f"({num_participants} participant(s)) - Completed")
            
            results.extend(qa_results)
            processed_count += len(qa_results)
            
            # Print progress
            for result in qa_results:
                if result.get('error'):
                    print(f"  Error: {result['error']}")
                else:
                    print(f"  Participant {result['participant_id']}: "
                          f"{result['initial_rating']} -> {result['final_rating']} "
                          f"({result['iterations']} iterations, "
                          f"{result['rating_improvement']:+d} improvement)")
    
    # Save results
    output_file = output_dir / 'exp1_human_in_loop_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"Group B (Human-in-Loop) processing complete!")
    print(f"Results saved to: {output_file}")
    print(f"Total participant-answer pairs processed: {len(results)}")
    print(f"{'='*80}")
    
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
    print("EXPERIMENT 1 - STEP 4: HUMAN-IN-LOOP GROUP (Group B)")
    print("="*80)
    
    results = await process_group_b(
        stratified_file,
        feedback_dir,
        human_input_file,
        output_dir,
        level="Junior-Mid"
    )
    
    # Print summary statistics
    successful = [r for r in results if 'error' not in r]
    if successful:
        avg_improvement = sum(r['rating_improvement'] for r in successful) / len(successful)
        avg_iterations = sum(r['iterations'] for r in successful) / len(successful)
        strong_hire_count = sum(1 for r in successful if r['reached_strong_hire'])
        
        print("\nSummary Statistics:")
        print(f"  Successful: {len(successful)}/{len(results)}")
        print(f"  Average rating improvement: {avg_improvement:.2f}")
        print(f"  Average iterations: {avg_iterations:.2f}")
        print(f"  Reached Strong Hire: {strong_hire_count}/{len(successful)} "
              f"({100*strong_hire_count/len(successful):.1f}%)")
        
        # Participant statistics
        unique_participants = len(set(r['participant_id'] for r in successful if 'participant_id' in r))
        print(f"  Unique participants: {unique_participants}")


if __name__ == '__main__':
    asyncio.run(main())

