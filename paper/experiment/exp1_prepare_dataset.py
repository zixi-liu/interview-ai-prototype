#!/usr/bin/env python3
"""
Experiment 1 - Step 1: Prepare Dataset

Load answers.toml, perform initial evaluation of all 50 answers,
save initial ratings and feedback, and stratify by rating for balanced groups.
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Add project root to path
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Fallback to tomli
    except ImportError:
        print("Error: Need tomllib (Python 3.11+) or tomli package")
        print("Install with: pip install tomli")
        sys.exit(1)

from interview_analyzer import InterviewAnalyzer
from prompts import BQQuestions
from utils import StreamProcessor, FeedbackParser, FeedbackRecorder

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


def load_questions_answers(toml_file: Path) -> list[dict]:
    """Load questions and answers from TOML file."""
    with open(toml_file, 'rb') as f:
        data = tomllib.load(f)
    
    return [
        {
            'id': item.get('id'),
            'question': item.get('question', ''),
            'answer': item.get('answer', '')
        }
        for item in data.get('questions', [])
    ]


def extract_rating(feedback_text: str) -> str:
    """Extract and normalize rating from feedback text."""
    rating = FeedbackParser.extract_rating(feedback_text)
    if rating:
        return normalize_rating(rating)
    return 'Unknown'


async def evaluate_single_qa(
    analyzer: InterviewAnalyzer,
    qa_id: int,
    question: str,
    answer: str,
    level: str = "Junior-Mid"
) -> dict:
    """Evaluate a single question-answer pair and return structured result."""
    try:
        # Initial evaluation with bar_raiser
        prompt = BQQuestions.real_interview(question, answer, level) + BQQuestions.bar_raiser(level)
        result = await analyzer.customized_analyze(prompt, stream=True)
        feedback = await StreamProcessor.get_text(result)
        rating = extract_rating(feedback)

        # Red flag evaluation
        red_flag_prompt = BQQuestions.red_flag(question, answer, level) + BQQuestions.bar_raiser(level)
        red_flag_result = await analyzer.customized_analyze(red_flag_prompt, stream=True)
        red_flag_feedback = await StreamProcessor.get_text(result)

        # Extract probing questions
        probing_questions = FeedbackParser.extract_probing_questions(feedback)

        return {
            'qa_id': qa_id,
            'question': question,
            'answer': answer,
            'rating': rating,
            'rating_score': RATING_SCORES.get(rating, -1),
            'feedback': feedback,
            'red_flag_feedback': red_flag_feedback,
            'probing_questions': probing_questions,
            'level': level,
            'evaluation_timestamp': datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"Error evaluating Q&A {qa_id}: {e}", file=sys.stderr)
        return {
            'qa_id': qa_id,
            'question': question,
            'answer': answer,
            'rating': 'Error',
            'rating_score': -1,
            'error': str(e),
        }


async def batch_evaluate(
    questions_answers: list,
    level: str = "Junior-Mid",
    max_concurrent: int = 5
) -> list[dict]:
    """Evaluate all questions and answers concurrently."""
    analyzer = InterviewAnalyzer()
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def evaluate_with_semaphore(qa):
        async with semaphore:
            return await evaluate_single_qa(
                analyzer, qa['id'], qa['question'], qa['answer'], level
            )
    
    tasks = [evaluate_with_semaphore(qa) for qa in questions_answers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle exceptions
    processed = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            qa = questions_answers[i]
            processed.append({
                'qa_id': qa['id'],
                'question': qa['question'],
                'answer': qa['answer'],
                'rating': 'Error',
                'rating_score': -1,
                'error': str(result),
            })
        else:
            processed.append(result)
    
    return processed


def stratify_by_rating(results: list[dict]) -> dict:
    """
    Stratify results by initial rating for balanced groups.
    
    Target distribution:
    - ~20 "Leaning No Hire"
    - ~20 "Hire"
    - ~10 "Strong Hire"
    """
    # Group by rating
    by_rating = defaultdict(list)
    for result in results:
        if result.get('rating') != 'Error' and result.get('rating') != 'Unknown':
            by_rating[result['rating']].append(result)
    
    # Sort by rating score for balanced selection
    for rating in by_rating:
        by_rating[rating].sort(key=lambda x: x.get('qa_id', 0))
    
    # Create stratified groups
    stratified = {
        'leaning_no_hire': by_rating.get('Leaning No Hire', [])[:20],
        'hire': by_rating.get('Hire', [])[:20],
        'strong_hire': by_rating.get('Strong Hire', [])[:10],
        'other': [],
    }
    
    # Add remaining answers to 'other'
    all_used_ids = set()
    for group in stratified.values():
        if isinstance(group, list):
            all_used_ids.update(r['qa_id'] for r in group)
    
    for result in results:
        if result.get('qa_id') not in all_used_ids and result.get('rating') not in ['Error', 'Unknown']:
            stratified['other'].append(result)
    
    return stratified


def save_results(results: list[dict], stratified: dict, output_dir: Path):
    """Save evaluation results and stratified groups."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save all results
    all_results_file = output_dir / 'exp1_initial_evaluations.json'
    with open(all_results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Saved all evaluations to: {all_results_file}")
    
    # Save stratified groups
    stratified_file = output_dir / 'exp1_stratified_groups.json'
    with open(stratified_file, 'w', encoding='utf-8') as f:
        json.dump(stratified, f, indent=2, ensure_ascii=False, default=str)
    print(f"Saved stratified groups to: {stratified_file}")
    
    # Save feedback files for StorySelfImprove
    feedback_dir = output_dir / 'initial_feedbacks'
    feedback_dir.mkdir(exist_ok=True)
    
    feedback_recorder = FeedbackRecorder()
    for result in results:
        if result.get('rating') not in ['Error', 'Unknown']:
            feedback_path = feedback_dir / f"{result['qa_id']}-{result['rating']}.md"
            asyncio.run(feedback_recorder.save_feedback(
                question=result['question'],
                answer=result['answer'],
                feedback=result.get('feedback', ''),
                red_flag=result.get('red_flag_feedback', ''),
                path=str(feedback_path)
            ))
    
    print(f"Saved feedback files to: {feedback_dir}")
    
    # Print statistics
    print("\n" + "="*80)
    print("DATASET PREPARATION STATISTICS")
    print("="*80)
    print(f"Total Q&A pairs evaluated: {len(results)}")
    
    rating_counts = defaultdict(int)
    for result in results:
        rating_counts[result.get('rating', 'Unknown')] += 1
    
    print("\nRating Distribution:")
    for rating, count in sorted(rating_counts.items(), key=lambda x: -x[1]):
        print(f"  {rating:25s}: {count:3d}")
    
    print("\nStratified Groups:")
    print(f"  Leaning No Hire: {len(stratified['leaning_no_hire'])}")
    print(f"  Hire:            {len(stratified['hire'])}")
    print(f"  Strong Hire:     {len(stratified['strong_hire'])}")
    print(f"  Other:           {len(stratified['other'])}")
    print("="*80)


async def main():
    """Main function."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    toml_file = project_root / 'awesome-behavioral-interviews' / 'answers.toml'
    output_dir = script_dir / 'exp1_results'
    
    if not toml_file.exists():
        print(f"Error: {toml_file} not found!")
        return
    
    print(f"Loading questions and answers from: {toml_file}")
    questions_answers = load_questions_answers(toml_file)
    print(f"Loaded {len(questions_answers)} questions and answers")
    
    print("\nStarting initial evaluation (this may take a while)...")
    print("Using async concurrent processing (max 5 concurrent requests)\n")
    
    results = await batch_evaluate(questions_answers, level="Junior-Mid", max_concurrent=5)
    
    # Stratify by rating
    stratified = stratify_by_rating(results)
    
    # Save results
    save_results(results, stratified, output_dir)
    
    print("\nDataset preparation complete!")
    print(f"Results saved to: {output_dir}")


if __name__ == '__main__':
    asyncio.run(main())

