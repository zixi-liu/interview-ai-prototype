# Human-in-the-Loop Self-Improvement User Guide

> **Language**: [中文](self_improve_human_input.zh.md) | [English](self_improve_human_input.en.md)

## Overview

`self_improve_human_input.py` is a self-improvement tool for Behavioral Question (BQ) interview answers. It uses a **Human-in-the-Loop** approach to help you continuously optimize your interview answers until they reach a "Strong Hire" rating or reach the maximum number of iterations.

### Key Features

1. **Feedback-Based Iterative Improvement**: Extracts questions and initial answers from existing feedback files, then iteratively optimizes them
2. **Intelligent Probing Question Extraction**: Automatically extracts questions that need further clarification from feedback
3. **Human Input of Real Details**: Provides real, specific personal experience details by answering probing questions
4. **Automatic Answer Generation**: AI incorporates your real answers into the original answer to generate a more specific and persuasive improved version
5. **Continuous Evaluation and Optimization**: Re-evaluates after each improvement round until Strong Hire is achieved or max iterations are reached

---

## How It Works

### Improvement Process

```
Initial Answer
   ↓
Extract question and answer from feedback file
   ↓
Evaluate current answer → Generate feedback and probing questions
   ↓
Check if Strong Hire achieved?
   ├─ Yes → Complete ✅
   └─ No → Extract probing questions
       ↓
    User answers probing questions (provide real details)
       ↓
    Generate improved answer based on user input
       ↓
    Repeat evaluation... (up to max_iterations times)
```

### Key Components

1. **`HumanInLoopImprove` Class** (located in `advance/self_improve.py`)
   - Manages the logic for the entire improvement loop
   - Handles iteration count and state
   - Coordinates evaluation, question extraction, and answer improvement

2. **Probing Question Extraction**
   - Automatically identifies questions that need further clarification from feedback
   - Usually focuses on: Ownership (personal contribution), Metrics (specific indicators), Impact, Reflection, etc.

3. **Answer Improvement Mechanism**
   - Combines your real answers with the original answer
   - Generates a more specific and persuasive improved version
   - Maintains STAR method structure (Situation, Task, Action, Result)

---

## Usage

### Prerequisites

1. **Prepare Feedback File**
   - Need an existing feedback file (`.md` format)
   - The feedback file should contain: Question, Answer, Feedback, and Rating
   - Default: `feedbacks/20251129-Leaning_No_Hire_4.md`

2. **Install Dependencies**
   - Ensure all required Python packages are installed (see `requirements.txt`)

### Mode 1: Interactive Mode (Recommended)

Interactive mode prompts you in real-time to answer questions, suitable for real usage scenarios.

#### Steps to Run

1. **Modify Configuration** (if needed)

   ```python
   improver = HumanInLoopImprove(
       feedback_file=FEEDBACK_FILE,  # Path to feedback file
       level="Junior-Mid",            # Interview level: Junior-Mid, Mid-Senior, Senior, etc.
       max_iterations=3,              # Maximum number of iterations
   )
   ```

2. **Run the Program**

   ```python
   async def main():
       improver = HumanInLoopImprove(
           feedback_file=FEEDBACK_FILE,
           level="Junior-Mid",
           max_iterations=3,
       )
       
       result = await improver.run_interactive()
       
       # View results
       print(f"Status: {result['status']}")
       print(f"Iterations: {result['iterations']}")
       print(f"Final Answer:\n{result['final_answer']}")
   ```

3. **Answer Questions**

   The program will prompt you step by step:
   ```
   ============================================================
   Iteration 1
   ============================================================
   
   Evaluating answer...
   
   ----------------------------------------
   Please answer these probing questions to improve your answer:
   ----------------------------------------
   
   Q1: What was YOUR specific decision that changed the outcome?
   > [Enter your answer here]
   
   Q2: What mistake did you make, and what would you do differently?
   > [Enter your answer here]
   
   ...
   ```

4. **View Improvement Results**

   After each iteration, the program will display:
   - Improved answer
   - Current rating
   - Whether Strong Hire has been achieved

#### Complete Example Code

```python
import asyncio
from pathlib import Path
from advance.self_improve import HumanInLoopImprove

FEEDBACK_FILE = Path("feedbacks") / "20251129-Leaning_No_Hire_4.md"

async def main():
    improver = HumanInLoopImprove(
        feedback_file=FEEDBACK_FILE,
        level="Junior-Mid",
        max_iterations=3,
    )
    
    print(f"Original Question: {await improver.question()}")
    print(f"\nOriginal Answer:\n{await improver.answer()}")
    
    result = await improver.run_interactive()
    
    print("\n" + "=" * 80)
    print("Final Result")
    print("=" * 80)
    print(f"Status: {result['status']}")  # strong_hire or max_iterations
    print(f"Iterations: {result['iterations']}")
    print(f"\nFinal Answer:\n{result['final_answer']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Mode 2: Predefined Answers Mode (Testing/Demo)

Predefined answers mode uses a preset list of answers, suitable for testing and demonstration scenarios.

#### Use Cases

- Automated testing
- Feature demonstrations
- Batch processing of multiple answers

#### Steps to Run

1. **Prepare Predefined Answers**

   ```python
   PREDEFINED_PROBING_ANSWERS = [
       # Answers for iteration 1
       [
           "Answer to first probing question...",
           "Answer to second probing question...",
           "Answer to third probing question...",
           # ... more answers
       ],
       # Answers for iteration 2 (if needed)
       [
           "Answer to first question in iteration 2...",
           # ...
       ],
   ]
   ```

   **Note**: The order of answers must match the order of probing questions.

2. **Run the Program**

   ```python
   async def main():
       improver = HumanInLoopImprove(
           feedback_file=FEEDBACK_FILE,
           level="Junior-Mid",
           max_iterations=2,
       )
       
       result = await improver.run_with_predefined_answers(
           PREDEFINED_PROBING_ANSWERS
       )
       
       print(f"Status: {result['status']}")
       print(f"Iterations: {result['iterations']}")
       print(f"\nFinal Answer:\n{result['final_answer']}")
   ```

3. **View Complete History**

   The result dictionary contains complete improvement history:
   - `answer_history`: All versions of the answer (including initial version)
   - `feedback_history`: Feedback and red flag checks for each iteration

---

## Configuration Options

### `HumanInLoopImprove` Initialization Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `feedback_file` | `Path \| None` | `None` | Path to the feedback file |
| `feedback_full_content` | `str \| None` | `None` | Full content of the feedback file (as string) |
| `level` | `str` | `"Junior-Mid"` | Interview level, affects evaluation criteria. Options: `"Junior-Mid"`, `"Mid-Senior"`, `"Senior"`, `"Staff"`, etc. |
| `max_iterations` | `int` | `3` | Maximum number of iterations. The process will stop after this number is reached even if Strong Hire is not achieved |

### Return Value Structure

#### Dictionary returned by `run_interactive()` and `run_with_predefined_answers()`:

```python
{
    "status": str,              # "strong_hire" or "max_iterations" or "completed"
    "final_answer": str,        # Final improved answer
    "iterations": int,          # Actual number of iterations
    "answer_history": list,     # Answer history: [initial answer, iteration 1, iteration 2, ...]
    "feedback_history": list,   # Feedback history: [{"feedback": "...", "red_flag": "..."}, ...]
}
```

---

## Probing Question Types

The system automatically extracts probing questions from feedback. Common types include:

### 1. Ownership (Personal Contribution)
- "What was YOUR specific decision that changed the outcome?"
- "What role did you play in shaping the final decision?"
- "What was your personal contribution vs. the team's?"

### 2. Reflection
- "What mistake did you make, and what would you do differently?"
- "What would you do if faced with a similar situation again?"

### 3. Metrics (Specific Indicators)
- "What specific metrics can you share about YOUR contribution?"
- "Can you quantify the impact with numbers?"

### 4. Impact
- "Can you describe a situation where your actions directly influenced the outcome?"
- "What was the tangible result of your intervention?"

### 5. Clarity
- "How did you ensure stakeholders were aligned on the data?"
- "What specific steps did you take to communicate effectively?"

---

## Best Practices

### 1. Tips for Answering Probing Questions

✅ **Good answers should:**
- **Be specific**: Provide specific numbers, times, people, decisions
- **Use first-person perspective**: Emphasize what "I" did, not what "we" did
- **Be authentic**: Based on real experiences and details
- **Be structured**: Organize answers using the STAR method

✅ **Example (Good Answer):**
```
My specific decision was to propose a 60/40 resource allocation ratio instead of 
the 50/50 that everyone was debating. I calculated this myself by analyzing both 
projects' critical paths. I presented this to my manager first, got her buy-in, 
then brought it to the group meeting as a concrete proposal rather than opening 
another debate.
```

❌ **Avoid:**
- Overly general descriptions ("I did a lot of work")
- Team perspective ("We solved the problem together")
- Lack of specific details ("The results were good")

### 2. Iteration Strategy

- **Round 1**: Focus on Ownership and Impact, provide core personal contribution details
- **Round 2**: Add Metrics and Clarity, include specific data and communication details
- **Round 3**: Enhance Reflection, demonstrate learning ability and self-improvement awareness

### 3. Knowing When to Stop

The program will automatically stop in the following cases:
- ✅ Strong Hire rating achieved with no red flags
- ⏱️ Maximum iterations reached

**Recommendations**:
- If rating doesn't improve for 2 consecutive rounds, consider stopping manually
- If the answer is already very detailed and specific, you can accept the current Strong Hire

### 4. File Management

- After each iteration, improved answers are automatically saved to the `feedbacks/` directory
- File naming format: `YYYYMMDD-Rating_N.md`
- Keep historical versions for comparison and analysis

---

## Complete Example

### Example Scenario

Suppose you have a BQ answer about "solving a conflict" with an initial rating of "Leaning_No_Hire".

#### Step 1: Initial Answer
```
The original answer describes using a data-driven approach to resolve resource allocation 
conflicts, but lacks details about personal specific contributions.
```

#### Step 2: First Round Improvement

**Probing Questions:**
1. "What was YOUR specific decision that changed the outcome?"
2. "What mistake did you make, and what would you do differently?"

**Your Answers:**
1. "I proposed a 60/40 resource allocation ratio and reached this conclusion by analyzing critical paths."
2. "My mistake was not communicating privately with the infrastructure lead before the meeting, which made him feel surprised during the meeting."

**The improved answer** will automatically include these details, making the answer more specific and credible.

#### Step 3: Evaluation and Continuation

- If rating improves to "Hire", continue to the next round
- If "Strong Hire" is achieved, complete ✅

---

## Frequently Asked Questions (FAQ)

### Q1: What is the required feedback file format?

The feedback file should contain the following sections:
- **Question**: Interview question
- **Answer**: Original answer
- **Feedback**: Detailed feedback (including probing questions)
- **Rating**: Rating (e.g., Leaning_No_Hire, Hire, Strong Hire, etc.)

### Q2: How do I generate an initial feedback file?

You can use `examples/solve_conflict.py` or other example scripts to generate initial feedback.

### Q3: Can I skip some probing questions?

In interactive mode, you can enter an empty string to skip a question, but this may affect improvement effectiveness. It's recommended to answer all questions if possible.

### Q4: How to handle multiple iterations?

Each iteration is independent:
- Round 1 uses feedback from the feedback file
- Subsequent rounds use feedback generated from new evaluations
- Answers continue to improve and accumulate details

### Q5: How to adjust evaluation strictness?

Control through the `level` parameter:
- `"Junior-Mid"`: More lenient standards
- `"Senior"`: Stricter standards
- `"Staff"`: Most strict standards

---

## Technical Details

### Dependencies

- `advance.self_improve.HumanInLoopImprove`: Core improvement logic
- `interview_analyzer.InterviewAnalyzer`: AI evaluation and analysis
- `prompts.BQAnswer`, `prompts.BQQuestions`, `prompts.BQFeedback`: Prompt templates
- `utils.FeedbackParser`: Feedback parsing and question extraction

### Async Processing

All methods are asynchronous (`async`), and need to be run using `asyncio.run()`.

---

## Related Files

- **Example File**: `examples/self_improve_human_input.py`
- **Core Implementation**: `advance/self_improve.py`
- **Prompt Templates**: `prompts.py`
- **Utility Functions**: `utils.py`
- **Feedback File Example**: `feedbacks/20251129-Leaning_No_Hire_4.md`

---

## Summary

`self_improve_human_input.py` is a powerful tool that combines AI evaluation with human input to help you create better, more specific BQ answers. The key is to:

1. **Provide authentic details**: Be as specific and authentic as possible when answering probing questions
2. **Iterate and improve**: Don't expect perfection in one go; multiple iterations will continuously improve quality
3. **Focus on personal contribution**: Emphasize what "I" did, not what the team did
4. **Be patient**: Strong Hire may take 2-3 iterations to achieve

Good luck with your interviews! 🚀

