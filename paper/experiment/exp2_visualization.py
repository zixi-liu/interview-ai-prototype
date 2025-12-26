#!/usr/bin/env python3
"""
Experiment 2 - Visualization

Creates plot for convergence analysis:
- Success Rate by Iteration (line plot)
"""

import json
from pathlib import Path
import matplotlib.pyplot as plt

# Rating score mapping
RATING_SCORES = {
    'No Hire': 0, 'Leaning No Hire': 1, 'No-Pass': 1,
    'Borderline': 2, 'Leaning Hire': 2, 'Weak Hire': 2,
    'Hire': 3, 'Pass': 3, 'Strong Hire': 4,
}

SUCCESS_THRESHOLD = 3  # "Hire" or better


def load_results(results_file: Path) -> list:
    """Load convergence results."""
    with open(results_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_success_rate_by_iteration(results: list, max_iter: int = 10) -> dict:
    """
    Calculate success rate (% reached Hire+) at each iteration for both methods.

    Returns:
        {
            'iterations': [0, 1, 2, ...],
            'automated': [50, 60, 65, ...],  # % success at each iteration
            'human_in_loop': [50, 70, 78, ...]
        }
    """
    # Initialize counters
    auto_success_by_iter = {i: 0 for i in range(max_iter + 1)}
    human_success_by_iter = {i: 0 for i in range(max_iter + 1)}
    auto_count_by_iter = {i: 0 for i in range(max_iter + 1)}
    human_count_by_iter = {i: 0 for i in range(max_iter + 1)}

    for result in results:
        if 'error' in result:
            continue

        # Automated
        if 'automated' in result:
            auto_data = result['automated']
            rating_history = auto_data.get('rating_score_history', [])

            for i, score in enumerate(rating_history):
                if i <= max_iter:
                    auto_count_by_iter[i] += 1
                    if score >= SUCCESS_THRESHOLD:
                        auto_success_by_iter[i] += 1

            # Fill remaining iterations with final value
            final_score = rating_history[-1] if rating_history else 0
            for i in range(len(rating_history), max_iter + 1):
                auto_count_by_iter[i] += 1
                if final_score >= SUCCESS_THRESHOLD:
                    auto_success_by_iter[i] += 1

        # Human-in-loop
        if 'human_in_loop' in result:
            human_data = result['human_in_loop']
            rating_history = human_data.get('rating_score_history', [])

            for i, score in enumerate(rating_history):
                if i <= max_iter:
                    human_count_by_iter[i] += 1
                    if score >= SUCCESS_THRESHOLD:
                        human_success_by_iter[i] += 1

            # Fill remaining iterations with final value
            final_score = rating_history[-1] if rating_history else 0
            for i in range(len(rating_history), max_iter + 1):
                human_count_by_iter[i] += 1
                if final_score >= SUCCESS_THRESHOLD:
                    human_success_by_iter[i] += 1

    # Calculate percentages
    iterations = list(range(max_iter + 1))
    auto_rates = []
    human_rates = []

    for i in iterations:
        if auto_count_by_iter[i] > 0:
            auto_rates.append(100 * auto_success_by_iter[i] / auto_count_by_iter[i])
        else:
            auto_rates.append(0)

        if human_count_by_iter[i] > 0:
            human_rates.append(100 * human_success_by_iter[i] / human_count_by_iter[i])
        else:
            human_rates.append(0)

    return {
        'iterations': iterations,
        'automated': auto_rates,
        'human_in_loop': human_rates,
    }


def plot_success_rate_by_iteration(results: list, output_file: Path, max_iter: int = 6):
    """
    Plot success rate by iteration for both methods.
    Main result showing convergence behavior.
    """
    data = calculate_success_rate_by_iteration(results, max_iter)

    plt.figure(figsize=(10, 6))

    # Plot lines
    plt.plot(data['iterations'], data['automated'],
             'o-', color='#2196F3', linewidth=2, markersize=8,
             label='Automated (CoT only)')
    plt.plot(data['iterations'], data['human_in_loop'],
             's-', color='#4CAF50', linewidth=2, markersize=8,
             label='Human-in-Loop (CoT + Context)')

    # Styling
    plt.xlabel('Iteration', fontsize=12)
    plt.ylabel('Success Rate (% Reached Hire or Better)', fontsize=12)
    plt.title('Convergence Analysis: Success Rate by Iteration', fontsize=14)
    plt.legend(loc='lower right', fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 100)
    plt.xlim(0, max_iter)
    plt.xticks(range(max_iter + 1))

    # Add annotations for final values
    auto_final = data['automated'][max_iter]
    human_final = data['human_in_loop'][max_iter]
    plt.annotate(f'{auto_final:.0f}%',
                 xy=(max_iter, auto_final),
                 xytext=(max_iter - 0.5, auto_final - 8),
                 fontsize=10, color='#2196F3')
    plt.annotate(f'{human_final:.0f}%',
                 xy=(max_iter, human_final),
                 xytext=(max_iter - 0.5, human_final + 5),
                 fontsize=10, color='#4CAF50')

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Saved: {output_file}")

    # Print data table
    print("\nSuccess Rate by Iteration:")
    print(f"{'Iter':<6} {'Automated':<12} {'Human-in-Loop':<12}")
    print("-" * 30)
    for i in range(min(max_iter + 1, len(data['iterations']))):
        print(f"{i:<6} {data['automated'][i]:<12.1f} {data['human_in_loop'][i]:<12.1f}")


def main():
    """Generate visualization."""
    script_dir = Path(__file__).parent
    results_dir = script_dir / 'exp2_results'
    results_file = results_dir / 'exp2_convergence_results.json'

    if not results_file.exists():
        print(f"Error: {results_file} not found!")
        print("Please run exp2_convergence.py first.")
        return

    # Load results
    results = load_results(results_file)
    print(f"Loaded {len(results)} results")

    # Create output directory for analysis
    analysis_dir = results_dir / 'analysis'
    analysis_dir.mkdir(exist_ok=True)

    # Generate plot
    print("\n" + "="*60)
    print("Generating Exp 2 Visualization")
    print("="*60)

    plot_success_rate_by_iteration(
        results,
        analysis_dir / 'exp2_success_rate_by_iteration.png',
        max_iter=6
    )

    print("\n" + "="*60)
    print(f"Figure saved to: {analysis_dir}")
    print("="*60)


if __name__ == '__main__':
    main()
