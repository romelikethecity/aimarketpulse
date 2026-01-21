#!/usr/bin/env python3
"""
Generate individual company pages for AI Market Pulse
Each company with AI job postings gets a dedicated page
"""

import pandas as pd
import os
import glob
from datetime import datetime
import sys
sys.path.insert(0, 'scripts')

from templates import slugify, format_salary, BASE_URL, SITE_NAME

DATA_DIR = 'data'
SITE_DIR = 'site'
COMPANIES_DIR = f'{SITE_DIR}/companies'


def get_latest_jobs():
    """Load latest enriched job data"""
    job_files = glob.glob(f"{DATA_DIR}/ai_jobs_*.csv")
    if not job_files:
        return pd.DataFrame()

    latest_file = sorted(job_files)[-1]
    print(f"  Loading: {latest_file}")
    return pd.read_csv(latest_file)


def generate_company_page(company_name, jobs_df):
    """Generate a single company page"""
    company_slug = slugify(company_name)
    if not company_slug:
        return None

    company_dir = f"{COMPANIES_DIR}/{company_slug}"
    os.makedirs(company_dir, exist_ok=True)

    # Get company jobs
    company_jobs = jobs_df[jobs_df['company'] == company_name].copy()
    num_jobs = len(company_jobs)

    # Get unique categories
    categories = []
    if 'job_category' in company_jobs.columns:
        categories = company_jobs['job_category'].dropna().unique().tolist()

    # Calculate salary range
    salary_range = ""
    if 'salary_max' in company_jobs.columns:
        salaries = pd.to_numeric(company_jobs['salary_max'], errors='coerce').dropna()
        if len(salaries) > 0:
            min_sal = salaries.min()
            max_sal = salaries.max()
            salary_range = f"${int(min_sal/1000)}K - ${int(max_sal/1000)}K"

    # Get locations
    locations = []
    if 'location' in company_jobs.columns:
        locations = company_jobs['location'].dropna().unique().tolist()[:5]

    # Skills mentioned
    skills_mentioned = []
    if 'skills_tags' in company_jobs.columns:
        for skills in company_jobs['skills_tags'].dropna():
            if isinstance(skills, str):
                skills_mentioned.extend(skills.split(','))
    skills_count = {}
    for skill in skills_mentioned:
        skill = skill.strip()
        if skill:
            skills_count[skill] = skills_count.get(skill, 0) + 1
    top_skills = sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:10]

    # Generate job listings HTML
    jobs_html = ""
    for _, job in company_jobs.iterrows():
        title = job.get('title', 'Untitled')
        location = job.get('location', 'Location not specified')
        salary = format_salary(job.get('salary_min'), job.get('salary_max'))
        category = job.get('job_category', '')
        url = job.get('job_url_direct', job.get('source_url', '#'))

        jobs_html += f'''
        <div class="job-card">
            <div class="job-category">{category}</div>
            <h3 class="job-title"><a href="{url}" target="_blank" rel="noopener">{title}</a></h3>
            <div class="job-meta">
                <span class="job-location">{location}</span>
                {f'<span class="job-salary">{salary}</span>' if salary else ''}
            </div>
        </div>
        '''

    # Generate skills HTML
    skills_html = ""
    if top_skills:
        skills_html = '<div class="skills-list">'
        for skill, count in top_skills:
            skills_html += f'<span class="skill-tag">{skill} ({count})</span>'
        skills_html += '</div>'

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} AI Jobs | AI Market Pulse</title>
    <meta name="description" content="View {num_jobs} AI and machine learning jobs at {company_name}. {salary_range if salary_range else 'Competitive salaries'} for roles in {", ".join(categories[:3]) if categories else "AI/ML"}.">

    <link rel="canonical" href="{BASE_URL}/companies/{company_slug}/">

    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #334155;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --accent: #22d3ee;
            --accent-gold: #f5a623;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }}

        .container {{ max-width: 1000px; margin: 0 auto; padding: 0 20px; }}

        nav {{
            background: var(--bg-secondary);
            padding: 1rem 0;
            border-bottom: 1px solid var(--bg-card);
        }}
        nav .container {{ display: flex; justify-content: space-between; align-items: center; }}
        .nav-brand {{ font-size: 1.5rem; font-weight: 700; color: var(--accent); text-decoration: none; }}
        .nav-links {{ display: flex; gap: 2rem; }}
        .nav-links a {{ color: var(--text-secondary); text-decoration: none; }}
        .nav-links a:hover {{ color: var(--accent); }}

        .breadcrumb {{
            padding: 1rem 0;
            color: var(--text-secondary);
            font-size: 0.875rem;
        }}
        .breadcrumb a {{ color: var(--accent); text-decoration: none; }}

        .company-header {{
            padding: 2rem 0;
            border-bottom: 1px solid var(--bg-card);
        }}
        .company-header h1 {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        .company-stats {{
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }}
        .company-stat {{
            background: var(--bg-secondary);
            padding: 1rem 1.5rem;
            border-radius: 8px;
        }}
        .stat-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--accent);
        }}
        .stat-label {{
            font-size: 0.875rem;
            color: var(--text-secondary);
        }}

        .company-details {{
            padding: 2rem 0;
        }}
        .section-title {{
            font-size: 1.25rem;
            margin-bottom: 1rem;
            color: var(--text-primary);
        }}
        .skills-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 2rem;
        }}
        .skill-tag {{
            background: var(--bg-card);
            color: var(--accent);
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
        }}
        .locations-list {{
            color: var(--text-secondary);
            margin-bottom: 2rem;
        }}

        .jobs-section {{
            padding: 2rem 0;
        }}
        .job-card {{
            background: var(--bg-secondary);
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border: 1px solid var(--bg-card);
        }}
        .job-card:hover {{ border-color: var(--accent); }}
        .job-category {{
            font-size: 0.75rem;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}
        .job-title {{ margin-bottom: 0.5rem; }}
        .job-title a {{
            color: var(--text-primary);
            text-decoration: none;
        }}
        .job-title a:hover {{ color: var(--accent); }}
        .job-meta {{
            display: flex;
            gap: 1.5rem;
            color: var(--text-secondary);
            font-size: 0.875rem;
        }}
        .job-salary {{
            color: var(--accent-gold);
            font-weight: 600;
        }}

        footer {{
            background: var(--bg-secondary);
            padding: 2rem 0;
            margin-top: 3rem;
            border-top: 1px solid var(--bg-card);
            text-align: center;
            color: var(--text-secondary);
        }}

        @media (max-width: 768px) {{
            .nav-links {{ display: none; }}
            .company-header h1 {{ font-size: 1.75rem; }}
            .company-stats {{ flex-direction: column; }}
        }}
    </style>
</head>
<body>
    <nav>
        <div class="container">
            <a href="/" class="nav-brand">AI Market Pulse</a>
            <div class="nav-links">
                <a href="/jobs/">AI Jobs</a>
                <a href="/salaries/">Salaries</a>
                <a href="/insights/">Insights</a>
                <a href="/companies/">Companies</a>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> / <a href="/companies/">Companies</a> / {company_name}
        </div>

        <header class="company-header">
            <h1>{company_name}</h1>
            <div class="company-stats">
                <div class="company-stat">
                    <div class="stat-value">{num_jobs}</div>
                    <div class="stat-label">Open AI Roles</div>
                </div>
                {f'<div class="company-stat"><div class="stat-value">{salary_range}</div><div class="stat-label">Salary Range</div></div>' if salary_range else ''}
                <div class="company-stat">
                    <div class="stat-value">{len(categories)}</div>
                    <div class="stat-label">Role Types</div>
                </div>
            </div>
        </header>

        <section class="company-details">
            {f'<h2 class="section-title">Skills & Technologies</h2>{skills_html}' if top_skills else ''}

            {f'<h2 class="section-title">Locations</h2><p class="locations-list">{", ".join(locations)}</p>' if locations else ''}

            {f'<h2 class="section-title">Role Categories</h2><p class="locations-list">{", ".join(categories)}</p>' if categories else ''}
        </section>

        <section class="jobs-section">
            <h2 class="section-title">All Open Positions ({num_jobs})</h2>
            {jobs_html}
        </section>
    </div>

    <footer>
        <div class="container">
            <p>© 2026 AI Market Pulse. All rights reserved.</p>
            <p><a href="/jobs/" style="color: var(--accent);">Browse All AI Jobs</a></p>
        </div>
    </footer>
</body>
</html>
'''

    output_path = f"{company_dir}/index.html"
    with open(output_path, 'w') as f:
        f.write(html)

    return company_slug


def generate_companies_index(companies_data):
    """Generate the companies index page"""
    os.makedirs(COMPANIES_DIR, exist_ok=True)

    # Sort by job count
    sorted_companies = sorted(companies_data.items(), key=lambda x: x[1]['count'], reverse=True)

    companies_html = ""
    for company, data in sorted_companies:
        slug = slugify(company)
        if not slug:
            continue
        companies_html += f'''
        <a href="/companies/{slug}/" class="company-card">
            <h3>{company}</h3>
            <div class="company-meta">
                <span>{data['count']} open roles</span>
                {f'<span class="salary">{data["salary_range"]}</span>' if data.get("salary_range") else ''}
            </div>
        </a>
        '''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Companies Hiring for AI Roles | AI Market Pulse</title>
    <meta name="description" content="Browse {len(sorted_companies)} companies actively hiring for AI, ML, and Prompt Engineering roles.">

    <link rel="canonical" href="{BASE_URL}/companies/">

    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #334155;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --accent: #22d3ee;
            --accent-gold: #f5a623;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }}

        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}

        nav {{
            background: var(--bg-secondary);
            padding: 1rem 0;
            border-bottom: 1px solid var(--bg-card);
        }}
        nav .container {{ display: flex; justify-content: space-between; align-items: center; }}
        .nav-brand {{ font-size: 1.5rem; font-weight: 700; color: var(--accent); text-decoration: none; }}

        .page-header {{
            padding: 3rem 0;
            text-align: center;
        }}
        .page-header h1 {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        .page-header p {{
            color: var(--text-secondary);
            font-size: 1.1rem;
        }}

        .companies-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.5rem;
            padding: 2rem 0;
        }}
        .company-card {{
            background: var(--bg-secondary);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--bg-card);
            text-decoration: none;
            color: var(--text-primary);
            transition: transform 0.2s, border-color 0.2s;
        }}
        .company-card:hover {{
            transform: translateY(-4px);
            border-color: var(--accent);
        }}
        .company-card h3 {{
            margin-bottom: 0.5rem;
        }}
        .company-meta {{
            display: flex;
            justify-content: space-between;
            color: var(--text-secondary);
            font-size: 0.875rem;
        }}
        .salary {{
            color: var(--accent-gold);
        }}

        footer {{
            background: var(--bg-secondary);
            padding: 2rem 0;
            margin-top: 3rem;
            text-align: center;
            color: var(--text-secondary);
        }}
    </style>
</head>
<body>
    <nav>
        <div class="container">
            <a href="/" class="nav-brand">AI Market Pulse</a>
        </div>
    </nav>

    <div class="container">
        <header class="page-header">
            <h1>Companies Hiring for AI Roles</h1>
            <p>{len(sorted_companies)} companies with open AI, ML, and Prompt Engineering positions</p>
        </header>

        <div class="companies-grid">
            {companies_html}
        </div>
    </div>

    <footer>
        <p>© 2026 AI Market Pulse</p>
    </footer>
</body>
</html>
'''

    output_path = f"{COMPANIES_DIR}/index.html"
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"  Saved companies index: {output_path}")


def main():
    print("="*70)
    print("  GENERATING COMPANY PAGES")
    print("="*70)

    # Load job data
    jobs_df = get_latest_jobs()
    if jobs_df.empty:
        print("  No job data found")
        return

    print(f"  Loaded {len(jobs_df)} jobs")

    # Get companies with enough jobs
    company_counts = jobs_df['company'].value_counts()
    companies_to_generate = company_counts[company_counts >= 2].index.tolist()

    print(f"  Found {len(companies_to_generate)} companies with 2+ jobs")

    # Generate individual company pages
    companies_data = {}
    generated = 0

    for company in companies_to_generate:
        if pd.isna(company) or not company or company == 'Unknown':
            continue

        company_jobs = jobs_df[jobs_df['company'] == company]

        # Calculate salary range
        salary_range = ""
        if 'salary_max' in company_jobs.columns:
            salaries = pd.to_numeric(company_jobs['salary_max'], errors='coerce').dropna()
            if len(salaries) > 0:
                min_sal = salaries.min()
                max_sal = salaries.max()
                salary_range = f"${int(min_sal/1000)}K - ${int(max_sal/1000)}K"

        companies_data[company] = {
            'count': len(company_jobs),
            'salary_range': salary_range
        }

        slug = generate_company_page(company, jobs_df)
        if slug:
            generated += 1

    # Generate index page
    generate_companies_index(companies_data)

    print(f"\n{'='*70}")
    print(f"  Generated {generated} company pages")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
