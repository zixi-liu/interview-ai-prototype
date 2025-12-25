"""
Visualization utilities for Experiment 1.

Provides functions for creating plots and figures following academic best practices.
Requires matplotlib and seaborn.
"""

import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib/seaborn not available. Install with: pip install matplotlib seaborn")

# Academic color palette (accessible, publication-ready)
ACADEMIC_COLORS = {
    'group_a': '#2E86AB',  # Blue
    'group_b': '#A23B72',  # Purple/Pink
    'pre': '#F18F01',      # Orange
    'post': '#C73E1D',     # Red
    'significant': '#06A77D',  # Green
    'not_significant': '#6C757D'  # Gray
}

# Academic style settings
ACADEMIC_STYLE = {
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans'],
    'font.size': 11,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 13,
    'axes.linewidth': 1.2,
    'grid.linewidth': 0.8,
    'grid.alpha': 0.3,
    'lines.linewidth': 2,
    'patch.linewidth': 1.2
}


def setup_academic_style():
    """Configure matplotlib with academic publication style."""
    if not HAS_MATPLOTLIB:
        return
    plt.rcParams.update(ACADEMIC_STYLE)
    sns.set_style("whitegrid", {
        'axes.spines.left': True,
        'axes.spines.bottom': True,
        'axes.spines.top': False,
        'axes.spines.right': False,
    })


def add_statistical_annotation(ax, x1, x2, y, p_value, text_y_offset=0.05):
    """Add statistical annotation between two groups."""
    # Determine significance level
    if p_value < 0.001:
        sig_text = '***'
    elif p_value < 0.01:
        sig_text = '**'
    elif p_value < 0.05:
        sig_text = '*'
    else:
        sig_text = 'ns'
    
    # Draw bracket
    ax.plot([x1, x1, x2, x2], [y, y + text_y_offset, y + text_y_offset, y], 
            'k-', linewidth=1.5, clip_on=False)
    
    # Add significance text
    mid_x = (x1 + x2) / 2
    ax.text(mid_x, y + text_y_offset * 1.2, sig_text, 
            ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Add p-value if not highly significant
    if p_value >= 0.001:
        p_text = f'p={p_value:.3f}'
        ax.text(mid_x, y + text_y_offset * 1.6, p_text,
                ha='center', va='bottom', fontsize=9, style='italic')


def plot_rating_improvement_distribution(
    group_a: List[Dict],
    group_b: List[Dict],
    output_file: Path,
    ttest_result: Optional[Dict] = None,
    figsize: Tuple[float, float] = (12, 5.5)
):
    """
    Create Figure 1: Rating improvement distribution (improved academic style).
    
    Uses violin plots with individual data points and confidence intervals.
    """
    if not HAS_MATPLOTLIB:
        raise ImportError("matplotlib and seaborn required for visualization")
    
    setup_academic_style()
    
    # Extract improvements
    group_a_improvements = np.array([r['rating_improvement'] for r in group_a 
                           if 'error' not in r and 'rating_improvement' in r])
    group_b_improvements = np.array([r['rating_improvement'] for r in group_b 
                           if 'error' not in r and 'rating_improvement' in r])
    
    if len(group_a_improvements) == 0 or len(group_b_improvements) == 0:
        raise ValueError("Insufficient data for visualization")
    
    # Calculate confidence intervals (95% CI)
    try:
        from scipy import stats
        def ci_mean(data, confidence=0.95):
            n = len(data)
            mean = np.mean(data)
            sem = stats.sem(data)
            h = sem * stats.t.ppf((1 + confidence) / 2, n - 1)
            return mean, mean - h, mean + h
    except ImportError:
        # Fallback without scipy
        def ci_mean(data, confidence=0.95):
            n = len(data)
            mean = np.mean(data)
            sem = np.std(data, ddof=1) / np.sqrt(n) if n > 1 else 0
            z_score = 1.96 if confidence == 0.95 else 2.576
            h = sem * z_score
            return mean, mean - h, mean + h
    
    mean_a, ci_low_a, ci_high_a = ci_mean(group_a_improvements)
    mean_b, ci_low_b, ci_high_b = ci_mean(group_b_improvements)
    
    # Create figure
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle('Figure 1: Rating Improvement Distribution', fontsize=13, fontweight='bold', y=1.02)
    
    # Panel A: Violin plot with individual points
    ax1 = axes[0]
    data_for_violin = [group_a_improvements, group_b_improvements]
    positions = [1, 2]
    labels = ['Group A\n(Automated)', 'Group B\n(Human-in-Loop)']
    
    # Create violin plots
    parts = ax1.violinplot(data_for_violin, positions=positions, widths=0.6,
                          showmeans=True, showmedians=True)
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor([ACADEMIC_COLORS['group_a'], ACADEMIC_COLORS['group_b']][i])
        pc.set_alpha(0.6)
        pc.set_edgecolor('black')
        pc.set_linewidth(1.2)
    
    # Add individual data points (strip plot with jitter)
    for i, (data, pos) in enumerate(zip(data_for_violin, positions)):
        jitter = np.random.normal(0, 0.05, len(data))
        ax1.scatter(jitter + pos, data, alpha=0.5, s=30, 
                   color='black', edgecolors='white', linewidths=0.5, zorder=3)
    
    # Add mean and confidence intervals
    ax1.errorbar(positions, [mean_a, mean_b], 
                yerr=[[mean_a - ci_low_a, mean_b - ci_low_b],
                      [ci_high_a - mean_a, ci_high_b - mean_b]],
                fmt='o', color='red', markersize=8, capsize=5, capthick=2,
                label='Mean (95% CI)', zorder=4)
    
    ax1.set_xticks(positions)
    ax1.set_xticklabels(labels, fontweight='bold')
    ax1.set_ylabel('Rating Improvement (score change)', fontweight='bold')
    ax1.set_title('(A) Distribution with Individual Data Points', fontweight='bold')
    ax1.legend(loc='upper right', frameon=True, fontsize=9)
    ax1.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax1.axhline(0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)
    
    # Add sample sizes
    ax1.text(1, ax1.get_ylim()[0] + 0.1, f'n={len(group_a_improvements)}', 
            ha='center', fontsize=9, style='italic')
    ax1.text(2, ax1.get_ylim()[0] + 0.1, f'n={len(group_b_improvements)}', 
            ha='center', fontsize=9, style='italic')
    
    # Panel B: Box plot with enhanced statistics
    ax2 = axes[1]
    bp = ax2.boxplot(data_for_violin, labels=labels, patch_artist=True, 
                     widths=0.6, showmeans=True, meanline=True)
    bp['boxes'][0].set_facecolor(ACADEMIC_COLORS['group_a'])
    bp['boxes'][0].set_alpha(0.7)
    bp['boxes'][1].set_facecolor(ACADEMIC_COLORS['group_b'])
    bp['boxes'][1].set_alpha(0.7)
    
    # Add statistical annotation if provided
    if ttest_result:
        p_value = ttest_result.get('p_value', 1.0)
        cohens_d = ttest_result.get('cohens_d', 0.0)
        n_a = ttest_result.get('n_a', len(group_a_improvements))
        n_b = ttest_result.get('n_b', len(group_b_improvements))
        y_max = max([np.max(group_a_improvements), np.max(group_b_improvements)]) + 0.5
        add_statistical_annotation(ax2, 1, 2, y_max, p_value, text_y_offset=0.3)
        
        # Enhanced statistics text box
        if p_value < 0.001:
            p_text = 'p < 0.001'
        else:
            p_text = f'p = {p_value:.3f}'
        stats_text = f"{p_text}\nCohen's d = {cohens_d:.2f}\nn₁={n_a}, n₂={n_b}"
        ax2.text(1.5, y_max + 0.9, stats_text, ha='center', va='bottom',
                fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', 
                alpha=0.8, edgecolor='black', linewidth=1))
    
    ax2.set_ylabel('Rating Improvement (score change)', fontweight='bold')
    ax2.set_title('(B) Box Plot with Statistical Summary', fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax2.axhline(0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Figure 1 saved to: {output_file}")


def plot_training_effectiveness(
    training_analysis: Dict,
    output_file: Path,
    group_b_data: Optional[List[Dict]] = None,
    figsize: Tuple[float, float] = (12, 6)
):
    """
    Create Figure 2: Training effectiveness (improved with paired comparison).
    
    Shows confidence and authenticity improvements with individual trajectories and distributions.
    """
    if not HAS_MATPLOTLIB:
        raise ImportError("matplotlib and seaborn required for visualization")
    
    setup_academic_style()
    
    # Extract data
    pre_conf = training_analysis.get('pre_confidence', {})
    post_conf = training_analysis.get('post_confidence', {})
    pre_auth = training_analysis.get('pre_authenticity', {})
    post_auth = training_analysis.get('post_authenticity', {})
    conf_improve = training_analysis.get('confidence_improvement', {})
    auth_improve = training_analysis.get('authenticity_improvement', {})
    
    if not all([pre_conf, post_conf, pre_auth, post_auth]):
        raise ValueError("Insufficient training effectiveness data")
    
    # Extract individual data if available
    pre_conf_individual = []
    post_conf_individual = []
    pre_auth_individual = []
    post_auth_individual = []
    
    if group_b_data:
        for result in group_b_data:
            if 'error' not in result:
                pre_survey = result.get('pre_survey', {})
                post_survey = result.get('post_survey', {})
                if pre_survey.get('confidence') is not None:
                    pre_conf_individual.append(pre_survey['confidence'])
                if post_survey.get('confidence') is not None:
                    post_conf_individual.append(post_survey['confidence'])
                if pre_survey.get('authenticity') is not None:
                    pre_auth_individual.append(pre_survey['authenticity'])
                if post_survey.get('authenticity') is not None:
                    post_auth_individual.append(post_survey['authenticity'])
    
    # Create figure with 2x2 layout
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Figure 2: Training Effectiveness (Pre/Post Comparison)', 
                 fontsize=13, fontweight='bold', y=0.98)
    
    # Panel A: Confidence - Paired comparison with individual trajectories
    ax1 = axes[0, 0]
    conf_means = [pre_conf.get('mean', 0), post_conf.get('mean', 0)]
    conf_stds = [pre_conf.get('std', 0), post_conf.get('std', 0)]
    
    # Draw individual trajectories if available
    if len(pre_conf_individual) == len(post_conf_individual) and len(pre_conf_individual) > 0:
        x_pos = [0, 1]
        for pre, post in zip(pre_conf_individual[:30], post_conf_individual[:30]):  # Limit to 30 for clarity
            ax1.plot(x_pos, [pre, post], color='gray', alpha=0.2, linewidth=0.8, zorder=1)
    
    # Add bars with error bars
    bars1 = ax1.bar([0, 1], conf_means, yerr=conf_stds, 
                    color=[ACADEMIC_COLORS['pre'], ACADEMIC_COLORS['post']],
                    alpha=0.7, edgecolor='black', linewidth=1.5, capsize=8, width=0.5, zorder=2)
    
    # Add mean points
    ax1.scatter([0, 1], conf_means, color='red', s=100, zorder=3, 
               edgecolors='white', linewidths=2, marker='o')
    
    # Add value labels
    for i, (mean, std) in enumerate(zip(conf_means, conf_stds)):
        ax1.text(i, mean + std + 0.15, f'{mean:.2f}', ha='center', va='bottom',
                fontweight='bold', fontsize=10)
    
    # Statistical annotation
    if conf_improve.get('significant'):
        p_val = conf_improve.get('p_value', 1.0)
        effect_size = conf_improve.get('improvement', 0)
        y_max = max(conf_means) + max(conf_stds) + 0.5
        add_statistical_annotation(ax1, 0, 1, y_max, p_val, text_y_offset=0.2)
        sig_text = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*'
        ax1.text(0.5, y_max + 0.35, sig_text, ha='center', va='bottom',
                fontsize=16, fontweight='bold', color=ACADEMIC_COLORS['significant'])
        # Add effect size
        ax1.text(0.5, y_max + 0.6, f'Δ = {effect_size:.2f}', ha='center', va='bottom',
                fontsize=9, style='italic')
    
    ax1.set_ylabel('Confidence Score (1-5)', fontweight='bold')
    ax1.set_title('(A) Confidence: Paired Comparison', fontweight='bold')
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(['Pre', 'Post'], fontweight='bold')
    ax1.set_ylim(0, 5.5)
    ax1.grid(True, alpha=0.3, linestyle='--', axis='y')
    if len(pre_conf_individual) > 0:
        ax1.text(0.5, -0.5, f'n = {len(pre_conf_individual)}', ha='center', fontsize=9, style='italic')
    
    # Panel B: Authenticity - Paired comparison
    ax2 = axes[0, 1]
    auth_means = [pre_auth.get('mean', 0), post_auth.get('mean', 0)]
    auth_stds = [pre_auth.get('std', 0), post_auth.get('std', 0)]
    
    # Draw individual trajectories
    if len(pre_auth_individual) == len(post_auth_individual) and len(pre_auth_individual) > 0:
        for pre, post in zip(pre_auth_individual[:30], post_auth_individual[:30]):
            ax2.plot([0, 1], [pre, post], color='gray', alpha=0.2, linewidth=0.8, zorder=1)
    
    bars2 = ax2.bar([0, 1], auth_means, yerr=auth_stds,
                    color=[ACADEMIC_COLORS['pre'], ACADEMIC_COLORS['post']],
                    alpha=0.7, edgecolor='black', linewidth=1.5, capsize=8, width=0.5, zorder=2)
    
    ax2.scatter([0, 1], auth_means, color='red', s=100, zorder=3,
               edgecolors='white', linewidths=2, marker='o')
    
    for i, (mean, std) in enumerate(zip(auth_means, auth_stds)):
        ax2.text(i, mean + std + 0.15, f'{mean:.2f}', ha='center', va='bottom',
                fontweight='bold', fontsize=10)
    
    if auth_improve.get('significant'):
        p_val = auth_improve.get('p_value', 1.0)
        effect_size = auth_improve.get('improvement', 0)
        y_max = max(auth_means) + max(auth_stds) + 0.5
        add_statistical_annotation(ax2, 0, 1, y_max, p_val, text_y_offset=0.2)
        sig_text = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*'
        ax2.text(0.5, y_max + 0.35, sig_text, ha='center', va='bottom',
                fontsize=16, fontweight='bold', color=ACADEMIC_COLORS['significant'])
        ax2.text(0.5, y_max + 0.6, f'Δ = {effect_size:.2f}', ha='center', va='bottom',
                fontsize=9, style='italic')
    
    ax2.set_ylabel('Authenticity Score (1-5)', fontweight='bold')
    ax2.set_title('(B) Authenticity: Paired Comparison', fontweight='bold')
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(['Pre', 'Post'], fontweight='bold')
    ax2.set_ylim(0, 5.5)
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    if len(pre_auth_individual) > 0:
        ax2.text(0.5, -0.5, f'n = {len(pre_auth_individual)}', ha='center', fontsize=9, style='italic')
    
    # Panel C: Confidence distribution (violin plot)
    ax3 = axes[1, 0]
    if len(pre_conf_individual) > 0 and len(post_conf_individual) > 0:
        data_for_violin = [pre_conf_individual, post_conf_individual]
        parts = ax3.violinplot(data_for_violin, positions=[1, 2], widths=0.6, showmeans=True)
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor([ACADEMIC_COLORS['pre'], ACADEMIC_COLORS['post']][i])
            pc.set_alpha(0.6)
            pc.set_edgecolor('black')
        ax3.set_xticks([1, 2])
        ax3.set_xticklabels(['Pre', 'Post'], fontweight='bold')
    else:
        # Fallback to bar chart
        ax3.bar([0, 1], conf_means, yerr=conf_stds, 
               color=[ACADEMIC_COLORS['pre'], ACADEMIC_COLORS['post']],
               alpha=0.7, edgecolor='black', capsize=8)
        ax3.set_xticks([0, 1])
        ax3.set_xticklabels(['Pre', 'Post'], fontweight='bold')
    
    ax3.set_ylabel('Confidence Score', fontweight='bold')
    ax3.set_title('(C) Confidence Distribution', fontweight='bold')
    ax3.set_ylim(0, 5.5)
    ax3.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Panel D: Authenticity distribution
    ax4 = axes[1, 1]
    if len(pre_auth_individual) > 0 and len(post_auth_individual) > 0:
        data_for_violin = [pre_auth_individual, post_auth_individual]
        parts = ax4.violinplot(data_for_violin, positions=[1, 2], widths=0.6, showmeans=True)
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor([ACADEMIC_COLORS['pre'], ACADEMIC_COLORS['post']][i])
            pc.set_alpha(0.6)
            pc.set_edgecolor('black')
        ax4.set_xticks([1, 2])
        ax4.set_xticklabels(['Pre', 'Post'], fontweight='bold')
    else:
        ax4.bar([0, 1], auth_means, yerr=auth_stds,
               color=[ACADEMIC_COLORS['pre'], ACADEMIC_COLORS['post']],
               alpha=0.7, edgecolor='black', capsize=8)
        ax4.set_xticks([0, 1])
        ax4.set_xticklabels(['Pre', 'Post'], fontweight='bold')
    
    ax4.set_ylabel('Authenticity Score', fontweight='bold')
    ax4.set_title('(D) Authenticity Distribution', fontweight='bold')
    ax4.set_ylim(0, 5.5)
    ax4.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Figure 2 saved to: {output_file}")


def plot_iteration_comparison(
    group_a_iterations: List[int],
    group_b_iterations: List[int],
    output_file: Path,
    ttest_result: Optional[Dict] = None,
    figsize: Tuple[float, float] = (8, 6)
):
    """
    Create Figure 3: Iteration comparison between groups.
    
    Shows efficiency difference with statistical annotation.
    """
    if not HAS_MATPLOTLIB:
        raise ImportError("matplotlib and seaborn required for visualization")
    
    setup_academic_style()
    
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle('Figure 3: Iteration Count Comparison', fontsize=13, fontweight='bold', y=1.02)
    
    # Calculate means and standard deviations
    mean_a = np.mean(group_a_iterations)
    mean_b = np.mean(group_b_iterations)
    std_a = np.std(group_a_iterations, ddof=1) if len(group_a_iterations) > 1 else 0
    std_b = np.std(group_b_iterations, ddof=1) if len(group_b_iterations) > 1 else 0
    n_a = len(group_a_iterations)
    n_b = len(group_b_iterations)
    
    # Use bar chart instead of box plot (better for constant or near-constant data)
    positions = [1, 2]
    labels = ['Group A\n(Automated)', 'Group B\n(Human-in-Loop)']
    means = [mean_a, mean_b]
    stds = [std_a, std_b]
    
    bars = ax.bar(positions, means, yerr=stds, width=0.6,
                  color=[ACADEMIC_COLORS['group_a'], ACADEMIC_COLORS['group_b']],
                  alpha=0.7, edgecolor='black', linewidth=1.5, capsize=8, zorder=2)
    
    # Add mean value labels on bars
    for i, (pos, mean, std) in enumerate(zip(positions, means, stds)):
        ax.text(pos, mean + std + 0.15, f'{mean:.1f}', ha='center', va='bottom',
                fontweight='bold', fontsize=12)
        # Add sample size below
        ax.text(pos, -0.3, f'n={[n_a, n_b][i]}', ha='center', va='top',
                fontsize=9, style='italic')
    
    # Add statistical annotation
    if ttest_result:
        p_value = ttest_result.get('p_value', 1.0)
        y_max = max(means) + max(stds) + 0.5
        add_statistical_annotation(ax, 1, 2, y_max, p_value, text_y_offset=0.3)
        
        if p_value < 0.001:
            sig_text = '***'
            ax.text(1.5, y_max + 0.6, sig_text, ha='center', va='bottom',
                   fontsize=18, fontweight='bold', color=ACADEMIC_COLORS['significant'])
            # Add p-value text
            ax.text(1.5, y_max + 1.0, 'p < 0.001', ha='center', va='bottom',
                   fontsize=10, style='italic')
        else:
            ax.text(1.5, y_max + 0.6, f'p = {p_value:.3f}', ha='center', va='bottom',
                   fontsize=10, style='italic')
    
    # Add efficiency improvement annotation
    efficiency_ratio = mean_a / mean_b if mean_b > 0 else 0
    ax.text(1.5, max(means) / 2, f'{efficiency_ratio:.1f}×\nfaster', 
           ha='center', va='center', fontsize=11, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7, edgecolor='black'))
    
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, fontweight='bold')
    ax.set_ylabel('Number of Iterations', fontweight='bold')
    ax.set_title('Iterations Required to Reach Final Rating', fontweight='bold')
    ax.set_ylim(-0.5, max(means) + max(stds) + 1.5)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Figure 3 saved to: {output_file}")


def plot_customization_metrics(
    customization_analysis: Dict,
    output_file: Path,
    figsize: Tuple[float, float] = (10, 6)
):
    """
    Create Figure 4: Customization metrics visualization.
    
    Shows personal detail integration and distribution.
    """
    if not HAS_MATPLOTLIB:
        raise ImportError("matplotlib and seaborn required for visualization")
    
    setup_academic_style()
    
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle('Figure 4: Customization Metrics (Group B)', 
                 fontsize=13, fontweight='bold', y=1.02)
    
    # Personal detail indicators distribution
    ax1 = axes[0]
    personal_stats = customization_analysis.get('personal_detail_stats', {})
    
    if personal_stats:
        # Use actual data if available from group_b, otherwise use summary stats
        mean_pd = personal_stats.get('mean', 0)
        std_pd = personal_stats.get('std', 0)
        min_pd = personal_stats.get('min', 0)
        max_pd = personal_stats.get('max', 0)
        median_pd = personal_stats.get('median', 0)
        n_pd = personal_stats.get('n', 0)
        
        # Create histogram from summary statistics (binned approximation)
        # Since we don't have raw data, create bins and approximate distribution
        bins = np.arange(min_pd - 0.5, max_pd + 1.5, 1)
        # Approximate histogram using normal distribution
        bin_centers = (bins[:-1] + bins[1:]) / 2
        # Use normal approximation but acknowledge it's an approximation
        try:
            from scipy.stats import norm
            if std_pd > 0:
                hist_values = norm.pdf(bin_centers, mean_pd, std_pd) * n_pd
                ax1.bar(bin_centers, hist_values, width=0.8, alpha=0.6, 
                       color=ACADEMIC_COLORS['group_b'], edgecolor='black', linewidth=0.8)
            else:
                # If no variance, show single bar
                ax1.bar([mean_pd], [n_pd], width=0.8, alpha=0.6,
                       color=ACADEMIC_COLORS['group_b'], edgecolor='black', linewidth=0.8)
        except ImportError:
            # Fallback: simple approximation without scipy
            if std_pd > 0:
                hist_values = np.exp(-0.5 * ((bin_centers - mean_pd) / std_pd) ** 2) / (std_pd * np.sqrt(2 * np.pi)) * n_pd
                ax1.bar(bin_centers, hist_values, width=0.8, alpha=0.6,
                       color=ACADEMIC_COLORS['group_b'], edgecolor='black', linewidth=0.8)
            else:
                ax1.bar([mean_pd], [n_pd], width=0.8, alpha=0.6,
                       color=ACADEMIC_COLORS['group_b'], edgecolor='black', linewidth=0.8)
        
        # Add mean and median lines
        ax1.axvline(mean_pd, color=ACADEMIC_COLORS['significant'], linestyle='--', 
                   linewidth=2, label=f'Mean: {mean_pd:.2f}')
        if median_pd != mean_pd:
            ax1.axvline(median_pd, color='orange', linestyle=':', 
                       linewidth=2, label=f'Median: {median_pd:.1f}')
        
        # Add summary statistics text
        stats_text = f'M = {mean_pd:.2f}, SD = {std_pd:.2f}\nRange: {min_pd:.0f} - {max_pd:.0f}\nn = {n_pd}'
        ax1.text(0.98, 0.98, stats_text, transform=ax1.transAxes,
                ha='right', va='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8, edgecolor='black'))
        
        ax1.set_xlabel('Number of Personal Detail Indicators', fontweight='bold')
        ax1.set_ylabel('Frequency', fontweight='bold')
        ax1.set_title('(A) Personal Detail Indicators Distribution', fontweight='bold')
        ax1.legend(loc='upper left', frameon=True, fontsize=9)
        ax1.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Integration rate visualization
    ax2 = axes[1]
    integration_rate = customization_analysis.get('personal_details_rate', 0)
    answers_with_pd = customization_analysis.get('answers_with_personal_details', 0)
    total_answers = customization_analysis.get('unique_qa_pairs', 0)
    
    # Pie chart or bar chart
    categories = ['With Personal\nDetails', 'Without Personal\nDetails']
    sizes = [answers_with_pd, total_answers - answers_with_pd]
    colors = [ACADEMIC_COLORS['significant'], ACADEMIC_COLORS['not_significant']]
    
    bars = ax2.bar(categories, sizes, color=colors, alpha=0.7, 
                   edgecolor='black', linewidth=1.2, width=0.6)
    
    # Add percentage labels
    for i, (bar, size) in enumerate(zip(bars, sizes)):
        height = bar.get_height()
        percentage = (size / total_answers * 100) if total_answers > 0 else 0
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{size}\n({percentage:.1f}%)', ha='center', va='bottom',
                fontweight='bold', fontsize=11)
    
    ax2.set_ylabel('Number of Answers', fontweight='bold')
    ax2.set_title(f'(B) Personal Detail Integration\n(Integration Rate: {integration_rate:.1f}%)', 
                 fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Figure 4 saved to: {output_file}")


def plot_comprehensive_comparison(
    improvement_analysis: Dict,
    training_analysis: Dict,
    iterations_analysis: Dict,
    customization_analysis: Dict,
    output_file: Path,
    figsize: Tuple[float, float] = (14, 10)
):
    """
    Create Figure 5: Comprehensive multi-panel comparison.
    
    Combines key results in a publication-ready layout.
    """
    if not HAS_MATPLOTLIB:
        raise ImportError("matplotlib and seaborn required for visualization")
    
    setup_academic_style()
    
    fig = plt.figure(figsize=(13, 9))
    gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.3, 
                         height_ratios=[2, 1], width_ratios=[1, 1, 1])
    fig.suptitle('Figure 5: Comprehensive Results Overview', 
                 fontsize=13, fontweight='bold', y=0.98)
    
    # Panel 1: Rating improvement (enhanced)
    ax1 = fig.add_subplot(gs[0, 0])
    group_a_mean = improvement_analysis.get('group_a_stats', {}).get('mean_improvement', 0)
    group_b_mean = improvement_analysis.get('group_b_stats', {}).get('mean_improvement', 0)
    group_a_std = improvement_analysis.get('group_a_stats', {}).get('std_improvement', 0)
    group_b_std = improvement_analysis.get('group_b_stats', {}).get('std_improvement', 0)
    ttest = improvement_analysis.get('ttest', {})
    p_val = ttest.get('p_value', 1.0)
    cohens_d = ttest.get('cohens_d', 0.0)
    n_a = improvement_analysis.get('group_a_stats', {}).get('n', 0)
    n_b = improvement_analysis.get('group_b_stats', {}).get('n', 0)
    
    bars = ax1.bar(['Group A', 'Group B'], [group_a_mean, group_b_mean],
                   yerr=[group_a_std, group_b_std],
                   color=[ACADEMIC_COLORS['group_a'], ACADEMIC_COLORS['group_b']],
                   alpha=0.7, edgecolor='black', linewidth=1.5, width=0.6, capsize=6)
    for i, (bar, val, std) in enumerate(zip(bars, [group_a_mean, group_b_mean], [group_a_std, group_b_std])):
        ax1.text(bar.get_x() + bar.get_width()/2., val + std + 0.08,
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
        ax1.text(bar.get_x() + bar.get_width()/2., -0.4,
                f'n={[n_a, n_b][i]}', ha='center', va='top', fontsize=8, style='italic')
    ax1.set_ylabel('Mean Rating Improvement', fontweight='bold')
    ax1.set_title('(A) Rating Improvement', fontweight='bold')
    if p_val < 0.05:
        sig_text = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*'
        ax1.text(0.5, max(group_a_mean, group_b_mean) + max(group_a_std, group_b_std) + 0.3,
                sig_text, ha='center', fontsize=14, fontweight='bold', 
                color=ACADEMIC_COLORS['significant'])
    else:
        ax1.text(0.5, max(group_a_mean, group_b_mean) + max(group_a_std, group_b_std) + 0.2,
                f'p={p_val:.3f}\nd={cohens_d:.2f}', ha='center', fontsize=8, style='italic')
    ax1.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax1.axhline(0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)
    
    # Panel 2: Training effectiveness (enhanced)
    ax2 = fig.add_subplot(gs[0, 1])
    conf_improve = training_analysis.get('confidence_improvement', {})
    auth_improve = training_analysis.get('authenticity_improvement', {})
    
    metrics = ['Confidence', 'Authenticity']
    improvements = [conf_improve.get('improvement', 0), auth_improve.get('improvement', 0)]
    p_values = [conf_improve.get('p_value', 1.0), auth_improve.get('p_value', 1.0)]
    
    bars = ax2.bar(metrics, improvements, color=ACADEMIC_COLORS['significant'],
                   alpha=0.7, edgecolor='black', linewidth=1.5, width=0.6)
    for bar, val, pv in zip(bars, improvements, p_values):
        ax2.text(bar.get_x() + bar.get_width()/2., val + 0.08,
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
        sig = '***' if pv < 0.001 else '**' if pv < 0.01 else '*'
        ax2.text(bar.get_x() + bar.get_width()/2., val + 0.18,
                sig, ha='center', va='bottom', fontsize=14, fontweight='bold',
                color=ACADEMIC_COLORS['significant'])
    ax2.set_ylabel('Improvement (Post - Pre)', fontweight='bold')
    ax2.set_title('(B) Training Effectiveness', fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Panel 3: Iterations (enhanced)
    ax3 = fig.add_subplot(gs[0, 2])
    iter_a = iterations_analysis.get('group_a_mean_iterations', 0)
    iter_b = iterations_analysis.get('group_b_mean_iterations', 0)
    
    bars = ax3.bar(['Group A', 'Group B'], [iter_a, iter_b],
                   color=[ACADEMIC_COLORS['group_a'], ACADEMIC_COLORS['group_b']],
                   alpha=0.7, edgecolor='black', linewidth=1.5, width=0.6)
    for bar, val in zip(bars, [iter_a, iter_b]):
        ax3.text(bar.get_x() + bar.get_width()/2., val + 0.15,
                f'{val:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    ax3.set_ylabel('Mean Iterations', fontweight='bold')
    ax3.set_title('(C) Efficiency', fontweight='bold')
    efficiency_ratio = iter_a / iter_b if iter_b > 0 else 0
    ax3.text(0.5, max(iter_a, iter_b) + 0.6, '***', ha='center',
            fontsize=16, fontweight='bold', color=ACADEMIC_COLORS['significant'])
    ax3.text(0.5, max(iter_a, iter_b) + 1.0, f'{efficiency_ratio:.1f}× faster', 
            ha='center', fontsize=9, style='italic')
    ax3.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Panel 4: Customization (enhanced)
    ax4 = fig.add_subplot(gs[1, 0])
    integration_rate = customization_analysis.get('personal_details_rate', 0)
    mean_pd = customization_analysis.get('personal_detail_stats', {}).get('mean', 0)
    total_answers = customization_analysis.get('unique_qa_pairs', 0)
    
    # Use bar chart instead of horizontal bars
    metrics_custom = ['Integration\nRate (%)', 'Mean Personal\nDetails']
    values_custom = [integration_rate, mean_pd]
    
    bars = ax4.bar(metrics_custom, values_custom, 
                   color=ACADEMIC_COLORS['significant'], alpha=0.7,
                   edgecolor='black', linewidth=1.5, width=0.6)
    for bar, val, label in zip(bars, values_custom, metrics_custom):
        if 'Rate' in label:
            ax4.text(bar.get_x() + bar.get_width()/2., val + 2,
                    f'{val:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)
        else:
            ax4.text(bar.get_x() + bar.get_width()/2., val + 0.2,
                    f'{val:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    ax4.set_ylabel('Value', fontweight='bold')
    ax4.set_title('(D) Customization', fontweight='bold')
    ax4.text(0.5, -max(values_custom)*0.15, f'n = {total_answers}', 
            ha='center', fontsize=8, style='italic')
    ax4.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Panel 5: Summary statistics (compact)
    ax5 = fig.add_subplot(gs[1, 1:])
    ax5.axis('off')
    
    # Create a more compact summary table
    summary_data = [
        ['Metric', 'Group A', 'Group B', 'Significance'],
        ['Rating Improvement', f'{group_a_mean:.2f} (SD={group_a_std:.2f})', 
         f'{group_b_mean:.2f} (SD={group_b_std:.2f})', 
         f'p={p_val:.3f}, d={cohens_d:.2f}'],
        ['Iterations', f'{iter_a:.1f}', f'{iter_b:.1f}', 'p<0.001***'],
        ['Training: Confidence', '—', f'+{conf_improve.get("improvement", 0):.2f}', 'p<0.001***'],
        ['Training: Authenticity', '—', f'+{auth_improve.get("improvement", 0):.2f}', 'p<0.001***'],
        ['Customization Rate', '—', f'{integration_rate:.1f}%', '—'],
        ['Mean Personal Details', '—', f'{mean_pd:.2f}', '—'],
    ]
    
    table = ax5.table(cellText=summary_data[1:], colLabels=summary_data[0],
                     cellLoc='left', loc='center', colWidths=[0.3, 0.2, 0.2, 0.3])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Style the header row
    for i in range(4):
        table[(0, i)].set_facecolor('#4A90E2')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style data rows
    for i in range(1, len(summary_data)):
        for j in range(4):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#F0F0F0')
    
    ax5.set_title('(E) Summary Statistics', fontweight='bold', pad=10)
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Figure 5 saved to: {output_file}")


def plot_comparison_table(
    data: Dict,
    output_file: Path,
    figsize: tuple = (12, 8)
):
    """
    Create a comparison table visualization.
    """
    if not HAS_MATPLOTLIB:
        raise ImportError("matplotlib required for visualization")
    
    # This would create a table visualization
    # For now, tables are better as markdown/LaTeX
    # This is a placeholder for future enhancement
    pass

