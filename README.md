# Simple Interview Analyzer

A minimal AI-powered interview analyzer that provides feedback on interview transcriptions using LiteLLM.

## Features

- Analyzes interview transcriptions
- Provides hiring feedback (Strong Hire / Weak Hire / No Hire)
- Supports multiple LLM providers via LiteLLM (OpenAI, Anthropic, etc.)

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up API key

Create a `.env` file:

```bash
OPENAI_API_KEY=your_api_key_here
```

### 3. Run

```bash
python interview_analyzer.py
```

## Usage

```python
from interview_analyzer import InterviewAnalyzer

analyzer = InterviewAnalyzer()
feedback = analyzer.analyze(transcription, role="Software Engineer")
print(feedback)
```

## Supported Models

Any model supported by LiteLLM:
- OpenAI: `gpt-4o-mini`, `gpt-4o`
- Anthropic: `claude-3-5-sonnet-20241022`
- Google: `gemini-1.5-pro`

To use a different model:

```python
analyzer = InterviewAnalyzer(model="claude-3-5-sonnet-20241022")
```

## Project Structure

```
interview-ai-prototype/
├── interview_analyzer.py    # Main analyzer (simple version)
├── example_usage.py         # Simple example
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## License

MIT
