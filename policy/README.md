# Stop Policy for Interview Probing Agent

Learned policy to decide when to STOP vs CONTINUE probing during behavioral interviews.

## Results (30 sessions, 125 samples)

| Model | Accuracy | Stop Recall | Stop Precision |
|-------|----------|-------------|----------------|
| **Learned Policy** | **88%** | **92%** | 85% |
| Heuristic Baseline | 60% | 17% | 100% |
| LLM Zero-shot (gpt-4o) | 56% | 8% | 100% |

The learned policy significantly outperforms both baselines, especially in recall (knowing when to stop).

## Feature Importances

| Feature | Weight | Interpretation |
|---------|--------|----------------|
| `good_responses` | +3.04 | More good answers → stop |
| `turn_count` | +0.99 | Later turns → stop |
| `gaps_resolved` | +0.97 | More resolved → stop |
| `is_senior` | +0.77 | Senior level → stop earlier |
| `vague_responses` | +0.68 | More vague → stop (diminishing returns) |
| `gaps_remaining` | -0.66 | Fewer gaps → stop |
| `pushback_count` | +0.36 | More pushback → stop |
| `idk_count` | -0.33 | More IDK → continue (try different angle) |

## Usage

### Generate Training Data
```bash
python policy/bootstrap_training.py --synthetic 30
```

### Relabel with gpt-4o (optional, better labels)
```bash
python policy/bootstrap_training.py --relabel
mv policy/session_logs_relabeled/* policy/session_logs/
```

### Train Model
```bash
python policy/bootstrap_training.py --train
```

## Files

- `stop_policy.py` - Core policy classes (StateFeatures, SessionLog, HybridStopPolicy)
- `bootstrap_training.py` - Training data generation and model training
- `stop_policy_model.pkl` - Trained logistic regression model
- `session_logs/` - Generated training sessions (JSON) - not committed to git
- `session_logs_relabeled/` - Relabeled sessions (temporary)

## Training Data

Training data (`session_logs/`) is not committed to git. To regenerate or obtain:

1. **Regenerate from scratch** (requires OpenAI API key, ~$2-5):
   ```bash
   python policy/bootstrap_training.py --synthetic 30
   python policy/bootstrap_training.py --relabel
   python policy/bootstrap_training.py --train
   ```

2. **Download from GCS** (public bucket):
   ```bash
   gsutil -m cp -r gs://interview-ai-prototype/training-data/session_logs/ policy/
   ```

## Architecture

```
StateFeatures (10 features)
    ↓
LearnedStopPolicy (logistic regression)
    ↓
HybridStopPolicy (combines learned + heuristics)
    ↓
StopDecision (STOP / CONTINUE)
```

## Data Format

Each session log contains:
```json
{
  "session_id": "abc123",
  "question": "Tell me about...",
  "original_answer": "...",
  "level": "Senior",
  "initial_gaps": ["gap1", "gap2"],
  "trajectory": [
    {
      "turn": 1,
      "state": { "gaps_remaining": 2, "good_responses": 1, ... },
      "response_type": "ANSWER_GOOD",
      "action": "PROBE_SAME"
    }
  ],
  "optimal_stop_turn": 3,
  "teacher_feedback": "..."
}
```

## Next Steps

- [ ] Add more friction-heavy examples (currently ~7% of responses)
- [ ] Test on real interview data
- [ ] A/B test learned policy vs heuristic in production
