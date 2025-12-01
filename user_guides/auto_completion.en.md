# Auto-Completion Feature User Guide

> **Language**: [中文](auto_completion.zh.md) | [English](auto_completion.en.md)

## Overview

The `auto_completion` feature provides intelligent completion suggestions for interview answers. It helps candidates complete their self-introductions and behavioral question (BQ) answers by analyzing partial input and generating up to 3 recommended completion options based on FAANG interview standards.

### Key Features

1. **Smart Completeness Detection**: Automatically detects if the input is structurally complete (has a clear ending) or content-complete (covers all required elements)
2. **Context-Aware Suggestions**: Generates completion suggestions tailored to the specific role, company, and interview level
3. **FAANG Standards Compliance**: All suggestions follow FAANG interview best practices
4. **Two Scenarios Supported**: 
   - Self-introduction completion
   - Behavioral question (BQ) answer completion
5. **Top 3 Recommendations**: Provides the most relevant completion options with explanations

---

## How It Works

### Completion Process

```
User Input (Partial Text)
   ↓
Check if structurally complete (has clear ending)?
   ├─ Yes → Return is_complete: true ✅
   └─ No → Check content completeness
       ├─ All elements present → Return is_complete: true ✅
       └─ Missing elements → Generate TOP 3 completion suggestions
           ↓
        Return suggestions with reasons and confidence
```

### Completeness Detection Logic

The system uses a **two-priority** approach:

1. **Priority 1: Structural Completeness**
   - Checks if the last sentence clearly indicates the answer has ended
   - Recognizes closing phrases like: "Thank you", "I'm looking forward to...", "In conclusion", "Overall", etc.
   - If structurally complete → Returns `is_complete: true` immediately
   - Suggests evaluation to ensure all key elements are covered

2. **Priority 2: Content Completeness**
   - For self-intro: Checks for Background, Experience, Achievements, Motivation, Connection
   - For BQ answers: Checks for STAR elements (Situation, Task, Action, Result) plus level-specific requirements
   - If all elements present → Returns `is_complete: true`

### Key Components

1. **`AutoCompletionEngine` Class** (located in `advance/auto_completion.py`)
   - Main engine for generating completion suggestions
   - Handles both self-intro and BQ answer scenarios
   - Uses LLM to analyze and generate suggestions

2. **Completion Suggestions**
   - Up to 3 recommended completion options
   - Each option includes:
     * `text`: The completion text
     * `reason`: Why this completion is recommended
     * `confidence`: Confidence level (0-100%)

3. **Response Format**
   - Returns JSON object with either:
     * `is_complete: true` + `message` (if complete)
     * `is_complete: false` + `completions` array (if incomplete)

---

## Usage

### Prerequisites

1. **Install Dependencies**
   - Ensure all required Python packages are installed (see `requirements.txt`)
   - Requires `litellm` for LLM access

2. **Environment Setup**
   - Set up your `.env` file with API keys if needed

### Basic Usage

#### Example 1: Self-Introduction Completion

```python
import asyncio
from advance.auto_completion import AutoCompletionEngine

async def main():
    engine = AutoCompletionEngine()
    
    partial_text = """Hi, I'm John, and I'm a software engineer with 5 years of experience. 
    I've worked on several projects involving distributed systems and microservices."""
    
    result = await engine.complete_self_intro(
        partial_text=partial_text,
        role="Senior Software Engineer",
        company="Google"
    )
    
    if result.get("is_complete"):
        print(f"✅ {result['message']}")
    else:
        print("📝 Completion Suggestions:")
        for i, comp in enumerate(result.get("completions", []), 1):
            print(f"\n{i}. {comp['text']}")
            print(f"   Reason: {comp['reason']}")

asyncio.run(main())
```

#### Example 2: BQ Answer Completion

```python
import asyncio
from advance.auto_completion import AutoCompletionEngine

async def main():
    engine = AutoCompletionEngine()
    
    question = "Tell me about your most challenging project."
    partial_text = """I was leading a team to migrate our monolithic application 
    to a microservices architecture. The challenge was that we had to do this migration 
    while maintaining 99.9% uptime and without disrupting our users.
    
    My task was to design and execute a zero-downtime migration strategy."""
    
    result = await engine.complete_bq_answer(
        partial_text=partial_text,
        question=question,
        role="Senior Software Engineer",
        level="Senior"
    )
    
    if result.get("is_complete"):
        print(f"✅ {result['message']}")
    else:
        print("📝 Completion Suggestions:")
        for i, comp in enumerate(result.get("completions", []), 1):
            print(f"\n{i}. {comp['text']}")
            print(f"   Reason: {comp['reason']}")

asyncio.run(main())
```

### API Reference

#### `AutoCompletionEngine`

**Initialization**

```python
engine = AutoCompletionEngine(model="gpt-4o-mini")
```

**Parameters:**
- `model` (str, optional): LLM model to use. Default: `"gpt-4o-mini"`

#### `complete_self_intro()`

Generate completion suggestions for self-introduction.

```python
async def complete_self_intro(
    partial_text: str,
    role: str = "Software Engineer",
    company: str = "FAANG"
) -> Dict[str, Any]
```

**Parameters:**
- `partial_text` (str, required): Partial self-introduction text
- `role` (str, optional): Job role. Default: `"Software Engineer"`
- `company` (str, optional): Company name. Default: `"FAANG"`

**Returns:**
- `Dict[str, Any]`: JSON object with either:
  - `{"is_complete": true, "message": "..."}` if complete
  - `{"is_complete": false, "completions": [...]}` if incomplete

#### `complete_bq_answer()`

Generate completion suggestions for BQ answer.

```python
async def complete_bq_answer(
    partial_text: str,
    question: str,
    role: str = "Software Engineer",
    level: str = "Senior"
) -> Dict[str, Any]
```

**Parameters:**
- `partial_text` (str, required): Partial BQ answer text
- `question` (str, required): The behavioral question
- `role` (str, optional): Job role. Default: `"Software Engineer"`
- `level` (str, optional): Candidate level. Default: `"Senior"`. Options: `"Junior-Mid"`, `"Senior"`, `"Staff"`

**Returns:**
- `Dict[str, Any]`: JSON object with either:
  - `{"is_complete": true, "message": "..."}` if complete
  - `{"is_complete": false, "completions": [...]}` if incomplete

#### `complete()` (Generic Method)

Generic method for both scenarios.

```python
async def complete(
    scenario: Literal["self-intro", "bq answer"],
    partial_text: str,
    role: str = "Software Engineer",
    company: str = "FAANG",
    question: Optional[str] = None,
    level: str = "Senior"
) -> Dict[str, Any]
```

**Parameters:**
- `scenario` (str, required): Either `"self-intro"` or `"bq answer"`
- `partial_text` (str, required): Partial text input
- `role` (str, optional): Job role
- `company` (str, optional): Company name (for self-intro)
- `question` (str, optional): BQ question (required for `"bq answer"` scenario)
- `level` (str, optional): Candidate level (for BQ answers)

---

## Response Format

### Complete Response

When the input is complete:

```json
{
  "is_complete": true,
  "message": "Your self-introduction is already complete and strong."
}
```

### Incomplete Response

When the input needs completion:

```json
{
  "is_complete": false,
  "reason": "why the introduction is completed or not",
  "confidence": "85%",
  "completions": [
    {
      "text": "completion option 1",
      "reason": "why this is recommended",
      "confidence": "90%"
    },
    {
      "text": "completion option 2",
      "reason": "why this is recommended",
      "confidence": "85%"
    },
    {
      "text": "completion option 3",
      "reason": "why this is recommended",
      "confidence": "80%"
    }
  ]
}
```

### Error Response

If JSON parsing fails:

```json
{
  "is_complete": false,
  "error": "Failed to parse LLM response as JSON: ...",
  "raw_response": "original LLM response text"
}
```

---

## Best Practices

### For Self-Introduction

1. **Include Key Elements**:
   - Background and experience level
   - Relevant work experience
   - Key achievements with metrics
   - Motivation for the role/company
   - Connection to the role/company

2. **Keep It Concise**: Aim for 1-2 minutes when spoken

3. **Be Specific**: Use concrete examples and metrics

4. **End Clearly**: Use closing phrases to indicate completion

### For BQ Answers

1. **Follow STAR Method**:
   - **Situation**: Clear context and background
   - **Task**: Specific challenge or goal
   - **Action**: Detailed actions with clear ownership
   - **Result**: Measurable outcomes and impact

2. **Level-Specific Requirements**:
   - **Junior-Mid**: Focus on clarity and structured thinking
   - **Senior**: Show ownership, cross-functional collaboration, execution
   - **Staff**: Demonstrate influence, multi-team strategy, systemic thinking

3. **Include Metrics**: Always include quantifiable results

4. **Show Ownership**: Use "I" statements, not just "we"

5. **Add Reflection**: Include learnings when appropriate

---

## Examples

See `examples/auto_completion_example.py` for complete working examples including:

1. Self-introduction completion with partial input
2. BQ answer completion with STAR structure
3. Testing with complete answers (should return `is_complete: true`)

---

## Troubleshooting

### Common Issues

1. **JSON Parsing Errors**
   - The system uses regex to extract JSON from LLM response
   - If parsing fails, check the `raw_response` field in error output
   - The LLM should output valid JSON according to the prompt

2. **No Completions Generated**
   - Check if the input is already complete (returns `is_complete: true`)
   - Ensure the input is actually incomplete (not just short)

3. **Low Quality Suggestions**
   - Try providing more context in `partial_text`
   - Specify the correct `role` and `level` parameters
   - Ensure the input follows interview answer structure

---

## Integration

### CLI Integration

You can integrate this feature into the CLI by adding a new command:

```python
# In cli.py
from advance.auto_completion import AutoCompletionEngine

async def auto_complete_command(scenario, text, **kwargs):
    engine = AutoCompletionEngine()
    result = await engine.complete(scenario, text, **kwargs)
    return result
```

### Web API Integration

For web API integration, create an endpoint:

```python
# In app.py
from advance.auto_completion import AutoCompletionEngine

@app.post("/api/auto-complete")
async def auto_complete(
    scenario: str,
    partial_text: str,
    role: str = "Software Engineer",
    company: str = "FAANG",
    question: Optional[str] = None,
    level: str = "Senior"
):
    engine = AutoCompletionEngine()
    result = await engine.complete(
        scenario=scenario,
        partial_text=partial_text,
        role=role,
        company=company,
        question=question,
        level=level
    )
    return result
```

---

## Technical Details

### LLM Model

- Default model: `gpt-4o-mini`
- Can be customized via `AutoCompletionEngine(model="...")`
- Uses streaming for better performance

### JSON Extraction

- Uses regex pattern `r"\{[\s\S]*\}"` to extract JSON from response
- Handles cases where LLM adds extra text before/after JSON
- Falls back to parsing entire response if no JSON block found

### Error Handling

- Catches `JSONDecodeError` and returns error info
- Preserves `raw_response` for debugging
- Returns structured error response instead of raising exceptions

---

## Related Features

- **Self-Improvement**: Use `advance/self_improve.py` to iteratively improve answers
- **Story Builder**: Use `advance/story_builder.py` to build BQ stories from scratch
- **Interview Analyzer**: Use `interview_analyzer.py` to analyze complete answers

---

## Support

For issues or questions:
1. Check the examples in `examples/auto_completion_example.py`
2. Review the prompt templates in `prompts.py` (class `AutoCompletion`)
3. Check error messages in the `error` and `raw_response` fields

