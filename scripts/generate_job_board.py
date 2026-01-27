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
    from seo_core import generate_collectionpage_schema, generate_itemlist_schema
except Exception as e:
    print(f"ERROR importing templates: {e}")
    traceback.print_exc()
    sys.exit(1)

DATA_DIR = 'data'
SITE_DIR = 'site'
JOBS_DIR = f'{SITE_DIR}/jobs'

# Pagination settings
JOBS_PER_PAGE = 50  # Jobs per page for SEO (reduces page size)
MAX_PAGES = 100  # Maximum pages to generate (prevents infinite pages)


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


def generate_job_card_html(row):
    """Generate HTML for a single job card."""
    company = escape_html(str(row.get('company', row.get('company_name', 'Unknown'))))
    title = escape_html(str(row.get('title', 'AI Role')))
    location = escape_html(str(row.get('location', ''))) if pd.notna(row.get('location')) else ''
    category = escape_html(str(row.get('job_category', ''))) if pd.notna(row.get('job_category')) else ''
    remote_status = is_remote(row)
    salary_val = row.get('salary_max', row.get('max_amount', 0))
    salary_val = float(salary_val) if pd.notna(salary_val) else 0
    salary = format_salary(row.get('salary_min', row.get('min_amount')), row.get('salary_max', row.get('max_amount')))

    job_slug = f"{make_slug(row.get('company', row.get('company_name', '')))}-{make_slug(row.get('title', ''))}"
    hash_suffix = hashlib.md5(f"{row.get('company', row.get('company_name', ''))}{row.get('title','')}{row.get('location','')}".encode()).hexdigest()[:6]
    job_slug = f"{job_slug}-{hash_suffix}"

    return f'''
        <a href="/jobs/{job_slug}/" class="job-card">
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


def generate_pagination_html(current_page, total_pages):
    """Generate pagination navigation HTML."""
    if total_pages <= 1:
        return ""

    pagination_items = []

    # Previous button
    if current_page > 1:
        prev_url = "/jobs/" if current_page == 2 else f"/jobs/page/{current_page - 1}/"
        pagination_items.append(f'<a href="{prev_url}" class="pagination-btn">← Previous</a>')
    else:
        pagination_items.append('<span class="pagination-btn disabled">← Previous</span>')

    # Page numbers (show first, last, and surrounding pages)
    def page_url(p):
        return "/jobs/" if p == 1 else f"/jobs/page/{p}/"

    # Always show first page
    if current_page > 3:
        pagination_items.append(f'<a href="{page_url(1)}" class="pagination-num">1</a>')
        if current_page > 4:
            pagination_items.append('<span class="pagination-ellipsis">...</span>')

    # Show surrounding pages
    start = max(1, current_page - 2)
    end = min(total_pages, current_page + 2)

    for p in range(start, end + 1):
        if p == current_page:
            pagination_items.append(f'<span class="pagination-num current">{p}</span>')
        else:
            pagination_items.append(f'<a href="{page_url(p)}" class="pagination-num">{p}</a>')

    # Always show last page
    if current_page < total_pages - 2:
        if current_page < total_pages - 3:
            pagination_items.append('<span class="pagination-ellipsis">...</span>')
        pagination_items.append(f'<a href="{page_url(total_pages)}" class="pagination-num">{total_pages}</a>')

    # Next button
    if current_page < total_pages:
        next_url = f"/jobs/page/{current_page + 1}/"
        pagination_items.append(f'<a href="{next_url}" class="pagination-btn">Next →</a>')
    else:
        pagination_items.append('<span class="pagination-btn disabled">Next →</span>')

    return f'''
        <nav class="pagination" aria-label="Job listings pagination">
            {''.join(pagination_items)}
        </nav>
    '''


def generate_pagination_seo_links(current_page, total_pages):
    """Generate prev/next link tags for SEO."""
    links = []
    if current_page > 1:
        prev_url = f"{BASE_URL}/jobs/" if current_page == 2 else f"{BASE_URL}/jobs/page/{current_page - 1}/"
        links.append(f'<link rel="prev" href="{prev_url}">')
    if current_page < total_pages:
        next_url = f"{BASE_URL}/jobs/page/{current_page + 1}/"
        links.append(f'<link rel="next" href="{next_url}">')
    return '\n    '.join(links)


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

    # Calculate pagination
    total_pages = min((total_jobs + JOBS_PER_PAGE - 1) // JOBS_PER_PAGE, MAX_PAGES)
    print(f"\n Generating {total_pages} paginated pages ({JOBS_PER_PAGE} jobs per page)")

    # Generate paginated pages
    for page_num in range(1, total_pages + 1):
        start_idx = (page_num - 1) * JOBS_PER_PAGE
        end_idx = min(start_idx + JOBS_PER_PAGE, total_jobs)
        page_jobs = df.iloc[start_idx:end_idx]

        # Generate job cards for this page
        job_cards_html = ""
        for idx, row in page_jobs.iterrows():
            job_cards_html += generate_job_card_html(row)

        # Generate pagination navigation
        pagination_html = generate_pagination_html(page_num, total_pages)
        pagination_seo = generate_pagination_seo_links(page_num, total_pages)

        # Page-specific title and canonical
        if page_num == 1:
            page_title = f"{total_jobs} AI & ML Engineer Jobs - ${avg_salary}K avg"
            page_path = "jobs/"
            page_desc = f"Browse {total_jobs} AI engineer, ML engineer, and prompt engineer jobs. Average salary ${avg_salary}K. {remote_jobs} remote positions available. Updated weekly."
        else:
            page_title = f"AI & ML Jobs - Page {page_num} of {total_pages}"
            page_path = f"jobs/page/{page_num}/"
            page_desc = f"Page {page_num} of {total_pages}: Browse AI engineer, ML engineer, and prompt engineer jobs. {total_jobs} total positions with salary data."

        # Build top 10 jobs for ItemList schema (only on page 1)
        schemas_html = ""
        if page_num == 1:
            top_jobs_for_schema = []
            for idx, row in df.head(10).iterrows():
                job_slug_temp = f"{make_slug(row.get('company', row.get('company_name', '')))}-{make_slug(row.get('title', ''))}"
                hash_suffix_temp = hashlib.md5(f"{row.get('company', row.get('company_name', ''))}{row.get('title','')}{row.get('location','')}".encode()).hexdigest()[:6]
                job_slug_temp = f"{job_slug_temp}-{hash_suffix_temp}"
                top_jobs_for_schema.append({
                    'name': f"{row.get('title', 'AI Role')} at {row.get('company', row.get('company_name', 'Unknown'))}",
                    'url': f"/jobs/{job_slug_temp}/"
                })

            collection_schema = generate_collectionpage_schema(
                name=f"{total_jobs} AI & ML Engineer Jobs",
                description=f"Browse {total_jobs} AI engineer, ML engineer, and prompt engineer jobs. Average salary ${avg_salary}K.",
                url="/jobs/",
                item_count=total_jobs,
                keywords=["AI jobs", "ML engineer jobs", "prompt engineer jobs", "AI engineer salary", "remote AI jobs"]
            )
            itemlist_schema = generate_itemlist_schema(
                items=top_jobs_for_schema,
                list_name="Top AI Jobs",
                url="/jobs/"
            )
            schemas_html = f"{collection_schema}\n    {itemlist_schema}"

        # Combine extra head content
        extra_head = f"{pagination_seo}\n    {schemas_html}" if schemas_html else pagination_seo

        # Category filter links (only show on page 1)
        category_filters = ""
        if page_num == 1:
            for cat, count in categories.items():
                cat_slug = make_slug(cat)
                category_filters += f'<a href="/jobs/{cat_slug}/" class="filter-btn">{escape_html(cat)} ({count})</a>\n'

        # Generate page HTML
        _generate_page_html(
            page_num=page_num,
            total_pages=total_pages,
            total_jobs=total_jobs,
            avg_salary=avg_salary,
            remote_jobs=remote_jobs,
            categories=categories,
            job_cards_html=job_cards_html,
            pagination_html=pagination_html,
            page_title=page_title,
            page_desc=page_desc,
            page_path=page_path,
            extra_head=extra_head,
            category_filters=category_filters,
            start_idx=start_idx,
            end_idx=end_idx
        )

        print(f"   Generated page {page_num}/{total_pages} (jobs {start_idx+1}-{end_idx})")

    print(f"\n Generated job board with {total_jobs} jobs across {total_pages} pages")
    print("="*70)


def _generate_page_html(page_num, total_pages, total_jobs, avg_salary, remote_jobs, categories,
                        job_cards_html, pagination_html, page_title, page_desc, page_path,
                        extra_head, category_filters, start_idx, end_idx):
    """Generate a single paginated job board page."""

    # Show stats only on page 1
    stats_html = ""
    if page_num == 1:
        stats_html = f'''
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
        '''

    # Category filters only on page 1
    filters_html = ""
    if page_num == 1 and category_filters:
        filters_html = f'''
            <div class="filters-section" style="margin-bottom: 32px;">
                <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center;">
                    <span class="filter-btn active">All Jobs ({total_jobs})</span>
                    <a href="/jobs/remote/" class="filter-btn">Remote Only ({remote_jobs})</a>
                    {category_filters}
                </div>
            </div>
        '''

    # SEO content only on page 1
    seo_content = ""
    if page_num == 1:
        seo_content = f'''
            <div class="seo-content" style="max-width: 800px; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--border); color: var(--text-secondary); line-height: 1.8;">
                <h2 style="font-size: 1.5rem; color: var(--text-primary); margin-bottom: 1rem;">About Our AI Job Board</h2>
                <p style="margin-bottom: 1rem;">
                    AI Market Pulse aggregates <strong style="color: var(--text-primary);">{total_jobs:,} AI and ML job postings</strong> from Indeed, LinkedIn, Greenhouse, Lever, and company career pages. We focus exclusively on roles in the AI ecosystem: <strong style="color: var(--text-primary);">AI/ML Engineers</strong>, <strong style="color: var(--text-primary);">Prompt Engineers</strong>, <strong style="color: var(--text-primary);">LLM Engineers</strong>, <strong style="color: var(--text-primary);">MLOps Engineers</strong>, <strong style="color: var(--text-primary);">Research Scientists</strong>, and <strong style="color: var(--text-primary);">AI Product Managers</strong>.
                </p>
                <p style="margin-bottom: 1rem;">
                    Every listing shows real salary ranges when available—no hidden compensation, no bait-and-switch. We update our database weekly to remove filled positions and add new opportunities.
                </p>
            </div>
        '''

    html = f'''{get_html_head(
        page_title,
        page_desc,
        page_path,
        extra_head=extra_head
    )}
{get_nav_html('jobs')}

    <div class="page-header">
        <div class="container">
            <div class="page-label">AI Job Board</div>
            <h1>{total_jobs} AI & ML Jobs{f' - Page {page_num}' if page_num > 1 else ''}</h1>
            <p class="lead">Prompt Engineer, AI Engineer, ML Engineer, and more. Real salaries, no recruiter spin. Updated weekly.</p>
            {stats_html}
        </div>
    </div>

    <main>
        <div class="container">
            {filters_html}

            <style>
                .jobs-grid {{
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }}
                .pagination {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    gap: 8px;
                    margin: 32px 0;
                    flex-wrap: wrap;
                }}
                .pagination-btn, .pagination-num {{
                    display: inline-block;
                    padding: 10px 16px;
                    background: var(--bg-card);
                    border: 1px solid var(--border);
                    border-radius: 8px;
                    color: var(--text-secondary);
                    text-decoration: none;
                    font-size: 0.9rem;
                    transition: all 0.15s;
                }}
                .pagination-btn:hover, .pagination-num:hover {{
                    border-color: var(--teal-light);
                    color: var(--text-primary);
                }}
                .pagination-num.current {{
                    background: var(--gold);
                    color: var(--bg-darker);
                    border-color: var(--gold);
                }}
                .pagination-btn.disabled {{
                    opacity: 0.5;
                    cursor: not-allowed;
                }}
                .pagination-ellipsis {{
                    color: var(--text-muted);
                    padding: 0 8px;
                }}
                .job-count-display {{
                    margin-bottom: 16px;
                    font-size: 0.9rem;
                    color: var(--text-muted);
                }}
            </style>

            <div class="job-count-display">
                Showing jobs {start_idx + 1} - {end_idx} of {total_jobs}
            </div>

            <div class="jobs-grid" id="jobs-container">
                {job_cards_html}
            </div>

            {pagination_html}

            {get_cta_box()}

            {seo_content}
        </div>
    </main>

{get_footer_html()}'''

    # Determine output path
    if page_num == 1:
        output_path = f'{JOBS_DIR}/index.html'
    else:
        page_dir = f'{JOBS_DIR}/page/{page_num}'
        os.makedirs(page_dir, exist_ok=True)
        output_path = f'{page_dir}/index.html'

    with open(output_path, 'w') as f:
        f.write(html)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
