"""
Visualization utilities for Experiment 1.

Provides functions for creating plots and figures.
Requires matplotlib and seaborn.
"""

import numpy as np
from pathlib import Path
from typing import List, Dict, Optional

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib/seaborn not available. Install with: pip install matplotlib seaborn")


def plot_rating_improvement_distribution(
    group_a: List[Dict],
    group_b: List[Dict],
    output_file: Path,
    figsize: tuple = (10, 6)
):
    """
    Create Figure 1: Rating improvement distribution.
    
    Shows distribution of rating improvements for Group A vs Group B.
    """
    if not HAS_MATPLOTLIB:
        raise ImportError("matplotlib and seaborn required for visualization")
    
    # Extract improvements
    group_a_improvements = [r['rating_improvement'] for r in group_a 
                           if 'error' not in r and 'rating_improvement' in r]
    group_b_improvements = [r['rating_improvement'] for r in group_b 
                           if 'error' not in r and 'rating_improvement' in r]
    
    if not group_a_improvements or not group_b_improvements:
        raise ValueError("Insufficient data for visualization")
    
    # Create figure
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle('Figure 1: Rating Improvement Distribution', fontsize=14, fontweight='bold')
    
    # Histogram
    ax1 = axes[0]
    ax1.hist(group_a_improvements, bins=10, alpha=0.7, label='Group A (Automated)', color='blue')
    ax1.hist(group_b_improvements, bins=10, alpha=0.7, label='Group B (Human-in-Loop)', color='orange')
    ax1.set_xlabel('Rating Improvement')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Distribution of Rating Improvements')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Box plot
    ax2 = axes[1]
    data_to_plot = [group_a_improvements, group_b_improvements]
    bp = ax2.boxplot(data_to_plot, labels=['Group A\n(Automated)', 'Group B\n(Human-in-Loop)'],
                     patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][1].set_facecolor('lightcoral')
    ax2.set_ylabel('Rating Improvement')
    ax2.set_title('Box Plot Comparison')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Figure saved to: {output_file}")


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

