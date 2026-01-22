#!/usr/bin/env python3
"""
Generate the main job board listing page at /jobs/index.html
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

# Add scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    from templates import (
        get_html_head, get_nav_html, get_footer_html, get_cta_box,
        slugify, format_salary, is_remote, BASE_URL, SITE_NAME
    )
except Exception as e:
    print(f"ERROR importing templates: {e}")
    traceback.print_exc()
    sys.exit(1)

DATA_DIR = 'data'
SITE_DIR = 'site'
JOBS_DIR = f'{SITE_DIR}/jobs'


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


def main():
    print("="*70)
    print("  AI MARKET PULSE - GENERATING JOB BOARD")
    print("="*70)

    os.makedirs(JOBS_DIR, exist_ok=True)

    # Load job data
    files = glob.glob(f"{DATA_DIR}/ai_jobs_*.csv")
    print(f"  Looking for CSV files in {DATA_DIR}/")
    print(f"  Found: {files}")

    if files:
        latest_file = max(files, key=os.path.getmtime)
        print(f"  Loading: {latest_file}")
        df = pd.read_csv(latest_file)
        print(f"\n Loaded {len(df)} jobs from {latest_file}")
        print(f"  Columns: {list(df.columns)}")
    elif os.path.exists(f"{DATA_DIR}/jobs.json"):
        with open(f"{DATA_DIR}/jobs.json") as f:
            data = json.load(f)
        df = pd.DataFrame(data.get('jobs', []))
        print(f"\n Loaded {len(df)} jobs from jobs.json")
    else:
        print(f" No job data found in {DATA_DIR}/")
        print(f"  Current directory: {os.getcwd()}")
        print(f"  Directory contents: {os.listdir('.')}")
        if os.path.exists(DATA_DIR):
            print(f"  Data dir contents: {os.listdir(DATA_DIR)}")
        sys.exit(1)

    # Calculate stats
    total_jobs = len(df)

    # Count remote jobs safely
    remote_jobs = 0
    if 'remote_type' in df.columns:
        remote_jobs = len(df[df['remote_type'].astype(str).str.contains('remote', case=False, na=False)])

    # Salary stats
    salary_col = 'salary_max' if 'salary_max' in df.columns else 'max_amount'
    salaries = df[salary_col].dropna() if salary_col in df.columns else pd.Series([])
    salaries = salaries[salaries > 0]
    avg_salary = int(salaries.mean() / 1000) if len(salaries) > 0 else 0

    # Category counts
    categories = df['job_category'].value_counts().head(6).to_dict() if 'job_category' in df.columns else {}

    # Sort by salary (highest first), then by date
    if salary_col in df.columns:
        df['_sort_salary'] = pd.to_numeric(df[salary_col], errors='coerce').fillna(0)
        df = df.sort_values('_sort_salary', ascending=False)

    # Generate job cards HTML for ALL jobs
    job_cards_html = ""
    for idx, row in df.iterrows():
        company = escape_html(str(row.get('company', row.get('company_name', 'Unknown'))))
        title = escape_html(str(row.get('title', 'AI Role')))
        location = escape_html(str(row.get('location', ''))) if pd.notna(row.get('location')) else ''
        category = escape_html(str(row.get('job_category', ''))) if pd.notna(row.get('job_category')) else ''
        remote_status = is_remote(row)
        salary_val = row.get('salary_max', row.get('max_amount', 0))
        salary_val = float(salary_val) if pd.notna(salary_val) else 0

        salary = format_salary(row.get('salary_min', row.get('min_amount')), row.get('salary_max', row.get('max_amount')))

        # Generate slug
        job_slug = f"{make_slug(row.get('company', row.get('company_name', '')))}-{make_slug(row.get('title', ''))}"
        hash_suffix = hashlib.md5(f"{row.get('company', row.get('company_name', ''))}{row.get('title','')}{row.get('location','')}".encode()).hexdigest()[:6]
        job_slug = f"{job_slug}-{hash_suffix}"

        # Data attributes for filtering/searching
        job_cards_html += f'''
            <a href="/jobs/{job_slug}/" class="job-card"
               data-company="{company.lower()}"
               data-title="{title.lower()}"
               data-category="{category.lower()}"
               data-remote="{'true' if remote_status else 'false'}"
               data-salary="{int(salary_val)}">
                <div class="job-card__content">
                    <div class="job-card__company">{company}</div>
                    <div class="job-card__title">{title}</div>
                    <div class="job-card__meta">
                        {f'<span class="job-card__tag job-card__tag--salary">{salary}</span>' if salary else ''}
                        {f'<span class="job-card__tag job-card__tag--remote">Remote</span>' if remote_status else ''}
                        {f'<span class="job-card__tag">{location}</span>' if location and not remote_status else ''}
                        {f'<span class="job-card__tag">{category}</span>' if category else ''}
                    </div>
                </div>
            </a>
        '''

    # Category filter buttons
    category_filters = ""
    for cat, count in categories.items():
        cat_slug = make_slug(cat)
        category_filters += f'<a href="/jobs/{cat_slug}/" class="filter-btn">{escape_html(cat)} ({count})</a>\n'

    # Page HTML with search, filters, and pagination
    html = f'''{get_html_head(
        f"{total_jobs} AI & ML Engineer Jobs - ${avg_salary}K avg",
        f"Browse {total_jobs} AI engineer, ML engineer, and prompt engineer jobs. Average salary ${avg_salary}K. {remote_jobs} remote positions available. Updated weekly.",
        "jobs/"
    )}
{get_nav_html('jobs')}

    <div class="page-header">
        <div class="container">
            <div class="page-label">AI Job Board</div>
            <h1>{total_jobs} AI & ML Jobs</h1>
            <p class="lead">Prompt Engineer, AI Engineer, ML Engineer, and more. Real salaries, no recruiter spin. Updated weekly.</p>

            <div class="stats-row">
                <div class="stat-box">
                    <div class="stat-number">{total_jobs}</div>
                    <div class="stat-label">Open Roles</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">${avg_salary}K</div>
                    <div class="stat-label">Avg Salary</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{remote_jobs}</div>
                    <div class="stat-label">Remote</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{len(categories)}</div>
                    <div class="stat-label">Categories</div>
                </div>
            </div>
        </div>
    </div>

    <main>
        <div class="container">
            <!-- Search Box -->
            <div class="search-section" style="margin-bottom: 24px;">
                <input type="text" id="job-search" placeholder="Search jobs by title, company, or keyword..."
                       style="width: 100%; padding: 16px 20px; font-size: 1rem; background: var(--bg-card);
                              border: 1px solid var(--border); border-radius: 12px; color: var(--text-primary);
                              outline: none; transition: border-color 0.15s;">
                <div id="search-results" style="margin-top: 8px; font-size: 0.875rem; color: var(--text-muted);"></div>
            </div>

            <!-- Filter Buttons -->
            <div class="filters-section" style="margin-bottom: 32px;">
                <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center;">
                    <button class="filter-btn active" data-filter="all">All Jobs ({total_jobs})</button>
                    <button class="filter-btn" data-filter="remote">Remote Only ({remote_jobs})</button>
                    <button class="filter-btn" data-filter="salary-200">$200K+ ({len(df[df['_sort_salary'] >= 200000]) if '_sort_salary' in df.columns else 0})</button>
                    <button class="filter-btn" data-filter="salary-150">$150K+ ({len(df[df['_sort_salary'] >= 150000]) if '_sort_salary' in df.columns else 0})</button>
                    {category_filters}
                </div>
            </div>

            <style>
                #job-search:focus {{
                    border-color: var(--gold);
                    box-shadow: 0 0 0 3px rgba(232, 168, 124, 0.1);
                }}
                .filter-btn {{
                    display: inline-block;
                    padding: 8px 16px;
                    background: var(--bg-card);
                    border: 1px solid var(--border);
                    border-radius: 20px;
                    color: var(--text-secondary);
                    text-decoration: none;
                    font-size: 0.875rem;
                    transition: all 0.15s;
                    cursor: pointer;
                }}
                .filter-btn:hover {{
                    border-color: var(--teal-light);
                    color: var(--text-primary);
                }}
                .filter-btn.active {{
                    background: var(--gold);
                    color: var(--bg-darker);
                    border-color: var(--gold);
                }}
                .jobs-grid {{
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }}
                .job-card.hidden {{
                    display: none !important;
                }}
                .load-more-section {{
                    text-align: center;
                    padding: 32px 0;
                }}
                .load-more-btn {{
                    display: inline-block;
                    padding: 16px 48px;
                    background: var(--teal-primary);
                    color: var(--text-primary);
                    border: none;
                    border-radius: 8px;
                    font-size: 1rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.15s;
                }}
                .load-more-btn:hover {{
                    background: var(--teal-light);
                    transform: translateY(-2px);
                }}
                .job-count-display {{
                    margin-bottom: 16px;
                    font-size: 0.9rem;
                    color: var(--text-muted);
                }}
            </style>

            <div class="job-count-display">
                Showing <span id="visible-count">50</span> of <span id="total-filtered">{total_jobs}</span> jobs
            </div>

            <div class="jobs-grid" id="jobs-container">
                {job_cards_html}
            </div>

            <div class="load-more-section">
                <button class="load-more-btn" id="load-more">Load More Jobs</button>
            </div>

            {get_cta_box()}

            <!-- SEO Content Section -->
            <div class="seo-content" style="max-width: 800px; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--border); color: var(--text-secondary); line-height: 1.8;">
                <h2 style="font-size: 1.5rem; color: var(--text-primary); margin-bottom: 1rem;">About Our AI Job Board</h2>
                <p style="margin-bottom: 1rem;">
                    AI Market Pulse aggregates <strong style="color: var(--text-primary);">{total_jobs:,} AI and ML job postings</strong> from Indeed, LinkedIn, Greenhouse, Lever, and company career pages. We focus exclusively on roles in the AI ecosystem: <strong style="color: var(--text-primary);">AI/ML Engineers</strong>, <strong style="color: var(--text-primary);">Prompt Engineers</strong>, <strong style="color: var(--text-primary);">LLM Engineers</strong>, <strong style="color: var(--text-primary);">MLOps Engineers</strong>, <strong style="color: var(--text-primary);">Research Scientists</strong>, <strong style="color: var(--text-primary);">Data Scientists</strong>, and <strong style="color: var(--text-primary);">AI Product Managers</strong>.
                </p>
                <p style="margin-bottom: 1rem;">
                    Every listing shows real salary ranges when available—no hidden compensation, no bait-and-switch. We update our database weekly to remove filled positions and add new opportunities. Currently, <strong style="color: var(--text-primary);">{remote_jobs}</strong> positions offer remote work options, and the average salary across all listings is <strong style="color: var(--text-primary);">${avg_salary}K</strong>.
                </p>

                <h3 style="font-size: 1.25rem; color: var(--text-primary); margin: 2rem 0 1rem;">What Makes Our Job Board Different</h3>
                <p style="margin-bottom: 1rem;">
                    Most job boards are cluttered with irrelevant postings, outdated listings, and hidden salaries. AI Market Pulse is built by AI professionals for AI professionals. We curate roles specifically in artificial intelligence and machine learning—no generic "software engineer" postings with AI buzzwords. When a job says "Prompt Engineer," it's actually a prompt engineering role.
                </p>
                <p style="margin-bottom: 1rem;">
                    We prioritize transparency: jobs with disclosed salary ranges appear first, and we filter out postings with obvious red flags. Our data feeds the salary benchmarks and market intelligence you'll find elsewhere on the site, giving you context for every opportunity.
                </p>

                <h3 style="font-size: 1.25rem; color: var(--text-primary); margin: 2rem 0 1rem;">AI Job Categories Explained</h3>
                <p style="margin-bottom: 1rem;">
                    <strong style="color: var(--text-primary);">AI/ML Engineer:</strong> The broad category covering engineers who build and deploy machine learning models. Typically requires Python, PyTorch/TensorFlow, and cloud platform experience. Salaries range from $150K to $300K+ depending on seniority.
                </p>
                <p style="margin-bottom: 1rem;">
                    <strong style="color: var(--text-primary);">Prompt Engineer:</strong> Specialists in crafting prompts and optimizing LLM outputs. Emerged as a distinct role in 2023 and has rapidly professionalized. Focus on evaluation, prompt optimization, and RAG systems. Salaries typically $120K-$250K.
                </p>
                <p style="margin-bottom: 1rem;">
                    <strong style="color: var(--text-primary);">LLM Engineer:</strong> Engineers focused specifically on large language model development and deployment. More technical than prompt engineering, involving fine-tuning, inference optimization, and model serving. Salaries $160K-$300K.
                </p>
                <p style="margin-bottom: 1rem;">
                    <strong style="color: var(--text-primary);">MLOps Engineer:</strong> The infrastructure specialists who make ML models production-ready. Focus on deployment pipelines, monitoring, and scaling. Combines DevOps skills with ML knowledge. Salaries $140K-$280K.
                </p>

                <h3 style="font-size: 1.25rem; color: var(--text-primary); margin: 2rem 0 1rem;">Tips for AI Job Seekers</h3>
                <p style="margin-bottom: 1rem;">
                    <strong style="color: var(--text-primary);">Focus on fundamentals:</strong> Python proficiency, understanding of ML concepts, and familiarity with at least one major framework (PyTorch preferred in 2026) are non-negotiable for most roles.
                </p>
                <p style="margin-bottom: 1rem;">
                    <strong style="color: var(--text-primary);">Build demonstrable projects:</strong> GitHub portfolios matter more than certifications. Show working code, deployed applications, or contributions to open-source AI projects.
                </p>
                <p style="margin-bottom: 1rem;">
                    <strong style="color: var(--text-primary);">Specialize strategically:</strong> As the market matures, specialists command premium salaries. Choose a focus area—LLM orchestration, computer vision, MLOps, or a specific industry vertical—and go deep.
                </p>
            </div>
        </div>
    </main>

    <script>
    (function() {{
        const JOBS_PER_PAGE = 50;
        let visibleCount = JOBS_PER_PAGE;
        let currentFilter = 'all';
        let searchTerm = '';

        const container = document.getElementById('jobs-container');
        const allJobs = Array.from(container.querySelectorAll('.job-card'));
        const loadMoreBtn = document.getElementById('load-more');
        const searchInput = document.getElementById('job-search');
        const searchResults = document.getElementById('search-results');
        const visibleCountEl = document.getElementById('visible-count');
        const totalFilteredEl = document.getElementById('total-filtered');
        const filterBtns = document.querySelectorAll('.filter-btn[data-filter]');

        function getFilteredJobs() {{
            return allJobs.filter(job => {{
                // Search filter
                if (searchTerm) {{
                    const company = job.dataset.company || '';
                    const title = job.dataset.title || '';
                    if (!company.includes(searchTerm) && !title.includes(searchTerm)) {{
                        return false;
                    }}
                }}

                // Category/type filter
                if (currentFilter === 'all') return true;
                if (currentFilter === 'remote') return job.dataset.remote === 'true';
                if (currentFilter === 'salary-200') return parseInt(job.dataset.salary) >= 200000;
                if (currentFilter === 'salary-150') return parseInt(job.dataset.salary) >= 150000;

                // Category filter
                const category = job.dataset.category || '';
                return category.includes(currentFilter.toLowerCase());
            }});
        }}

        function updateDisplay() {{
            const filtered = getFilteredJobs();
            const toShow = filtered.slice(0, visibleCount);

            allJobs.forEach(job => job.classList.add('hidden'));
            toShow.forEach(job => job.classList.remove('hidden'));

            visibleCountEl.textContent = Math.min(visibleCount, filtered.length);
            totalFilteredEl.textContent = filtered.length;

            loadMoreBtn.style.display = visibleCount >= filtered.length ? 'none' : 'inline-block';

            if (searchTerm) {{
                searchResults.textContent = `Found ${{filtered.length}} jobs matching "${{searchTerm}}"`;
            }} else {{
                searchResults.textContent = '';
            }}
        }}

        // Load more
        loadMoreBtn.addEventListener('click', () => {{
            visibleCount += JOBS_PER_PAGE;
            updateDisplay();
        }});

        // Search
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {{
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {{
                searchTerm = e.target.value.toLowerCase().trim();
                visibleCount = JOBS_PER_PAGE;
                updateDisplay();
            }}, 200);
        }});

        // Filter buttons
        filterBtns.forEach(btn => {{
            btn.addEventListener('click', () => {{
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.dataset.filter;
                visibleCount = JOBS_PER_PAGE;
                updateDisplay();
            }});
        }});

        // Initial display
        updateDisplay();
    }})();
    </script>

{get_footer_html()}'''

    # Save
    with open(f'{JOBS_DIR}/index.html', 'w') as f:
        f.write(html)

    print(f"\n Generated job board with {total_jobs} jobs")
    print(f" Saved to {JOBS_DIR}/index.html")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
