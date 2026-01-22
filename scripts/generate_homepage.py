#!/usr/bin/env python3
"""
Generate the main homepage for AI Market Pulse
Includes Market Pulse stats, featured jobs, and newsletter signup

Uses the shared templates for consistent styling with other pages.
"""

import json
import pandas as pd
import os
import glob
import re
import hashlib
from datetime import datetime
import sys

# Add scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from templates import (
    get_html_head, get_nav_html, get_footer_html,
    format_salary, slugify, BASE_URL, SITE_NAME
)

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


def make_slug(text):
    """Create URL-safe slug"""
    if pd.isna(text):
        return ''
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')[:50]


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
        title = str(job.get('title', 'Untitled')).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        company = str(job.get('company', 'Unknown')).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        location = str(job.get('location', '')).replace('&', '&amp;') if pd.notna(job.get('location')) else ''
        salary = format_salary(job.get('salary_min'), job.get('salary_max'))
        category = str(job.get('job_category', '')).replace('&', '&amp;') if pd.notna(job.get('job_category')) else ''

        # Generate job slug for link
        job_slug = f"{make_slug(job.get('company', ''))}-{make_slug(job.get('title', ''))}"
        hash_suffix = hashlib.md5(f"{job.get('company', '')}{job.get('title','')}{job.get('location','')}".encode()).hexdigest()[:6]
        job_slug = f"{job_slug}-{hash_suffix}"

        featured_html += f'''
        <a href="/jobs/{job_slug}/" class="job-card">
            <div class="job-card__category">{category}</div>
            <h3 class="job-card__title">{title}</h3>
            <div class="job-card__company">{company}</div>
            <div class="job-card__meta">
                <span class="job-card__location">{location}</span>
                {f'<span class="job-card__salary">{salary}</span>' if salary else ''}
            </div>
        </a>
        '''

    html = f'''{get_html_head(
        "AI & Prompt Engineering Jobs",
        f"Find the best AI, ML, and Prompt Engineering jobs. {stats['total_jobs']} open roles tracked with salary data and market insights.",
        ""
    )}
{get_nav_html('home')}

    <style>
        /* Hero Section */
        .hero {{
            padding: 5rem 0 4rem;
            text-align: center;
            background: linear-gradient(180deg, var(--bg-darker) 0%, var(--bg-dark) 100%);
        }}
        .hero-eyebrow {{
            display: inline-block;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--gold);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 1rem;
        }}
        .hero h1 {{
            font-size: 3.5rem;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
        }}
        .hero .lead {{
            font-size: 1.25rem;
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto 1.5rem;
        }}
        .hero-proof {{
            font-size: 0.9rem;
            color: var(--text-muted);
            margin-bottom: 2rem;
        }}
        .hero-proof span {{
            margin: 0 0.5rem;
        }}
        .hero-actions {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }}
        .btn-primary {{
            display: inline-block;
            background: var(--gold);
            color: var(--bg-darker);
            padding: 1rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.2s;
        }}
        .btn-primary:hover {{
            background: var(--gold-light);
            color: var(--bg-darker);
            transform: translateY(-2px);
        }}
        .hero .btn-secondary {{
            display: inline-block;
            background: transparent;
            color: var(--text-primary);
            padding: 1rem 2rem;
            border-radius: 8px;
            border: 1px solid var(--border);
            text-decoration: none;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.2s;
        }}
        .hero .btn-secondary:hover {{
            background: var(--bg-card);
            border-color: var(--teal-light);
        }}
        .hero-cta {{
            display: inline-block;
            background: var(--gold);
            color: var(--bg-darker);
            padding: 1rem 2.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.2s;
        }}
        .hero-cta:hover {{
            background: var(--gold-light);
            color: var(--bg-darker);
            transform: translateY(-2px);
        }}

        /* Market Pulse */
        .market-pulse {{
            background: var(--bg-card);
            padding: 4rem 0;
            border-top: 1px solid var(--border);
            border-bottom: 1px solid var(--border);
        }}
        .section-header {{
            text-align: center;
            margin-bottom: 3rem;
        }}
        .section-header h2 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        .section-header p {{
            color: var(--text-muted);
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.5rem;
        }}
        .stat-card {{
            background: var(--bg-dark);
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid var(--border);
        }}
        .stat-card__value {{
            font-size: 2.75rem;
            font-weight: 700;
            color: var(--gold);
            font-family: 'Space Grotesk', sans-serif;
        }}
        .stat-card__value.positive {{ color: var(--success); }}
        .stat-card__value.negative {{ color: var(--error); }}
        .stat-card__label {{
            color: var(--text-secondary);
            margin-top: 0.5rem;
            font-size: 0.9rem;
        }}

        /* Featured Jobs */
        .featured-jobs {{
            padding: 5rem 0;
        }}
        .jobs-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        .job-card {{
            display: block;
            background: var(--bg-card);
            padding: 1.75rem;
            border-radius: 12px;
            border: 1px solid var(--border);
            text-decoration: none;
            transition: all 0.2s;
        }}
        .job-card:hover {{
            transform: translateY(-4px);
            border-color: var(--gold);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        .job-card__category {{
            font-size: 0.75rem;
            color: var(--teal-accent);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.75rem;
        }}
        .job-card__title {{
            font-size: 1.15rem;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}
        .job-card__company {{
            color: var(--text-secondary);
            margin-bottom: 1rem;
        }}
        .job-card__meta {{
            display: flex;
            gap: 1rem;
            font-size: 0.875rem;
            color: var(--text-muted);
        }}
        .job-card__salary {{
            color: var(--gold);
            font-weight: 600;
        }}
        .view-all {{
            text-align: center;
        }}
        .view-all a {{
            color: var(--gold);
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
        }}
        .view-all a:hover {{
            text-decoration: underline;
        }}

        /* CTA Section */
        .cta-section {{
            background: linear-gradient(135deg, var(--teal-primary) 0%, var(--bg-card) 100%);
            padding: 5rem 0;
            text-align: center;
            border-top: 1px solid var(--border);
        }}
        .cta-section h2 {{
            font-size: 2rem;
            margin-bottom: 1rem;
        }}
        .cta-section p {{
            color: var(--text-secondary);
            margin-bottom: 2rem;
            max-width: 500px;
            margin-left: auto;
            margin-right: auto;
        }}

        /* Categories Section */
        .categories-section {{
            padding: 4rem 0;
            background: var(--bg-darker);
        }}
        .categories-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            justify-content: center;
        }}
        .category-tag {{
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 30px;
            color: var(--text-secondary);
            text-decoration: none;
            transition: all 0.2s;
        }}
        .category-tag:hover {{
            background: var(--teal-primary);
            border-color: var(--teal-light);
            color: var(--text-primary);
        }}

        @media (max-width: 900px) {{
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        @media (max-width: 600px) {{
            .hero h1 {{ font-size: 2.25rem; }}
            .hero .lead {{ font-size: 1.1rem; }}
            .hero-actions {{ flex-direction: column; align-items: center; }}
            .stats-grid {{ grid-template-columns: 1fr 1fr; gap: 1rem; }}
            .stat-card {{ padding: 1.25rem; }}
            .stat-card__value {{ font-size: 2rem; }}
        }}
    </style>

    <section class="hero">
        <div class="container">
            <span class="hero-eyebrow">AI Career Intelligence</span>
            <h1>Stay ahead in AI</h1>
            <p class="lead">Track the AI job market. Know what's hiring, what pays, and what skills matter.</p>
            <p class="hero-proof">
                <span>2.6K+ subscribers</span> ·
                <span>1.3K+ community members</span> ·
                <span>{stats['total_jobs']:,}+ jobs tracked</span>
            </p>
            <div class="hero-actions">
                <a href="https://www.theainewsdigest.com/" class="btn-primary" target="_blank" rel="noopener">Subscribe Free</a>
                <a href="/jobs/" class="btn-secondary">Browse Jobs</a>
            </div>
        </div>
    </section>

    <section class="market-pulse">
        <div class="container">
            <div class="section-header">
                <h2>Market Pulse</h2>
                <p>AI Job Market as of {update_date}</p>
            </div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-card__value">{stats['total_jobs']:,}</div>
                    <div class="stat-card__label">Open Roles</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card__value {wow_class}">{wow_arrow} {abs(stats['wow_change']):.0f}%</div>
                    <div class="stat-card__label">Week over Week</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card__value">{stats['remote_pct']:.0f}%</div>
                    <div class="stat-card__label">Remote Jobs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card__value">${stats['avg_max_salary']//1000}K</div>
                    <div class="stat-card__label">Avg Max Salary</div>
                </div>
            </div>
        </div>
    </section>

    <section class="featured-jobs">
        <div class="container">
            <div class="section-header">
                <h2>Featured AI Jobs</h2>
                <p>Highest paying opportunities this week</p>
            </div>
            <div class="jobs-grid">
                {featured_html}
            </div>
            <div class="view-all">
                <a href="/jobs/">View All {stats['total_jobs']:,} Jobs →</a>
            </div>
        </div>
    </section>

    <section class="categories-section">
        <div class="container">
            <div class="section-header">
                <h2>Browse by Category</h2>
            </div>
            <div class="categories-grid">
                <a href="/jobs/ai-ml-engineer/" class="category-tag">AI/ML Engineer</a>
                <a href="/jobs/prompt-engineer/" class="category-tag">Prompt Engineer</a>
                <a href="/jobs/data-scientist/" class="category-tag">Data Scientist</a>
                <a href="/jobs/research-scientist/" class="category-tag">Research Scientist</a>
                <a href="/jobs/mlops-engineer/" class="category-tag">MLOps Engineer</a>
                <a href="/jobs/data-engineer/" class="category-tag">Data Engineer</a>
                <a href="/jobs/remote/" class="category-tag">Remote Jobs</a>
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

    <!-- SEO Content Section -->
    <section class="seo-content" style="padding: 4rem 0; background: var(--bg-darker);">
        <div class="container" style="max-width: 800px;">
            <h2 style="font-size: 1.75rem; margin-bottom: 1.5rem; color: var(--text-primary);">About AI Market Pulse</h2>

            <div style="color: var(--text-secondary); line-height: 1.8; font-size: 1rem;">
                <p style="margin-bottom: 1.25rem;">
                    AI Market Pulse is the career intelligence platform built specifically for AI professionals. We track thousands of AI, ML, and prompt engineering job postings weekly, providing real salary data and market insights that help you make informed career decisions.
                </p>

                <h3 style="font-size: 1.25rem; color: var(--text-primary); margin: 2rem 0 1rem;">What We Track</h3>
                <p style="margin-bottom: 1.25rem;">
                    Our platform aggregates job postings from Indeed, LinkedIn, company career pages, and other major job boards. We focus on roles across the AI ecosystem: <strong>AI/ML Engineers</strong>, <strong>Prompt Engineers</strong>, <strong>LLM Engineers</strong>, <strong>Data Scientists</strong>, <strong>MLOps Engineers</strong>, <strong>Research Scientists</strong>, and <strong>AI Product Managers</strong>. Every listing is enriched with structured data including salary ranges, required skills, experience levels, and remote work options.
                </p>

                <h3 style="font-size: 1.25rem; color: var(--text-primary); margin: 2rem 0 1rem;">Why Salary Transparency Matters</h3>
                <p style="margin-bottom: 1.25rem;">
                    The AI job market moves fast—compensation benchmarks from even a year ago may no longer apply. We collect and analyze salary data from job postings with disclosed compensation, giving you real-time benchmarks by role, location, and experience level. Whether you're negotiating an offer, planning a career transition, or benchmarking your current compensation, our data helps you understand your market value.
                </p>

                <h3 style="font-size: 1.25rem; color: var(--text-primary); margin: 2rem 0 1rem;">Skills & Tools Intelligence</h3>
                <p style="margin-bottom: 1.25rem;">
                    Beyond job listings, we track which skills and tools employers are actually hiring for. From foundational frameworks like <strong>PyTorch</strong> and <strong>TensorFlow</strong> to emerging LLM tools like <strong>LangChain</strong>, <strong>LlamaIndex</strong>, and vector databases, our market intelligence shows you where demand is growing. This helps you prioritize learning investments and stay ahead of hiring trends.
                </p>

                <h3 style="font-size: 1.25rem; color: var(--text-primary); margin: 2rem 0 1rem;">For AI Professionals, By AI Professionals</h3>
                <p style="margin-bottom: 1.25rem;">
                    AI Market Pulse is part of the AI News Digest network, serving a community of 2,600+ subscribers and 1,300+ community members. We cut through recruiter spin to deliver actionable intelligence: which companies are actually hiring, what they're paying, and what skills will matter in 2026 and beyond.
                </p>
            </div>
        </div>
    </section>

{get_footer_html()}'''

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
