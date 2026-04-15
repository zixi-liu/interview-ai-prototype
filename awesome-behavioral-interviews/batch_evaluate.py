#!/usr/bin/env python3
"""
Batch evaluate all questions and answers from questions_answers.toml
using async concurrent processing and generate rating statistics.
"""

import os
import sys
import asyncio
import re
from pathlib import Path
from datetime import datetime
from collections import Counter
from dataclasses import dataclass

# Add project root to path
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
from utils import StreamProcessor, FeedbackParser, EvaluationParser, FeedbackRecorder

# Constants
RATING_CATEGORIES = {
    'pass': ['Pass', 'Hire', 'Strong Hire'],
    'borderline': ['Borderline', 'Weak Hire', 'Leaning Hire'],
    'no_pass': ['No-Pass', 'No Hire', 'Leaning No Hire'],
}

SEPARATOR = "=" * 80
SUBSECTION = "-" * 80


@dataclass
class EvaluationResult:
    """Result of a single Q&A evaluation."""
    qa_id: int
    question: str
    answer: str
    feedback_text: str
    rating: str


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


def extract_overall_rating(feedback_text: str) -> str:
    """Extract and normalize overall rating from feedback text."""
    # Try EvaluationParser first (most structured)
    try:
        parsed = EvaluationParser.parse(feedback_text)
        if parsed.recommendation:
            rec = re.sub(r'[🌟👍🤔🤨❌]', '', parsed.recommendation).strip()
            if rec:
                return normalize_rating(rec)
    except Exception:
        pass
    
    # Fallback to FeedbackParser
    rating = FeedbackParser.extract_rating(feedback_text)
    if rating:
        return normalize_rating(rating)
    
    # Fallback to FeedbackRecorder patterns (reuse existing patterns)
    recorder = FeedbackRecorder()
    extracted = recorder._extract_rating(feedback_text)
    if extracted != "NA":
        return normalize_rating(extracted.replace("_", " "))
    
    return 'Unknown'


def normalize_rating(rating: str) -> str:
    """Normalize rating to standard names."""
    rating_map = {
        'strong hire': 'Strong Hire', 'hire': 'Hire', 'weak hire': 'Weak Hire',
        'leaning hire': 'Leaning Hire', 'borderline': 'Borderline',
        'leaning no hire': 'Leaning No Hire', 'no hire': 'No Hire',
        'no-pass': 'No-Pass', 'no pass': 'No-Pass', 'pass': 'Pass',
    }
    return rating_map.get(rating.strip().lower(), rating.strip())


async def evaluate_single_qa(analyzer: InterviewAnalyzer, qa_id: int, question: str, answer: str, level: str = "Junior-Mid") -> EvaluationResult:
    """Evaluate a single question-answer pair."""
    try:
        prompt = BQQuestions.real_interview(question, answer, level) + BQQuestions.bar_raiser(level)
        result = await analyzer.customized_analyze(prompt, stream=True)
        feedback = await StreamProcessor.get_text(result)
        rating = extract_overall_rating(feedback)

        red_flag_prompt = BQQuestions.red_flag(question, answer, level) + BQQuestions.bar_raiser(level)
        red_flag_result = await analyzer.customized_analyze(red_flag_prompt, stream=True)
        red_flag_feedback = await StreamProcessor.get_text(red_flag_result)
        feedback_recorder = FeedbackRecorder()
        script_dir = Path(__file__).parent
        feedback_path = script_dir / f"feedbacks/{qa_id}-{rating}.md"
        await feedback_recorder.save_feedback(
            question, answer, feedback, red_flag_feedback, feedback_path)

        return EvaluationResult(qa_id, question, answer, feedback, rating)
    except Exception as e:
        print(f"Error evaluating Q&A {qa_id}: {e}", file=sys.stderr)
        return EvaluationResult(qa_id, question, answer, f"Error: {str(e)}", "Error")


async def batch_evaluate(questions_answers: list, level: str = "Junior-Mid", max_concurrent: int = 25) -> list[EvaluationResult]:
    """Evaluate all questions and answers concurrently."""
    analyzer = InterviewAnalyzer()
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def evaluate_with_semaphore(qa):
        async with semaphore:
            return await evaluate_single_qa(analyzer, qa['id'], qa['question'], qa['answer'], level)
    
    tasks = [evaluate_with_semaphore(qa) for qa in questions_answers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle exceptions
    processed = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            qa = questions_answers[i]
            processed.append(EvaluationResult(qa['id'], qa['question'], qa['answer'], f"Exception: {str(result)}", "Error"))
        else:
            processed.append(result)
    
    return processed


def generate_statistics(results: list[EvaluationResult]) -> dict:
    """Generate statistics from evaluation results."""
    rating_counter = Counter(r.rating for r in results)
    total = len(results)
    
    # Calculate category counts
    counts = {
        'pass': sum(rating_counter.get(r, 0) for r in RATING_CATEGORIES['pass']),
        'borderline': sum(rating_counter.get(r, 0) for r in RATING_CATEGORIES['borderline']),
        'no_pass': sum(rating_counter.get(r, 0) for r in RATING_CATEGORIES['no_pass']),
        'error': rating_counter.get('Error', 0) + rating_counter.get('Unknown', 0),
    }
    
    return {
        'total': total,
        'by_rating': dict(rating_counter),
        'pass_count': counts['pass'],
        'borderline_count': counts['borderline'],
        'no_pass_count': counts['no_pass'],
        'error_count': counts['error'],
        'pass_percentage': (counts['pass'] / total * 100) if total > 0 else 0,
        'borderline_percentage': (counts['borderline'] / total * 100) if total > 0 else 0,
        'no_pass_percentage': (counts['no_pass'] / total * 100) if total > 0 else 0,
    }


def format_statistics(stats: dict, include_header: bool = True) -> str:
    """Format statistics as text (reusable for both print and save)."""
    lines = []
    
    if include_header:
        lines.extend([SEPARATOR, "EVALUATION STATISTICS", SEPARATOR, ""])
    
    lines.extend([
        f"Total Questions Evaluated: {stats['total']}",
        "",
        SUBSECTION,
        "Rating Distribution:",
        SUBSECTION,
    ])
    
    # Sort by count descending
    sorted_ratings = sorted(stats['by_rating'].items(), key=lambda x: x[1], reverse=True)
    for rating, count in sorted_ratings:
        percentage = (count / stats['total'] * 100) if stats['total'] > 0 else 0
        lines.append(f"  {rating:25s}: {count:3d} ({percentage:5.1f}%)")
    
    lines.extend([
        "",
        SUBSECTION,
        "Summary by Category:",
        SUBSECTION,
        f"  Pass/Hire/Strong Hire:     {stats['pass_count']:3d} ({stats['pass_percentage']:5.1f}%)",
        f"  Borderline/Weak/Leaning Hire:     {stats['borderline_count']:3d} ({stats['borderline_percentage']:5.1f}%)",
        f"  No-Pass/No Hire/Leaning No Hire:            {stats['no_pass_count']:3d} ({stats['no_pass_percentage']:5.1f}%)",
    ])
    
    if stats['error_count'] > 0:
        lines.append(f"  Errors/Unknown:              {stats['error_count']:3d}")
    
    lines.append(SEPARATOR)
    return "\n".join(lines)


def print_statistics(stats: dict):
    """Print statistics to console."""
    print("\n" + format_statistics(stats, include_header=True) + "\n")


def save_statistics(stats: dict, results: list[EvaluationResult], output_file: Path):
    """Save statistics to a text file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(SEPARATOR + "\n")
        f.write("BATCH EVALUATION STATISTICS\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(format_statistics(stats, include_header=False) + "\n")


async def main():
    """Main function."""
    script_dir = Path(__file__).parent
    toml_file = script_dir / 'answers.toml'
    output_file = script_dir / 'evaluation_statistics.txt'
    
    if not toml_file.exists():
        print(f"Error: {toml_file} not found!")
        return
    
    print(f"Loading questions and answers from: {toml_file}")
    questions_answers = load_questions_answers(toml_file)
    print(f"Loaded {len(questions_answers)} questions and answers")
    
    print("\nStarting batch evaluation (this may take a while)...")
    print("Using async concurrent processing (max 50 concurrent requests)\n")
    
    results = await batch_evaluate(questions_answers, level="Junior-Mid", max_concurrent=5)
    stats = generate_statistics(results)
    
    print_statistics(stats)
    save_statistics(stats, results, output_file)
    print(f"Statistics saved to: {output_file}")


if __name__ == '__main__':
    asyncio.run(main())

