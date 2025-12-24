#!/usr/bin/env python3
"""
Experiment 1 - Step 5: Analysis

Compare rating improvements (t-test, effect size)
Compare iterations to convergence
Analyze training effectiveness metrics
Generate comparison tables and visualizations
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

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent / 'utils'))

from paper.experiment.utils.statistics import (
    independent_ttest,
    rating_improvement_stats,
    descriptive_stats,
    format_statistical_results,
    cohens_d,
)

# Try to import visualization (may not be available)
try:
    from utils.visualization import (
        plot_rating_improvement_distribution,
        plot_comparison_table,
    )
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False
    print("Warning: Visualization utilities not available. Install matplotlib and seaborn for plots.")


def load_results(results_dir: Path) -> tuple[list, list]:
    """Load results from Group A and Group B."""
    automated_file = results_dir / 'exp1_automated_results.json'
    human_in_loop_file = results_dir / 'exp1_human_in_loop_results.json'
    
    group_a = []
    if automated_file.exists():
        with open(automated_file, 'r', encoding='utf-8') as f:
            group_a = json.load(f)
    else:
        print(f"Warning: {automated_file} not found")
    
    group_b = []
    if human_in_loop_file.exists():
        with open(human_in_loop_file, 'r', encoding='utf-8') as f:
            group_b = json.load(f)
    else:
        print(f"Warning: {human_in_loop_file} not found")
    
    return group_a, group_b


def analyze_rating_improvement(group_a: list, group_b: list) -> dict:
    """
    Analyze rating improvement comparison between Group A and Group B.
    
    Returns:
        Dict with statistical analysis results
    """
    # Filter out errors
    group_a_valid = [r for r in group_a if 'error' not in r and 'initial_rating_score' in r]
    group_b_valid = [r for r in group_b if 'error' not in r and 'initial_rating_score' in r]
    
    if not group_a_valid or not group_b_valid:
        return {
            'error': 'Insufficient data for comparison',
            'group_a_n': len(group_a_valid),
            'group_b_n': len(group_b_valid),
        }
    
    # Extract improvement scores
    group_a_improvements = [r['rating_improvement'] for r in group_a_valid]
    group_b_improvements = [r['rating_improvement'] for r in group_b_valid]
    
    # Statistical test
    ttest_result = independent_ttest(group_a_improvements, group_b_improvements)
    
    # Improvement statistics for each group
    group_a_stats = rating_improvement_stats(group_a_valid)
    group_b_stats = rating_improvement_stats(group_b_valid)
    
    # Descriptive statistics
    group_a_desc = descriptive_stats(group_a_improvements)
    group_b_desc = descriptive_stats(group_b_improvements)
    
    return {
        'ttest': ttest_result,
        'group_a_stats': group_a_stats,
        'group_b_stats': group_b_stats,
        'group_a_descriptive': group_a_desc,
        'group_b_descriptive': group_b_desc,
        'group_a_n': len(group_a_valid),
        'group_b_n': len(group_b_valid),
    }


def analyze_iterations(group_a: list, group_b: list) -> dict:
    """Analyze iteration counts and convergence."""
    group_a_valid = [r for r in group_a if 'error' not in r and 'iterations' in r]
    group_b_valid = [r for r in group_b if 'error' not in r and 'iterations' in r]
    
    if not group_a_valid or not group_b_valid:
        return {'error': 'Insufficient data'}
    
    group_a_iterations = [r['iterations'] for r in group_a_valid]
    group_b_iterations = [r['iterations'] for r in group_b_valid]
    
    # Statistical comparison
    ttest_result = independent_ttest(group_a_iterations, group_b_iterations)
    
    return {
        'ttest': ttest_result,
        'group_a_mean_iterations': sum(group_a_iterations) / len(group_a_iterations),
        'group_b_mean_iterations': sum(group_b_iterations) / len(group_b_iterations),
        'group_a_stats': descriptive_stats(group_a_iterations),
        'group_b_stats': descriptive_stats(group_b_iterations),
    }


def analyze_training_effectiveness(group_b: list) -> dict:
    """
    Analyze training effectiveness metrics (Group B only).
    
    Metrics:
    - Pre/post survey: confidence and authenticity
    - Recall test (if available)
    """
    group_b_valid = [r for r in group_b if 'error' not in r]
    
    if not group_b_valid:
        return {'error': 'No Group B data available'}
    
    # Extract survey data
    pre_confidence = []
    pre_authenticity = []
    post_confidence = []
    post_authenticity = []
    recall_tests = []
    
    for result in group_b_valid:
        pre_survey = result.get('pre_survey', {})
        post_survey = result.get('post_survey', {})
        
        if pre_survey.get('confidence') is not None:
            pre_confidence.append(pre_survey['confidence'])
        if pre_survey.get('authenticity') is not None:
            pre_authenticity.append(pre_survey['authenticity'])
        if post_survey.get('confidence') is not None:
            post_confidence.append(post_survey['confidence'])
        if post_survey.get('authenticity') is not None:
            post_authenticity.append(post_survey['authenticity'])
        if post_survey.get('recall_test'):
            recall_tests.append(post_survey['recall_test'])
    
    results = {
        'pre_confidence': descriptive_stats(pre_confidence) if pre_confidence else None,
        'pre_authenticity': descriptive_stats(pre_authenticity) if pre_authenticity else None,
        'post_confidence': descriptive_stats(post_confidence) if post_confidence else None,
        'post_authenticity': descriptive_stats(post_authenticity) if post_authenticity else None,
        'confidence_improvement': None,
        'authenticity_improvement': None,
        'recall_test_count': len(recall_tests),
    }
    
    # Paired t-test for confidence and authenticity (if we have paired data)
    # TODO: This requires matching pre/post pairs by participant_id
    # For now, we'll do independent comparison (less ideal but still informative)
    if pre_confidence and post_confidence:
        # Independent comparison (not ideal, but paired data matching is complex)
        confidence_ttest = independent_ttest(pre_confidence, post_confidence)
        results['confidence_improvement'] = {
            'mean_pre': confidence_ttest['mean_a'],
            'mean_post': confidence_ttest['mean_b'],
            'improvement': confidence_ttest['mean_b'] - confidence_ttest['mean_a'],
            'p_value': confidence_ttest['p_value'],
            'significant': confidence_ttest['significant'],
        }
    
    if pre_authenticity and post_authenticity:
        authenticity_ttest = independent_ttest(pre_authenticity, post_authenticity)
        results['authenticity_improvement'] = {
            'mean_pre': authenticity_ttest['mean_a'],
            'mean_post': authenticity_ttest['mean_b'],
            'improvement': authenticity_ttest['mean_b'] - authenticity_ttest['mean_a'],
            'p_value': authenticity_ttest['p_value'],
            'significant': authenticity_ttest['significant'],
        }
    
    return results


def analyze_customization(group_b: list) -> dict:
    """
    Analyze customization metrics.
    
    Metrics:
    - Answer uniqueness: Compare improved answers across participants for same original answer
    - Personal detail integration: Count of personal experiences/metrics added
    """
    # Group by qa_id to compare answers for same question
    by_qa_id = {}
    for result in group_b:
        if 'error' not in result:
            qa_id = result['qa_id']
            if qa_id not in by_qa_id:
                by_qa_id[qa_id] = []
            by_qa_id[qa_id].append(result)
    
    # Analyze uniqueness (for answers with multiple participants)
    uniqueness_scores = []
    personal_detail_counts = []
    
    for qa_id, results_list in by_qa_id.items():
        if len(results_list) > 1:
            # Compare final answers for uniqueness
            # Simple metric: count unique words (excluding common words)
            # TODO: More sophisticated similarity metric (e.g., BLEU, embedding similarity)
            final_answers = [r['final_answer'] for r in results_list]
            # For now, just count that we have multiple different answers
            uniqueness_scores.append(len(set(final_answers)) / len(final_answers))
        
        # Count personal details in participant answers
        for result in results_list:
            participant_answers = result.get('participant_answers', [])
            # Simple heuristic: count answers with metrics/numbers, "I" statements, specific details
            personal_count = 0
            for answer in participant_answers:
                if answer and isinstance(answer, str):
                    # Check for metrics (numbers, percentages)
                    import re
                    if re.search(r'\d+', answer):
                        personal_count += 1
                    # Check for "I" statements
                    if re.search(r'\bI\s+(?:decided|led|implemented|created|built|designed)', answer, re.IGNORECASE):
                        personal_count += 1
            personal_detail_counts.append(personal_count)
    
    return {
        'unique_qa_pairs': len(by_qa_id),
        'qa_pairs_with_multiple_participants': sum(1 for r in by_qa_id.values() if len(r) > 1),
        'average_uniqueness': sum(uniqueness_scores) / len(uniqueness_scores) if uniqueness_scores else 0,
        'personal_detail_stats': descriptive_stats(personal_detail_counts) if personal_detail_counts else None,
        'answers_with_personal_details': sum(1 for c in personal_detail_counts if c > 0) if personal_detail_counts else 0,
        'personal_details_rate': sum(1 for c in personal_detail_counts if c > 0) / len(personal_detail_counts) * 100 if personal_detail_counts else 0,
    }


def generate_comparison_table(group_a: list, group_b: list, output_file: Path):
    """Generate comparison table (Table 1)."""
    group_a_valid = [r for r in group_a if 'error' not in r]
    group_b_valid = [r for r in group_b if 'error' not in r]
    
    group_a_stats = rating_improvement_stats(group_a_valid)
    group_b_stats = rating_improvement_stats(group_b_valid)
    
    table = {
        'title': 'Table 1: Rating Improvement Comparison (Group A vs Group B)',
        'columns': ['Metric', 'Group A (Automated)', 'Group B (Human-in-Loop)'],
        'rows': [
            ['N', str(group_a_stats['n']), str(group_b_stats['n'])],
            ['Mean Improvement', f"{group_a_stats['mean_improvement']:.2f}", f"{group_b_stats['mean_improvement']:.2f}"],
            ['Std Improvement', f"{group_a_stats['std_improvement']:.2f}", f"{group_b_stats['std_improvement']:.2f}"],
            ['Improved Count', str(group_a_stats['improved_count']), str(group_b_stats['improved_count'])],
            ['Improvement Rate (%)', f"{group_a_stats['improvement_rate']:.1f}%", f"{group_b_stats['improvement_rate']:.1f}%"],
            ['Reached Strong Hire', str(group_a_stats['reached_strong_hire']), str(group_b_stats['reached_strong_hire'])],
            ['Strong Hire Rate (%)', f"{group_a_stats['reached_strong_hire_rate']:.1f}%", f"{group_b_stats['reached_strong_hire_rate']:.1f}%"],
        ],
    }
    
    # Save as JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(table, f, indent=2, ensure_ascii=False)
    
    # Also save as markdown table
    md_file = output_file.with_suffix('.md')
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# {table['title']}\n\n")
        f.write("| " + " | ".join(table['columns']) + " |\n")
        f.write("| " + " | ".join(["---"] * len(table['columns'])) + " |\n")
        for row in table['rows']:
            f.write("| " + " | ".join(row) + " |\n")
    
    print(f"Comparison table saved to: {output_file}")
    print(f"Markdown table saved to: {md_file}")


def generate_training_effectiveness_table(training_stats: dict, output_file: Path):
    """Generate training effectiveness table (Table 2)."""
    table = {
        'title': 'Table 2: Training Effectiveness Metrics (Group B)',
        'columns': ['Metric', 'Pre', 'Post', 'Improvement', 'Significant'],
        'rows': [],
    }
    
    if training_stats.get('confidence_improvement'):
        ci = training_stats['confidence_improvement']
        table['rows'].append([
            'Confidence (1-5)',
            f"{ci['mean_pre']:.2f}",
            f"{ci['mean_post']:.2f}",
            f"{ci['improvement']:.2f}",
            'Yes' if ci['significant'] else 'No',
        ])
    
    if training_stats.get('authenticity_improvement'):
        ai = training_stats['authenticity_improvement']
        table['rows'].append([
            'Authenticity (1-5)',
            f"{ai['mean_pre']:.2f}",
            f"{ai['mean_post']:.2f}",
            f"{ai['improvement']:.2f}",
            'Yes' if ai['significant'] else 'No',
        ])
    
    if training_stats.get('recall_test_count'):
        table['rows'].append([
            'Recall Test Responses',
            'N/A',
            str(training_stats['recall_test_count']),
            'N/A',
            'N/A',
        ])
    
    if not table['rows']:
        table['rows'].append([
            'Note',
            'Data collection pending',
            'Data collection pending',
            'N/A',
            'N/A',
        ])
    
    # Save as JSON and Markdown
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(table, f, indent=2, ensure_ascii=False)
    
    md_file = output_file.with_suffix('.md')
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# {table['title']}\n\n")
        f.write("| " + " | ".join(table['columns']) + " |\n")
        f.write("| " + " | ".join(["---"] * len(table['columns'])) + " |\n")
        for row in table['rows']:
            f.write("| " + " | ".join(row) + " |\n")
    
    print(f"Training effectiveness table saved to: {output_file}")


def main():
    """Main analysis function."""
    script_dir = Path(__file__).parent
    results_dir = script_dir / 'exp1_results'
    output_dir = results_dir / 'analysis'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*80)
    print("EXPERIMENT 1 - STEP 5: ANALYSIS")
    print("="*80)
    
    # Load results
    print("\nLoading results...")
    group_a, group_b = load_results(results_dir)
    print(f"Group A (Automated): {len(group_a)} results")
    print(f"Group B (Human-in-Loop): {len(group_b)} results")
    
    if not group_a and not group_b:
        print("Error: No results found. Please run previous steps first.")
        return
    
    # Analysis 1: Rating Improvement Comparison
    print("\n" + "="*80)
    print("Analysis 1: Rating Improvement Comparison")
    print("="*80)
    improvement_analysis = analyze_rating_improvement(group_a, group_b)
    
    if 'error' not in improvement_analysis:
        print("\nStatistical Test Results:")
        print(format_statistical_results(improvement_analysis['ttest'], "Independent t-test (Rating Improvement)"))
        
        print("\nGroup A (Automated) Statistics:")
        print(f"  N: {improvement_analysis['group_a_stats']['n']}")
        print(f"  Mean improvement: {improvement_analysis['group_a_stats']['mean_improvement']:.2f}")
        print(f"  Improvement rate: {improvement_analysis['group_a_stats']['improvement_rate']:.1f}%")
        print(f"  Strong Hire rate: {improvement_analysis['group_a_stats']['reached_strong_hire_rate']:.1f}%")
        
        print("\nGroup B (Human-in-Loop) Statistics:")
        print(f"  N: {improvement_analysis['group_b_stats']['n']}")
        print(f"  Mean improvement: {improvement_analysis['group_b_stats']['mean_improvement']:.2f}")
        print(f"  Improvement rate: {improvement_analysis['group_b_stats']['improvement_rate']:.1f}%")
        print(f"  Strong Hire rate: {improvement_analysis['group_b_stats']['reached_strong_hire_rate']:.1f}%")
        
        # Save analysis
        analysis_file = output_dir / 'exp1_rating_improvement_analysis.json'
        print(improvement_analysis)
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(improvement_analysis, f, indent=2, ensure_ascii=False)
        print(f"\nAnalysis saved to: {analysis_file}")
    else:
        print(f"Error: {improvement_analysis['error']}")
    
    # Analysis 2: Iterations Comparison
    print("\n" + "="*80)
    print("Analysis 2: Iterations Comparison")
    print("="*80)
    iterations_analysis = analyze_iterations(group_a, group_b)
    
    if 'error' not in iterations_analysis:
        print(f"\nGroup A mean iterations: {iterations_analysis['group_a_mean_iterations']:.2f}")
        print(f"Group B mean iterations: {iterations_analysis['group_b_mean_iterations']:.2f}")
        print(format_statistical_results(iterations_analysis['ttest'], "Independent t-test (Iterations)"))
        
        iterations_file = output_dir / 'exp1_iterations_analysis.json'
        with open(iterations_file, 'w', encoding='utf-8') as f:
            json.dump(iterations_analysis, f, indent=2, ensure_ascii=False)
        print(f"Analysis saved to: {iterations_file}")
    else:
        print(f"Error: {iterations_analysis['error']}")
    
    # Analysis 3: Training Effectiveness
    print("\n" + "="*80)
    print("Analysis 3: Training Effectiveness (Group B)")
    print("="*80)
    training_analysis = analyze_training_effectiveness(group_b)
    
    if 'error' not in training_analysis:
        if training_analysis.get('confidence_improvement'):
            ci = training_analysis['confidence_improvement']
            print(f"\nConfidence: {ci['mean_pre']:.2f} -> {ci['mean_post']:.2f} "
                  f"(improvement: {ci['improvement']:.2f}, "
                  f"p={ci['p_value']:.4f}, "
                  f"significant: {ci['significant']})")
        
        if training_analysis.get('authenticity_improvement'):
            ai = training_analysis['authenticity_improvement']
            print(f"Authenticity: {ai['mean_pre']:.2f} -> {ai['mean_post']:.2f} "
                  f"(improvement: {ai['improvement']:.2f}, "
                  f"p={ai['p_value']:.4f}, "
                  f"significant: {ai['significant']})")
        
        print(f"Recall test responses: {training_analysis['recall_test_count']}")
        
        training_file = output_dir / 'exp1_training_effectiveness_analysis.json'
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(training_analysis, f, indent=2, ensure_ascii=False)
        print(f"Analysis saved to: {training_file}")
        
        # Generate table
        generate_training_effectiveness_table(training_analysis, output_dir / 'exp1_table2_training_effectiveness')
    else:
        print(f"Error: {training_analysis['error']}")
        print("Note: Training effectiveness data may not be available yet.")
        print("      Fill in pre_survey and post_survey in exp1_human_input.json")
    
    # Analysis 4: Customization
    print("\n" + "="*80)
    print("Analysis 4: Customization (Group B)")
    print("="*80)
    customization_analysis = analyze_customization(group_b)
    
    print(f"Unique Q&A pairs: {customization_analysis['unique_qa_pairs']}")
    print(f"Q&A pairs with multiple participants: {customization_analysis['qa_pairs_with_multiple_participants']}")
    print(f"Average uniqueness: {customization_analysis['average_uniqueness']:.2f}")
    
    if customization_analysis.get('personal_detail_stats'):
        pd_stats = customization_analysis['personal_detail_stats']
        print(f"Personal detail stats: M={pd_stats['mean']:.2f}, SD={pd_stats['std']:.2f}")
        print(f"Answers with personal details: {customization_analysis['answers_with_personal_details']} "
              f"({customization_analysis['personal_details_rate']:.1f}%)")
    
    customization_file = output_dir / 'exp1_customization_analysis.json'
    with open(customization_file, 'w', encoding='utf-8') as f:
        json.dump(customization_analysis, f, indent=2, ensure_ascii=False)
    print(f"Analysis saved to: {customization_file}")
    
    # Generate comparison table
    print("\n" + "="*80)
    print("Generating Comparison Tables")
    print("="*80)
    generate_comparison_table(group_a, group_b, output_dir / 'exp1_table1_rating_improvement')
    
    # Generate visualization (if available)
    if HAS_VISUALIZATION:
        print("\nGenerating visualizations...")
        try:
            plot_rating_improvement_distribution(
                group_a, group_b, output_dir / 'exp1_figure1_rating_improvement_distribution.png'
            )
            print("Figure 1 saved to: exp1_figure1_rating_improvement_distribution.png")
        except Exception as e:
            print(f"Warning: Could not generate visualization: {e}")
    else:
        print("\nVisualization not available. Install matplotlib and seaborn for plots.")
        print("Figure 1 (Rating Improvement Distribution) - TODO: Generate manually")
    
    # Summary
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nAll analysis results saved to: {output_dir}")
    print("\nGenerated outputs:")
    print("  - Table 1: Rating improvement comparison")
    print("  - Table 2: Training effectiveness metrics")
    print("  - Statistical analysis results (JSON)")
    print("  - Figure 1: Rating improvement distribution (if visualization available)")


if __name__ == '__main__':
    main()

