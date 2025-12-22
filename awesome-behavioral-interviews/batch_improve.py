#!/usr/bin/env python3
"""
Batch improve all feedback files by improving answers using StorySelfImprove,
then re-evaluate and compare statistics.
"""

import os
import sys
import asyncio
import re
from pathlib import Path
from datetime import datetime
from collections import Counter
from dataclasses import dataclass

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from interview_analyzer import InterviewAnalyzer
from prompts import BQQuestions
from utils import StreamProcessor, FeedbackParser, FeedbackRecorder
from advance.self_improve import StorySelfImprove

RATING_CATEGORIES = {
    'pass': ['Pass', 'Hire', 'Strong Hire'],
    'borderline': ['Borderline', 'Weak Hire', 'Leaning Hire'],
    'no_pass': ['No-Pass', 'No Hire', 'Leaning No Hire'],
}

RATING_SCORES = {
    'No Hire': 0, 'Leaning No Hire': 1, 'No-Pass': 1,
    'Borderline': 2, 'Leaning Hire': 2, 'Weak Hire': 2,
    'Hire': 3, 'Pass': 3, 'Strong Hire': 4,
}

SEPARATOR = "=" * 80
SUBSECTION = "-" * 80


@dataclass
class ImprovementResult:
    qa_id: int
    question: str
    original_answer: str
    improved_answer: str
    original_rating: str
    improved_rating: str


def extract_id_rating(filename: str) -> tuple[int | None, str | None]:
    """Extract QA ID and rating from filename like '1-Leaning No Hire.md'."""
    match = re.match(r'^(\d+)-(.+?)\.md$', filename)
    if match:
        return int(match.group(1)), match.group(2).replace("_", " ")
    return None, None


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
    extracted = FeedbackRecorder()._extract_rating(feedback_text)
    return normalize_rating(extracted.replace("_", " ")) if extracted != "NA" else 'Unknown'


def escape_toml_string(s: str) -> str:
    """Escape string for TOML multiline string."""
    if '"""' in s:
        escaped = s.replace("'", "''")
        return f"'''{escaped}'''"
    return f'"""{s}"""'


async def improve_single_feedback(feedback_file: Path, level: str = "Junior-Mid") -> ImprovementResult | None:
    """Improve a single feedback file."""
    try:
        qa_id, original_rating = extract_id_rating(feedback_file.name)
        if qa_id is None:
            print(f"Warning: Could not extract QA ID from {feedback_file.name}, skipping")
            return None
        
        
        # Use StorySelfImprove with iterative improvement strategy
        self_improve = StorySelfImprove(feedback_file=feedback_file, level=level)
        question = await self_improve.question()
        original_answer = await self_improve.answer()
        
        if not question or not original_answer:
            print(f"Warning: Could not extract question/answer from {feedback_file.name}, skipping")
            return None
        
        # Run iterative improvement (similar to story_improve_with_feedback)
        await self_improve.run()
        
        # Get final improved results after iteration
        improved_answer = await self_improve.improved_answer()
        improved_feedback = await self_improve.feedback()
        improved_red_flag = await self_improve.red_flag_feedback()
        
        improved_rating = extract_rating(improved_feedback)
        
        # Determine final file path (may have changed during iteration)
        final_feedback_file = self_improve.feedback_file or feedback_file
        
        # Generate new filename with updated rating
        new_filename = f"{qa_id}-{improved_rating}.md"
        new_filepath = feedback_file.parent / new_filename
        
        date_str = datetime.now().strftime("%Y%m%d")
        rating_header = improved_rating.replace(" ", "_")
        content_lines = [
            f"# Red Flag Evaluation ({date_str})", "", f"**Rating**: {rating_header}", "",
            "## Question", "", question.strip(), "",
            "## Answer", "", improved_answer.strip(), "",
            "## Feedback", "", improved_feedback.strip(), "",
            "## Red Flag", "", improved_red_flag.strip(), "",
        ]
        
        with open(new_filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(content_lines))
        
        # Remove old files if needed (run() may have created intermediate files)
        if final_feedback_file != new_filepath and final_feedback_file.exists():
            final_feedback_file.unlink()
        if feedback_file != new_filepath and feedback_file != final_feedback_file and feedback_file.exists():
            feedback_file.unlink()
        
        print(f"  {normalize_rating(original_rating or 'Unknown')} -> {improved_rating} (iterations: {self_improve.iterate_times})")
        
        return ImprovementResult(
            qa_id=qa_id, question=question, original_answer=original_answer,
            improved_answer=improved_answer, original_rating=normalize_rating(original_rating or 'Unknown'),
            improved_rating=improved_rating
        )
        
    except Exception as e:
        print(f"Error improving {feedback_file.name}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return None


async def batch_improve(feedback_dir: Path, level: str = "Junior-Mid", max_concurrent: int = 10) -> list[ImprovementResult]:
    """Improve all feedback files concurrently."""
    files = sorted(feedback_dir.glob("*.md"), key=lambda f: extract_id_rating(f.name)[0] or 0)
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process(f):
        async with semaphore:
            return await improve_single_feedback(f, level)
    
    results = await asyncio.gather(*[process(f) for f in files], return_exceptions=True)
    return [r for r in results if not isinstance(r, (Exception, type(None)))]


def save_improved_answers_toml(results: list[ImprovementResult], output_file: Path):
    """Save improved answers to TOML file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('# Improved Answers\n\n')
        for r in sorted(results, key=lambda x: x.qa_id):
            f.write(f'[[questions]]\nid = {r.qa_id}\n')
            f.write(f'question = {escape_toml_string(r.question)}\n')
            f.write(f'answer = {escape_toml_string(r.improved_answer)}\n\n')


def generate_statistics(results: list[ImprovementResult]) -> dict:
    """Generate improvement statistics."""
    total = len(results)
    orig_counter = Counter(r.original_rating for r in results)
    imp_counter = Counter(r.improved_rating for r in results)
    
    def count_category(counter, key):
        return sum(counter.get(r, 0) for r in RATING_CATEGORIES[key])
    
    def get_score(rating):
        return RATING_SCORES.get(rating, -1)
    
    improvements = sum(1 for r in results if get_score(r.improved_rating) > get_score(r.original_rating))
    degradations = sum(1 for r in results if get_score(r.improved_rating) < get_score(r.original_rating))
    
    return {
        'total': total,
        'original_by_rating': dict(orig_counter),
        'improved_by_rating': dict(imp_counter),
        'original_counts': {k: count_category(orig_counter, k) for k in RATING_CATEGORIES},
        'improved_counts': {k: count_category(imp_counter, k) for k in RATING_CATEGORIES},
        'improvements': improvements,
        'no_change': total - improvements - degradations,
        'degradations': degradations,
        'improvement_rate': (improvements / total * 100) if total > 0 else 0,
    }


def format_statistics(stats: dict) -> str:
    """Format improvement statistics as text."""
    total = stats['total']
    def format_ratings(counter):
        return "\n".join(f"  {r:25s}: {c:3d} ({c/total*100:5.1f}%)" 
                        for r, c in sorted(counter.items(), key=lambda x: x[1], reverse=True))
    
    orig_counts = stats['original_counts']
    imp_counts = stats['improved_counts']
    
    return f"""{SEPARATOR}
IMPROVEMENT STATISTICS
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{SEPARATOR}

Total Questions Improved: {stats['total']}

{SUBSECTION}
Improvement Summary:
{SUBSECTION}
  Improved:              {stats['improvements']:3d} ({stats['improvement_rate']:5.1f}%)
  No Change:             {stats['no_change']:3d}
  Degraded:              {stats['degradations']:3d}

{SUBSECTION}
Rating Distribution (Original):
{SUBSECTION}
{format_ratings(stats['original_by_rating'])}

{SUBSECTION}
Rating Distribution (Improved):
{SUBSECTION}
{format_ratings(stats['improved_by_rating'])}

{SUBSECTION}
Category Comparison:
{SUBSECTION}
  Pass/Hire/Strong Hire:
    Original:  {orig_counts['pass']:3d}
    Improved:  {imp_counts['pass']:3d}
    Change:    {imp_counts['pass'] - orig_counts['pass']:+3d}

  Borderline/Weak/Leaning Hire:
    Original:  {orig_counts['borderline']:3d}
    Improved:  {imp_counts['borderline']:3d}

  No-Pass/No Hire/Leaning No Hire:
    Original:  {orig_counts['no_pass']:3d}
    Improved:  {imp_counts['no_pass']:3d}
    Change:    {orig_counts['no_pass'] - imp_counts['no_pass']:+3d}

{SEPARATOR}
"""


async def main():
    """Main function."""
    script_dir = Path(__file__).parent
    feedback_dir = script_dir / 'feedbacks'
    improved_answers_file = script_dir / 'improved_answers.toml'
    statistics_file = script_dir / 'evaluation_statistics.txt'
    
    if not feedback_dir.exists():
        print(f"Error: {feedback_dir} not found!")
        return
    
    print(f"Found {len(list(feedback_dir.glob('*.md')))} feedback files to improve")
    print("\nStarting batch improvement (this may take a while)...")
    print("Using async concurrent processing (max 50 concurrent requests)\n")
    
    results = await batch_improve(feedback_dir, level="Junior-Mid", max_concurrent=50)
    
    if not results:
        print("No results to process")
        return
    
    print(f"\nSuccessfully improved {len(results)} feedback files")
    
    save_improved_answers_toml(results, improved_answers_file)
    print(f"Improved answers saved to: {improved_answers_file}")
    
    stats = generate_statistics(results)
    stats_text = format_statistics(stats)
    print("\n" + stats_text)
    
    with open(statistics_file, 'a', encoding='utf-8') as f:
        f.write("\n\n" + stats_text + "\n")
    print(f"Improvement statistics appended to: {statistics_file}")


if __name__ == '__main__':
    asyncio.run(main())
