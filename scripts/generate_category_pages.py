#!/usr/bin/env python3
"""
Generate category filter pages for programmatic SEO.
Creates pages like /jobs/prompt-engineer/, /jobs/remote/, /jobs/san-francisco/
"""

import pandas as pd
from datetime import datetime
import glob
import os
import json
import sys
import hashlib
import re
import traceback

# Add scripts directory to path using absolute path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    from templates import get_html_head, get_nav_html, get_footer_html, get_cta_box, format_salary, is_remote, BASE_URL, SITE_NAME
except Exception as e:
    print(f"ERROR importing templates: {e}")
    traceback.print_exc()
    sys.exit(1)

DATA_DIR = 'data'
SITE_DIR = 'site'
JOBS_DIR = f'{SITE_DIR}/jobs'

print("="*70)
print("  AI MARKET PULSE - GENERATING CATEGORY PAGES")
print("="*70)

# Load job data
files = glob.glob(f"{DATA_DIR}/ai_jobs_*.csv")
if files:
    df = pd.read_csv(max(files, key=os.path.getctime))
elif os.path.exists(f"{DATA_DIR}/jobs.json"):
    with open(f"{DATA_DIR}/jobs.json") as f:
        df = pd.DataFrame(json.load(f).get('jobs', []))
else:
    print(" No job data found")
    exit(1)

print(f"\n Loaded {len(df)} jobs")


def make_slug(text):
    if pd.isna(text):
        return ''
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')[:50]


def escape_html(text):
    if pd.isna(text):
        return ''
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def generate_category_page(filtered_df, slug, title, description):
    """Generate a category listing page"""
    if len(filtered_df) < 1:
        return False

    # Calculate stats
    total = len(filtered_df)
    salary_col = 'salary_max' if 'salary_max' in filtered_df.columns else 'max_amount'
    salaries = filtered_df[salary_col].dropna()
    avg_salary = int(salaries.mean() / 1000) if len(salaries) > 0 else 0

    # Generate job cards
    job_cards = ""
    for idx, row in filtered_df.head(50).iterrows():
        company = escape_html(str(row.get('company', row.get('company_name', 'Unknown'))))
        job_title = escape_html(str(row.get('title', 'AI Role')))
        location = escape_html(str(row.get('location', ''))) if pd.notna(row.get('location')) else ''
        category = escape_html(str(row.get('job_category', ''))) if pd.notna(row.get('job_category')) else ''
        remote_status = is_remote(row)
        salary = format_salary(row.get('salary_min', row.get('min_amount')), row.get('salary_max', row.get('max_amount')))

        job_slug = f"{make_slug(row.get('company', row.get('company_name', '')))}-{make_slug(row.get('title', ''))}"
        hash_suffix = hashlib.md5(f"{row.get('company', row.get('company_name', ''))}{row.get('title','')}{row.get('location','')}".encode()).hexdigest()[:6]
        job_slug = f"{job_slug}-{hash_suffix}"

        job_cards += f'''
            <a href="/jobs/{job_slug}/" class="job-card">
                <div class="job-card__content">
                    <div class="job-card__company">{company}</div>
                    <div class="job-card__title">{job_title}</div>
                    <div class="job-card__meta">
                        {f'<span class="job-card__tag job-card__tag--salary">{salary}</span>' if salary else ''}
                        {f'<span class="job-card__tag job-card__tag--remote">Remote</span>' if remote_status else ''}
                        {f'<span class="job-card__tag">{location}</span>' if location and not remote_status else ''}
                    </div>
                </div>
            </a>
        '''

    html = f'''{get_html_head(
        f"{title} - {total} Jobs",
        description,
        f"jobs/{slug}/"
    )}
{get_nav_html('jobs')}

    <div class="page-header">
        <div class="container">
            <div class="breadcrumb"><a href="/">Home</a> → <a href="/jobs/">AI Jobs</a> → {escape_html(title)}</div>
            <h1>{escape_html(title)}</h1>
            <p class="lead">{escape_html(description)}</p>
            <div class="stats-row">
                <div class="stat-box"><div class="stat-number">{total}</div><div class="stat-label">Open Roles</div></div>
                <div class="stat-box"><div class="stat-number">${avg_salary}K</div><div class="stat-label">Avg Salary</div></div>
            </div>
        </div>
    </div>

    <main>
        <div class="container">
            <style>.jobs-grid {{ display: flex; flex-direction: column; gap: 12px; }}</style>
            <div class="jobs-grid">{job_cards}</div>
            {get_cta_box()}
        </div>
    </main>

{get_footer_html()}'''

    page_dir = f'{JOBS_DIR}/{slug}'
    os.makedirs(page_dir, exist_ok=True)
    with open(f'{page_dir}/index.html', 'w') as f:
        f.write(html)
    return True


# Define categories
CATEGORIES = [
    # By Role
    ('job_category', 'Prompt Engineer', 'prompt-engineer', 'Prompt Engineer Jobs', f'Browse Prompt Engineer positions at top AI companies.'),
    ('job_category', 'AI/ML Engineer', 'ai-ml-engineer', 'AI/ML Engineer Jobs', f'Machine Learning and AI Engineer positions.'),
    ('job_category', 'LLM Engineer', 'llm-engineer', 'LLM Engineer Jobs', f'Large Language Model Engineer positions.'),
    ('job_category', 'MLOps Engineer', 'mlops-engineer', 'MLOps Engineer Jobs', f'MLOps and ML Infrastructure Engineer roles.'),
    ('job_category', 'Research Engineer', 'research-engineer', 'Research Engineer Jobs', f'AI Research Engineer and Applied Scientist roles.'),
    ('job_category', 'AI Agent Developer', 'ai-agent-developer', 'AI Agent Developer Jobs', f'AI Agent and Autonomous Systems Developer roles.'),
    # By Experience
    ('experience_level', 'senior', 'senior', 'Senior AI Jobs', f'Senior and Lead AI/ML positions.'),
    ('experience_level', 'entry', 'entry-level', 'Entry-Level AI Jobs', f'Entry-level and junior AI/ML positions.'),
    # By Location
    ('metro', 'San Francisco', 'san-francisco', 'AI Jobs in San Francisco', f'AI and ML jobs in the San Francisco Bay Area.'),
    ('metro', 'New York', 'new-york', 'AI Jobs in New York', f'AI and ML jobs in New York City.'),
    ('metro', 'Seattle', 'seattle', 'AI Jobs in Seattle', f'AI and ML jobs in Seattle.'),
    ('metro', 'Remote', 'remote', 'Remote AI Jobs', f'Remote AI and ML engineering positions.'),
]

print("\n Generating category pages...")
for field, value, slug, title, desc in CATEGORIES:
    if field == 'metro' and value == 'Remote':
        filtered = df[df.get('remote_type', df.get('is_remote', '')).astype(str).str.contains('remote', case=False, na=False)]
    elif field in df.columns:
        filtered = df[df[field] == value]
    else:
        filtered = df[df['location'].str.contains(value, case=False, na=False)] if 'location' in df.columns else pd.DataFrame()

    if generate_category_page(filtered, slug, title, desc):
        print(f"   Generated /jobs/{slug}/ ({len(filtered)} jobs)")

print("="*70)
