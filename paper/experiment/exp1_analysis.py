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

from paper.experiment.utils._statistics import (
    independent_ttest,
    paired_ttest,
    rating_improvement_stats,
    descriptive_stats,
    format_statistical_results,
    cohens_d,
    test_normality,
    test_homogeneity_of_variance,
)

# # Try to import visualization (may not be available)
# try:
#     # Try relative import first (when running from experiment directory)
#     from utils.visualization import (
#         plot_rating_improvement_distribution,
#         plot_training_effectiveness,
#         plot_iteration_comparison,
#         plot_customization_metrics,
#         plot_comprehensive_comparison,
#     )
#     HAS_VISUALIZATION = True
# except ImportError:
#     try:
#         # Try absolute import (when running from project root)
#         from paper.experiment.utils.visualization import (
#             plot_rating_improvement_distribution,
#             plot_training_effectiveness,
#             plot_iteration_comparison,
#             plot_customization_metrics,
#             plot_comprehensive_comparison,
#         )
#         HAS_VISUALIZATION = True
#     except ImportError:
#         HAS_VISUALIZATION = False
#         print("Warning: Visualization utilities not available. Install matplotlib and seaborn for plots.")
from paper.experiment.utils.visualization import (
    plot_rating_improvement_distribution,
    plot_training_effectiveness,
    plot_iteration_comparison,
    plot_customization_metrics,
    plot_comprehensive_comparison,
)
HAS_VISUALIZATION = True

def load_results(results_dir: Path) -> tuple[list, list]:
    """Load results from Group A and Group B."""
    automated_file = results_dir / 'exp1_automated_results.json'
    human_in_loop_file = results_dir / 'exp1_human_in_loop_results.json'
    paired_file = results_dir / 'exp1_paired_results.json'
    
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

    paired_results = []
    if paired_file.exists():
        with open(paired_file, 'r', encoding='utf-8') as f:
            paired_results = json.load(f)
    else:
        print(f"Warning: {paired_file} not found")
    
    return group_a, group_b, paired_results


def extract_paired_data_for_visualization(paired_results: list) -> dict:
    """
    Extract paired data for visualization.
    
    Returns:
        Dict with:
        - automated_improvements: List of automated rating improvements
        - human_improvements: List of human-in-loop rating improvements
        - automated_iterations: List of automated iteration counts
        - human_iterations: List of human-in-loop iteration counts
        - pre_conf_individual: List of pre-confidence scores
        - post_conf_individual: List of post-confidence scores
        - pre_auth_individual: List of pre-authenticity scores
        - post_auth_individual: List of post-authenticity scores
    """
    automated_improvements = []
    human_improvements = []
    automated_iterations = []
    human_iterations = []
    pre_conf_individual = []
    post_conf_individual = []
    pre_auth_individual = []
    post_auth_individual = []
    
    for result in paired_results:
        if ('error' not in result and 
            'automated' in result and 'human_in_loop' in result and
            'error' not in result.get('automated', {}) and
            'error' not in result.get('human_in_loop', {})):
            
            # Rating improvements
            if 'rating_improvement' in result.get('automated', {}):
                automated_improvements.append(result['automated']['rating_improvement'])
            if 'rating_improvement' in result.get('human_in_loop', {}):
                human_improvements.append(result['human_in_loop']['rating_improvement'])
            
            # Iterations
            if 'iterations' in result.get('automated', {}):
                automated_iterations.append(result['automated']['iterations'])
            if 'iterations' in result.get('human_in_loop', {}):
                human_iterations.append(result['human_in_loop']['iterations'])
            
            # Training effectiveness (from human_in_loop)
            human_data = result.get('human_in_loop', {})
            pre_survey = human_data.get('pre_survey', {})
            post_survey = human_data.get('post_survey', {})
            
            if pre_survey.get('confidence') is not None:
                pre_conf_individual.append(pre_survey['confidence'])
            if post_survey.get('confidence') is not None:
                post_conf_individual.append(post_survey['confidence'])
            if pre_survey.get('authenticity') is not None:
                pre_auth_individual.append(pre_survey['authenticity'])
            if post_survey.get('authenticity') is not None:
                post_auth_individual.append(post_survey['authenticity'])
    
    return {
        'automated_improvements': automated_improvements,
        'human_improvements': human_improvements,
        'automated_iterations': automated_iterations,
        'human_iterations': human_iterations,
        'pre_conf_individual': pre_conf_individual,
        'post_conf_individual': post_conf_individual,
        'pre_auth_individual': pre_auth_individual,
        'post_auth_individual': post_auth_individual,
    }


def analyze_rating_improvement_paired(paired_results: list) -> dict:
    """
    Analyze rating improvement using paired design.
    Each result should have both 'automated' and 'human_in_loop' entries.
    
    Returns:
        Dict with statistical analysis results using paired t-test
    """
    # Filter out errors and extract paired data
    paired_data = []
    for result in paired_results:
        if ('error' not in result and 
            'automated' in result and 'human_in_loop' in result and
            'error' not in result.get('automated', {}) and
            'error' not in result.get('human_in_loop', {}) and
            'initial_rating_score' in result['automated'] and
            'initial_rating_score' in result['human_in_loop']):
            paired_data.append(result)
    
    if not paired_data:
        return {
            'error': 'Insufficient paired data for comparison',
            'n': 0,
        }
    
    # Extract improvement scores (paired)
    automated_improvements = [r['automated']['rating_improvement'] for r in paired_data]
    human_improvements = [r['human_in_loop']['rating_improvement'] for r in paired_data]
    
    # Paired t-test
    ttest_result = paired_ttest(automated_improvements, human_improvements)
    
    # Improvement statistics for each group
    automated_results = [r['automated'] for r in paired_data]
    human_results = [r['human_in_loop'] for r in paired_data]
    
    automated_stats = rating_improvement_stats(automated_results)
    human_stats = rating_improvement_stats(human_results)
    
    # Descriptive statistics
    automated_desc = descriptive_stats(automated_improvements)
    human_desc = descriptive_stats(human_improvements)
    
    return {
        'ttest': ttest_result,
        'design': 'paired',
        'automated_stats': automated_stats,
        'human_stats': human_stats,
        'automated_descriptive': automated_desc,
        'human_descriptive': human_desc,
        'n': len(paired_data),
    }


def analyze_rating_improvement(group_a: list, group_b: list) -> dict:
    """
    Analyze rating improvement comparison between Group A and Group B.
    Supports both independent groups and paired design.
    
    If data appears to be paired (same qa_ids in both groups), uses paired analysis.
    Otherwise uses independent groups analysis.
    
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
    
    # Check if data is paired (same qa_ids in both groups)
    group_a_ids = {r['qa_id'] for r in group_a_valid}
    group_b_ids = {r['qa_id'] for r in group_b_valid}
    common_ids = group_a_ids & group_b_ids
    
    # If most IDs are common, treat as paired design
    if len(common_ids) >= min(len(group_a_valid), len(group_b_valid)) * 0.8:
        # Paired design: match by qa_id
        paired_automated = []
        paired_human = []
        
        # Create lookup dicts
        group_a_dict = {r['qa_id']: r for r in group_a_valid}
        group_b_dict = {r['qa_id']: r for r in group_b_valid}
        
        # Match pairs
        for qa_id in common_ids:
            if qa_id in group_a_dict and qa_id in group_b_dict:
                paired_automated.append(group_a_dict[qa_id]['rating_improvement'])
                paired_human.append(group_b_dict[qa_id]['rating_improvement'])
        
        if len(paired_automated) >= 2:
            # Use paired t-test
            ttest_result = paired_ttest(paired_automated, paired_human)
            automated_stats = rating_improvement_stats([group_a_dict[qa_id] for qa_id in common_ids if qa_id in group_a_dict])
            human_stats = rating_improvement_stats([group_b_dict[qa_id] for qa_id in common_ids if qa_id in group_b_dict])
            
            return {
                'ttest': ttest_result,
                'design': 'paired',
                'group_a_stats': automated_stats,
                'group_b_stats': human_stats,
                'group_a_descriptive': descriptive_stats(paired_automated),
                'group_b_descriptive': descriptive_stats(paired_human),
                'group_a_n': len(paired_automated),
                'group_b_n': len(paired_human),
            }
    
    # Independent groups design
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
        'design': 'independent',
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
    
    # Paired t-test for confidence and authenticity
    # Match pre/post pairs by participant_id
    participant_pre_conf = {}
    participant_post_conf = {}
    participant_pre_auth = {}
    participant_post_auth = {}
    
    for result in group_b_valid:
        participant_id = result.get('participant_id')
        if not participant_id:
            continue
        
        pre_survey = result.get('pre_survey', {})
        post_survey = result.get('post_survey', {})
        
        if pre_survey.get('confidence') is not None:
            participant_pre_conf[participant_id] = pre_survey['confidence']
        if post_survey.get('confidence') is not None:
            participant_post_conf[participant_id] = post_survey['confidence']
        if pre_survey.get('authenticity') is not None:
            participant_pre_auth[participant_id] = pre_survey['authenticity']
        if post_survey.get('authenticity') is not None:
            participant_post_auth[participant_id] = post_survey['authenticity']
    
    # Match paired data for confidence
    paired_pre_conf = []
    paired_post_conf = []
    for pid in participant_pre_conf:
        if pid in participant_post_conf:
            paired_pre_conf.append(participant_pre_conf[pid])
            paired_post_conf.append(participant_post_conf[pid])
    
    if len(paired_pre_conf) >= 2:
        # Use paired t-test
        confidence_ttest = paired_ttest(paired_pre_conf, paired_post_conf)
        results['confidence_improvement'] = {
            'mean_pre': confidence_ttest['mean_before'],
            'mean_post': confidence_ttest['mean_after'],
            'improvement': confidence_ttest['mean_difference'],
            'p_value': confidence_ttest['p_value'],
            'significant': confidence_ttest['significant'],
            'cohens_d': confidence_ttest['cohens_d'],
            'n_paired': len(paired_pre_conf),
        }
    elif pre_confidence and post_confidence:
        # Fallback to independent if no paired data available
        confidence_ttest = independent_ttest(pre_confidence, post_confidence)
        results['confidence_improvement'] = {
            'mean_pre': confidence_ttest['mean_a'],
            'mean_post': confidence_ttest['mean_b'],
            'improvement': confidence_ttest['mean_b'] - confidence_ttest['mean_a'],
            'p_value': confidence_ttest['p_value'],
            'significant': confidence_ttest['significant'],
            'cohens_d': confidence_ttest['cohens_d'],
            'n_paired': 0,  # Indicates independent test was used
        }
    
    # Match paired data for authenticity
    paired_pre_auth = []
    paired_post_auth = []
    for pid in participant_pre_auth:
        if pid in participant_post_auth:
            paired_pre_auth.append(participant_pre_auth[pid])
            paired_post_auth.append(participant_post_auth[pid])
    
    if len(paired_pre_auth) >= 2:
        # Use paired t-test
        authenticity_ttest = paired_ttest(paired_pre_auth, paired_post_auth)
        results['authenticity_improvement'] = {
            'mean_pre': authenticity_ttest['mean_before'],
            'mean_post': authenticity_ttest['mean_after'],
            'improvement': authenticity_ttest['mean_difference'],
            'p_value': authenticity_ttest['p_value'],
            'significant': authenticity_ttest['significant'],
            'cohens_d': authenticity_ttest['cohens_d'],
            'n_paired': len(paired_pre_auth),
        }
    elif pre_authenticity and post_authenticity:
        # Fallback to independent if no paired data available
        authenticity_ttest = independent_ttest(pre_authenticity, post_authenticity)
        results['authenticity_improvement'] = {
            'mean_pre': authenticity_ttest['mean_a'],
            'mean_post': authenticity_ttest['mean_b'],
            'improvement': authenticity_ttest['mean_b'] - authenticity_ttest['mean_a'],
            'p_value': authenticity_ttest['p_value'],
            'significant': authenticity_ttest['significant'],
            'cohens_d': authenticity_ttest['cohens_d'],
            'n_paired': 0,  # Indicates independent test was used
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
    group_a, group_b, paired_results = load_results(results_dir)
    print(f"Group A (Automated): {len(group_a)} results")
    print(f"Group B (Human-in-Loop): {len(group_b)} results")
    if paired_results:
        print(f"Paired design results: {len(paired_results)} pairs")
    
    if not group_a and not group_b and not paired_results:
        print("Error: No results found. Please run previous steps first.")
        return
    
    # Analysis 1: Rating Improvement Comparison
    print("\n" + "="*80)
    print("Analysis 1: Rating Improvement Comparison")
    print("="*80)
    
    # Use paired design analysis if available, otherwise use independent
    if paired_results:
        print("Using paired design analysis...")
        improvement_analysis = analyze_rating_improvement_paired(paired_results)
    else:
        print("Using independent groups analysis...")
        improvement_analysis = analyze_rating_improvement(group_a, group_b)
    
    if 'error' not in improvement_analysis:
        design_type = improvement_analysis.get('design', 'independent')
        test_name = "Paired t-test (Rating Improvement)" if design_type == 'paired' else "Independent t-test (Rating Improvement)"
        print("\nStatistical Test Results:")
        print(format_statistical_results(improvement_analysis['ttest'], test_name))
        
        # Add normality and variance tests for independent design
        if design_type == 'independent':
            # Extract actual improvement scores for testing
            group_a_valid = [r for r in group_a if 'error' not in r and 'rating_improvement' in r]
            group_b_valid = [r for r in group_b if 'error' not in r and 'rating_improvement' in r]
            if group_a_valid and group_b_valid:
                group_a_scores = [r['rating_improvement'] for r in group_a_valid]
                group_b_scores = [r['rating_improvement'] for r in group_b_valid]
                
                print("\nAssumption Tests:")
                norm_a = test_normality(group_a_scores)
                norm_b = test_normality(group_b_scores)
                if norm_a.get('p_value') is not None:
                    print(f"  Group A normality ({norm_a['test']}): p={norm_a['p_value']:.4f}, {norm_a['interpretation']}")
                if norm_b.get('p_value') is not None:
                    print(f"  Group B normality ({norm_b['test']}): p={norm_b['p_value']:.4f}, {norm_b['interpretation']}")
                
                var_test = test_homogeneity_of_variance(group_a_scores, group_b_scores)
                print(f"  Variance homogeneity ({var_test['test']}): p={var_test['p_value']:.4f}, {var_test['interpretation']}")
                if not var_test['equal_variances']:
                    print(f"  Recommendation: {var_test['recommendation']}")
        
        # Handle different key names for paired vs independent design
        if design_type == 'paired':
            group_a_stats = improvement_analysis.get('automated_stats', {})
            group_b_stats = improvement_analysis.get('human_stats', {})
        else:
            group_a_stats = improvement_analysis.get('group_a_stats', {})
            group_b_stats = improvement_analysis.get('group_b_stats', {})
        
        print("\nGroup A (Automated) Statistics:")
        print(f"  N: {group_a_stats.get('n', improvement_analysis.get('group_a_n', improvement_analysis.get('n', 0)))}")
        print(f"  Mean improvement: {group_a_stats.get('mean_improvement', 0):.2f}")
        print(f"  Improvement rate: {group_a_stats.get('improvement_rate', 0):.1f}%")
        print(f"  Strong Hire rate: {group_a_stats.get('reached_strong_hire_rate', 0):.1f}%")
        
        print("\nGroup B (Human-in-Loop) Statistics:")
        print(f"  N: {group_b_stats.get('n', improvement_analysis.get('group_b_n', improvement_analysis.get('n', 0)))}")
        print(f"  Mean improvement: {group_b_stats.get('mean_improvement', 0):.2f}")
        print(f"  Improvement rate: {group_b_stats.get('improvement_rate', 0):.1f}%")
        print(f"  Strong Hire rate: {group_b_stats.get('reached_strong_hire_rate', 0):.1f}%")
        
        # Save analysis
        analysis_file = output_dir / 'exp1_rating_improvement_analysis.json'
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
    
    # Generate visualizations (if available)
    if HAS_VISUALIZATION:
        print("\n" + "="*80)
        print("Generating Core Visualizations (Paired Design Focus)")
        print("="*80)
        
        # Detect if using paired design
        is_paired = paired_results and len(paired_results) > 0
        paired_viz_data = None
        
        if is_paired:
            print("Detected paired design - extracting paired data for visualization...")
            paired_viz_data = extract_paired_data_for_visualization(paired_results)
            print(f"  Extracted {len(paired_viz_data['automated_improvements'])} paired comparisons")
        
        try:
            # Figure 1: Rating Improvement (Core - Paired Design Focus)
            print("\nGenerating Figure 1: Paired Rating Improvement Comparison...")
            if is_paired and paired_viz_data:
                # Use paired design visualization
                plot_rating_improvement_distribution(
                    group_a, group_b, 
                    output_dir / 'exp1_figure1_rating_improvement_distribution.png',
                    ttest_result=improvement_analysis.get('ttest') if 'error' not in improvement_analysis else None,
                    is_paired_design=True,
                    paired_data=paired_results
                )
            else:
                # Fallback to independent design
                plot_rating_improvement_distribution(
                    group_a, group_b, 
                    output_dir / 'exp1_figure1_rating_improvement_distribution.png',
                    ttest_result=improvement_analysis.get('ttest') if 'error' not in improvement_analysis else None,
                    is_paired_design=False
                )
            print("✓ Figure 1 saved")
        except Exception as e:
            print(f"✗ Warning: Could not generate Figure 1: {e}")
        
        try:
            # Figure 2: Training Effectiveness (Core - Significant Finding)
            if 'error' not in training_analysis:
                print("\nGenerating Figure 2: Training Effectiveness (Paired Comparison)...")
                # Use paired data if available
                group_b_for_viz = group_b
                if is_paired and paired_viz_data:
                    # Create group_b data structure from paired results for training effectiveness
                    group_b_for_viz = [r.get('human_in_loop', {}) for r in paired_results 
                                      if 'human_in_loop' in r and 'error' not in r.get('human_in_loop', {})]
                
                plot_training_effectiveness(
                    training_analysis,
                    output_dir / 'exp1_figure2_training_effectiveness.png',
                    group_b_data=group_b_for_viz
                )
                print("✓ Figure 2 saved")
            else:
                print("\nSkipping Figure 2: Training effectiveness data not available")
        except Exception as e:
            print(f"✗ Warning: Could not generate Figure 2: {e}")
        
        try:
            # Figure 3: Efficiency Comparison (Optional - Significant Finding)
            if 'error' not in iterations_analysis:
                print("\nGenerating Figure 3: Efficiency Comparison...")
                if is_paired and paired_viz_data:
                    # Use paired data
                    automated_iterations = paired_viz_data['automated_iterations']
                    human_iterations = paired_viz_data['human_iterations']
                else:
                    # Fallback to independent groups
                    group_a_valid = [r for r in group_a if 'error' not in r and 'iterations' in r]
                    group_b_valid = [r for r in group_b if 'error' not in r and 'iterations' in r]
                    automated_iterations = [r['iterations'] for r in group_a_valid]
                    human_iterations = [r['iterations'] for r in group_b_valid]
                
                if automated_iterations and human_iterations:
                    plot_iteration_comparison(
                        automated_iterations,
                        human_iterations,
                        output_dir / 'exp1_figure3_iteration_comparison.png',
                        ttest_result=iterations_analysis.get('ttest')
                    )
                    print("✓ Figure 3 saved")
                else:
                    print("  Skipping: Insufficient iteration data")
            else:
                print("\nSkipping Figure 3: Iteration data not available")
        except Exception as e:
            print(f"✗ Warning: Could not generate Figure 3: {e}")
        
        print("\n" + "="*80)
        print("Core Visualization Generation Complete!")
        print("="*80)
        print("Generated: Figure 1 (Rating Improvement), Figure 2 (Training Effectiveness)")
        if 'error' not in iterations_analysis:
            print("          Figure 3 (Efficiency)")
        print("\nNote: Customization metrics available in analysis JSON (not visualized)")
    else:
        print("\nVisualization not available. Install matplotlib and seaborn for plots.")
        print("Figures - TODO: Generate manually")
    
    # Summary
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nAll analysis results saved to: {output_dir}")
    print("\nGenerated outputs:")
    print("  - Table 1: Rating improvement comparison")
    print("  - Table 2: Training effectiveness metrics")
    print("  - Statistical analysis results (JSON)")
    if HAS_VISUALIZATION:
        print("  - Figure 1: Rating improvement distribution")
        print("  - Figure 2: Training effectiveness (pre/post)")
        print("  - Figure 3: Iteration comparison")
        print("  - Figure 4: Customization metrics")
        print("  - Figure 5: Comprehensive comparison")
    else:
        print("  - Figures: Not generated (install matplotlib/seaborn)")


if __name__ == '__main__':
    main()

