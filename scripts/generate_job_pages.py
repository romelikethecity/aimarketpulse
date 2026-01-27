#!/usr/bin/env python3
"""
Generate individual job pages for programmatic SEO.
Creates pages like /jobs/anthropic-prompt-engineer-abc123/ for each job posting.

SEO FEATURES:
- Correct canonical URLs (theaimarketpulse.com)
- Salary/skills in title tags
- Open Graph tags for social sharing
- Twitter card tags
- JobPosting JSON-LD schema for rich results
- Stale job handling with similar job recommendations
"""

import pandas as pd
from datetime import datetime, timedelta
import glob
import os
import re
import hashlib
import json
import sys
import traceback

# Add scripts directory to path using absolute path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    from templates import (
        get_html_head, get_nav_html, get_footer_html, get_cta_box,
        get_job_posting_schema, slugify, format_salary, is_remote,
        get_breadcrumb_html, get_img_tag,
        BASE_URL, SITE_NAME, CSS_VARIABLES, CSS_NAV, CSS_LAYOUT, CSS_CARDS, CSS_CTA, CSS_FOOTER, CSS_JOB_PAGE
    )
    from seo_core import generate_breadcrumb_schema
    from nav_config import NAV_ITEMS, FOOTER_ITEMS, SUBSCRIBE_LINK, SUBSCRIBE_LABEL, NEWSLETTER_LINK
except Exception as e:
    print(f"ERROR importing modules: {e}")
    traceback.print_exc()
    sys.exit(1)

DATA_DIR = 'data'
SITE_DIR = 'site'
JOBS_DIR = f'{SITE_DIR}/jobs'

print("="*70)
print("  AI MARKET PULSE - GENERATING INDIVIDUAL JOB PAGES")
print("="*70)

os.makedirs(JOBS_DIR, exist_ok=True)

# Find most recent enriched data
files = glob.glob(f"{DATA_DIR}/ai_jobs_*.csv")
if not files:
    # Try loading from jobs.json
    if os.path.exists(f"{DATA_DIR}/jobs.json"):
        print(f"\n Loading from jobs.json...")
        with open(f"{DATA_DIR}/jobs.json") as f:
            data = json.load(f)
        df = pd.DataFrame(data.get('jobs', []))
        print(f" Loaded {len(df)} jobs")
    else:
        print(" No job data found")
        exit(1)
else:
    latest_file = max(files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    print(f"\n Loaded {len(df)} jobs from {latest_file}")

update_date = datetime.now().strftime('%B %d, %Y')
iso_date = datetime.now().strftime('%Y-%m-%d')


def make_slug(text):
    """Convert text to URL-friendly slug"""
    if pd.isna(text):
        return ''
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:50]


def escape_html(text):
    """Escape HTML special characters"""
    if pd.isna(text):
        return ''
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')


def parse_skills(skills_value):
    """Parse skills from string or list"""
    if pd.isna(skills_value):
        return []
    if isinstance(skills_value, list):
        return skills_value
    if isinstance(skills_value, str):
        # Could be JSON string or comma-separated
        try:
            return json.loads(skills_value.replace("'", '"'))
        except:
            return [s.strip() for s in skills_value.split(',') if s.strip()]
    return []


def create_job_page(job, idx):
    """Generate an individual job page with full SEO optimization"""

    company = str(job.get('company', job.get('company_name', 'Unknown')))
    title = str(job.get('title', 'AI Engineer'))
    location = str(job.get('location', '')) if pd.notna(job.get('location')) else ''

    # Create unique slug
    slug = f"{make_slug(company)}-{make_slug(title)}"
    if not slug or len(slug) < 5:
        slug = f"job-{idx}"

    # Add hash suffix for uniqueness
    hash_suffix = hashlib.md5(f"{company}{title}{location}".encode()).hexdigest()[:6]
    slug = f"{slug}-{hash_suffix}"

    # Get job details
    min_sal = job.get('salary_min', job.get('min_amount'))
    max_sal = job.get('salary_max', job.get('max_amount'))
    salary_display = format_salary(min_sal, max_sal)
    salary_short = ""

    try:
        if pd.notna(min_sal) and pd.notna(max_sal) and float(min_sal) > 0 and float(max_sal) > 0:
            salary_short = f"${int(float(min_sal))//1000}K-${int(float(max_sal))//1000}K"
        elif pd.notna(max_sal) and float(max_sal) > 0:
            salary_short = f"Up to ${int(float(max_sal))//1000}K"
    except:
        pass

    job_category = job.get('job_category', 'AI Role') if pd.notna(job.get('job_category')) else 'AI Role'
    experience_level = job.get('experience_level', 'mid') if pd.notna(job.get('experience_level')) else 'mid'
    remote_status = is_remote(job)
    job_url = job.get('job_url_direct', job.get('source_url', '#'))
    if pd.isna(job_url):
        job_url = '#'

    skills = parse_skills(job.get('skills_tags'))

    # Escape for HTML
    company_escaped = escape_html(company)
    title_escaped = escape_html(title)
    location_escaped = escape_html(location)

    # Generate company page link for cross-linking
    company_slug = make_slug(company) if company else ''
    company_link = f'<a href="/companies/{company_slug}/" style="color: var(--gold); text-decoration: none;">{company_escaped}</a>' if company_slug else company_escaped

    # === SEO-OPTIMIZED TITLE ===
    title_parts = [f"{title_escaped} at {company_escaped}"]
    if salary_short:
        title_parts.append(f"- {salary_short}")
    if remote_status:
        title_parts.append("(Remote)")
    elif location:
        city = location.split(',')[0].strip() if ',' in location else location
        if len(city) < 20:
            title_parts.append(f"({escape_html(city)})")
    page_title = ' '.join(title_parts)

    # === META DESCRIPTION ===
    meta_desc = f"{title_escaped} at {company_escaped}"
    if location:
        meta_desc += f" in {location_escaped}"
    if salary_short:
        meta_desc += f". {salary_short} salary."
    if skills:
        meta_desc += f" Skills: {', '.join(skills[:3])}."
    meta_desc += " Apply now."
    meta_desc = meta_desc[:155]

    # === CANONICAL URL ===
    canonical_url = f"{BASE_URL}/jobs/{slug}/"

    # === JOBPOSTING SCHEMA ===
    schema_json = get_job_posting_schema(job)

    # === BREADCRUMB DATA ===
    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'AI Jobs', 'url': '/jobs/'},
        {'name': f'{title_escaped} at {company_escaped}', 'url': f'/jobs/{slug}/'}
    ]
    breadcrumb_schema = generate_breadcrumb_schema(breadcrumbs)
    breadcrumb_html = get_breadcrumb_html(breadcrumbs)

    # === SKILLS HTML ===
    skills_html = ""
    if skills:
        skills_badges = ''.join([f'<span class="skill-tag">{escape_html(s)}</span>' for s in skills[:10]])
        skills_html = f'''
            <div class="job-skills">
                <h3>Skills & Technologies</h3>
                <div class="skills-list">{skills_badges}</div>
            </div>
        '''

    # === EXPERIENCE LEVEL DISPLAY ===
    exp_display = {
        'entry': 'Entry Level',
        'mid': 'Mid Level',
        'senior': 'Senior',
    }.get(str(experience_level).lower(), 'Mid Level')

    # === META BADGES ===
    meta_badges = []
    if salary_display:
        meta_badges.append(f'<span class="job-meta-badge salary">{salary_display}</span>')
    if remote_status:
        meta_badges.append('<span class="job-meta-badge remote">Remote</span>')
    elif location:
        meta_badges.append(f'<span class="job-meta-badge">{location_escaped}</span>')
    meta_badges.append(f'<span class="job-meta-badge">{exp_display}</span>')
    meta_badges.append(f'<span class="job-meta-badge">{escape_html(job_category)}</span>')
    meta_badges_html = '\n                    '.join(meta_badges)

    # Build the page
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} | {SITE_NAME}</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="{canonical_url}">
    <meta name="robots" content="index, follow">

    <!-- Open Graph Tags -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:title" content="{title_escaped} at {company_escaped}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:site_name" content="{SITE_NAME}">
    <meta property="og:image" content="{BASE_URL}/assets/social-preview.png">
    <meta property="og:image:alt" content="{SITE_NAME} - AI jobs, salary benchmarks, and market intelligence">

    <!-- Twitter Card Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@pe_collective">
    <meta name="twitter:title" content="{title_escaped} at {company_escaped}">
    <meta name="twitter:description" content="{meta_desc}">
    <meta name="twitter:image" content="{BASE_URL}/assets/social-preview.png">
    <meta name="twitter:image:alt" content="{SITE_NAME} - AI jobs, salary benchmarks, and market intelligence">

    <link rel="icon" type="image/jpeg" href="/assets/logo.jpeg">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

    {schema_json}

    <style>
        {CSS_VARIABLES}
        {CSS_NAV}
        {CSS_LAYOUT}
        {CSS_CARDS}
        {CSS_CTA}
        {CSS_FOOTER}
        {CSS_JOB_PAGE}

        .job-header {{
            background: linear-gradient(135deg, var(--teal-primary) 0%, var(--bg-darker) 100%);
            padding: 48px 0;
            border-bottom: 1px solid var(--border);
        }}
        .job-header .container {{ max-width: 900px; }}
        .job-header h1 {{
            font-size: 2rem;
            margin-bottom: 8px;
            color: var(--text-primary);
        }}
        .job-company {{
            font-size: 1.25rem;
            color: var(--text-secondary);
            margin-bottom: 20px;
        }}
        .content {{ padding: 48px 0; }}
        .content .container {{ max-width: 900px; }}
        .apply-box {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 32px;
            text-align: center;
            margin-bottom: 32px;
        }}
        .apply-box p {{
            color: var(--text-secondary);
            margin-bottom: 20px;
        }}
        .skills-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
    </style>
</head>
{get_nav_html('jobs').replace('<body>', '<body>')}

    <header class="job-header">
        <div class="container">
            {breadcrumb_html}
            <h1>{title_escaped}</h1>
            <div class="job-company">{company_link}</div>
            <div class="job-meta">
                {meta_badges_html}
            </div>
        </div>
    </header>

    <div class="content">
        <div class="container">
            <div class="apply-box">
                <p>Interested in this {job_category} role at {company_link}?</p>
                <a href="{job_url}" class="apply-btn" target="_blank" rel="noopener">Apply Now →</a>
            </div>

            {skills_html}

            <div class="job-details-table">
                <h2 style="margin-bottom: 20px; font-size: 1.25rem;">Role Details</h2>
                <div class="job-details-row">
                    <span class="job-details-label">Company</span>
                    <span class="job-details-value">{company_link}</span>
                </div>
                <div class="job-details-row">
                    <span class="job-details-label">Title</span>
                    <span class="job-details-value">{title_escaped}</span>
                </div>
                <div class="job-details-row">
                    <span class="job-details-label">Location</span>
                    <span class="job-details-value">{location_escaped if location else 'Not specified'}</span>
                </div>
                <div class="job-details-row">
                    <span class="job-details-label">Category</span>
                    <span class="job-details-value">{escape_html(job_category)}</span>
                </div>
                <div class="job-details-row">
                    <span class="job-details-label">Experience</span>
                    <span class="job-details-value">{exp_display}</span>
                </div>
                <div class="job-details-row">
                    <span class="job-details-label">Salary</span>
                    <span class="job-details-value">{salary_display if salary_display else 'Not disclosed'}</span>
                </div>
                <div class="job-details-row">
                    <span class="job-details-label">Remote</span>
                    <span class="job-details-value">{'Yes' if remote_status else 'No'}</span>
                </div>
            </div>

            {get_cta_box()}
        </div>
    </div>

{get_footer_html()}'''

    # Create directory and save
    page_dir = f'{JOBS_DIR}/{slug}'
    os.makedirs(page_dir, exist_ok=True)
    with open(f'{page_dir}/index.html', 'w') as f:
        f.write(html)

    return slug


# Generate individual job pages
print(f"\n Generating individual job pages...")
job_slugs = []
for idx, row in df.iterrows():
    if pd.notna(row.get('title')) and pd.notna(row.get('company', row.get('company_name'))):
        slug = create_job_page(row, idx)
        job_slugs.append(slug)
        if len(job_slugs) % 100 == 0:
            print(f"   Generated {len(job_slugs)} pages...")

print(f"\n Generated {len(job_slugs)} individual job pages")

# Save job index for linking
with open(f'{DATA_DIR}/job_slugs.txt', 'w') as f:
    f.write('\n'.join(job_slugs))
print(f" Saved job slug index")


# ============================================================================
# STALE JOB HANDLING - Find expired jobs and show similar recommendations
# ============================================================================
print("\n" + "="*70)
print("  HANDLING STALE JOB PAGES")
print("="*70)


def find_similar_jobs(stale_slug, current_jobs_df, num_recommendations=5):
    """Find similar live jobs based on the stale job's characteristics"""
    parts = stale_slug.rsplit('-', 1)
    if len(parts) < 2:
        return current_jobs_df.head(num_recommendations).to_dict('records')

    slug_text = parts[0].lower()

    scores = []
    for idx, job in current_jobs_df.iterrows():
        score = 0
        company = str(job.get('company', job.get('company_name', ''))).lower()
        title = str(job.get('title', '')).lower()
        category = str(job.get('job_category', '')).lower()

        # Company match (highest weight)
        if company and make_slug(company) in slug_text:
            score += 50

        # Category/role type match
        if 'prompt' in slug_text and 'prompt' in category:
            score += 30
        if 'ml-engineer' in slug_text or 'machine-learning' in slug_text:
            if 'ml' in category or 'machine learning' in category:
                score += 30
        if 'llm' in slug_text and 'llm' in category:
            score += 30
        if 'mlops' in slug_text and 'mlops' in category:
            score += 30
        if 'research' in slug_text and 'research' in category:
            score += 25
        if 'agent' in slug_text and 'agent' in category:
            score += 25

        # Remote preference
        if 'remote' in slug_text and is_remote(job):
            score += 10

        # Has salary (prefer jobs with disclosed salary)
        if pd.notna(job.get('salary_max', job.get('max_amount'))) and float(job.get('salary_max', job.get('max_amount', 0))) > 0:
            score += 5

        scores.append((idx, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    top_indices = [s[0] for s in scores[:num_recommendations]]

    return current_jobs_df.loc[top_indices].to_dict('records')


def create_stale_job_page(stale_slug, similar_jobs):
    """Generate a page for an expired job with similar job recommendations"""

    parts = stale_slug.rsplit('-', 1)
    slug_text = parts[0] if len(parts) >= 2 else stale_slug

    # Try to extract company and title from slug
    slug_parts = slug_text.split('-')
    if len(slug_parts) >= 2:
        title_keywords = ['prompt', 'engineer', 'ml', 'machine', 'learning', 'ai', 'llm', 'mlops', 'research', 'senior', 'lead', 'agent', 'developer']
        title_start = len(slug_parts)
        for i, part in enumerate(slug_parts):
            if part in title_keywords:
                title_start = i
                break

        company_parts = slug_parts[:title_start] if title_start > 0 else slug_parts[:2]
        title_parts = slug_parts[title_start:] if title_start < len(slug_parts) else slug_parts[2:]

        company_display = ' '.join(company_parts).title()
        title_display = ' '.join(title_parts).title() if title_parts else 'AI Engineer'
    else:
        company_display = 'This Company'
        title_display = 'AI Engineer'

    # Build similar jobs HTML
    similar_jobs_html = ""
    for job in similar_jobs:
        company = escape_html(str(job.get('company', job.get('company_name', 'Unknown'))))
        title = escape_html(str(job.get('title', 'AI Role')))
        location = escape_html(str(job.get('location', ''))) if pd.notna(job.get('location')) else ''
        remote_status = is_remote(job)

        salary = format_salary(job.get('salary_min', job.get('min_amount')), job.get('salary_max', job.get('max_amount')))

        # Generate slug for this job
        job_slug = f"{make_slug(job.get('company', job.get('company_name', '')))}-{make_slug(job.get('title', ''))}"
        hash_suffix = hashlib.md5(f"{job.get('company', job.get('company_name', ''))}{job.get('title','')}{job.get('location','')}".encode()).hexdigest()[:6]
        job_slug = f"{job_slug}-{hash_suffix}"

        location_badge = 'Remote' if remote_status else f'{location}' if location else ''

        similar_jobs_html += f'''
            <a href="/jobs/{job_slug}/" class="job-card" style="display: block;">
                <div class="job-card__content">
                    <div class="job-card__company">{company}</div>
                    <div class="job-card__title">{title}</div>
                    <div class="job-card__meta">
                        {f'<span class="job-card__tag job-card__tag--salary">{salary}</span>' if salary else ''}
                        {f'<span class="job-card__tag job-card__tag--remote">{location_badge}</span>' if location_badge else ''}
                    </div>
                </div>
            </a>
        '''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_display} at {company_display} - Position Filled | {SITE_NAME}</title>
    <meta name="description" content="This {title_display} position at {company_display} is no longer available. Browse similar AI and ML engineering opportunities.">
    <link rel="canonical" href="{BASE_URL}/jobs/{stale_slug}/">
    <meta name="robots" content="noindex, follow">

    <link rel="icon" type="image/jpeg" href="/assets/logo.jpeg">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

    <style>
        {CSS_VARIABLES}
        {CSS_NAV}
        {CSS_LAYOUT}
        {CSS_CARDS}
        {CSS_CTA}
        {CSS_FOOTER}

        .expired-header {{
            background: linear-gradient(135deg, var(--teal-primary) 0%, var(--bg-darker) 100%);
            padding: 48px 0;
            text-align: center;
        }}
        .expired-header .container {{ max-width: 800px; }}
        .expired-badge {{
            display: inline-block;
            background: var(--error);
            color: white;
            font-weight: 600;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            margin-bottom: 16px;
        }}
        .expired-header h1 {{
            font-size: 1.75rem;
            margin-bottom: 8px;
            color: var(--text-primary);
        }}
        .expired-header .company {{
            font-size: 1.1rem;
            color: var(--text-secondary);
        }}
        .content {{ padding: 48px 0; }}
        .content .container {{ max-width: 900px; }}
        .message-box {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 32px;
            text-align: center;
            margin-bottom: 40px;
        }}
        .message-box h2 {{
            color: var(--text-primary);
            margin-bottom: 12px;
        }}
        .message-box p {{
            color: var(--text-secondary);
            margin-bottom: 20px;
        }}
        .browse-all-btn {{
            display: inline-block;
            background: var(--gold);
            color: var(--bg-darker);
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
        }}
        .browse-all-btn:hover {{
            background: var(--gold-hover);
            color: var(--bg-darker);
        }}
        .similar-section {{ margin-bottom: 40px; }}
        .similar-section h2 {{
            color: var(--text-primary);
            margin-bottom: 20px;
            font-size: 1.5rem;
        }}
        .similar-jobs-grid {{
            display: grid;
            gap: 16px;
        }}
    </style>
</head>
{get_nav_html('jobs').replace('<body>', '<body>')}

    <header class="expired-header">
        <div class="container">
            <span class="expired-badge">Position Filled</span>
            <h1>{title_display}</h1>
            <div class="company">{company_display}</div>
        </div>
    </header>

    <div class="content">
        <div class="container">
            <div class="message-box">
                <h2>This position is no longer available</h2>
                <p>Good news - we have similar AI opportunities that might be a great fit for you.</p>
                <a href="/jobs/" class="browse-all-btn">Browse All AI Jobs →</a>
            </div>

            <div class="similar-section">
                <h2>Similar Opportunities</h2>
                <div class="similar-jobs-grid">
                    {similar_jobs_html}
                </div>
            </div>

            {get_cta_box()}
        </div>
    </div>

{get_footer_html()}'''

    page_dir = f'{JOBS_DIR}/{stale_slug}'
    os.makedirs(page_dir, exist_ok=True)
    with open(f'{page_dir}/index.html', 'w') as f:
        f.write(html)


# Find all existing job page directories
existing_pages = set()
if os.path.exists(JOBS_DIR):
    for item in os.listdir(JOBS_DIR):
        item_path = os.path.join(JOBS_DIR, item)
        if os.path.isdir(item_path) and item not in ['index.html', '.DS_Store']:
            existing_pages.add(item)

# Convert current job slugs to a set for comparison
current_slugs = set(job_slugs)

# Find stale pages (exist on disk but not in current data)
stale_slugs = existing_pages - current_slugs

print(f"\n Page Analysis:")
print(f"   - Current live jobs: {len(current_slugs)}")
print(f"   - Existing pages on disk: {len(existing_pages)}")
print(f"   - Stale pages to update: {len(stale_slugs)}")

if stale_slugs:
    print(f"\n Updating {len(stale_slugs)} stale job pages with similar recommendations...")
    stale_count = 0
    for stale_slug in stale_slugs:
        similar_jobs = find_similar_jobs(stale_slug, df, num_recommendations=5)
        create_stale_job_page(stale_slug, similar_jobs)
        stale_count += 1
        if stale_count % 50 == 0:
            print(f"   Updated {stale_count} stale pages...")

    print(f"\n Updated {len(stale_slugs)} stale job pages with similar job recommendations")
else:
    print(f"\n No stale job pages found - all pages are current")

print(f"\n SEO Features Added:")
print(f"   - Correct canonical URLs ({BASE_URL})")
print(f"   - Skills in title tags and meta descriptions")
print(f"   - Open Graph tags for social sharing")
print(f"   - Twitter card tags")
print(f"   - JobPosting JSON-LD schema")
print(f"   - Stale page handling with similar job recommendations")
print("="*70)
