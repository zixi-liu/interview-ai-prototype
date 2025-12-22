#!/usr/bin/env python3
"""
Extract questions and answers from README.md and save them to a TOML file.
"""

import re
from pathlib import Path
from html import unescape

def clean_html_text(html_text):
    """Remove HTML tags and decode HTML entities to get plain text."""
    if not html_text:
        return ""
    
    # Remove HTML tags using regex
    text = re.sub(r'<[^>]+>', '', html_text)
    
    # Decode HTML entities
    text = unescape(text)
    
    # Normalize whitespace: replace multiple spaces/newlines with single space
    # but preserve paragraph breaks (double newlines)
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Preserve paragraph breaks
    text = re.sub(r'[ \t]*\n[ \t]*', ' ', text)  # Single newlines to space
    text = text.strip()
    
    return text

def extract_answers(md_file_path):
    """Extract questions and answers from the markdown file."""
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all <details> sections
    details_pattern = r'<details>\s*<summary>(.*?)</summary>\s*(.*?)</details>'
    matches = re.findall(details_pattern, content, re.DOTALL)
    
    questions_answers = []
    
    for summary, answer_content in matches:
        # Extract question from summary (remove <b> tags if present)
        question = clean_html_text(summary)
        
        # Extract answer content
        answer = clean_html_text(answer_content)
        
        # Only add if both question and answer are non-empty
        # Skip answers that are essentially empty (only whitespace or empty tags)
        if question and answer and answer.strip():
            questions_answers.append({
                'question': question,
                'answer': answer
            })
    
    return questions_answers

def escape_toml_multiline_string(s):
    """Escape a string for TOML multiline string (triple quotes)."""
    # If string contains triple quotes, we need to escape them
    # TOML doesn't support escaping in multiline strings, so we use literal strings
    if '"""' in s:
        # Use literal multiline string (single quotes)
        s = s.replace("'", "''")  # Escape single quotes
        return f"'''{s}'''"
    else:
        return f'"""{s}"""'

def save_to_toml(data, output_file):
    """Save questions and answers to a TOML file using array of tables format."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('# Questions and Answers extracted from README.md\n\n')
        
        for idx, qa in enumerate(data, start=1):
            f.write('[[questions]]\n')
            f.write(f'id = {idx}\n')
            
            # Escape question
            question_str = escape_toml_multiline_string(qa["question"])
            f.write(f'question = {question_str}\n')
            
            # Escape answer
            answer_str = escape_toml_multiline_string(qa["answer"])
            f.write(f'answer = {answer_str}\n')
            
            f.write('\n')

def main():
    # Get the script directory and construct paths
    # Script is in the same directory as README.md
    script_dir = Path(__file__).parent
    md_file = script_dir / 'README.md'
    output_file = script_dir / 'answers.toml'
    
    if not md_file.exists():
        print(f"Error: {md_file} not found!")
        return
    
    print(f"Reading from: {md_file}")
    
    # Extract questions and answers
    qa_data = extract_answers(md_file)
    
    print(f"Found {len(qa_data)} questions and answers")
    
    # Save to TOML
    save_to_toml(qa_data, output_file)
    
    print(f"Saved to: {output_file}")

if __name__ == '__main__':
    main()

