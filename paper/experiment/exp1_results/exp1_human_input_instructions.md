
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
