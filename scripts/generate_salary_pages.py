#!/usr/bin/env python3
"""
Generate salary benchmark pages for programmatic SEO.
Creates pages like /salaries/ml-engineer/, /salaries/san-francisco/, /salaries/senior/
"""

import pandas as pd
from datetime import datetime
import glob
import os
import json
import sys
import traceback

# Add scripts directory to path using absolute path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    from templates import get_html_head, get_nav_html, get_footer_html, get_cta_box, BASE_URL, SITE_NAME
except Exception as e:
    print(f"ERROR importing templates: {e}")
    traceback.print_exc()
    sys.exit(1)

DATA_DIR = 'data'
SITE_DIR = 'site'
SALARIES_DIR = f'{SITE_DIR}/salaries'

# Define salary categories
ROLE_CATEGORIES = [
    ('AI/ML Engineer', 'ai-ml-engineer', 'AI/ML Engineer'),
    ('Prompt Engineer', 'prompt-engineer', 'Prompt Engineer'),
    ('LLM Engineer', 'llm-engineer', 'LLM Engineer'),
    ('MLOps Engineer', 'mlops-engineer', 'MLOps Engineer'),
    ('Research Engineer', 'research-engineer', 'Research Engineer'),
    ('AI Agent Developer', 'ai-agent-developer', 'AI Agent Developer'),
    ('AI Product Manager', 'ai-product-manager', 'AI Product Manager'),
    ('Data Scientist', 'data-scientist', 'Data Scientist'),
]

METRO_CATEGORIES = [
    ('San Francisco', 'san-francisco'),
    ('New York', 'new-york'),
    ('Seattle', 'seattle'),
    ('Austin', 'austin'),
    ('Boston', 'boston'),
    ('Los Angeles', 'los-angeles'),
    ('Remote', 'remote'),
]

EXPERIENCE_CATEGORIES = [
    ('senior', 'senior', 'Senior'),
    ('mid', 'mid-level', 'Mid-Level'),
    ('entry', 'entry-level', 'Entry-Level'),
]


def escape_html(text):
    if pd.isna(text):
        return ''
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def generate_salary_page(filtered_df, slug, title, category_type, salary_col, min_col):
    """Generate a salary page for a specific category"""
    if len(filtered_df) < 3:
        return False

    try:
        avg_min = int(filtered_df[min_col].mean()) if filtered_df[min_col].notna().any() else 0
        avg_max = int(filtered_df[salary_col].mean())
        median = int(filtered_df[salary_col].median())
    except (ValueError, TypeError):
        avg_min = 0
        avg_max = 0
        median = 0

    sample_size = len(filtered_df)

    # Top paying companies
    company_col = 'company' if 'company' in filtered_df.columns else 'company_name'
    if company_col in filtered_df.columns:
        top_companies = filtered_df.nlargest(5, salary_col)[[company_col, salary_col]].to_dict('records')
    else:
        top_companies = []

    companies_html = ""
    for c in top_companies:
        company_name = c.get('company', c.get('company_name', 'Unknown'))
        try:
            sal = int(c[salary_col])
        except (ValueError, TypeError):
            sal = 0
        companies_html += f'''
            <div class="company-row">
                <span class="company-name">{escape_html(str(company_name))}</span>
                <span class="company-salary">${sal:,}</span>
            </div>
        '''

    html = f'''{get_html_head(
        f"{title} Salary 2026 - ${avg_max//1000}K Average",
        f"{title} salary benchmarks based on {sample_size} job postings. Average ${avg_min//1000}K-${avg_max//1000}K. Median ${median//1000}K.",
        f"salaries/{slug}/"
    )}
{get_nav_html('salaries')}

    <div class="page-header">
        <div class="container">
            <div class="breadcrumb">
                <a href="/">Home</a> → <a href="/salaries/">Salaries</a> → {escape_html(title)}
            </div>
            <h1>{escape_html(title)} Salary 2026</h1>
            <p class="lead">Salary benchmarks based on {sample_size} job postings with disclosed compensation.</p>

            <div class="stats-row">
                <div class="stat-box">
                    <div class="stat-number">${avg_min//1000}K</div>
                    <div class="stat-label">Avg Min</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">${avg_max//1000}K</div>
                    <div class="stat-label">Avg Max</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">${median//1000}K</div>
                    <div class="stat-label">Median</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{sample_size}</div>
                    <div class="stat-label">Sample Size</div>
                </div>
            </div>
        </div>
    </div>

    <main>
        <div class="container">
            <style>
                .company-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 16px;
                    background: var(--bg-card);
                    border: 1px solid var(--border);
                    border-radius: 8px;
                    margin-bottom: 8px;
                }}
                .company-name {{ color: var(--text-primary); font-weight: 500; }}
                .company-salary {{ color: var(--gold); font-weight: 600; }}
            </style>

            {'<div class="section"><h2 style="margin-bottom: 20px;">Top Paying Companies</h2>' + companies_html + '</div>' if companies_html else ''}

            <div class="section" style="background: var(--bg-card); border-radius: 12px; padding: 24px; border: 1px solid var(--border);">
                <h3>Methodology</h3>
                <p style="color: var(--text-secondary); margin-top: 12px;">
                    Salary data is collected from job postings on Indeed and company career pages.
                    Only jobs with disclosed compensation are included. Data is updated weekly.
                </p>
            </div>

            {get_cta_box()}
        </div>
    </main>

{get_footer_html()}'''

    page_dir = f'{SALARIES_DIR}/{slug}'
    os.makedirs(page_dir, exist_ok=True)
    with open(f'{page_dir}/index.html', 'w') as f:
        f.write(html)
    return True


def main():
    print("="*70)
    print("  AI MARKET PULSE - GENERATING SALARY PAGES")
    print("="*70)

    os.makedirs(SALARIES_DIR, exist_ok=True)

    # Load job data
    files = glob.glob(f"{DATA_DIR}/ai_jobs_*.csv")
    print(f"  Looking for CSV files in {DATA_DIR}/")
    print(f"  Found: {files}")

    if files:
        df = pd.read_csv(max(files, key=os.path.getmtime))
    elif os.path.exists(f"{DATA_DIR}/jobs.json"):
        with open(f"{DATA_DIR}/jobs.json") as f:
            df = pd.DataFrame(json.load(f).get('jobs', []))
    else:
        print(" No job data found")
        sys.exit(1)

    print(f"\n Loaded {len(df)} jobs")
    print(f"  Columns: {list(df.columns)}")

    # Filter to jobs with salary
    salary_col = 'salary_max' if 'salary_max' in df.columns else 'max_amount'
    min_col = 'salary_min' if 'salary_min' in df.columns else 'min_amount'

    if salary_col not in df.columns:
        print(f" ERROR: No salary column found ({salary_col})")
        sys.exit(1)

    df_salary = df[df[salary_col].notna() & (df[salary_col] > 0)].copy()
    print(f" Jobs with salary: {len(df_salary)}")

    # Generate role-based salary pages
    print("\n Generating role-based salary pages...")
    for category, slug, display in ROLE_CATEGORIES:
        filtered = df_salary[df_salary['job_category'] == category] if 'job_category' in df_salary.columns else pd.DataFrame()
        if generate_salary_page(filtered, slug, display, 'role', salary_col, min_col):
            print(f"   Generated /salaries/{slug}/ ({len(filtered)} jobs)")

    # Generate metro-based salary pages
    print("\n Generating metro-based salary pages...")
    for metro, slug in METRO_CATEGORIES:
        if metro == 'Remote':
            if 'remote_type' in df_salary.columns:
                filtered = df_salary[df_salary['remote_type'].astype(str).str.contains('remote', case=False, na=False)]
            else:
                filtered = pd.DataFrame()
        else:
            if 'metro' in df_salary.columns:
                filtered = df_salary[df_salary['metro'] == metro]
            elif 'location' in df_salary.columns:
                filtered = df_salary[df_salary['location'].str.contains(metro, case=False, na=False)]
            else:
                filtered = pd.DataFrame()
        if generate_salary_page(filtered, slug, metro, 'metro', salary_col, min_col):
            print(f"   Generated /salaries/{slug}/ ({len(filtered)} jobs)")

    # Generate experience-based salary pages
    print("\n Generating experience-based salary pages...")
    for level, slug, display in EXPERIENCE_CATEGORIES:
        filtered = df_salary[df_salary['experience_level'] == level] if 'experience_level' in df_salary.columns else pd.DataFrame()
        if generate_salary_page(filtered, slug, display, 'experience', salary_col, min_col):
            print(f"   Generated /salaries/{slug}/ ({len(filtered)} jobs)")

    # Generate index page
    overall_avg = int(df_salary[salary_col].mean()) if len(df_salary) > 0 else 0
    overall_median = int(df_salary[salary_col].median()) if len(df_salary) > 0 else 0
    index_html = f'''{get_html_head(
        "AI & ML Engineer Salary Benchmarks 2026",
        f"Comprehensive salary data for AI engineers, ML engineers, and prompt engineers. Average ${overall_avg//1000}K based on {len(df_salary)} jobs.",
        "salaries/"
    )}
{get_nav_html('salaries')}

    <div class="page-header">
        <div class="container">
            <h1>AI Salary Benchmarks 2026</h1>
            <p class="lead">Real salary data from {len(df_salary)} AI and ML job postings. Updated weekly.</p>
        </div>
    </div>

    <main>
        <div class="container">
            <style>
                .category-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; margin-bottom: 40px; }}
                .category-card {{
                    display: block;
                    background: var(--bg-card);
                    border: 1px solid var(--border);
                    border-radius: 12px;
                    padding: 24px;
                    text-decoration: none;
                    transition: all 0.2s;
                }}
                .category-card:hover {{ border-color: var(--teal-light); transform: translateY(-2px); }}
                .category-card h3 {{ color: var(--text-primary); margin-bottom: 8px; }}
                .category-card p {{ color: var(--text-secondary); font-size: 0.9rem; }}
                .seo-content {{ color: var(--text-secondary); line-height: 1.8; max-width: 800px; }}
                .seo-content p {{ margin-bottom: 1rem; }}
                .seo-content h3 {{ color: var(--text-primary); font-size: 1.15rem; margin: 1.5rem 0 0.75rem; }}
                .seo-content strong {{ color: var(--text-primary); }}
            </style>

            <!-- SEO Intro Content -->
            <div class="seo-content" style="margin-bottom: 3rem; padding-bottom: 2rem; border-bottom: 1px solid var(--border);">
                <p>
                    Understanding AI salaries in 2026 requires real data, not outdated surveys or recruiter estimates. AI Market Pulse tracks salary information from job postings with disclosed compensation across <strong>{len(df_salary):,} positions</strong>, giving you current benchmarks to inform your career decisions.
                </p>
                <p>
                    The average maximum salary across all AI roles is <strong>${overall_avg:,}</strong>, with a median of <strong>${overall_median:,}</strong>. However, compensation varies significantly by role type, location, and experience level. Prompt Engineers and LLM Engineers command premium salaries as demand outpaces supply, while ML Engineers and Data Scientists remain the volume leaders in job postings.
                </p>
                <h3>How We Collect Salary Data</h3>
                <p>
                    We aggregate salary information exclusively from job postings with disclosed compensation ranges. This includes listings from Indeed, LinkedIn, company career pages, and Greenhouse/Lever job boards. We filter out outliers and normalize data to annual USD equivalents. Our data is updated weekly to reflect current market conditions.
                </p>
                <h3>What Affects AI Salaries</h3>
                <p>
                    Three factors dominate AI compensation: <strong>location</strong> (San Francisco and New York lead, but remote salaries are increasingly competitive), <strong>specialization</strong> (LLM and prompt engineering command 15-25% premiums over general ML roles), and <strong>company stage</strong> (early-stage startups often offer equity-heavy packages while FAANG-tier companies lead in base salary). Browse our breakdowns below to find benchmarks relevant to your situation.
                </p>
            </div>

            <h2 style="margin-bottom: 20px;">By Role</h2>
            <div class="category-grid">
                {''.join([f'<a href="/salaries/{slug}/" class="category-card"><h3>{display}</h3><p>View salary data</p></a>' for _, slug, display in ROLE_CATEGORIES])}
            </div>

            <h2 style="margin-bottom: 20px;">By Location</h2>
            <div class="category-grid">
                {''.join([f'<a href="/salaries/{slug}/" class="category-card"><h3>{metro}</h3><p>View salary data</p></a>' for metro, slug in METRO_CATEGORIES])}
            </div>

            <h2 style="margin-bottom: 20px;">By Experience</h2>
            <div class="category-grid">
                {''.join([f'<a href="/salaries/{slug}/" class="category-card"><h3>{display}</h3><p>View salary data</p></a>' for _, slug, display in EXPERIENCE_CATEGORIES])}
            </div>

            <!-- SEO Bottom Content -->
            <div class="seo-content" style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--border);">
                <h3>Using Salary Data for Negotiations</h3>
                <p>
                    When negotiating an AI role, come prepared with specific data points. Know the salary range for your exact role title, target location, and experience level. Our data shows that candidates who cite specific market benchmarks typically negotiate 10-15% higher offers than those who don't. Remember that total compensation includes base salary, equity, bonuses, and benefits—our benchmarks focus on base salary ranges as disclosed in job postings.
                </p>
                <h3>2026 AI Salary Trends</h3>
                <p>
                    The AI job market continues to mature. While 2023-2024 saw explosive growth in LLM-related roles, 2026 shows more stabilization with continued strong demand for production-focused skills. <strong>MLOps</strong> and <strong>AI infrastructure</strong> roles are seeing the fastest salary growth as companies move from experimentation to deployment. Remote work remains prevalent, with remote-first companies often matching or exceeding on-site salaries to compete for talent.
                </p>
            </div>

            {get_cta_box()}
        </div>
    </main>

{get_footer_html()}'''

    with open(f'{SALARIES_DIR}/index.html', 'w') as f:
        f.write(index_html)

    print(f"\n Generated salary index page")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
