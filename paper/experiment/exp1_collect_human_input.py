#!/usr/bin/env python3
"""
Experiment 1 - Step 3: Collect Human Input

Extract probing questions for each answer and create interface for participants
to provide answers to probing questions.

This script:
1. Extracts probing questions from initial feedback
2. Creates a data structure for human input collection
3. Provides template for survey/interface
4. Saves structure to exp1_human_input_template.json

NOTE: Actual human input collection needs to be done separately (survey, interface, etc.)
This script prepares the structure and template.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from utils import FeedbackParser


def load_initial_evaluations(evaluations_file: Path) -> list[dict]:
    """Load initial evaluation results."""
    with open(evaluations_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_probing_questions_for_qa(evaluation: dict) -> list[str]:
    """Extract probing questions from evaluation feedback."""
    feedback = evaluation.get('feedback', '')
    if not feedback:
        return []
    
    probing_questions = FeedbackParser.extract_probing_questions(feedback)
    return probing_questions


def create_human_input_template(evaluations: list[dict], output_file: Path):
    """
    Create template structure for human input collection.
    
    Structure:
    {
        "qa_id": int,
        "question": str,
        "original_answer": str,
        "probing_questions": [str],
        "participant_id": str,  # To be filled
        "participant_answers": [str],  # To be filled
        "collection_timestamp": str,  # To be filled
        "pre_survey": {  # To be filled
            "confidence": int,  # 1-5 scale
            "authenticity": int,  # 1-5 scale
        },
        "post_survey": {  # To be filled after improvement
            "confidence": int,  # 1-5 scale
            "authenticity": int,  # 1-5 scale
            "recall_test": str,  # To be filled after 1 week
        }
    }
    """
    template_data = []
    
    for eval_data in evaluations:
        if eval_data.get('rating') in ['Error', 'Unknown']:
            continue
        
        qa_id = eval_data['qa_id']
        probing_questions = extract_probing_questions_for_qa(eval_data)
        
        if not probing_questions:
            print(f"Warning: No probing questions found for Q&A {qa_id}")
            continue
        
        template_item = {
            'qa_id': qa_id,
            'question': eval_data['question'],
            'original_answer': eval_data['answer'],
            'initial_rating': eval_data['rating'],
            'probing_questions': probing_questions,
            'participant_id': None,  # To be filled during collection
            'participant_answers': [None] * len(probing_questions),  # To be filled
            'collection_timestamp': None,  # To be filled
            'pre_survey': {
                'confidence': None,  # 1-5 scale: How confident are you in your answer?
                'authenticity': None,  # 1-5 scale: How authentic is your answer?
            },
            'post_survey': {
                'confidence': None,  # 1-5 scale: After improvement, how confident?
                'authenticity': None,  # 1-5 scale: After improvement, how authentic?
                'recall_test': None,  # To be filled after 1 week: Can you recall key details?
            },
        }
        
        template_data.append(template_item)
    
    # Save template
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(template_data, f, indent=2, ensure_ascii=False)
    
    print(f"Human input template saved to: {output_file}")
    print(f"Total Q&A pairs with probing questions: {len(template_data)}")
    
    return template_data


def create_survey_instructions(output_file: Path):
    """
    Create instructions for human input collection.
    This can be used to create a survey (Google Forms, etc.) or custom interface.
    """
    instructions = """
# Human Input Collection Instructions

## Overview
This survey collects human-provided answers to probing questions for Experiment 1.
Each participant will answer probing questions for 2-3 interview answers.

## Survey Structure

For each Q&A pair, participants should:

1. **Read the original question and answer**
2. **Answer each probing question** with:
   - Real, specific details from their own experience
   - Concrete metrics/numbers where applicable
   - Personal decisions and actions (use "I" statements)
   - Authentic reflections and learnings

3. **Complete Pre-Survey**:
   - Confidence (1-5): How confident are you in your original answer?
   - Authenticity (1-5): How authentic does your original answer feel?

4. **After improvement process, complete Post-Survey**:
   - Confidence (1-5): How confident are you in the improved answer?
   - Authenticity (1-5): How authentic does the improved answer feel?

5. **After 1 week, complete Recall Test**:
   - Can you recall key details from your improved answer?
   - Describe what you remember (free text)

## Data Collection Methods

### Option 1: Google Forms / Survey Tool
- Create form with questions from template
- Export responses to JSON format
- Map to template structure

### Option 2: Custom Interface
- Build web interface using template structure
- Store responses directly in JSON format

### Option 3: Manual Collection
- Use template JSON file
- Manually fill in participant responses
- Ensure participant_id is unique for each participant

## Participant Assignment

- Each participant should answer probing questions for 2-3 Q&A pairs
- Distribute Q&A pairs across participants to ensure coverage
- Aim for 20-30 participants total
- Each Q&A pair should have at least 1 participant response

## Data Format

See `exp1_human_input_template.json` for the exact structure.
Each entry should have:
- participant_id: Unique identifier
- participant_answers: List of answers matching probing_questions
- collection_timestamp: ISO format timestamp
- pre_survey: Confidence and authenticity scores
- post_survey: Confidence, authenticity, and recall_test

## Notes

- Ensure participant anonymity (use participant_id, not names)
- Collect consent for data use in research
- Store data securely
- Follow IRB guidelines if applicable
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"Survey instructions saved to: {output_file}")


def create_example_filled_data(template_file: Path, output_file: Path):
    """
    Create example filled data structure to show expected format.
    This is for reference only - actual data should come from participants.
    """
    with open(template_file, 'r', encoding='utf-8') as f:
        template = json.load(f)
    
    # Create example with first 2 items (for demonstration)
    example = []
    for item in template[:2]:  # Just first 2 as example
        example_item = item.copy()
        example_item['participant_id'] = 'EXAMPLE_PARTICIPANT_001'
        example_item['participant_answers'] = [
            'EXAMPLE ANSWER: This is a sample answer to probing question 1...',
            'EXAMPLE ANSWER: This is a sample answer to probing question 2...',
        ]
        example_item['collection_timestamp'] = datetime.now().isoformat()
        example_item['pre_survey'] = {
            'confidence': 3,  # Example: 3/5
            'authenticity': 4,  # Example: 4/5
        }
        example_item['post_survey'] = {
            'confidence': 4,  # Example: 4/5 (improved)
            'authenticity': 5,  # Example: 5/5 (improved)
            'recall_test': 'EXAMPLE: After 1 week, I can recall...',  # To be filled after 1 week
        }
        example.append(example_item)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(example, f, indent=2, ensure_ascii=False)
    
    print(f"Example filled data saved to: {output_file}")
    print("NOTE: This is example data only. Replace with actual participant responses.")


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    results_dir = script_dir / 'exp1_results'
    evaluations_file = results_dir / 'exp1_initial_evaluations.json'
    output_dir = results_dir
    
    if not evaluations_file.exists():
        print(f"Error: {evaluations_file} not found!")
        print("Please run exp1_prepare_dataset.py first.")
        return
    
    print("="*80)
    print("EXPERIMENT 1 - STEP 3: COLLECT HUMAN INPUT (Template Creation)")
    print("="*80)
    
    # Load initial evaluations
    print(f"\nLoading initial evaluations from: {evaluations_file}")
    evaluations = load_initial_evaluations(evaluations_file)
    print(f"Loaded {len(evaluations)} evaluations")
    
    # Create template
    template_file = output_dir / 'exp1_human_input_template.json'
    print(f"\nCreating human input template...")
    template_data = create_human_input_template(evaluations, template_file)
    
    # Create instructions
    instructions_file = output_dir / 'exp1_human_input_instructions.md'
    create_survey_instructions(instructions_file)
    
    # Create example
    example_file = output_dir / 'exp1_human_input_example.json'
    create_example_filled_data(template_file, example_file)
    
    print("\n" + "="*80)
    print("Human input collection template created!")
    print("="*80)
    print("\nNext steps:")
    print("1. Review exp1_human_input_template.json")
    print("2. Use exp1_human_input_instructions.md to create survey/interface")
    print("3. Collect participant responses")
    print("4. Save collected data to exp1_human_input.json")
    print("5. Run exp1_human_in_loop.py to process Group B")


if __name__ == '__main__':
    main()

