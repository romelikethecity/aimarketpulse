#!/usr/bin/env python3
"""
PE Collective - Insights Chart Generator
========================================

Generates visualization charts for the insights page:
- Tools & frameworks usage heatmap
- Industry hiring breakdown
- Buzzwords frequency chart
- Skills demand chart

Outputs to site/assets/ for the website.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import os
import glob
from collections import Counter

# ============================================================
# CONFIGURATION
# ============================================================
DATA_DIR = "data"
SITE_ASSETS = "site/assets"

os.makedirs(SITE_ASSETS, exist_ok=True)

# Brand colors (PE Collective)
COLORS = {
    'bg': '#1f2937',
    'cyan': '#22d3ee',
    'gold': '#f5a623',
    'green': '#10b981',
    'purple': '#a855f7',
    'pink': '#ec4899',
    'text': '#e5e7eb',
    'gray': '#9ca3af',
    'grid': '#374151',
}

# Color palette for bars
BAR_COLORS = ['#22d3ee', '#10b981', '#f5a623', '#a855f7', '#ec4899', '#3b82f6', '#ef4444', '#14b8a6']


def setup_style():
    """Setup matplotlib style."""
    plt.style.use('dark_background')
    plt.rcParams['figure.facecolor'] = COLORS['bg']
    plt.rcParams['axes.facecolor'] = COLORS['bg']
    plt.rcParams['axes.edgecolor'] = COLORS['grid']
    plt.rcParams['axes.labelcolor'] = COLORS['text']
    plt.rcParams['text.color'] = COLORS['text']
    plt.rcParams['xtick.color'] = COLORS['gray']
    plt.rcParams['ytick.color'] = COLORS['gray']
    plt.rcParams['grid.color'] = COLORS['grid']


def load_market_intelligence():
    """Load market intelligence data."""
    intel_file = f"{DATA_DIR}/market_intelligence.json"
    if os.path.exists(intel_file):
        with open(intel_file) as f:
            return json.load(f)
    return None


def load_jobs_data():
    """Load latest jobs data."""
    job_files = glob.glob(f"{DATA_DIR}/ai_jobs_*.csv")
    if not job_files:
        return None
    latest_file = sorted(job_files)[-1]
    return pd.read_csv(latest_file)


def create_tools_chart(intel):
    """Create horizontal bar chart of most mentioned tools/frameworks."""
    if not intel or 'skills' not in intel:
        print("  No skills data available")
        return

    setup_style()
    fig, ax = plt.subplots(figsize=(12, 10), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])

    # Get top 15 skills
    skills = dict(sorted(intel['skills'].items(), key=lambda x: x[1], reverse=True)[:15])

    # Reverse for horizontal bar chart (highest at top)
    labels = list(skills.keys())[::-1]
    values = list(skills.values())[::-1]

    # Create gradient colors based on position
    colors = [COLORS['cyan'] if i % 2 == 0 else COLORS['green'] for i in range(len(labels))]

    bars = ax.barh(labels, values, color=colors, alpha=0.85)

    # Add value labels
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
               f'{val}', va='center', fontsize=12, color=COLORS['gold'], fontweight='bold')

    ax.set_xlabel('Number of Job Postings', fontsize=14, color=COLORS['text'])
    ax.set_title('Most In-Demand AI Tools & Skills', fontsize=22, fontweight='bold',
                color=COLORS['text'], pad=20)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=12)
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    output_path = f"{SITE_ASSETS}/insights_tools.png"
    plt.savefig(output_path, dpi=150, facecolor=COLORS['bg'], bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")


def create_skills_by_category_chart(intel):
    """Create grouped bar chart showing skills by category."""
    if not intel or 'skills_by_category' not in intel:
        print("  No skills by category data available")
        return

    setup_style()
    fig, axes = plt.subplots(2, 3, figsize=(18, 12), facecolor=COLORS['bg'])
    axes = axes.flatten()

    categories = ['LLM Providers', 'LLM Frameworks', 'Techniques', 'Vector Databases', 'ML Frameworks', 'Cloud/Infrastructure']
    cat_colors = [COLORS['cyan'], COLORS['green'], COLORS['gold'], COLORS['purple'], COLORS['pink'], '#3b82f6']

    for idx, (cat, color) in enumerate(zip(categories, cat_colors)):
        ax = axes[idx]
        ax.set_facecolor(COLORS['bg'])

        if cat in intel['skills_by_category']:
            skills = intel['skills_by_category'][cat]
            # Get top 6 for this category
            sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)[:6]
            labels = [s[0] for s in sorted_skills][::-1]
            values = [s[1] for s in sorted_skills][::-1]

            bars = ax.barh(labels, values, color=color, alpha=0.85)

            for bar, val in zip(bars, values):
                ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                       f'{val}', va='center', fontsize=10, color=COLORS['gold'])
        else:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)

        ax.set_title(cat, fontsize=14, fontweight='bold', color=COLORS['text'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(labelsize=10)
        ax.grid(axis='x', alpha=0.3)

    plt.suptitle('Skills Breakdown by Category', fontsize=24, fontweight='bold',
                color=COLORS['text'], y=1.02)
    plt.tight_layout()
    output_path = f"{SITE_ASSETS}/insights_skills_categories.png"
    plt.savefig(output_path, dpi=150, facecolor=COLORS['bg'], bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")


def create_buzzwords_chart(intel):
    """Create word cloud style chart of buzzwords."""
    if not intel or 'buzzwords' not in intel:
        print("  No buzzwords data available")
        return

    setup_style()
    fig, ax = plt.subplots(figsize=(12, 8), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])

    buzzwords = intel.get('buzzwords', {})
    if not buzzwords:
        print("  No buzzwords found")
        return

    # Get top 12 buzzwords
    sorted_buzz = sorted(buzzwords.items(), key=lambda x: x[1], reverse=True)[:12]
    labels = [b[0] for b in sorted_buzz][::-1]
    values = [b[1] for b in sorted_buzz][::-1]

    colors = [BAR_COLORS[i % len(BAR_COLORS)] for i in range(len(labels))]

    bars = ax.barh(labels, values, color=colors, alpha=0.85)

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
               f'{val}', va='center', fontsize=12, color=COLORS['gold'], fontweight='bold')

    ax.set_xlabel('Mentions in Job Postings', fontsize=14, color=COLORS['text'])
    ax.set_title('Common Buzzwords in AI Job Postings', fontsize=22, fontweight='bold',
                color=COLORS['text'], pad=20)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=12)
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    output_path = f"{SITE_ASSETS}/insights_buzzwords.png"
    plt.savefig(output_path, dpi=150, facecolor=COLORS['bg'], bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")


def create_categories_pie_chart(intel):
    """Create pie chart of job categories."""
    if not intel or 'categories' not in intel:
        print("  No categories data available")
        return

    setup_style()
    fig, ax = plt.subplots(figsize=(12, 10), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])

    categories = intel['categories']
    if not categories:
        return

    # Get top 8 categories
    sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:8]
    labels = [c[0] for c in sorted_cats]
    values = [c[1] for c in sorted_cats]

    colors = BAR_COLORS[:len(labels)]

    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct='%1.1f%%',
        colors=colors,
        textprops={'color': COLORS['text'], 'fontsize': 12},
        startangle=90,
        pctdistance=0.75
    )

    for autotext in autotexts:
        autotext.set_color(COLORS['bg'])
        autotext.set_fontweight('bold')
        autotext.set_fontsize(11)

    ax.set_title('AI Jobs by Role Type', fontsize=22, fontweight='bold',
                color=COLORS['text'], pad=20)

    plt.tight_layout()
    output_path = f"{SITE_ASSETS}/insights_categories.png"
    plt.savefig(output_path, dpi=150, facecolor=COLORS['bg'], bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")


def create_red_flags_chart(intel):
    """Create chart showing red flags in job postings."""
    if not intel or 'red_flags' not in intel:
        print("  No red flags data available")
        return

    setup_style()
    fig, ax = plt.subplots(figsize=(12, 6), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])

    red_flags = intel.get('red_flags', {})
    if not red_flags:
        print("  No red flags found")
        return

    # Format labels nicely
    label_map = {
        'vague_compensation': 'Vague Compensation',
        'unrealistic_requirements': 'Unrealistic Requirements',
        'overwork_signals': 'Overwork Signals',
        'vague_role': 'Vague Role Description'
    }

    labels = [label_map.get(k, k) for k in red_flags.keys()]
    values = list(red_flags.values())

    # Sort by value
    sorted_data = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
    labels = [x[0] for x in sorted_data][::-1]
    values = [x[1] for x in sorted_data][::-1]

    bars = ax.barh(labels, values, color='#ef4444', alpha=0.85)

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
               f'{val}', va='center', fontsize=14, color=COLORS['gold'], fontweight='bold')

    ax.set_xlabel('Number of Job Postings', fontsize=14, color=COLORS['text'])
    ax.set_title('Red Flags in AI Job Postings', fontsize=22, fontweight='bold',
                color=COLORS['text'], pad=20)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=14)
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    output_path = f"{SITE_ASSETS}/insights_red_flags.png"
    plt.savefig(output_path, dpi=150, facecolor=COLORS['bg'], bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")


def create_remote_chart(intel):
    """Create pie chart of remote vs onsite breakdown."""
    if not intel or 'remote_breakdown' not in intel:
        print("  No remote breakdown data available")
        return

    setup_style()
    fig, ax = plt.subplots(figsize=(10, 10), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])

    remote = intel['remote_breakdown']
    if not remote:
        return

    labels = list(remote.keys())
    values = list(remote.values())

    colors = [COLORS['cyan'], COLORS['green'], COLORS['purple']][:len(labels)]

    wedges, texts, autotexts = ax.pie(
        values,
        labels=[l.title() for l in labels],
        autopct='%1.1f%%',
        colors=colors,
        textprops={'color': COLORS['text'], 'fontsize': 14},
        startangle=90
    )

    for autotext in autotexts:
        autotext.set_color(COLORS['bg'])
        autotext.set_fontweight('bold')
        autotext.set_fontsize(14)

    ax.set_title('Remote Work Distribution', fontsize=22, fontweight='bold',
                color=COLORS['text'], pad=20)

    plt.tight_layout()
    output_path = f"{SITE_ASSETS}/insights_remote.png"
    plt.savefig(output_path, dpi=150, facecolor=COLORS['bg'], bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")


def create_metros_chart(intel):
    """Create horizontal bar chart of top hiring locations."""
    if not intel or 'top_metros' not in intel:
        print("  No metros data available")
        return

    setup_style()
    fig, ax = plt.subplots(figsize=(12, 8), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])

    metros = intel['top_metros']
    if not metros:
        return

    labels = list(metros.keys())[::-1]
    values = list(metros.values())[::-1]

    colors = [BAR_COLORS[i % len(BAR_COLORS)] for i in range(len(labels))]

    bars = ax.barh(labels, values, color=colors, alpha=0.85)

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
               f'{val}', va='center', fontsize=12, color=COLORS['gold'], fontweight='bold')

    ax.set_xlabel('Number of Jobs', fontsize=14, color=COLORS['text'])
    ax.set_title('Top Hiring Locations for AI Roles', fontsize=22, fontweight='bold',
                color=COLORS['text'], pad=20)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=12)
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    output_path = f"{SITE_ASSETS}/insights_metros.png"
    plt.savefig(output_path, dpi=150, facecolor=COLORS['bg'], bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")


# ============================================================
# MAIN EXECUTION
# ============================================================
def main():
    print("="*70)
    print("  PE COLLECTIVE - INSIGHTS CHART GENERATOR")
    print("="*70)

    # Load market intelligence
    print("\n Loading market intelligence data...")
    intel = load_market_intelligence()

    if not intel:
        print("  No market intelligence data found.")
        print("  Run enrich_jobs.py first to generate market_intelligence.json")
        return

    print(f"  Loaded data for {intel.get('total_jobs', 0)} jobs")

    # Generate all charts
    print(f"\n{'GENERATING INSIGHT CHARTS':-^70}")

    print("\n1. Tools & Skills Chart")
    create_tools_chart(intel)

    print("\n2. Skills by Category Chart")
    create_skills_by_category_chart(intel)

    print("\n3. Buzzwords Chart")
    create_buzzwords_chart(intel)

    print("\n4. Job Categories Pie Chart")
    create_categories_pie_chart(intel)

    print("\n5. Red Flags Chart")
    create_red_flags_chart(intel)

    print("\n6. Remote Work Chart")
    create_remote_chart(intel)

    print("\n7. Top Metros Chart")
    create_metros_chart(intel)

    print(f"\n{'='*70}")
    print("  ALL INSIGHT CHARTS GENERATED!")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
