# Experiment 1: Human-in-the-Loop Mechanisms and Value Exploration

This directory contains the implementation for Experiment 1, which quantitatively compares `StorySelfImprove` (automated CoT) vs `HumanInLoopImprove` (CoT + human input) to explore the mechanisms, value propositions, and trade-offs of human-in-the-loop approaches. The experiment investigates whether and under what conditions human-in-the-loop provides advantages in training effectiveness and customization, with effectiveness potentially depending on participant quality and context.

## Directory Structure

```
paper/experiment/
├── README.md                          # This file
├── plan.md                            # Full experimental plan
├── exp1_prepare_dataset.py           # Step 1: Prepare dataset and initial evaluation
├── exp1_automated.py                 # Step 2: Run automated group (Group A)
├── exp1_collect_human_input.py       # Step 3: Create template for human input collection
├── exp1_human_in_loop.py            # Step 4: Run human-in-loop group (Group B)
├── exp1_analysis.py                  # Step 5: Statistical analysis and visualization
├── utils/
│   ├── statistics.py                 # Statistical analysis utilities
│   └── visualization.py              # Visualization utilities
└── exp1_results/                     # Results directory (created during execution)
    ├── exp1_initial_evaluations.json
    ├── exp1_stratified_groups.json
    ├── exp1_automated_results.json
    ├── exp1_human_input_template.json
    ├── exp1_human_input.json         # To be filled with actual participant data
    ├── exp1_human_in_loop_results.json
    └── analysis/                     # Analysis outputs
        ├── exp1_table1_rating_improvement.md
        ├── exp1_table2_training_effectiveness.md
        └── exp1_figure1_rating_improvement_distribution.png
```

## Prerequisites

### Python Packages
```bash
pip install scipy numpy matplotlib seaborn tomli  # or tomllib (Python 3.11+)
```

### Data Requirements
- `awesome-behavioral-interviews/answers.toml` - 50 Q&A pairs
- OpenAI API key (set in environment or `.env` file)

## Execution Steps

### Step 1: Prepare Dataset
```bash
python paper/experiment/exp1_prepare_dataset.py
```

**What it does:**
- Loads all 50 Q&A pairs from `answers.toml`
- Performs initial evaluation using `BQQuestions.real_interview()` + `bar_raiser()`
- Extracts initial ratings and probing questions
- Stratifies answers by rating for balanced groups
- Saves initial evaluations and feedback files

**Outputs:**
- `exp1_results/exp1_initial_evaluations.json` - All initial evaluations
- `exp1_results/exp1_stratified_groups.json` - Stratified groups
- `exp1_results/initial_feedbacks/*.md` - Feedback files for improvement

### Step 2: Run Automated Group (Group A)
```bash
python paper/experiment/exp1_automated.py
```

**What it does:**
- Selects ~25 answers for Group A (balanced across rating categories)
- Runs `StorySelfImprove.run()` on each answer
- Records iterations, ratings, and improved answers
- Saves results for comparison

**Outputs:**
- `exp1_results/exp1_automated_results.json` - Group A results

**Note:** Current implementation has a limitation - `StorySelfImprove` doesn't expose iteration-by-iteration ratings. The code includes TODO comments for future enhancement.

### Step 3: Collect Human Input
```bash
python paper/experiment/exp1_collect_human_input.py
```

**What it does:**
- Extracts probing questions from initial feedback
- Creates template structure for human input collection
- Generates instructions for survey/interface creation
- Creates example filled data structure

**Outputs:**
- `exp1_results/exp1_human_input_template.json` - Template for participant responses
- `exp1_results/exp1_human_input_instructions.md` - Instructions for data collection
- `exp1_results/exp1_human_input_example.json` - Example filled data

**Next Steps (Manual):**
1. Review the template and instructions
2. Create survey/interface (Google Forms, custom web app, etc.)
3. Recruit 20-30 participants
4. Collect participant responses to probing questions
5. Collect pre/post survey data (confidence, authenticity)
6. Save collected data to `exp1_results/exp1_human_input.json`

**Data Format:**
See `exp1_human_input_template.json` for the exact structure. Each entry should have:
- `participant_id`: Unique identifier
- `participant_answers`: List of answers matching `probing_questions`
- `pre_survey`: `{confidence: int, authenticity: int}` (1-5 scale)
- `post_survey`: `{confidence: int, authenticity: int, recall_test: str}`

### Step 4: Run Human-in-Loop Group (Group B)
```bash
python paper/experiment/exp1_human_in_loop.py
```

**What it does:**
- Loads human-provided probing answers from `exp1_human_input.json`
- Selects remaining answers for Group B (not used in Group A)
- Runs `HumanInLoopImprove.run_with_predefined_answers()` for each answer
- Records iterations, ratings, and improved answers
- Saves results for comparison

**Outputs:**
- `exp1_results/exp1_human_in_loop_results.json` - Group B results

**Note:** Requires `exp1_human_input.json` with actual participant data. If file doesn't exist, script will create empty structure.

### Step 5: Analysis
```bash
python paper/experiment/exp1_analysis.py
```

**What it does:**
- Compares rating improvements between Group A and Group B (t-test, effect size)
- Compares iteration counts
- Analyzes training effectiveness metrics (Group B only)
- Analyzes customization metrics (Group B only)
- Generates comparison tables and visualizations

**Outputs:**
- `exp1_results/analysis/exp1_table1_rating_improvement.md` - Table 1
- `exp1_results/analysis/exp1_table2_training_effectiveness.md` - Table 2
- `exp1_results/analysis/exp1_figure1_rating_improvement_distribution.png` - Figure 1
- Various JSON files with detailed analysis results

## Expected Outputs

### Table 1: Rating Improvement Comparison
Compares Group A vs Group B on:
- Mean improvement
- Improvement rate
- Strong Hire rate
- Statistical significance (t-test, p-value)
- Effect size (Cohen's d)

### Table 2: Training Effectiveness Metrics
For Group B only:
- Pre/post confidence scores
- Pre/post authenticity scores
- Recall test responses
- Statistical significance of improvements

### Figure 1: Rating Improvement Distribution
Visualization showing:
- Histogram of rating improvements for both groups
- Box plot comparison

## Success Criteria

According to the experimental plan, success is defined using a tiered approach:

**Tier 1 (Ideal - if results support hypothesis):**
- Statistically significant difference (p < 0.05)
- Effect size ≥ 0.5 (medium effect)
- ≥70% participants report improved confidence
- ≥80% answers show unique personal details

**Tier 2 (Acceptable - if results are directionally consistent):**
- Directionally consistent (p < 0.10) OR effect size ≥ 0.3
- ≥50% participants report improved confidence
- ≥60% answers show unique personal details
- Qualitative evidence supports value proposition

**Tier 3 (Exploratory - if results differ from hypothesis):**
- No significant difference or opposite direction, but:
  - Mechanism analysis provides insights
  - Trade-offs are clearly identified
  - Context-dependent recommendations are possible

**Note:** All outcomes are valuable. The experiment aims to understand mechanisms and trade-offs, not just prove superiority. Results will inform when to use each approach based on system objectives and constraints.

## Data Collection Notes

### Missing Data Handling
The code includes comments (`# TODO:`, `# NOTE:`) where data may be missing:
- **Iteration history**: `StorySelfImprove` doesn't currently expose per-iteration ratings
- **Human input**: Requires manual collection from participants
- **Training effectiveness**: Requires pre/post surveys and recall tests
- **Customization metrics**: Some metrics require manual analysis

### Filling Missing Data
1. **Human Input**: Fill `exp1_human_input.json` with actual participant responses
2. **Surveys**: Add `pre_survey` and `post_survey` data to human input entries
3. **Recall Tests**: Add `recall_test` to `post_survey` after 1 week
4. **Iteration History**: Modify `StorySelfImprove` to return iteration history (future enhancement)

## Limitations and Future Enhancements

1. **Iteration History**: `StorySelfImprove.run()` doesn't expose per-iteration ratings. Enhancement needed to track rating changes at each iteration.

2. **Paired Data**: Training effectiveness analysis uses independent t-test instead of paired t-test. Requires matching pre/post pairs by `participant_id`.

3. **Customization Metrics**: Current uniqueness metric is simple. Could be enhanced with BLEU scores, embedding similarity, etc.

4. **Visualization**: Requires matplotlib/seaborn. Falls back gracefully if not available.

5. **Experimental Uncertainty**:
   - Results may vary depending on participant quality, engagement level, and answer types
   - Statistical significance is not guaranteed; results may be non-significant or directionally opposite to hypothesis
   - Sample size (50 answers) may limit statistical power
   - Participant quality significantly impacts Group B results; low-quality input may lead to different conclusions
   - All outcomes (including non-significant or opposite results) provide valuable insights into mechanisms and trade-offs

## Troubleshooting

### Error: "answers.toml not found"
- Ensure you're running from project root
- Check that `awesome-behavioral-interviews/answers.toml` exists

### Error: "No human input data found"
- Run `exp1_collect_human_input.py` first
- Fill in `exp1_human_input.json` with participant responses
- See instructions in `exp1_human_input_instructions.md`

### Error: "matplotlib not available"
- Install: `pip install matplotlib seaborn`
- Or skip visualization (analysis will still work)

### Warning: "No probing questions found"
- Some answers may not generate probing questions
- These will be skipped in human-in-loop processing

## References

- Full experimental plan: `plan.md`
- Review feedback: `../review_feedbacks/feedback-20251224.md`
- Paper draft: `../draft.md`

## Contact

For questions or issues, refer to the main project README or contact the authors.

