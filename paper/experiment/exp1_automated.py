#!/usr/bin/env python3
"""
Experiment 1 - Step 2: Run Automated Group

For each answer in Group A:
- Initialize StorySelfImprove
- Run improvement (max 5 iterations)
- Record: iterations, ratings at each iteration, final answer
- Save results to exp1_automated_results.json
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

from advance.self_improve import StorySelfImprove
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


async def process_single_answer(
    feedback_file: Path,
    qa_id: int,
    level: str = "Junior-Mid"
) -> dict:
    """
    Process a single answer using StorySelfImprove.
    Records rating at each iteration.
    """
    start_time = time.time()
    
    try:
        # Initialize StorySelfImprove
        self_improve = StorySelfImprove(
            feedback_file=feedback_file,
            level=level
        )
        
        # Get initial state
        initial_question = await self_improve.question()
        initial_answer = await self_improve.answer()
        initial_feedback = self_improve.feedback_full_content
        initial_rating = extract_rating(initial_feedback)
        
        # Record iteration history
        iteration_history = []
        iteration_history.append({
            'iteration': 0,
            'rating': initial_rating,
            'rating_score': RATING_SCORES.get(initial_rating, -1),
            'answer': initial_answer,
            'feedback': initial_feedback,
        })
        
        # Run improvement (modify to capture iteration ratings)
        # Note: Current StorySelfImprove.run() doesn't expose iteration ratings
        # We need to manually track by monitoring feedback_file changes
        await self_improve.run()
        
        # Get final results
        final_answer = await self_improve.improved_answer()
        final_feedback = await self_improve.feedback()
        final_rating = extract_rating(final_feedback)
        
        # Try to extract intermediate ratings from feedback files
        # (This is a workaround since StorySelfImprove doesn't expose iteration history)
        # TODO: Modify StorySelfImprove to return iteration history
        
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
            'iteration_history': iteration_history,  # TODO: Populate with actual iteration data
            'reached_strong_hire': final_rating == 'Strong Hire',
            'elapsed_time_seconds': elapsed_time,
            'level': level,
            'timestamp': datetime.now().isoformat(),
        }
        
    except Exception as e:
        print(f"Error processing Q&A {qa_id}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return {
            'qa_id': qa_id,
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
        }


async def process_group_a(
    stratified_file: Path,
    feedback_dir: Path,
    output_dir: Path,
    level: str = "Junior-Mid"
):
    """
    Process Group A (Automated) - use stratified groups to select answers.
    For balanced comparison, we'll use answers from different rating categories.
    """
    # Load stratified groups
    with open(stratified_file, 'r', encoding='utf-8') as f:
        stratified = json.load(f)
    
    # Select Group A: Mix of different initial ratings
    # Use ~25 answers (half of 50) for Group A
    group_a_answers = []
    
    # Take ~8 from each category for balanced distribution
    group_a_answers.extend(stratified.get('leaning_no_hire', [])[:8])
    group_a_answers.extend(stratified.get('hire', [])[:8])
    group_a_answers.extend(stratified.get('strong_hire', [])[:5])
    group_a_answers.extend(stratified.get('other', [])[:4])
    
    print(f"Selected {len(group_a_answers)} answers for Group A (Automated)")
    print(f"Distribution:")
    rating_counts = {}
    for item in group_a_answers:
        rating = item.get('rating', 'Unknown')
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
    for rating, count in sorted(rating_counts.items()):
        print(f"  {rating}: {count}")
    
    # Process each answer concurrently
    semaphore = asyncio.Semaphore(5)  # Limit concurrent processing
    
    async def process_with_progress(item, index, total):
        qa_id = item['qa_id']
        feedback_file = feedback_dir / f"{qa_id}-{item['rating']}.md"
        
        if not feedback_file.exists():
            print(f"Warning: Feedback file not found for Q&A {qa_id}, skipping")
            return None
        
        async with semaphore:
            print(f"\n[{index}/{total}] Processing Q&A {qa_id}...")
            result = await process_single_answer(feedback_file, qa_id, level)
            
            # Print progress
            if result.get('error'):
                print(f"  [{index}/{total}] Q&A {qa_id} Error: {result['error']}")
            else:
                print(f"  [{index}/{total}] Q&A {qa_id}: {result['initial_rating']} -> {result['final_rating']} "
                      f"({result['iterations']} iterations, "
                      f"{result['rating_improvement']:+d} improvement)")
            return result
    
    tasks = [
        process_with_progress(item, i+1, len(group_a_answers))
        for i, item in enumerate(group_a_answers)
    ]
    results = await asyncio.gather(*tasks)
    results = [r for r in results if r is not None]  # Filter out None (skipped items)
    
    # Save results
    output_file = output_dir / 'exp1_automated_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"Group A (Automated) processing complete!")
    print(f"Results saved to: {output_file}")
    print(f"Total answers processed: {len(results)}")
    print(f"{'='*80}")
    
    return results


async def main():
    """Main function."""
    script_dir = Path(__file__).parent
    results_dir = script_dir / 'exp1_results'
    stratified_file = results_dir / 'exp1_stratified_groups.json'
    feedback_dir = results_dir / 'initial_feedbacks'
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
    print("EXPERIMENT 1 - STEP 2: AUTOMATED GROUP (Group A)")
    print("="*80)
    
    results = await process_group_a(
        stratified_file,
        feedback_dir,
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


if __name__ == '__main__':
    asyncio.run(main())

