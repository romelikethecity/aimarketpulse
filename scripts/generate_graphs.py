#!/usr/bin/env python3
"""
PE Collective Trends Graph Generator
Generates multiple timeframe views with professional styling
Outputs to site/assets/ for GitHub Pages
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
import glob
import json

# ============================================================
# GITHUB ACTIONS CONFIGURATION
# ============================================================
DATA_DIR = "data"
SITE_ASSETS = "site/assets"

os.makedirs(SITE_ASSETS, exist_ok=True)

print("="*70)
print("  PE COLLECTIVE - TRENDS GRAPH GENERATOR")
print("="*70)

# Professional styling - matching PE Collective brand (dark teal + gold)
plt.style.use('dark_background')
colors = {
    'line': '#22d3ee',      # Cyan/teal
    'fill': '#0891b2',      # Darker cyan for fill
    'grid': '#374151',      # Dark gray grid
    'text': '#e5e7eb',      # Light gray text
    'highlight': '#f5a623', # Yellow/gold
    'bg': '#1f2937',        # Dark background
    'secondary': '#10b981', # Green for secondary lines
    'tertiary': '#a855f7',  # Purple for tertiary
}

# Load or create tracking data
tracking_file = f'{DATA_DIR}/job_count_history.csv'

def update_tracking_data():
    """Update job count tracking from current data"""
    # Find latest enriched file
    job_files = glob.glob(f'{DATA_DIR}/ai_jobs_*.csv')
    if not job_files:
        print("  No enriched job files found")
        return None

    # Load existing tracking data or create new
    if os.path.exists(tracking_file):
        df_tracking = pd.read_csv(tracking_file)
        # Handle various column name cases
        if 'Date' not in df_tracking.columns:
            if 'date' in df_tracking.columns:
                df_tracking = df_tracking.rename(columns={'date': 'Date'})
            else:
                # File exists but is malformed, recreate
                df_tracking = pd.DataFrame(columns=['Date', 'AI Job Openings'])
        if 'AI Job Openings' not in df_tracking.columns:
            if 'ai_job_openings' in df_tracking.columns:
                df_tracking = df_tracking.rename(columns={'ai_job_openings': 'AI Job Openings'})
            elif 'job_count' in df_tracking.columns:
                df_tracking = df_tracking.rename(columns={'job_count': 'AI Job Openings'})
            elif 'count' in df_tracking.columns:
                df_tracking = df_tracking.rename(columns={'count': 'AI Job Openings'})
        try:
            df_tracking['Date'] = pd.to_datetime(df_tracking['Date'])
        except Exception as e:
            print(f"  Warning: Could not parse dates, recreating tracking file: {e}")
            df_tracking = pd.DataFrame(columns=['Date', 'AI Job Openings'])
    else:
        df_tracking = pd.DataFrame(columns=['Date', 'AI Job Openings'])

    # Get today's count from latest file
    latest_file = sorted(job_files)[-1]
    jobs_df = pd.read_csv(latest_file)
    today_count = len(jobs_df)
    today = pd.Timestamp.now().normalize()

    # Add today's data if not already present
    if df_tracking.empty or today not in df_tracking['Date'].values:
        new_row = pd.DataFrame({'Date': [today], 'AI Job Openings': [today_count]})
        df_tracking = pd.concat([df_tracking, new_row], ignore_index=True)
        df_tracking = df_tracking.drop_duplicates(subset=['Date'], keep='last')
        df_tracking = df_tracking.sort_values('Date')
        df_tracking.to_csv(tracking_file, index=False)
        print(f"  Updated tracking data: {today_count} jobs on {today.strftime('%Y-%m-%d')}")

    return df_tracking


def create_graph(df_subset, title, filename, show_annotations=True):
    """Create a professionally styled graph matching PE Collective brand"""
    if df_subset is None or len(df_subset) < 2:
        print(f"  Skipping {filename} - insufficient data points")
        return

    fig, ax = plt.subplots(figsize=(14, 7), facecolor=colors['bg'])
    ax.set_facecolor(colors['bg'])

    # Plot line with area fill
    ax.plot(df_subset['Date'], df_subset['AI Job Openings'],
            color=colors['line'], linewidth=3, label='AI Job Openings', zorder=3)
    ax.fill_between(df_subset['Date'], df_subset['AI Job Openings'],
                     alpha=0.2, color=colors['fill'], zorder=2)

    # Styling with large fonts
    ax.set_title(title, fontsize=32, fontweight='bold', pad=30, color=colors['text'])
    ax.set_xlabel('', fontsize=24)
    ax.set_ylabel('Openings', fontsize=24, fontweight='bold', color=colors['text'])
    ax.grid(True, alpha=0.15, color=colors['grid'], linewidth=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(colors['grid'])
    ax.spines['left'].set_color(colors['grid'])
    ax.tick_params(colors=colors['text'], which='both', labelsize=20)

    if show_annotations:
        current_val = df_subset['AI Job Openings'].iloc[-1]
        current_date = df_subset['Date'].iloc[-1]

        # Yellow dot at current position
        ax.plot(current_date, current_val, 'o', color=colors['highlight'],
                markersize=14, zorder=5, markeredgewidth=3, markeredgecolor=colors['bg'])

        # Label
        ax.text(1.01, 0.5, f'AI Job\nOpenings',
               transform=ax.transAxes,
               fontsize=22, fontweight='bold',
               color=colors['line'],
               verticalalignment='center')

        # Max marker for longer timeframes
        max_val = df_subset['AI Job Openings'].max()
        max_date = df_subset[df_subset['AI Job Openings'] == max_val]['Date'].iloc[0]
        if len(df_subset) > 90:
            ax.plot(max_date, max_val, 'o', color=colors['highlight'],
                   markersize=12, zorder=5, alpha=0.7)

    # X-axis formatting based on timeframe
    days_spanned = (df_subset['Date'].max() - df_subset['Date'].min()).days

    if days_spanned > 365 * 2:
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    elif days_spanned > 365:
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    elif days_spanned > 180:
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    elif days_spanned > 60:
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    else:
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    plt.xticks(rotation=45, ha='right', fontsize=20)
    plt.yticks(fontsize=20)
    plt.tight_layout()

    # Save to site/assets/
    output_path = f"{SITE_ASSETS}/{filename}"
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=colors['bg'], edgecolor='none')
    print(f"  Saved: {output_path}")
    plt.close()


def create_category_chart():
    """Create a bar chart showing job distribution by category"""
    job_files = glob.glob(f'{DATA_DIR}/ai_jobs_*.csv')
    if not job_files:
        return

    latest_file = sorted(job_files)[-1]
    jobs_df = pd.read_csv(latest_file)

    if 'job_category' not in jobs_df.columns:
        return

    categories = jobs_df['job_category'].value_counts().head(8)

    fig, ax = plt.subplots(figsize=(12, 8), facecolor=colors['bg'])
    ax.set_facecolor(colors['bg'])

    bars = ax.barh(categories.index[::-1], categories.values[::-1], color=colors['line'], alpha=0.8)
    ax.set_xlabel('Number of Jobs', fontsize=18, color=colors['text'])
    ax.set_title('AI Jobs by Category', fontsize=28, fontweight='bold', pad=20, color=colors['text'])

    # Style
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(colors['grid'])
    ax.spines['left'].set_color(colors['grid'])
    ax.tick_params(colors=colors['text'], labelsize=14)
    ax.grid(True, alpha=0.15, axis='x', color=colors['grid'])

    # Add value labels
    for bar, val in zip(bars, categories.values[::-1]):
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
               f'{val}', va='center', fontsize=14, color=colors['highlight'], fontweight='bold')

    plt.tight_layout()
    output_path = f"{SITE_ASSETS}/jobs_by_category.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=colors['bg'])
    print(f"  Saved: {output_path}")
    plt.close()


def create_salary_distribution():
    """Create a histogram of salary distribution"""
    job_files = glob.glob(f'{DATA_DIR}/ai_jobs_*.csv')
    if not job_files:
        return

    latest_file = sorted(job_files)[-1]
    jobs_df = pd.read_csv(latest_file)

    if 'salary_max' not in jobs_df.columns:
        return

    salaries = jobs_df[jobs_df['salary_max'].notna() & (jobs_df['salary_max'] > 50000) & (jobs_df['salary_max'] < 1000000)]['salary_max']

    if len(salaries) < 10:
        print("  Skipping salary distribution - insufficient data")
        return

    fig, ax = plt.subplots(figsize=(12, 7), facecolor=colors['bg'])
    ax.set_facecolor(colors['bg'])

    # Create histogram
    n, bins, patches = ax.hist(salaries / 1000, bins=20, color=colors['line'], alpha=0.8, edgecolor=colors['bg'])

    ax.set_xlabel('Salary ($K)', fontsize=18, color=colors['text'])
    ax.set_ylabel('Number of Jobs', fontsize=18, color=colors['text'])
    ax.set_title('AI Job Salary Distribution', fontsize=28, fontweight='bold', pad=20, color=colors['text'])

    # Add median line
    median_sal = salaries.median() / 1000
    ax.axvline(median_sal, color=colors['highlight'], linestyle='--', linewidth=3, label=f'Median: ${median_sal:.0f}K')
    ax.legend(fontsize=14, facecolor=colors['bg'], edgecolor=colors['grid'])

    # Style
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(colors['grid'])
    ax.spines['left'].set_color(colors['grid'])
    ax.tick_params(colors=colors['text'], labelsize=14)
    ax.grid(True, alpha=0.15, axis='y', color=colors['grid'])

    plt.tight_layout()
    output_path = f"{SITE_ASSETS}/salary_distribution.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=colors['bg'])
    print(f"  Saved: {output_path}")
    plt.close()


def create_social_preview():
    """Create social preview image with highest paying job this week"""
    job_files = glob.glob(f'{DATA_DIR}/ai_jobs_*.csv')
    if not job_files:
        print(f"\n  No jobs file found - skipping social preview")
        return

    latest_file = sorted(job_files)[-1]
    print(f"\n  Social Preview")
    print(f"   Loading: {latest_file}")

    try:
        jobs_df = pd.read_csv(latest_file)

        if 'salary_max' not in jobs_df.columns:
            print("    No salary_max column found")
            return

        valid_jobs = jobs_df[jobs_df['salary_max'].notna() & (jobs_df['salary_max'] > 0)]

        if valid_jobs.empty:
            print("    No jobs with valid salary data")
            return

        top_job = valid_jobs.loc[valid_jobs['salary_max'].idxmax()]
        max_salary = int(top_job['salary_max'])
        salary_k = f"${max_salary // 1000}k"

        print(f"   Found top salary: {salary_k}")

        fig, ax = plt.subplots(figsize=(14.56, 10.48), facecolor=colors['bg'])
        ax.set_facecolor(colors['bg'])
        ax.axis('off')

        ax.text(0.5, 0.75, salary_k,
               transform=ax.transAxes,
               fontsize=200, fontweight='bold',
               color=colors['highlight'],
               horizontalalignment='center',
               verticalalignment='center')

        ax.text(0.5, 0.42, "This Week's\nHighest Paying AI Role",
               transform=ax.transAxes,
               fontsize=60, fontweight='bold',
               color=colors['text'],
               horizontalalignment='center',
               verticalalignment='center',
               linespacing=1.2)

        ax.text(0.5, 0.18, "PE Collective",
               transform=ax.transAxes,
               fontsize=50, fontweight='bold',
               color=colors['line'],
               horizontalalignment='center',
               verticalalignment='center')

        plt.tight_layout(pad=0)
        output_path = f"{SITE_ASSETS}/social_preview.png"
        plt.savefig(output_path, dpi=100, bbox_inches='tight',
                   facecolor=colors['bg'], edgecolor='none', pad_inches=0)
        print(f"  Saved: {output_path}")
        plt.close()

    except Exception as e:
        print(f"    Error creating social preview: {e}")


def create_remote_breakdown():
    """Create a pie chart showing remote vs onsite breakdown"""
    job_files = glob.glob(f'{DATA_DIR}/ai_jobs_*.csv')
    if not job_files:
        return

    latest_file = sorted(job_files)[-1]
    jobs_df = pd.read_csv(latest_file)

    if 'remote_type' not in jobs_df.columns:
        return

    remote_counts = jobs_df['remote_type'].value_counts()

    fig, ax = plt.subplots(figsize=(10, 10), facecolor=colors['bg'])
    ax.set_facecolor(colors['bg'])

    pie_colors = [colors['line'], colors['secondary'], colors['tertiary']]
    wedges, texts, autotexts = ax.pie(
        remote_counts.values,
        labels=remote_counts.index,
        autopct='%1.1f%%',
        colors=pie_colors[:len(remote_counts)],
        textprops={'color': colors['text'], 'fontsize': 16},
        startangle=90
    )

    for autotext in autotexts:
        autotext.set_color(colors['bg'])
        autotext.set_fontweight('bold')
        autotext.set_fontsize(14)

    ax.set_title('Remote Work Breakdown', fontsize=28, fontweight='bold', pad=20, color=colors['text'])

    plt.tight_layout()
    output_path = f"{SITE_ASSETS}/remote_breakdown.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=colors['bg'])
    print(f"  Saved: {output_path}")
    plt.close()


# ============================================================
# MAIN EXECUTION
# ============================================================

# Update tracking data
print("\n Updating tracking data...")
df = update_tracking_data()

# Generate trend graphs if we have data
if df is not None and len(df) >= 2:
    print(f"\n Loaded {len(df)} data points")
    print(f" Date range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")

    print(f"\n{'GENERATING TREND GRAPHS':-^70}")

    # 1. ALL TIME
    print("\n1. All-Time View")
    create_graph(df, 'AI Job Market Trends - Complete History', 'trend_all_time.png')

    # 2. LAST 12 MONTHS
    print("\n2. Last 12 Months")
    twelve_months_ago = df['Date'].max() - timedelta(days=365)
    df_12m = df[df['Date'] >= twelve_months_ago]
    if len(df_12m) >= 2:
        create_graph(df_12m, 'AI Job Trends - Last 12 Months', 'trend_12_months.png')

    # 3. LAST 6 MONTHS
    print("\n3. Last 6 Months")
    six_months_ago = df['Date'].max() - timedelta(days=180)
    df_6m = df[df['Date'] >= six_months_ago]
    if len(df_6m) >= 2:
        create_graph(df_6m, 'AI Job Trends - Last 6 Months', 'trend_6_months.png')

    # 4. LAST 90 DAYS
    print("\n4. Last 90 Days")
    ninety_days_ago = df['Date'].max() - timedelta(days=90)
    df_90d = df[df['Date'] >= ninety_days_ago]
    if len(df_90d) >= 2:
        create_graph(df_90d, 'AI Job Trends - Last 90 Days', 'trend_90_days.png')

    # 5. LAST 30 DAYS
    print("\n5. Last 30 Days")
    thirty_days_ago = df['Date'].max() - timedelta(days=30)
    df_30d = df[df['Date'] >= thirty_days_ago]
    if len(df_30d) >= 2:
        create_graph(df_30d, 'AI Job Trends - Last 30 Days', 'trend_30_days.png')
else:
    print("\n Insufficient data for trend graphs (need at least 2 data points)")

# Generate additional charts
print(f"\n{'GENERATING ANALYSIS CHARTS':-^70}")

print("\n6. Jobs by Category")
create_category_chart()

print("\n7. Salary Distribution")
create_salary_distribution()

print("\n8. Remote Work Breakdown")
create_remote_breakdown()

print("\n9. Social Preview")
create_social_preview()

print(f"\n{'='*70}")
print("  ALL GRAPHS GENERATED!")
print(f"{'='*70}")
