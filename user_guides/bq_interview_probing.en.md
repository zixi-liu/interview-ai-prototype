# BQ Interview Probing User Guide

> **Language**: [中文](bq_interview_probing.zh.md) | [English](bq_interview_probing.en.md)

## Overview

The BQ Interview Probing feature simulates a real FAANG behavioral interview by conducting follow-up questions after your initial answer. It uses an **intelligent probing agent** with a **learned stop policy** to know exactly when to stop asking questions - just like a real interviewer.

### Key Features

1. **Realistic Interview Simulation**: Mimics how FAANG interviewers probe for specifics
2. **Learned Stop Policy**: ML model trained on interview data decides when to stop (88% accuracy)
3. **Response Classification**: Automatically classifies your responses (GOOD, VAGUE, PARTIAL, etc.)
4. **Gap Tracking**: Identifies and tracks gaps in your answer that need addressing
5. **Level-Aware Probing**: Adjusts expectations based on Junior-Mid / Senior / Staff level

---

## How It Works

### Probing Flow

```
User Input: BQ Question + Initial Answer + Level
              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Initial Evaluation                                     │
│  - Evaluate answer against level expectations                   │
│  - Identify gaps (missing metrics, vague ownership, etc.)       │
│  - Generate initial probing questions                           │
│  - Assign preliminary rating                                    │
└─────────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Probing Loop                                           │
│                                                                 │
│  For each turn:                                                 │
│    1. Present probing question to user                          │
│    2. User responds                                             │
│    3. Classify response type:                                   │
│       • ANSWER_GOOD - Specific, with metrics/ownership          │
│       • ANSWER_PARTIAL - Some detail but incomplete             │
│       • ANSWER_VAGUE - Generic, lacks specifics                 │
│       • ASKS_QUESTION - User needs clarification                │
│       • SAYS_IDK - User doesn't have an answer                  │
│       • PUSHBACK - User challenges the question                 │
│                                                                 │
│    4. ══► LEARNED STOP POLICY ◄══                               │
│       │  Should we STOP or CONTINUE?                            │
│       │                                                         │
│       │  Inputs (10 features):                                  │
│       │  • gaps_remaining, gaps_resolved                        │
│       │  • turn_count, good_responses, vague_responses          │
│       │  • idk_count, pushback_count, friction_ratio            │
│       │  • is_senior, is_staff                                  │
│       │                                                         │
│       │  STOP when:                                              │
│       │  • Enough good responses gathered                       │
│       │  • High friction (candidate can't answer)               │
│       │  • All gaps addressed                                   │
│       │  • Maximum turns reached                                │
│                                                                 │
│    5. If CONTINUE → Generate contextual follow-up               │
│       If STOP → End probing                                     │
└─────────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Final Assessment                                       │
│  - Compile all Q&A pairs                                        │
│  - Update rating based on probing results                       │
│  - Generate comprehensive feedback                              │
└─────────────────────────────────────────────────────────────────┘
```

### The Learned Stop Policy

The stop policy uses a **logistic regression model** trained on 30+ synthetic interview sessions with teacher labels. It achieves **88% accuracy** vs 60% for rule-based heuristics.

#### Feature Importances

| Feature | Weight | Interpretation |
|---------|--------|----------------|
| `good_responses` | +3.04 | More substantive answers → stop |
| `turn_count` | +0.99 | Later in conversation → stop |
| `gaps_resolved` | +0.97 | More gaps addressed → stop |
| `is_senior` | +0.77 | Senior level → stop earlier |
| `vague_responses` | +0.68 | Many vague answers → stop (diminishing returns) |
| `gaps_remaining` | -0.66 | Fewer gaps left → stop |
| `pushback_count` | +0.36 | Candidate pushback → stop |

#### Example Decision

```
State: Turn 4, good_responses=2, gaps_remaining=1, friction=10%

Learned Policy: STOP (92% confidence)
Reasoning: "Gathered 2 substantive responses, only 1 minor gap remains"
```

---

## Usage

### Prerequisites

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API Keys**
   - Create `.env` file with your OpenAI API key
   ```
   OPENAI_API_KEY=sk-...
   ```

### CLI Usage

#### Analyze a BQ Question

```bash
python main.py
```

Then select option `[2] Practice BQ Question` and choose a question.

#### Programmatic Usage

```python
import asyncio
from interview_analyzer import AgenticInterviewer
from prompts import BQQuestions

async def main():
    question = "Tell me about a time you faced a challenging project."
    answer = """
    I led a migration from monolith to microservices at my company.
    It was challenging because we had to maintain uptime while doing the migration.
    I worked with the team to plan the migration in phases.
    We successfully completed it and improved system reliability.
    """
    level = "Senior"

    # Step 1: Get initial evaluation
    prompt = BQQuestions.real_interview(
        question=question,
        answer=answer,
        level=level
    )
    # ... call LLM to get evaluation ...

    # Step 2: Initialize probing agent
    interviewer = AgenticInterviewer(model="gpt-4o-mini", max_turns=8)
    result = interviewer.initialize(
        question=question,
        answer=answer,
        evaluation=evaluation,
        level=level
    )

    if result["action"] == "STOP":
        print("No probing needed - answer is complete!")
        return

    # Step 3: Probing loop
    while interviewer.should_continue():
        probe = interviewer.get_current_probe()
        print(f"\nInterviewer: {probe}")

        user_response = input("Your response: ")

        decision = await interviewer.step(user_response)

        if decision["action"] == "STOP":
            print("\nInterviewer: Thank you, I have enough information.")
            break

    # Step 4: Get final Q&A pairs
    qa_pairs = interviewer.get_qa_pairs()
    for q, a in qa_pairs:
        print(f"Q: {q}")
        print(f"A: {a}\n")

asyncio.run(main())
```

### API Reference

#### `AgenticInterviewer`

**Initialization**

```python
interviewer = AgenticInterviewer(
    model="gpt-4o-mini",  # LLM model to use
    max_turns=8           # Maximum probing turns
)
```

**Methods**

| Method | Description |
|--------|-------------|
| `initialize(question, answer, evaluation, level)` | Set up the interview session |
| `should_continue()` | Check if more probing is needed |
| `get_current_probe()` | Get the current question to ask |
| `step(user_response)` | Process user response and decide next action |
| `get_qa_pairs()` | Get all Q&A pairs from the session |
| `get_decisions()` | Get all decision history |

**`step()` Return Value**

```python
{
    "response_type": "ANSWER_GOOD",  # Classification of user response
    "action": "PROBE_SAME",          # PROBE_SAME, PROBE_NEXT, STOP, REDIRECT
    "agent_message": "...",          # Next question or closing message
    "reasoning": "...",              # Why this decision was made
    "classification": {
        "response_type": "ANSWER_GOOD",
        "confidence": "HIGH",
        "runner_up_type": null
    },
    "state_update": {
        "gaps_resolved": ["ownership"],
        "gaps_unresolvable": []
    }
}
```

---

## Response Types

The system classifies each user response:

| Type | Description | Example |
|------|-------------|---------|
| `ANSWER_GOOD` | Specific, with metrics/ownership | "I personally reduced latency by 40% by..." |
| `ANSWER_PARTIAL` | Some detail but incomplete | "I worked on the optimization..." |
| `ANSWER_VAGUE` | Generic, lacks specifics | "We improved things significantly" |
| `ASKS_QUESTION` | User needs clarification | "Do you mean technical or people challenges?" |
| `SAYS_IDK` | User doesn't have an answer | "I don't have a good example for that" |
| `PUSHBACK` | User challenges the question | "I don't think that's relevant" |
| `OFF_TOPIC` | User goes off-topic | "Speaking of which, I once..." |
| `NEW_INFO` | Reveals something new | "Actually, I forgot to mention..." |

---

## Example Session

```
Question: Tell me about a time you worked outside your comfort zone.

Initial Answer: I led a cross-functional project involving multiple departments...
[Missing: specific conflict examples, metrics, personal ownership]

───────────────────────────────────────────────────────────────────
Turn 1
───────────────────────────────────────────────────────────────────
Interviewer: Can you provide a specific example of a conflict you
             encountered and how you resolved it?

You: We had some disagreements about priorities between teams...

Classification: ANSWER_VAGUE (lacks specifics)
Policy Decision: CONTINUE (gaps remain, low friction)

───────────────────────────────────────────────────────────────────
Turn 2
───────────────────────────────────────────────────────────────────
Interviewer: Can you walk me through a specific disagreement?
             What was the conflict about and what did YOU do?

You: The marketing team wanted feature A, dev wanted feature B.
     I proposed a 60/40 split based on my analysis of critical paths.
     I got buy-in from my manager first, then presented to the group.

Classification: ANSWER_GOOD (specific, shows ownership)
Policy Decision: CONTINUE (more gaps to address)

───────────────────────────────────────────────────────────────────
Turn 3
───────────────────────────────────────────────────────────────────
Interviewer: What was the outcome? Do you have metrics on the impact?

You: The project delivered 2 weeks early. Team satisfaction went from
     6.2 to 8.1 in our quarterly survey. I learned to always do
     1:1s before bringing proposals to group meetings.

Classification: ANSWER_GOOD (metrics, reflection)
Policy Decision: STOP (88% confidence) ← Learned policy triggers

Interviewer: Thank you, I have enough information now.
```

---

## Best Practices

### For Users

1. **Be Specific**: Include numbers, dates, names, technologies
2. **Show Ownership**: Use "I" not "we" - what did YOU do?
3. **Follow STAR**: Situation → Task → Action → Result
4. **Include Metrics**: Quantify your impact whenever possible
5. **Reflect**: Share what you learned and would do differently

### For Developers

1. **Retrain Periodically**: Run `--train` after collecting more sessions
2. **Monitor Accuracy**: Check if policy is stopping too early/late
3. **Add Friction Examples**: Generate more IDK/PUSHBACK sessions for balance

---

## Troubleshooting

### Common Issues

1. **Policy Always Says CONTINUE**
   - Check if model file exists: `policy/stop_policy_model.pkl`
   - Verify model loaded: `interviewer.stop_policy.learned.model_loaded`

2. **Low Quality Probing Questions**
   - Ensure initial evaluation identified correct gaps
   - Check `level` parameter matches candidate experience

3. **Probing Ends Too Early**
   - Confidence threshold may be too low (default: 0.7)
   - Adjust in `HybridStopPolicy.confidence_threshold`

---

## Related Features

- **Auto-Completion**: Use `advance/auto_completion.py` to complete partial answers
- **Self-Improvement**: Use `advance/self_improve.py` to iteratively improve answers
- **Build Story**: Use BQ probing to help construct STAR stories from scratch

---

## Technical Details

### Stop Policy Training

The learned policy is trained using:
1. Synthetic interview sessions generated with `bootstrap_training.py`
2. Teacher labels from GPT-4o determining optimal stop points
3. Logistic regression on 10 state features

To retrain:
```bash
# Generate more training data
python policy/bootstrap_training.py --synthetic 50

# Relabel with GPT-4o (optional)
python policy/bootstrap_training.py --relabel

# Train model
python policy/bootstrap_training.py --train
```

### Model Performance

| Model | Accuracy | Stop Recall |
|-------|----------|-------------|
| **Learned Policy** | **88%** | **92%** |
| Heuristic Baseline | 60% | 17% |
| LLM Zero-shot | 56% | 8% |

---

## Support

For issues or questions:
1. Check examples in `examples/` directory
2. Review prompt templates in `prompts.py`
3. Check policy README: `policy/README.md`
