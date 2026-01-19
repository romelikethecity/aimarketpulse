#!/usr/bin/env python3
"""
Generate the main homepage for PE Collective
Includes Market Pulse stats, featured jobs, and newsletter signup
"""

import json
import pandas as pd
import os
import glob
from datetime import datetime
# Configuration
BASE_URL = 'https://pecollective.com'
SITE_NAME = 'PE Collective'

DATA_DIR = 'data'
SITE_DIR = 'site'


def get_jobs_files():
    """Find the two most recent ai_jobs CSV files"""
    pattern = f"{DATA_DIR}/ai_jobs_*.csv"
    files = sorted(glob.glob(pattern))
    if not files:
        return None, None
    current = files[-1]
    previous = files[-2] if len(files) >= 2 else None
    return current, previous


def calculate_stats():
    """Calculate market stats from job data"""
    current_file, previous_file = get_jobs_files()

    if not current_file:
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_jobs': 0,
            'wow_change': 0,
            'remote_pct': 0,
            'avg_max_salary': 0,
            'jobs_with_salary': 0,
            'top_categories': []
        }

    df = pd.read_csv(current_file)
    total_jobs = len(df)

    # Calculate WoW change
    wow_change = 0
    if previous_file:
        prev_df = pd.read_csv(previous_file)
        prev_jobs = len(prev_df)
        if prev_jobs > 0:
            wow_change = ((total_jobs - prev_jobs) / prev_jobs) * 100
            print(f"  WoW: {prev_jobs} -> {total_jobs} ({wow_change:+.0f}%)")

    # Calculate remote percentage
    remote_pct = 0
    if 'remote_type' in df.columns:
        remote_count = (df['remote_type'] == 'remote').sum()
        remote_pct = (remote_count / total_jobs * 100) if total_jobs > 0 else 0
    elif 'is_remote' in df.columns:
        remote_pct = (df['is_remote'].sum() / total_jobs * 100) if total_jobs > 0 else 0

    # Calculate average max salary
    avg_max_salary = 0
    jobs_with_salary = 0
    if 'salary_max' in df.columns:
        salary_data = pd.to_numeric(df['salary_max'], errors='coerce')
        salary_data = salary_data[(salary_data > 50000) & (salary_data < 1000000)]
        if len(salary_data) > 0:
            avg_max_salary = int(salary_data.mean())
            jobs_with_salary = len(salary_data)

    # Top categories
    top_categories = []
    if 'job_category' in df.columns:
        top_cats = df['job_category'].value_counts().head(5)
        top_categories = list(top_cats.index)

    return {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'total_jobs': total_jobs,
        'wow_change': wow_change,
        'remote_pct': remote_pct,
        'avg_max_salary': avg_max_salary,
        'jobs_with_salary': jobs_with_salary,
        'top_categories': top_categories
    }


def get_featured_jobs(limit=6):
    """Get featured jobs for homepage"""
    current_file, _ = get_jobs_files()
    if not current_file:
        return []

    df = pd.read_csv(current_file)

    # Prioritize jobs with salary data
    if 'salary_max' in df.columns:
        df['salary_max_num'] = pd.to_numeric(df['salary_max'], errors='coerce').fillna(0)
        df = df.sort_values('salary_max_num', ascending=False)

    featured = df.head(limit).to_dict('records')
    return featured


def format_salary_display(min_sal, max_sal):
    """Format salary for display"""
    try:
        min_val = float(min_sal) if pd.notna(min_sal) else 0
        max_val = float(max_sal) if pd.notna(max_sal) else 0
    except:
        return ""

    if min_val > 0 and max_val > 0:
        return f"${int(min_val/1000)}K - ${int(max_val/1000)}K"
    elif max_val > 0:
        return f"Up to ${int(max_val/1000)}K"
    return ""


def generate_homepage():
    """Generate the main homepage HTML"""
    print("="*70)
    print("  GENERATING HOMEPAGE")
    print("="*70)

    stats = calculate_stats()
    featured_jobs = get_featured_jobs(6)

    # Format date
    update_date = datetime.strptime(stats['date'], '%Y-%m-%d').strftime('%B %d, %Y')

    # WoW direction
    wow_arrow = '↑' if stats['wow_change'] >= 0 else '↓'
    wow_class = 'positive' if stats['wow_change'] >= 0 else 'negative'

    # Generate featured jobs HTML
    featured_html = ''
    for job in featured_jobs:
        title = job.get('title', 'Untitled')
        company = job.get('company', 'Unknown')
        location = job.get('location', '')
        salary = format_salary_display(job.get('salary_min'), job.get('salary_max'))
        category = job.get('job_category', '')

        # Create job card
        featured_html += f'''
        <div class="job-card">
            <div class="job-category">{category}</div>
            <h3 class="job-title">{title}</h3>
            <div class="job-company">{company}</div>
            <div class="job-meta">
                <span class="job-location">{location}</span>
                {f'<span class="job-salary">{salary}</span>' if salary else ''}
            </div>
        </div>
        '''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PE Collective | AI & Prompt Engineering Jobs</title>
    <meta name="description" content="Find the best AI, ML, and Prompt Engineering jobs. {stats['total_jobs']} open roles tracked with salary data and market insights.">

    <link rel="canonical" href="{BASE_URL}/">

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{BASE_URL}/">
    <meta property="og:title" content="PE Collective | AI & Prompt Engineering Jobs">
    <meta property="og:description" content="Find the best AI, ML, and Prompt Engineering jobs. {stats['total_jobs']} open roles tracked.">
    <meta property="og:site_name" content="{SITE_NAME}">
    <meta property="og:image" content="{BASE_URL}/assets/social_preview.png">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="PE Collective | AI & Prompt Engineering Jobs">
    <meta name="twitter:description" content="Find the best AI, ML, and Prompt Engineering jobs.">

    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #334155;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --accent: #22d3ee;
            --accent-gold: #f5a623;
            --success: #10b981;
            --danger: #ef4444;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }}

        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}

        /* Navigation */
        nav {{
            background: var(--bg-secondary);
            padding: 1rem 0;
            border-bottom: 1px solid var(--bg-card);
        }}
        nav .container {{ display: flex; justify-content: space-between; align-items: center; }}
        .nav-brand {{ font-size: 1.5rem; font-weight: 700; color: var(--accent); text-decoration: none; }}
        .nav-links {{ display: flex; gap: 2rem; }}
        .nav-links a {{ color: var(--text-secondary); text-decoration: none; transition: color 0.2s; }}
        .nav-links a:hover {{ color: var(--accent); }}
        .nav-cta {{
            background: var(--accent);
            color: var(--bg-primary);
            padding: 0.5rem 1rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
        }}

        /* Hero Section */
        .hero {{
            padding: 4rem 0;
            text-align: center;
        }}
        .hero h1 {{
            font-size: 3rem;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, var(--accent), var(--accent-gold));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .hero p {{
            font-size: 1.25rem;
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto 2rem;
        }}
        .hero-cta {{
            display: inline-block;
            background: var(--accent);
            color: var(--bg-primary);
            padding: 1rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
        }}

        /* Market Pulse */
        .market-pulse {{
            background: var(--bg-secondary);
            padding: 3rem 0;
            border-top: 1px solid var(--bg-card);
            border-bottom: 1px solid var(--bg-card);
        }}
        .market-pulse h2 {{
            text-align: center;
            margin-bottom: 0.5rem;
            font-size: 1.5rem;
        }}
        .market-pulse .subtitle {{
            text-align: center;
            color: var(--text-secondary);
            margin-bottom: 2rem;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
        }}
        .stat-card {{
            background: var(--bg-card);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--accent);
        }}
        .stat-value.positive {{ color: var(--success); }}
        .stat-value.negative {{ color: var(--danger); }}
        .stat-label {{
            color: var(--text-secondary);
            margin-top: 0.5rem;
        }}

        /* Featured Jobs */
        .featured-jobs {{
            padding: 4rem 0;
        }}
        .featured-jobs h2 {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        .jobs-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }}
        .job-card {{
            background: var(--bg-secondary);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--bg-card);
            transition: transform 0.2s, border-color 0.2s;
        }}
        .job-card:hover {{
            transform: translateY(-4px);
            border-color: var(--accent);
        }}
        .job-category {{
            font-size: 0.75rem;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}
        .job-title {{
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
        }}
        .job-company {{
            color: var(--text-secondary);
            margin-bottom: 0.75rem;
        }}
        .job-meta {{
            display: flex;
            gap: 1rem;
            font-size: 0.875rem;
            color: var(--text-secondary);
        }}
        .job-salary {{
            color: var(--accent-gold);
            font-weight: 600;
        }}
        .view-all {{
            text-align: center;
            margin-top: 2rem;
        }}
        .view-all a {{
            color: var(--accent);
            text-decoration: none;
            font-weight: 600;
        }}

        /* CTA Section */
        .cta-section {{
            background: linear-gradient(135deg, var(--bg-secondary), var(--bg-card));
            padding: 4rem 0;
            text-align: center;
        }}
        .cta-section h2 {{
            margin-bottom: 1rem;
        }}
        .cta-section p {{
            color: var(--text-secondary);
            margin-bottom: 2rem;
            max-width: 500px;
            margin-left: auto;
            margin-right: auto;
        }}

        /* Footer */
        footer {{
            background: var(--bg-secondary);
            padding: 2rem 0;
            border-top: 1px solid var(--bg-card);
        }}
        footer .container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .footer-links {{ display: flex; gap: 1.5rem; }}
        .footer-links a {{ color: var(--text-secondary); text-decoration: none; font-size: 0.875rem; }}
        .footer-links a:hover {{ color: var(--accent); }}
        .footer-copyright {{ color: var(--text-secondary); font-size: 0.875rem; }}

        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 2rem; }}
            .nav-links {{ display: none; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            footer .container {{ flex-direction: column; gap: 1rem; text-align: center; }}
        }}
    </style>
</head>
<body>
    <nav>
        <div class="container">
            <a href="/" class="nav-brand">PE Collective</a>
            <div class="nav-links">
                <a href="/jobs/">AI Jobs</a>
                <a href="/salaries/">Salaries</a>
                <a href="/insights/">Insights</a>
                <a href="/tools/">Tools</a>
            </div>
            <a href="/join/" class="nav-cta">Join Community</a>
        </div>
    </nav>

    <section class="hero">
        <div class="container">
            <h1>Find Your Next AI Role</h1>
            <p>Curated AI, Machine Learning, and Prompt Engineering jobs with salary transparency and market insights.</p>
            <a href="/jobs/" class="hero-cta">Browse {stats['total_jobs']} Open Roles →</a>
        </div>
    </section>

    <section class="market-pulse">
        <div class="container">
            <h2>Market Pulse</h2>
            <p class="subtitle">AI Job Market as of {update_date}</p>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{stats['total_jobs']:,}</div>
                    <div class="stat-label">Open Roles</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value {wow_class}">{wow_arrow} {abs(stats['wow_change']):.0f}%</div>
                    <div class="stat-label">Week over Week</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats['remote_pct']:.0f}%</div>
                    <div class="stat-label">Remote Jobs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats['avg_max_salary']//1000}K</div>
                    <div class="stat-label">Avg Max Salary</div>
                </div>
            </div>
        </div>
    </section>

    <section class="featured-jobs">
        <div class="container">
            <h2>Featured AI Jobs</h2>
            <div class="jobs-grid">
                {featured_html}
            </div>
            <div class="view-all">
                <a href="/jobs/">View All {stats['total_jobs']} Jobs →</a>
            </div>
        </div>
    </section>

    <section class="cta-section">
        <div class="container">
            <h2>Stay Updated on AI Jobs</h2>
            <p>Get weekly insights on the AI job market, salary trends, and top opportunities.</p>
            <a href="/join/" class="hero-cta">Join the Community</a>
        </div>
    </section>

    <footer>
        <div class="container">
            <div class="footer-links">
                <a href="/jobs/">Jobs</a>
                <a href="/salaries/">Salaries</a>
                <a href="/insights/">Insights</a>
                <a href="/about/">About</a>
            </div>
            <div class="footer-copyright">© 2026 PE Collective. All rights reserved.</div>
        </div>
    </footer>
</body>
</html>
'''

    # Ensure site directory exists
    os.makedirs(SITE_DIR, exist_ok=True)

    # Write homepage
    output_path = f"{SITE_DIR}/index.html"
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"\n  Saved: {output_path}")
    print(f"  Total jobs: {stats['total_jobs']}")
    print(f"  Jobs with salary: {stats['jobs_with_salary']}")
    print(f"  Avg max salary: ${stats['avg_max_salary']:,}")

    return stats


if __name__ == "__main__":
    generate_homepage()
