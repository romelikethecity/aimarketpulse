#!/usr/bin/env python3
"""
PE Collective - AI Jobs Compensation Aggregator & Analyzer
==========================================================

This script analyzes AI job salary data and generates compensation
benchmarking analysis for the newsletter and website.

Usage:
    1. Analysis: python ai_comp_aggregator.py --analyze
    2. Newsletter: python ai_comp_aggregator.py --newsletter
    3. Charts: python ai_comp_aggregator.py --charts

The script reads from the master jobs database and generates:
- comp_analysis.json - Detailed compensation data
- comp_newsletter_section.md - Newsletter-ready markdown
- comp_by_*.png - Visualization charts
"""

import pandas as pd
import numpy as np
import sys
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import json
import glob
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================
DATA_DIR = Path("data")
SITE_ASSETS = Path("site/assets")
MASTER_DB = DATA_DIR / "master_jobs_database.csv"
ANALYSIS_OUTPUT = DATA_DIR / "comp_analysis.json"
NEWSLETTER_OUTPUT = DATA_DIR / "comp_newsletter_section.md"

# Chart output paths
CHART_CATEGORY = SITE_ASSETS / "comp_by_category.png"
CHART_SENIORITY = SITE_ASSETS / "comp_by_seniority.png"
CHART_LOCATION = SITE_ASSETS / "comp_by_location.png"

# ============================================================
# CHART STYLING (PE Collective brand)
# ============================================================
DARK_BG = '#1f2937'
CYAN = '#22d3ee'
GOLD = '#f5a623'
WHITE = '#e5e7eb'
GRAY = '#9ca3af'
GRID_COLOR = '#374151'


def setup_chart_style():
    """Set up dark theme matching PE Collective brand."""
    import matplotlib.pyplot as plt
    plt.rcParams['figure.facecolor'] = DARK_BG
    plt.rcParams['axes.facecolor'] = DARK_BG
    plt.rcParams['axes.edgecolor'] = GRID_COLOR
    plt.rcParams['axes.labelcolor'] = WHITE
    plt.rcParams['text.color'] = WHITE
    plt.rcParams['xtick.color'] = GRAY
    plt.rcParams['ytick.color'] = GRAY
    plt.rcParams['grid.color'] = GRID_COLOR
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.size'] = 16


def generate_category_chart(analysis):
    """Create horizontal bar chart for comp by job category."""
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    if not analysis.get('by_category'):
        print("  No category data available for chart")
        return

    setup_chart_style()
    fig, ax = plt.subplots(figsize=(14, 10), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)

    # Prepare data - sort by max salary
    categories = []
    mins = []
    maxs = []
    samples = []

    sorted_cats = sorted(analysis['by_category'].items(),
                        key=lambda x: x[1]['max_base_avg'], reverse=True)

    for cat, data in sorted_cats[:10]:  # Top 10 categories
        categories.append(cat)
        mins.append(data['min_base_avg'])
        maxs.append(data['max_base_avg'])
        samples.append(data['count'])

    # Reverse for display (highest at top)
    categories = categories[::-1]
    mins = mins[::-1]
    maxs = maxs[::-1]
    samples = samples[::-1]

    y_pos = np.arange(len(categories))

    # Draw range bars
    for i, (cat, min_val, max_val, n) in enumerate(zip(categories, mins, maxs, samples)):
        ax.barh(i, max_val - min_val, left=min_val, height=0.5, color=CYAN, alpha=0.8)
        ax.scatter(min_val, i, color=CYAN, s=120, zorder=5)
        ax.scatter(max_val, i, color=GOLD, s=120, zorder=5)
        ax.text(min_val - 15000, i, f'${min_val/1000:.0f}K', ha='right', va='center',
               color=WHITE, fontsize=14, fontweight='bold')
        ax.text(max_val + 15000, i, f'${max_val/1000:.0f}K', ha='left', va='center',
               color=WHITE, fontsize=14, fontweight='bold')
        ax.text(max_val + 80000, i, f'n={n}', ha='left', va='center', color=GRAY, fontsize=12)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories, fontsize=14, fontweight='bold', color=WHITE)
    ax.set_xlabel('Salary Range', fontsize=16, color=GRAY)
    ax.set_title('AI Job Compensation by Role Type', fontsize=24, color=WHITE, pad=20, fontweight='bold')

    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
    ax.tick_params(axis='x', labelsize=14)
    ax.grid(axis='x', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    min_patch = mpatches.Patch(color=CYAN, label='Min Salary (Avg)')
    max_patch = mpatches.Patch(color=GOLD, label='Max Salary (Avg)')
    ax.legend(handles=[min_patch, max_patch], loc='lower right',
             facecolor=DARK_BG, edgecolor=GRID_COLOR, fontsize=12)

    plt.tight_layout()
    plt.savefig(CHART_CATEGORY, dpi=150, facecolor=DARK_BG, edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {CHART_CATEGORY}")


def generate_seniority_chart(analysis):
    """Create horizontal bar chart for comp by seniority."""
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    if not analysis.get('by_seniority'):
        print("  No seniority data available for chart")
        return

    setup_chart_style()
    fig, ax = plt.subplots(figsize=(14, 8), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)

    # Prepare data
    levels = []
    mins = []
    maxs = []
    samples = []

    # Order: Entry -> Mid -> Senior -> Director -> VP -> C-Level
    seniority_order = ['Entry', 'Mid', 'Senior', 'Director', 'VP', 'C-Level']
    for level in seniority_order:
        if level in analysis['by_seniority']:
            levels.append(level)
            mins.append(analysis['by_seniority'][level]['min_base_avg'])
            maxs.append(analysis['by_seniority'][level]['max_base_avg'])
            samples.append(analysis['by_seniority'][level]['count'])

    y_pos = np.arange(len(levels))

    # Draw range bars
    for i, (level, min_val, max_val, n) in enumerate(zip(levels, mins, maxs, samples)):
        ax.barh(i, max_val - min_val, left=min_val, height=0.5, color=CYAN, alpha=0.8)
        ax.scatter(min_val, i, color=CYAN, s=150, zorder=5)
        ax.scatter(max_val, i, color=GOLD, s=150, zorder=5)
        ax.text(min_val - 15000, i, f'${min_val/1000:.0f}K', ha='right', va='center',
               color=WHITE, fontsize=16, fontweight='bold')
        ax.text(max_val + 15000, i, f'${max_val/1000:.0f}K', ha='left', va='center',
               color=WHITE, fontsize=16, fontweight='bold')
        ax.text(max_val + 80000, i, f'n={n}', ha='left', va='center', color=GRAY, fontsize=14)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(levels, fontsize=18, fontweight='bold', color=WHITE)
    ax.set_xlabel('Salary Range', fontsize=16, color=GRAY)
    ax.set_title('AI Job Compensation by Seniority', fontsize=24, color=WHITE, pad=20, fontweight='bold')

    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
    ax.tick_params(axis='x', labelsize=14)
    ax.grid(axis='x', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    min_patch = mpatches.Patch(color=CYAN, label='Min Salary (Avg)')
    max_patch = mpatches.Patch(color=GOLD, label='Max Salary (Avg)')
    ax.legend(handles=[min_patch, max_patch], loc='lower right',
             facecolor=DARK_BG, edgecolor=GRID_COLOR, fontsize=14)

    plt.tight_layout()
    plt.savefig(CHART_SENIORITY, dpi=150, facecolor=DARK_BG, edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {CHART_SENIORITY}")


def generate_location_chart(analysis):
    """Create horizontal bar chart for comp by location."""
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    if not analysis.get('by_metro'):
        print("  No location data available for chart")
        return

    setup_chart_style()
    fig, ax = plt.subplots(figsize=(14, 9), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)

    # Sort by max salary descending
    sorted_locations = sorted(analysis['by_metro'].items(),
                             key=lambda x: x[1]['max_base_avg'], reverse=True)

    locations = [l[0] for l in sorted_locations[:10]]
    mins = [l[1]['min_base_avg'] for l in sorted_locations[:10]]
    maxs = [l[1]['max_base_avg'] for l in sorted_locations[:10]]
    samples = [l[1]['count'] for l in sorted_locations[:10]]

    # Reverse for display
    locations = locations[::-1]
    mins = mins[::-1]
    maxs = maxs[::-1]
    samples = samples[::-1]

    y_pos = np.arange(len(locations))

    for i, (loc, min_val, max_val, n) in enumerate(zip(locations, mins, maxs, samples)):
        ax.barh(i, max_val - min_val, left=min_val, height=0.5, color=CYAN, alpha=0.8)
        ax.scatter(min_val, i, color=CYAN, s=150, zorder=5)
        ax.scatter(max_val, i, color=GOLD, s=150, zorder=5)
        ax.text(min_val - 15000, i, f'${min_val/1000:.0f}K', ha='right', va='center',
               color=WHITE, fontsize=16, fontweight='bold')
        ax.text(max_val + 15000, i, f'${max_val/1000:.0f}K', ha='left', va='center',
               color=WHITE, fontsize=16, fontweight='bold')
        ax.text(max_val + 80000, i, f'n={n}', ha='left', va='center', color=GRAY, fontsize=14)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(locations, fontsize=16, fontweight='bold', color=WHITE)
    ax.set_xlabel('Salary Range', fontsize=16, color=GRAY)
    ax.set_title('AI Job Compensation by Location', fontsize=24, color=WHITE, pad=20, fontweight='bold')

    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
    ax.tick_params(axis='x', labelsize=14)
    ax.grid(axis='x', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    min_patch = mpatches.Patch(color=CYAN, label='Min Salary (Avg)')
    max_patch = mpatches.Patch(color=GOLD, label='Max Salary (Avg)')
    ax.legend(handles=[min_patch, max_patch], loc='lower right',
             facecolor=DARK_BG, edgecolor=GRID_COLOR, fontsize=14)

    plt.tight_layout()
    plt.savefig(CHART_LOCATION, dpi=150, facecolor=DARK_BG, edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {CHART_LOCATION}")


def generate_all_charts(analysis):
    """Generate all compensation benchmark charts."""
    print("\nGenerating charts...")
    SITE_ASSETS.mkdir(parents=True, exist_ok=True)
    generate_category_chart(analysis)
    generate_seniority_chart(analysis)
    generate_location_chart(analysis)


# ============================================================
# DATA MANAGEMENT
# ============================================================
def initialize_data_dir():
    """Create data and site/assets directories if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SITE_ASSETS.mkdir(parents=True, exist_ok=True)


def load_job_data():
    """Load job data from master database or latest enriched file."""
    # Try master database first
    if MASTER_DB.exists():
        df = pd.read_csv(MASTER_DB)
        print(f"  Loaded master database: {len(df)} records")
        return df

    # Fall back to latest enriched file
    job_files = glob.glob(str(DATA_DIR / "ai_jobs_*.csv"))
    if job_files:
        latest_file = sorted(job_files)[-1]
        df = pd.read_csv(latest_file)
        print(f"  Loaded {latest_file}: {len(df)} records")
        return df

    print("  No job data found")
    return pd.DataFrame()


# ============================================================
# COMPENSATION ANALYSIS
# ============================================================
def analyze_compensation(df):
    """Generate comprehensive compensation analysis for AI jobs."""

    # Filter to records with salary data
    salary_df = df[
        (df['salary_max'].notna()) &
        (pd.to_numeric(df['salary_max'], errors='coerce') > 50000) &
        (pd.to_numeric(df['salary_max'], errors='coerce') < 1000000)
    ].copy()

    salary_df['salary_min'] = pd.to_numeric(salary_df['salary_min'], errors='coerce').fillna(0)
    salary_df['salary_max'] = pd.to_numeric(salary_df['salary_max'], errors='coerce')
    salary_df['midpoint'] = (salary_df['salary_min'] + salary_df['salary_max']) / 2

    print(f"  {len(salary_df)} jobs with valid salary data (out of {len(df)} total)")

    analysis = {
        'generated_at': datetime.now().isoformat(),
        'total_records': len(df),
        'records_with_salary': len(salary_df),
        'disclosure_rate': round(len(salary_df) / len(df) * 100, 1) if len(df) > 0 else 0,
        'by_category': {},
        'by_seniority': {},
        'by_metro': {},
        'by_remote': {},
        'top_paying_roles': [],
        'overall_stats': {}
    }

    # Overall stats
    if len(salary_df) > 0:
        analysis['overall_stats'] = {
            'min_salary_avg': round(salary_df['salary_min'].mean()),
            'max_salary_avg': round(salary_df['salary_max'].mean()),
            'median_salary': round(salary_df['salary_max'].median()),
            'p25': round(salary_df['salary_max'].quantile(0.25)),
            'p75': round(salary_df['salary_max'].quantile(0.75)),
            'p90': round(salary_df['salary_max'].quantile(0.90)),
        }

    # By Job Category
    if 'job_category' in salary_df.columns:
        for category in salary_df['job_category'].unique():
            cat_df = salary_df[salary_df['job_category'] == category]
            if len(cat_df) >= 3:
                analysis['by_category'][category] = {
                    'count': len(cat_df),
                    'min_base_avg': round(cat_df['salary_min'].mean()),
                    'max_base_avg': round(cat_df['salary_max'].mean()),
                    'median': round(cat_df['salary_max'].median()),
                }

    # By Seniority
    if 'seniority' in salary_df.columns:
        for seniority in salary_df['seniority'].unique():
            sen_df = salary_df[salary_df['seniority'] == seniority]
            if len(sen_df) >= 3:
                analysis['by_seniority'][seniority] = {
                    'count': len(sen_df),
                    'min_base_avg': round(sen_df['salary_min'].mean()),
                    'max_base_avg': round(sen_df['salary_max'].mean()),
                    'median': round(sen_df['salary_max'].median()),
                }

    # By Metro
    if 'metro' in salary_df.columns:
        for metro in salary_df['metro'].dropna().unique():
            if metro and metro != 'Unknown':
                metro_df = salary_df[salary_df['metro'] == metro]
                if len(metro_df) >= 3:
                    analysis['by_metro'][metro] = {
                        'count': len(metro_df),
                        'min_base_avg': round(metro_df['salary_min'].mean()),
                        'max_base_avg': round(metro_df['salary_max'].mean()),
                        'median': round(metro_df['salary_max'].median()),
                    }

    # By Remote
    if 'remote_type' in salary_df.columns:
        for remote_type in salary_df['remote_type'].unique():
            remote_df = salary_df[salary_df['remote_type'] == remote_type]
            if len(remote_df) >= 3:
                analysis['by_remote'][remote_type] = {
                    'count': len(remote_df),
                    'min_base_avg': round(remote_df['salary_min'].mean()),
                    'max_base_avg': round(remote_df['salary_max'].mean()),
                    'median': round(remote_df['salary_max'].median()),
                }

    # Top Paying Roles
    top_cols = ['title', 'company', 'salary_min', 'salary_max', 'job_category', 'seniority']
    available_cols = [c for c in top_cols if c in salary_df.columns]
    top_roles = salary_df.nlargest(10, 'salary_max')[available_cols]
    analysis['top_paying_roles'] = top_roles.to_dict('records')

    # Save analysis
    with open(ANALYSIS_OUTPUT, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)

    print(f"  Analysis saved to {ANALYSIS_OUTPUT}")
    return analysis


# ============================================================
# NEWSLETTER SECTION GENERATOR
# ============================================================
def generate_newsletter_section(analysis):
    """Generate markdown section for newsletter."""

    md = f"""# AI Jobs Compensation Report

**Data as of {datetime.now().strftime('%B %d, %Y')}** | {analysis['records_with_salary']} roles with disclosed salary out of {analysis['total_records']} total ({analysis['disclosure_rate']}% disclosure rate)

"""

    # Overall Stats
    if analysis.get('overall_stats'):
        stats = analysis['overall_stats']
        md += f"""## Market Overview

- **Average Max Salary**: ${stats['max_salary_avg']:,}
- **Median Salary**: ${stats['median_salary']:,}
- **75th Percentile**: ${stats['p75']:,}
- **90th Percentile**: ${stats['p90']:,}

"""

    # By Category
    if analysis['by_category']:
        md += "## Compensation by Role Type\n\n"

        sorted_cats = sorted(analysis['by_category'].items(),
                            key=lambda x: x[1]['max_base_avg'], reverse=True)

        for cat, data in sorted_cats[:8]:
            md += f"**{cat}** (n={data['count']}): ${data['min_base_avg']:,}-${data['max_base_avg']:,}\n\n"

    # By Seniority
    if analysis['by_seniority']:
        md += "## Compensation by Seniority\n\n"

        seniority_order = ['Entry', 'Mid', 'Senior', 'Director', 'VP', 'C-Level']
        for level in seniority_order:
            if level in analysis['by_seniority']:
                data = analysis['by_seniority'][level]
                md += f"**{level}** (n={data['count']}): ${data['min_base_avg']:,}-${data['max_base_avg']:,}\n\n"

    # By Location
    if analysis['by_metro']:
        md += "## Compensation by Location\n\n"

        sorted_metros = sorted(analysis['by_metro'].items(),
                              key=lambda x: x[1]['max_base_avg'], reverse=True)

        for metro, data in sorted_metros[:6]:
            md += f"**{metro}** (n={data['count']}): ${data['min_base_avg']:,}-${data['max_base_avg']:,}\n\n"

    # Remote Analysis
    if analysis['by_remote']:
        md += "## Remote vs On-site\n\n"
        for remote_type, data in analysis['by_remote'].items():
            md += f"**{remote_type.title()}** (n={data['count']}): ${data['min_base_avg']:,}-${data['max_base_avg']:,}\n\n"

    # Top Paying Roles
    if analysis.get('top_paying_roles'):
        md += "## Highest Paying AI Roles This Week\n\n"

        for i, role in enumerate(analysis['top_paying_roles'][:5], 1):
            company = role.get('company', 'Undisclosed')
            if pd.isna(company) or not company:
                company = 'Undisclosed'
            sal_min = role.get('salary_min', 0)
            sal_max = role.get('salary_max', 0)
            md += f"{i}. **${sal_min:,.0f}-${sal_max:,.0f}**: {role['title']} @ {company}\n\n"

    md += """
---
*This analysis is based on disclosed salaries from PE Collective job listings. Actual offers may vary based on experience, skills, and negotiation.*
"""

    # Save
    with open(NEWSLETTER_OUTPUT, 'w') as f:
        f.write(md)

    print(f"  Newsletter section saved to {NEWSLETTER_OUTPUT}")
    return md


# ============================================================
# MAIN CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='PE Collective AI Jobs Compensation Analyzer')
    parser.add_argument('--analyze', action='store_true', help='Run compensation analysis')
    parser.add_argument('--newsletter', action='store_true', help='Generate newsletter section')
    parser.add_argument('--charts', action='store_true', help='Generate compensation charts')
    parser.add_argument('--all', action='store_true', help='Run analysis, generate charts and newsletter')
    parser.add_argument('--status', action='store_true', help='Show data status')

    args = parser.parse_args()

    print("="*70)
    print("  PE COLLECTIVE - COMPENSATION ANALYZER")
    print("="*70)

    initialize_data_dir()

    if args.all or (not any([args.analyze, args.newsletter, args.charts, args.status])):
        # Default: run everything
        df = load_job_data()
        if len(df) == 0:
            print("  No data available. Run enrichment first.")
            return

        analysis = analyze_compensation(df)
        generate_all_charts(analysis)
        generate_newsletter_section(analysis)

        print(f"\n{'='*70}")
        print("  ANALYSIS COMPLETE!")
        print(f"{'='*70}")
        print(f"  {analysis['records_with_salary']} jobs with salary data")
        print(f"  {len(analysis['by_category'])} job categories analyzed")
        print(f"  {len(analysis['by_metro'])} locations analyzed")

    elif args.analyze:
        df = load_job_data()
        if len(df) == 0:
            print("  No data available.")
            return
        analysis = analyze_compensation(df)
        print(f"\n  Analysis complete. Run --charts or --newsletter next.")

    elif args.charts:
        if not ANALYSIS_OUTPUT.exists():
            print("  No analysis found. Run --analyze first.")
            return
        with open(ANALYSIS_OUTPUT) as f:
            analysis = json.load(f)
        generate_all_charts(analysis)

    elif args.newsletter:
        if not ANALYSIS_OUTPUT.exists():
            print("  No analysis found. Run --analyze first.")
            return
        with open(ANALYSIS_OUTPUT) as f:
            analysis = json.load(f)
        generate_newsletter_section(analysis)

    elif args.status:
        df = load_job_data()
        if len(df) == 0:
            print("  No data available.")
        else:
            print(f"\n  Total jobs: {len(df)}")
            salary_count = df[pd.to_numeric(df.get('salary_max', 0), errors='coerce') > 0].shape[0]
            print(f"  Jobs with salary: {salary_count} ({round(salary_count/len(df)*100, 1)}%)")

            if 'job_category' in df.columns:
                print(f"  Categories: {df['job_category'].nunique()}")
            if 'metro' in df.columns:
                print(f"  Locations: {df['metro'].dropna().nunique()}")


if __name__ == "__main__":
    main()
