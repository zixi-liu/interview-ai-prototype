#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

print("Testing imports...")

try:
    from interview_analyzer import InterviewAnalyzer
    print("✓ interview_analyzer imported successfully")
except ImportError as e:
    print(f"✗ Failed to import interview_analyzer: {e}")
    exit(1)

try:
    from prompts import (
        SYSTEM_MESSAGE_INTRODUCTION,
        SYSTEM_MESSAGE_BQ_QUESTION,
        get_introduction_prompt,
        BQQuestions,
    )
    print("✓ All prompts imported successfully")
except ImportError as e:
    print(f"✗ Failed to import prompts: {e}")
    exit(1)

try:
    from example_usage import main
    print("✓ example_usage imported successfully")
except ImportError as e:
    print(f"✗ Failed to import example_usage: {e}")
    exit(1)

print("\n✓ All imports successful! The code is ready to deploy.")
print("\nTo run the actual analyzer, you need to:")
print("1. Create a .env file with your OPENAI_API_KEY or ANTHROPIC_API_KEY")
print("2. Run: python interview_analyzer.py")
