#!/usr/bin/env python3
"""
Generate individual company pages for AI Market Pulse
Each company with AI job postings gets a dedicated page

SEO FEATURES:
- Canonical URLs
- Open Graph and Twitter Card meta tags
- BreadcrumbList JSON-LD schema
- Organization JSON-LD schema (for larger companies)
- noindex for thin content (companies with < 3 jobs)
- Proper meta descriptions
"""

import pandas as pd
import os
import glob
from datetime import datetime
import json
import sys
sys.path.insert(0, 'scripts')

from templates import (
    slugify, format_salary, BASE_URL, SITE_NAME,
    get_html_head, get_nav_html, get_footer_html, get_cta_box,
    get_breadcrumb_html, get_img_tag
)
from seo_core import generate_breadcrumb_schema, generate_collectionpage_schema

# Minimum jobs required for a company page to be indexed
MIN_JOBS_FOR_INDEX = 3

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


def escape_html(text):
    """Escape HTML special characters"""
    if pd.isna(text) or text is None:
        return ''
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')


def get_company_breadcrumb_schema(company_name, company_slug):
    """Generate BreadcrumbList JSON-LD schema for company page"""
    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'Companies', 'url': '/companies/'},
        {'name': company_name, 'url': f'/companies/{company_slug}/'}
    ]
    return generate_breadcrumb_schema(breadcrumbs)


def get_organization_schema(company_name, company_slug, num_jobs, categories, locations):
    """Generate Organization JSON-LD schema for company employer branding"""
    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": company_name,
        "url": f"{BASE_URL}/companies/{company_slug}/",
        "description": f"{company_name} is hiring for {num_jobs} AI and machine learning positions.",
    }

    if categories:
        schema["knowsAbout"] = categories[:5]

    if locations:
        # Add first location as address
        first_loc = locations[0]
        if ',' in first_loc:
            parts = first_loc.split(',')
            schema["address"] = {
                "@type": "PostalAddress",
                "addressLocality": parts[0].strip(),
                "addressRegion": parts[1].strip()[:2] if len(parts) > 1 else "",
                "addressCountry": "US"
            }

    return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'


def find_similar_companies(company_name, jobs_df, all_companies_data, num_similar=6):
    """Find similar companies based on categories, skills, and job counts."""
    if not all_companies_data:
        return []

    # Get current company's characteristics
    company_jobs = jobs_df[jobs_df['company'] == company_name]
    company_categories = set()
    company_skills = set()

    if 'job_category' in company_jobs.columns:
        company_categories = set(company_jobs['job_category'].dropna().unique())

    if 'skills_tags' in company_jobs.columns:
        for skills in company_jobs['skills_tags'].dropna():
            if isinstance(skills, str):
                company_skills.update([s.strip() for s in skills.split(',')])

    # Score other companies
    scored_companies = []
    for other_company, other_data in all_companies_data.items():
        if other_company == company_name:
            continue

        score = 0
        other_jobs = jobs_df[jobs_df['company'] == other_company]

        # Category overlap
        other_categories = set()
        if 'job_category' in other_jobs.columns:
            other_categories = set(other_jobs['job_category'].dropna().unique())
        category_overlap = len(company_categories & other_categories)
        score += category_overlap * 20

        # Skill overlap
        other_skills = set()
        if 'skills_tags' in other_jobs.columns:
            for skills in other_jobs['skills_tags'].dropna():
                if isinstance(skills, str):
                    other_skills.update([s.strip() for s in skills.split(',')])
        skill_overlap = len(company_skills & other_skills)
        score += skill_overlap * 5

        # Similar job count (prefer companies with similar scale)
        current_count = len(company_jobs)
        other_count = other_data.get('count', 0)
        if other_count > 0:
            size_ratio = min(current_count, other_count) / max(current_count, other_count)
            score += int(size_ratio * 15)

        # Bonus for companies with disclosed salary
        if other_data.get('salary_range'):
            score += 5

        if score > 0:
            scored_companies.append({
                'name': other_company,
                'slug': slugify(other_company),
                'count': other_data.get('count', 0),
                'salary_range': other_data.get('salary_range', ''),
                'categories': list(other_categories)[:3],
                'score': score
            })

    # Sort by score and return top N
    scored_companies.sort(key=lambda x: (x['score'], x['count']), reverse=True)
    return scored_companies[:num_similar]


def generate_similar_companies_html(similar_companies, current_company):
    """Generate HTML for similar companies section."""
    if not similar_companies:
        return ""

    companies_html = ""
    for company in similar_companies:
        name_escaped = escape_html(company['name'])
        slug = company['slug']
        count = company['count']
        salary_range = company.get('salary_range', '')
        categories = company.get('categories', [])

        category_text = ', '.join(escape_html(c) for c in categories[:2]) if categories else ''

        companies_html += f'''
            <a href="/companies/{slug}/" class="similar-company-card">
                <div class="similar-company-name">{name_escaped}</div>
                <div class="similar-company-meta">
                    <span class="similar-company-jobs">{count} AI Roles</span>
                    {f'<span class="similar-company-salary">{salary_range}</span>' if salary_range else ''}
                </div>
                {f'<div class="similar-company-categories">{category_text}</div>' if category_text else ''}
            </a>
        '''

    return f'''
        <section class="similar-companies-section">
            <h2>Similar Companies Hiring</h2>
            <div class="similar-companies-grid">
                {companies_html}
            </div>
            <div class="similar-companies-cta">
                <a href="/companies/" class="btn-outline">Browse All Companies →</a>
            </div>
        </section>
    '''


# CSS for similar companies section
CSS_SIMILAR_COMPANIES = '''
    .similar-companies-section {
        margin: 40px 0;
        padding-top: 32px;
        border-top: 1px solid var(--border);
    }

    .similar-companies-section h2 {
        font-size: 1.25rem;
        margin-bottom: 20px;
        color: var(--text-primary);
    }

    .similar-companies-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }

    .similar-company-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        text-decoration: none;
        transition: all 0.25s;
    }

    .similar-company-card:hover {
        border-color: var(--teal-light);
        background: var(--bg-card-hover);
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }

    .similar-company-name {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 8px;
    }

    .similar-company-meta {
        display: flex;
        gap: 12px;
        font-size: 0.85rem;
        margin-bottom: 8px;
    }

    .similar-company-jobs {
        color: var(--text-secondary);
    }

    .similar-company-salary {
        color: var(--gold);
        font-weight: 600;
    }

    .similar-company-categories {
        font-size: 0.75rem;
        color: var(--text-muted);
    }

    .similar-companies-cta {
        text-align: center;
    }
'''


def generate_company_page(company_name, jobs_df, all_companies_data=None):
    """Generate a single company page with full SEO optimization"""
    company_slug = slugify(company_name)
    if not company_slug:
        return None

    company_dir = f"{COMPANIES_DIR}/{company_slug}"
    os.makedirs(company_dir, exist_ok=True)

    # Get company jobs
    company_jobs = jobs_df[jobs_df['company'] == company_name].copy()
    num_jobs = len(company_jobs)

    # Determine if page should be noindexed (thin content protection)
    is_thin_content = num_jobs < MIN_JOBS_FOR_INDEX
    robots_meta = '<meta name="robots" content="noindex, follow">' if is_thin_content else ''

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

    # Escape company name for safe HTML/meta use
    company_escaped = escape_html(company_name)
    categories_escaped = [escape_html(c) for c in categories]

    # Generate meta description
    meta_desc = f"View {num_jobs} AI and machine learning jobs at {company_escaped}."
    if salary_range:
        meta_desc += f" {salary_range} salary range."
    if categories:
        meta_desc += f" Roles in {', '.join(categories_escaped[:3])}."
    meta_desc = meta_desc[:155]

    # Generate canonical URL
    canonical_url = f"{BASE_URL}/companies/{company_slug}/"

    # Determine robots directive
    robots_directive = 'noindex, follow' if is_thin_content else 'index, follow'

    # Generate JSON-LD schemas
    breadcrumb_schema = get_company_breadcrumb_schema(company_escaped, company_slug)
    org_schema = get_organization_schema(company_escaped, company_slug, num_jobs, categories, locations) if num_jobs >= MIN_JOBS_FOR_INDEX else ''

    # Generate breadcrumb HTML with schema
    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'Companies', 'url': '/companies/'},
        {'name': company_name, 'url': f'/companies/{company_slug}/'}
    ]
    breadcrumb_html_block = get_breadcrumb_html(breadcrumbs)

    # Page title for display
    page_title = f"{company_escaped} AI Jobs - {num_jobs} Open Positions"

    # === SIMILAR COMPANIES ===
    similar_companies_html = ""
    if all_companies_data and len(all_companies_data) > 1:
        similar_companies = find_similar_companies(company_name, jobs_df, all_companies_data, num_similar=6)
        similar_companies_html = generate_similar_companies_html(similar_companies, company_name)

    # Custom CSS for company pages
    company_css = '''
    <style>
        .company-header {
            padding: 2rem 0;
            border-bottom: 1px solid var(--border);
        }
        .company-header h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        .company-stats {
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }
        .company-stat {
            background: var(--bg-card);
            padding: 1rem 1.5rem;
            border-radius: 8px;
        }
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--gold);
        }
        .stat-label {
            font-size: 0.875rem;
            color: var(--text-muted);
        }
        .company-details {
            padding: 2rem 0;
        }
        .section-title {
            font-size: 1.25rem;
            margin-bottom: 1rem;
            color: var(--text-primary);
        }
        .skills-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 2rem;
        }
        .skill-tag {
            background: var(--bg-darker);
            color: var(--gold);
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
        }
        .locations-list {
            color: var(--text-secondary);
            margin-bottom: 2rem;
        }
        .jobs-section {
            padding: 2rem 0;
        }
        .job-card {
            background: var(--bg-card);
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border: 1px solid var(--border);
            transition: all 0.25s;
        }
        .job-card:hover {
            border-color: var(--teal-light);
            background: var(--bg-card-hover);
        }
        .job-category {
            font-size: 0.75rem;
            color: var(--gold);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }
        .job-title { margin-bottom: 0.5rem; }
        .job-title a {
            color: var(--text-primary);
            text-decoration: none;
        }
        .job-title a:hover { color: var(--gold); }
        .job-meta {
            display: flex;
            gap: 1.5rem;
            color: var(--text-secondary);
            font-size: 0.875rem;
        }
        .job-salary {
            color: var(--gold);
            font-weight: 600;
        }
        @media (max-width: 768px) {
            .company-header h1 { font-size: 1.75rem; }
            .company-stats { flex-direction: column; }
        }
        ''' + CSS_SIMILAR_COMPANIES + '''
    </style>
    '''

    html = f'''{get_html_head(
        page_title,
        meta_desc,
        f"companies/{company_slug}/",
        extra_head=f'{org_schema}\\n{company_css}',
        robots=robots_directive
    )}
{get_nav_html('companies')}

    <div class="page-header">
        <div class="container">
            {breadcrumb_html_block}
            <h1>{company_escaped}</h1>
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
        </div>
    </div>

    <main>
        <div class="container">
            <section class="company-details">
                {f'<h2 class="section-title">Skills & Technologies</h2>{skills_html}' if top_skills else ''}

                {f'<h2 class="section-title">Locations</h2><p class="locations-list">{", ".join(locations)}</p>' if locations else ''}

                {f'<h2 class="section-title">Role Categories</h2><p class="locations-list">{", ".join(categories)}</p>' if categories else ''}
            </section>

            <section class="jobs-section">
                <h2 class="section-title">All Open Positions ({num_jobs})</h2>
                {jobs_html}
            </section>

            {get_cta_box()}

            {similar_companies_html}
        </div>
    </main>

{get_footer_html()}'''

    output_path = f"{company_dir}/index.html"
    with open(output_path, 'w') as f:
        f.write(html)

    return company_slug, is_thin_content


def generate_companies_index(companies_data):
    """Generate the companies index page"""
    os.makedirs(COMPANIES_DIR, exist_ok=True)

    # Sort by job count
    sorted_companies = sorted(companies_data.items(), key=lambda x: x[1]['count'], reverse=True)
    company_count = len(sorted_companies)

    # Generate CollectionPage schema
    collection_schema = generate_collectionpage_schema(
        name=f"Companies Hiring for AI Roles",
        description=f"Browse {company_count} companies actively hiring for AI, ML, and Prompt Engineering roles.",
        url="/companies/",
        item_count=company_count,
        keywords=["AI companies", "ML hiring", "AI jobs", "tech companies hiring AI engineers"]
    )

    companies_html = ""
    for company, data in sorted_companies:
        slug = slugify(company)
        if not slug:
            continue
        companies_html += f'''
        <a href="/companies/{slug}/" class="company-card">
            <h3>{escape_html(company)}</h3>
            <div class="company-meta">
                <span>{data['count']} open roles</span>
                {f'<span class="salary">{data["salary_range"]}</span>' if data.get("salary_range") else ''}
            </div>
        </a>
        '''

    # Custom CSS for companies index
    companies_css = '''
    <style>
        .companies-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.5rem;
            padding: 2rem 0;
        }
        .company-card {
            background: var(--bg-card);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border);
            text-decoration: none;
            color: var(--text-primary);
            transition: all 0.25s;
        }
        .company-card:hover {
            transform: translateY(-4px);
            border-color: var(--teal-light);
            background: var(--bg-card-hover);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }
        .company-card h3 {
            margin-bottom: 0.5rem;
        }
        .company-meta {
            display: flex;
            justify-content: space-between;
            color: var(--text-secondary);
            font-size: 0.875rem;
        }
        .salary {
            color: var(--gold);
        }
    </style>
    '''

    meta_desc = f"Browse {company_count} companies actively hiring for AI, ML, and Prompt Engineering roles."

    html = f'''{get_html_head(
        "Companies Hiring for AI Roles",
        meta_desc,
        "companies/",
        extra_head=f'{collection_schema}\\n{companies_css}'
    )}
{get_nav_html('companies')}

    <div class="page-header">
        <div class="container">
            <h1>Companies Hiring for AI Roles</h1>
            <p class="lead">{company_count} companies with open AI, ML, and Prompt Engineering positions</p>
        </div>
    </div>

    <main>
        <div class="container">
            <div class="companies-grid">
                {companies_html}
            </div>

            {get_cta_box()}
        </div>
    </main>

{get_footer_html()}'''

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

    # First pass: collect all companies data for similar companies feature
    companies_data = {}
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

    # Second pass: generate individual company pages with similar companies
    print(f"  (with similar companies internal linking)")
    generated = 0
    indexed_count = 0
    noindex_count = 0

    for company in companies_data.keys():
        result = generate_company_page(company, jobs_df, all_companies_data=companies_data)
        if result:
            slug, is_thin = result
            generated += 1
            if is_thin:
                noindex_count += 1
            else:
                indexed_count += 1

    # Generate index page
    generate_companies_index(companies_data)

    print(f"\n{'='*70}")
    print(f"  Generated {generated} company pages")
    print(f"  SEO Summary:")
    print(f"    - Indexed pages ({MIN_JOBS_FOR_INDEX}+ jobs): {indexed_count}")
    print(f"    - Noindexed pages (thin content): {noindex_count}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
