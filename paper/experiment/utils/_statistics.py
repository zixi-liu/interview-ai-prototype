"""
Statistical analysis utilities for Experiment 1.

Provides functions for:
- t-test (paired and independent)
- Effect size (Cohen's d)
- Descriptive statistics
- Rating score conversions
"""

import numpy as np
from scipy import stats
from typing import List, Dict, Tuple, Optional


# Rating score mapping
RATING_SCORES = {
    'No Hire': 0, 'Leaning No Hire': 1, 'No-Pass': 1,
    'Borderline': 2, 'Leaning Hire': 2, 'Weak Hire': 2,
    'Hire': 3, 'Pass': 3, 'Strong Hire': 4,
}


def rating_to_score(rating: str) -> int:
    """Convert rating string to numeric score."""
    return RATING_SCORES.get(rating, -1)


def scores_from_ratings(ratings: List[str]) -> List[int]:
    """Convert list of ratings to scores."""
    return [rating_to_score(r) for r in ratings]


def independent_ttest(group_a_scores: List[float], group_b_scores: List[float]) -> Dict:
    """
    Perform independent samples t-test.
    
    Args:
        group_a_scores: List of scores from Group A
        group_b_scores: List of scores from Group B
    
    Returns:
        Dict with t-statistic, p-value, degrees of freedom, and effect size
    """
    group_a = np.array(group_a_scores)
    group_b = np.array(group_b_scores)
    
    # Perform t-test
    t_stat, p_value = stats.ttest_ind(group_a, group_b)
    
    # Calculate degrees of freedom
    df = len(group_a) + len(group_b) - 2
    
    # Calculate Cohen's d (effect size)
    pooled_std = np.sqrt(
        ((len(group_a) - 1) * np.var(group_a, ddof=1) + 
         (len(group_b) - 1) * np.var(group_b, ddof=1)) / df
    )
    cohens_d = (np.mean(group_a) - np.mean(group_b)) / pooled_std if pooled_std > 0 else 0
    
    return {
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'degrees_of_freedom': int(df),
        'cohens_d': float(cohens_d),
        'mean_a': float(np.mean(group_a)),
        'mean_b': float(np.mean(group_b)),
        'std_a': float(np.std(group_a, ddof=1)),
        'std_b': float(np.std(group_b, ddof=1)),
        'n_a': len(group_a),
        'n_b': len(group_b),
        'significant': bool(p_value < 0.05),
    }


def paired_ttest(before_scores: List[float], after_scores: List[float]) -> Dict:
    """
    Perform paired samples t-test.
    
    Args:
        before_scores: Scores before intervention
        after_scores: Scores after intervention
    
    Returns:
        Dict with t-statistic, p-value, degrees of freedom, and effect size
    """
    before = np.array(before_scores)
    after = np.array(after_scores)
    
    if len(before) != len(after):
        raise ValueError("before_scores and after_scores must have same length")
    
    # Calculate differences
    differences = after - before
    
    # Perform paired t-test
    t_stat, p_value = stats.ttest_rel(before, after)
    
    # Degrees of freedom
    df = len(before) - 1
    
    # Calculate Cohen's d for paired samples
    mean_diff = np.mean(differences)
    std_diff = np.std(differences, ddof=1)
    cohens_d = mean_diff / std_diff if std_diff > 0 else 0
    
    return {
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'degrees_of_freedom': int(df),
        'cohens_d': float(cohens_d),
        'mean_before': float(np.mean(before)),
        'mean_after': float(np.mean(after)),
        'mean_difference': float(mean_diff),
        'std_difference': float(std_diff),
        'n': len(before),
        'significant': bool(p_value < 0.05),
    }


def cohens_d(group_a_scores: List[float], group_b_scores: List[float]) -> float:
    """
    Calculate Cohen's d effect size.
    
    Interpretation:
    - |d| < 0.2: Negligible
    - 0.2 ≤ |d| < 0.5: Small
    - 0.5 ≤ |d| < 0.8: Medium
    - |d| ≥ 0.8: Large
    """
    group_a = np.array(group_a_scores)
    group_b = np.array(group_b_scores)
    
    pooled_std = np.sqrt(
        (np.var(group_a, ddof=1) + np.var(group_b, ddof=1)) / 2
    )
    
    if pooled_std == 0:
        return 0.0
    
    return float((np.mean(group_a) - np.mean(group_b)) / pooled_std)


def descriptive_stats(scores: List[float]) -> Dict:
    """Calculate descriptive statistics."""
    arr = np.array(scores)
    return {
        'mean': float(np.mean(arr)),
        'median': float(np.median(arr)),
        'std': float(np.std(arr, ddof=1)),
        'min': float(np.min(arr)),
        'max': float(np.max(arr)),
        'q25': float(np.percentile(arr, 25)),
        'q75': float(np.percentile(arr, 75)),
        'n': len(arr),
    }


def rating_improvement_stats(results: List[Dict]) -> Dict:
    """
    Calculate rating improvement statistics from experiment results.
    
    Args:
        results: List of result dicts with 'initial_rating_score' and 'final_rating_score'
    
    Returns:
        Dict with improvement statistics
    """
    improvements = []
    initial_scores = []
    final_scores = []
    
    for result in results:
        if 'initial_rating_score' in result and 'final_rating_score' in result:
            initial = result['initial_rating_score']
            final = result['final_rating_score']
            if initial >= 0 and final >= 0:
                improvements.append(final - initial)
                initial_scores.append(initial)
                final_scores.append(final)
    
    if not improvements:
        return {
            'n': 0,
            'mean_improvement': 0,
            'std_improvement': 0,
            'improved_count': 0,
            'no_change_count': 0,
            'degraded_count': 0,
        }
    
    improvements_arr = np.array(improvements)
    
    return {
        'n': len(improvements),
        'mean_improvement': float(np.mean(improvements_arr)),
        'std_improvement': float(np.std(improvements_arr, ddof=1)),
        'median_improvement': float(np.median(improvements_arr)),
        'improved_count': int(np.sum(improvements_arr > 0)),
        'no_change_count': int(np.sum(improvements_arr == 0)),
        'degraded_count': int(np.sum(improvements_arr < 0)),
        'improvement_rate': float(np.mean(improvements_arr > 0) * 100),
        'reached_strong_hire': sum(1 for r in results if r.get('reached_strong_hire', False)),
        'reached_strong_hire_rate': sum(1 for r in results if r.get('reached_strong_hire', False)) / len(results) * 100 if results else 0,
    }


def format_statistical_results(ttest_result: Dict, test_name: str = "Independent t-test") -> str:
    """Format statistical test results as readable string."""
    lines = [
        f"{test_name} Results:",
        f"  t-statistic: {ttest_result['t_statistic']:.4f}",
        f"  p-value: {ttest_result['p_value']:.6f}",
        f"  Degrees of freedom: {ttest_result['degrees_of_freedom']}",
        f"  Cohen's d (effect size): {ttest_result['cohens_d']:.4f}",
        f"  Significant (p < 0.05): {'Yes' if ttest_result['significant'] else 'No'}",
    ]
    
    if 'mean_a' in ttest_result:
        lines.extend([
            f"  Group A: M={ttest_result['mean_a']:.2f}, SD={ttest_result['std_a']:.2f}, n={ttest_result['n_a']}",
            f"  Group B: M={ttest_result['mean_b']:.2f}, SD={ttest_result['std_b']:.2f}, n={ttest_result['n_b']}",
        ])
    elif 'mean_before' in ttest_result:
        lines.extend([
            f"  Before: M={ttest_result['mean_before']:.2f}, n={ttest_result['n']}",
            f"  After: M={ttest_result['mean_after']:.2f}, n={ttest_result['n']}",
            f"  Mean difference: {ttest_result['mean_difference']:.2f}",
        ])
    
    # Effect size interpretation
    d = abs(ttest_result['cohens_d'])
    if d < 0.2:
        effect_size = "Negligible"
    elif d < 0.5:
        effect_size = "Small"
    elif d < 0.8:
        effect_size = "Medium"
    else:
        effect_size = "Large"
    
    lines.append(f"  Effect size interpretation: {effect_size}")
    
    return "\n".join(lines)

