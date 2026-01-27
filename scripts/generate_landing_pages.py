#!/usr/bin/env python3
"""
Generate SEO-optimized landing pages for AI Market Pulse.

This script generates:
1. Location-based landing pages (/jobs/remote/, /jobs/san-francisco/, etc.)
2. Skill-based landing pages (/jobs/skills/python/, /jobs/skills/pytorch/, etc.)

These pages capture long-tail search traffic and provide better internal linking.
"""

import pandas as pd
import os
import glob
import json
import re
import hashlib
import sys
from datetime import datetime
from collections import Counter

# Add scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from templates import (
    get_html_head, get_nav_html, get_footer_html, get_cta_box,
    slugify, format_salary, is_remote, BASE_URL, SITE_NAME,
    CSS_VARIABLES, CSS_NAV, CSS_LAYOUT, CSS_CARDS, CSS_CTA, CSS_FOOTER
)
from seo_core import generate_breadcrumb_schema, generate_collectionpage_schema, generate_faq_schema, generate_faq_html, CSS_FAQ_SECTION

DATA_DIR = 'data'
SITE_DIR = 'site'
JOBS_DIR = f'{SITE_DIR}/jobs'

# Minimum jobs required for a landing page to be indexed
MIN_JOBS_FOR_LOCATION_INDEX = 5
MIN_JOBS_FOR_SKILL_INDEX = 10

print("=" * 70)
print("  AI MARKET PULSE - GENERATING LANDING PAGES")
print("=" * 70)


def get_latest_jobs():
    """Load latest enriched job data"""
    job_files = glob.glob(f"{DATA_DIR}/ai_jobs_*.csv")
    if not job_files:
        if os.path.exists(f"{DATA_DIR}/jobs.json"):
            with open(f"{DATA_DIR}/jobs.json") as f:
                data = json.load(f)
            return pd.DataFrame(data.get('jobs', []))
        return pd.DataFrame()
    latest_file = sorted(job_files)[-1]
    return pd.read_csv(latest_file)


def escape_html(text):
    """Escape HTML special characters"""
    if pd.isna(text) or text is None:
        return ''
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')


def make_slug(text):
    """Convert text to URL-friendly slug"""
    if pd.isna(text):
        return ''
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:50]


def parse_skills(skills_value):
    """Parse skills from string or list"""
    if pd.isna(skills_value):
        return []
    if isinstance(skills_value, list):
        return skills_value
    if isinstance(skills_value, str):
        try:
            return json.loads(skills_value.replace("'", '"'))
        except:
            return [s.strip() for s in skills_value.split(',') if s.strip()]
    return []


# =============================================================================
# CSS FOR LANDING PAGES
# =============================================================================

CSS_LANDING = '''
    .landing-header {
        padding: 48px 0;
        background: linear-gradient(135deg, var(--teal-primary) 0%, var(--bg-darker) 100%);
        border-bottom: 1px solid var(--border);
    }

    .landing-header h1 {
        font-size: 2.5rem;
        margin-bottom: 16px;
    }

    .landing-header .lead {
        font-size: 1.1rem;
        color: var(--text-secondary);
        max-width: 700px;
    }

    .landing-stats {
        display: flex;
        gap: 32px;
        margin-top: 24px;
    }

    .landing-stat {
        text-align: center;
    }

    .landing-stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--gold);
    }

    .landing-stat-label {
        font-size: 0.85rem;
        color: var(--text-muted);
    }

    .filters-section {
        padding: 24px 0;
        border-bottom: 1px solid var(--border);
        background: var(--bg-darker);
    }

    .filters-row {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        align-items: center;
    }

    .filter-btn {
        padding: 8px 16px;
        border-radius: 20px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        color: var(--text-secondary);
        text-decoration: none;
        font-size: 0.9rem;
        transition: all 0.2s;
    }

    .filter-btn:hover {
        background: var(--bg-card-hover);
        border-color: var(--teal-light);
        color: var(--text-primary);
    }

    .filter-btn.active {
        background: var(--gold);
        color: var(--bg-darker);
        border-color: var(--gold);
    }

    .jobs-grid {
        display: grid;
        gap: 16px;
        padding: 32px 0;
    }

    .landing-job-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        text-decoration: none;
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 16px;
        align-items: center;
        transition: all 0.25s;
    }

    .landing-job-card:hover {
        border-color: var(--teal-light);
        background: var(--bg-card-hover);
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }

    .job-card-main {
        min-width: 0;
    }

    .job-card-category {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--gold);
        margin-bottom: 8px;
    }

    .job-card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 6px;
    }

    .job-card-company {
        font-size: 0.95rem;
        color: var(--text-secondary);
        margin-bottom: 12px;
    }

    .job-card-meta {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
    }

    .job-card-badge {
        font-size: 0.8rem;
        padding: 4px 10px;
        border-radius: 4px;
        background: var(--bg-darker);
        color: var(--text-secondary);
    }

    .job-card-badge.salary {
        background: rgba(232, 168, 124, 0.15);
        color: var(--gold);
    }

    .job-card-badge.remote {
        background: rgba(74, 222, 128, 0.15);
        color: var(--success);
    }

    .job-card-cta {
        flex-shrink: 0;
    }

    .job-card-cta .btn {
        white-space: nowrap;
    }

    .related-landing-pages {
        margin: 40px 0;
        padding-top: 32px;
        border-top: 1px solid var(--border);
    }

    .related-landing-pages h2 {
        font-size: 1.25rem;
        margin-bottom: 20px;
    }

    .related-pages-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
    }

    .related-page-link {
        padding: 8px 16px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 20px;
        color: var(--text-secondary);
        text-decoration: none;
        font-size: 0.9rem;
        transition: all 0.2s;
    }

    .related-page-link:hover {
        background: var(--bg-card-hover);
        border-color: var(--teal-light);
        color: var(--text-primary);
    }

    @media (max-width: 768px) {
        .landing-header h1 { font-size: 1.75rem; }
        .landing-stats { flex-direction: column; gap: 16px; }
        .landing-job-card { grid-template-columns: 1fr; }
        .job-card-cta { justify-self: start; }
    }
'''


def generate_location_faqs(location_slug, config, num_jobs, avg_salary):
    """Generate FAQs for location-based landing pages."""
    location_name = config['h1'].replace('AI & Machine Learning Jobs in ', '').replace('Remote AI & Machine Learning Jobs', 'Remote')
    faqs = []

    # Core question about jobs available
    faqs.append({
        'question': f'How many AI jobs are available in {location_name}?',
        'answer': f'AI Market Pulse currently tracks {num_jobs} AI and machine learning job openings in {location_name}. This includes roles like AI engineer, ML engineer, data scientist, and prompt engineer positions.'
    })

    # Salary question if we have data
    if avg_salary > 0:
        faqs.append({
            'question': f'What is the average AI engineer salary in {location_name}?',
            'answer': f'Based on job postings with disclosed compensation, AI roles in {location_name} pay an average of ${int(avg_salary/1000)}K. Actual salaries vary based on experience, specific skills (like RAG or LangChain), and company size.'
        })

    # Remote-specific FAQs
    if location_slug == 'remote':
        faqs.append({
            'question': 'Do remote AI jobs pay less than in-office roles?',
            'answer': 'It depends on company policy. Some companies pay location-agnostic rates (same salary regardless of location), while others use geographic pay bands. Based on our data, remote AI roles average 5-10% below equivalent Bay Area in-office roles, but offer significant cost-of-living advantages.'
        })
        faqs.append({
            'question': 'What skills are most in-demand for remote AI jobs?',
            'answer': 'Remote AI positions typically emphasize self-directed skills: strong async communication, experience with remote collaboration tools, and ability to ship independently. Technical skills like Python, RAG systems, and LangChain remain important regardless of work location.'
        })
    else:
        # Location-specific benefits
        location_benefits = {
            'san-francisco': 'San Francisco offers access to top AI companies like OpenAI, Anthropic, and major tech giants. The Bay Area AI ecosystem provides networking opportunities, higher salaries, and cutting-edge research exposure.',
            'new-york': 'New York offers strong AI opportunities in fintech, media, and enterprise AI. NYC AI salaries are competitive with the Bay Area, and the city provides diverse industry exposure.',
            'seattle': 'Seattle is home to Amazon and Microsoft AI divisions. The area offers competitive salaries with no state income tax, making it financially attractive for AI professionals.',
            'austin': 'Austin combines a growing tech scene with lower cost of living than coastal cities. Many AI companies have opened offices here, and the city offers a good work-life balance.',
            'boston': 'Boston offers proximity to MIT, Harvard, and numerous AI research labs. The area excels in healthcare AI, robotics, and foundational ML research.',
            'los-angeles': 'Los Angeles has growing AI opportunities in entertainment tech, autonomous vehicles, and gaming. The city offers diverse AI applications beyond traditional tech.'
        }

        if location_slug in location_benefits:
            faqs.append({
                'question': f'Why work in AI in {location_name}?',
                'answer': location_benefits[location_slug]
            })

    return faqs


def generate_skill_faqs(skill_slug, config, num_jobs, avg_salary, remote_count):
    """Generate FAQs for skill-based landing pages."""
    skill_name = config['h1'].replace('AI Jobs Requiring ', '').replace('AI & ML Jobs Requiring ', '').replace(' Jobs', '')
    faqs = []

    # Jobs available
    faqs.append({
        'question': f'How many AI jobs require {skill_name}?',
        'answer': f'AI Market Pulse currently tracks {num_jobs} AI job openings that require {skill_name} skills. {remote_count} of these are remote positions.'
    })

    # Skill-specific FAQs
    skill_faqs = {
        'python': [
            {
                'question': 'Is Python essential for AI engineering?',
                'answer': 'Yes. Python appears in 65%+ of AI job postings. Every major AI framework (PyTorch, TensorFlow, LangChain) uses Python. While Rust is growing for performance-critical components, Python remains the foundation for AI work.'
            },
            {
                'question': 'How proficient in Python should I be for AI jobs?',
                'answer': 'Most AI roles expect intermediate to advanced Python. You should be comfortable with data structures, async programming, package management, and libraries like NumPy and Pandas. Production experience matters more than syntax expertise.'
            }
        ],
        'pytorch': [
            {
                'question': 'Is PyTorch or TensorFlow better for AI careers?',
                'answer': 'PyTorch has become the dominant framework for research and is increasingly popular in production. Learning PyTorch first gives you more flexibility, but understanding both is valuable. Many companies use PyTorch for development and export to other formats for deployment.'
            }
        ],
        'langchain': [
            {
                'question': 'Is LangChain worth learning for AI jobs?',
                'answer': 'Yes. LangChain is commonly requested in LLM application roles, especially for RAG systems and AI agents. While some teams build custom solutions, LangChain experience demonstrates you understand LLM orchestration patterns.'
            },
            {
                'question': 'What should I know besides LangChain?',
                'answer': 'Complement LangChain with: vector databases (Pinecone, Chroma), prompt engineering, evaluation frameworks, and understanding when to use alternatives like LlamaIndex or custom solutions. Production deployment experience is highly valued.'
            }
        ],
        'rag': [
            {
                'question': 'How important is RAG experience for AI jobs?',
                'answer': 'RAG (Retrieval-Augmented Generation) appears in 74% of LLM-focused AI engineering roles. It\'s the single most requested LLM-specific skill. Companies need engineers who can build production retrieval systems, not just call LLM APIs.'
            },
            {
                'question': 'What vector database should I learn for RAG?',
                'answer': 'Pinecone is most commonly requested, followed by Weaviate and Chroma. However, the concepts transfer between databases. Focus on understanding embeddings, similarity metrics, and chunking strategies rather than one specific tool.'
            }
        ],
        'llm': [
            {
                'question': 'Should I specialize in one LLM or learn multiple?',
                'answer': 'Learn concepts deeply, not just one API. Core skills (prompt engineering, RAG, evaluation) transfer across models. Most companies use multiple models—OpenAI for some tasks, Claude for others. Flexibility is more valuable than single-model expertise.'
            }
        ],
        'mlops': [
            {
                'question': 'How has MLOps changed with LLMs?',
                'answer': 'Traditional MLOps focused on training pipelines and model deployment. LLMOps adds: prompt management and versioning, RAG pipeline operations, LLM evaluation and monitoring, cost optimization, and caching strategies. The core principles remain but applied to different artifacts.'
            }
        ],
        'ai-agents': [
            {
                'question': 'What skills do I need for AI agent development?',
                'answer': 'Key skills include: multi-step reasoning and planning systems, tool use and function calling, state management and memory systems, evaluation frameworks, error handling and recovery, and security for autonomous systems. Experience with LangChain agents or custom implementations is valued.'
            }
        ],
        'prompt-engineering': [
            {
                'question': 'Is prompt engineering still a viable career?',
                'answer': 'Dedicated prompt engineer roles are declining, but prompt engineering skills are more valuable than ever as part of broader AI engineering roles. The career path leads to AI engineering, product management, or domain specialization.'
            }
        ]
    }

    if skill_slug in skill_faqs:
        faqs.extend(skill_faqs[skill_slug])

    # Salary question
    if avg_salary > 0:
        faqs.append({
            'question': f'What salary can I expect with {skill_name} skills?',
            'answer': f'AI roles requiring {skill_name} pay an average of ${int(avg_salary/1000)}K based on disclosed compensation. Specialized skills like {skill_name} combined with production experience typically command 10-20% premiums over general AI roles.'
        })

    return faqs


def generate_job_card_html(job):
    """Generate HTML for a single job card on landing pages."""
    company = str(job.get('company', job.get('company_name', 'Unknown')))
    title = str(job.get('title', 'AI Role'))
    location = str(job.get('location', '')) if pd.notna(job.get('location')) else ''
    salary = format_salary(job.get('salary_min', job.get('min_amount')), job.get('salary_max', job.get('max_amount')))
    category = job.get('job_category', '') if pd.notna(job.get('job_category')) else ''
    remote_status = is_remote(job)

    # Generate slug
    job_slug = f"{make_slug(company)}-{make_slug(title)}"
    hash_suffix = hashlib.md5(f"{company}{title}{location}".encode()).hexdigest()[:6]
    job_slug = f"{job_slug}-{hash_suffix}"

    company_escaped = escape_html(company)
    title_escaped = escape_html(title)
    location_escaped = escape_html(location)

    return f'''
        <a href="/jobs/{job_slug}/" class="landing-job-card">
            <div class="job-card-main">
                <div class="job-card-category">{escape_html(category)}</div>
                <div class="job-card-title">{title_escaped}</div>
                <div class="job-card-company">{company_escaped}</div>
                <div class="job-card-meta">
                    {f'<span class="job-card-badge salary">{salary}</span>' if salary else ''}
                    {f'<span class="job-card-badge remote">Remote</span>' if remote_status else f'<span class="job-card-badge">{location_escaped}</span>' if location else ''}
                </div>
            </div>
            <div class="job-card-cta">
                <span class="btn btn-outline">View Role →</span>
            </div>
        </a>
    '''


# =============================================================================
# LOCATION-BASED LANDING PAGES
# =============================================================================

# Key locations to generate pages for
LOCATION_CONFIGS = {
    'remote': {
        'title': 'Remote AI Jobs',
        'h1': 'Remote AI & Machine Learning Jobs',
        'description': 'Browse remote AI jobs that let you work from anywhere. Remote ML engineer, AI researcher, and prompt engineer positions.',
        'filter_func': lambda job: is_remote(job)
    },
    'san-francisco': {
        'title': 'AI Jobs in San Francisco',
        'h1': 'AI & Machine Learning Jobs in San Francisco',
        'description': 'Find AI jobs in San Francisco, the heart of tech innovation. ML engineer, AI researcher, and prompt engineer positions in the Bay Area.',
        'filter_func': lambda job: any(x in str(job.get('location', '')).lower() for x in ['san francisco', 'sf', 'bay area'])
    },
    'new-york': {
        'title': 'AI Jobs in New York',
        'h1': 'AI & Machine Learning Jobs in New York',
        'description': 'Discover AI jobs in New York City. Machine learning engineer, AI researcher, and data science positions in NYC.',
        'filter_func': lambda job: any(x in str(job.get('location', '')).lower() for x in ['new york', 'nyc', 'manhattan', 'brooklyn'])
    },
    'seattle': {
        'title': 'AI Jobs in Seattle',
        'h1': 'AI & Machine Learning Jobs in Seattle',
        'description': 'Explore AI jobs in Seattle. Home to Amazon and Microsoft, find ML engineer and AI research positions.',
        'filter_func': lambda job: 'seattle' in str(job.get('location', '')).lower()
    },
    'austin': {
        'title': 'AI Jobs in Austin',
        'h1': 'AI & Machine Learning Jobs in Austin',
        'description': 'Find AI jobs in Austin, Texas - a growing tech hub. Machine learning and AI engineer positions.',
        'filter_func': lambda job: 'austin' in str(job.get('location', '')).lower()
    },
    'boston': {
        'title': 'AI Jobs in Boston',
        'h1': 'AI & Machine Learning Jobs in Boston',
        'description': 'Discover AI jobs in Boston. Near MIT and Harvard, find cutting-edge ML and AI research positions.',
        'filter_func': lambda job: 'boston' in str(job.get('location', '')).lower()
    },
    'los-angeles': {
        'title': 'AI Jobs in Los Angeles',
        'h1': 'AI & Machine Learning Jobs in Los Angeles',
        'description': 'Find AI jobs in Los Angeles. Machine learning, AI engineering, and data science positions in LA.',
        'filter_func': lambda job: any(x in str(job.get('location', '')).lower() for x in ['los angeles', 'la', 'santa monica'])
    },
}


def generate_location_page(location_slug, config, jobs_df, all_locations):
    """Generate a location-based landing page."""
    # Filter jobs for this location
    location_jobs = jobs_df[jobs_df.apply(config['filter_func'], axis=1)]
    num_jobs = len(location_jobs)

    if num_jobs == 0:
        return None, False

    # Determine if thin content
    is_thin = num_jobs < MIN_JOBS_FOR_LOCATION_INDEX
    robots = 'noindex, follow' if is_thin else 'index, follow'

    # Calculate stats
    with_salary = location_jobs['salary_max'].notna().sum() if 'salary_max' in location_jobs.columns else 0
    avg_salary = location_jobs['salary_max'].dropna().mean() if 'salary_max' in location_jobs.columns and with_salary > 0 else 0

    # Breadcrumbs
    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'AI Jobs', 'url': '/jobs/'},
        {'name': config['title'], 'url': f'/jobs/{location_slug}/'}
    ]
    breadcrumb_schema = generate_breadcrumb_schema(breadcrumbs)

    # Collection schema
    collection_schema = generate_collectionpage_schema(
        name=config['title'],
        description=config['description'],
        url=f"/jobs/{location_slug}/",
        item_count=num_jobs,
        keywords=[f"{location_slug} AI jobs", f"{location_slug} ML jobs", "AI engineer jobs", "machine learning jobs"]
    )

    # Generate job cards (limit to 50)
    jobs_html = ""
    for _, job in location_jobs.head(50).iterrows():
        jobs_html += generate_job_card_html(job)

    # Generate FAQs
    faqs = generate_location_faqs(location_slug, config, num_jobs, avg_salary)
    faq_html = generate_faq_html(faqs, section_title="Frequently Asked Questions")

    # Related locations
    related_html = ""
    other_locations = [loc for loc in all_locations if loc != location_slug][:6]
    for loc in other_locations:
        loc_title = LOCATION_CONFIGS.get(loc, {}).get('title', loc.replace('-', ' ').title())
        related_html += f'<a href="/jobs/{loc}/" class="related-page-link">{loc_title}</a>'

    # Breadcrumb HTML
    breadcrumb_html = ' / '.join([
        f'<a href="{b["url"]}">{b["name"]}</a>' if i < len(breadcrumbs) - 1 else b['name']
        for i, b in enumerate(breadcrumbs)
    ])

    html = f'''{get_html_head(
        config['title'] + ' 2026',
        config['description'],
        f"jobs/{location_slug}/",
        robots=robots
    )}
    {breadcrumb_schema}
    {collection_schema}
    <style>{CSS_LANDING}{CSS_FAQ_SECTION}</style>
{get_nav_html('jobs')}

    <div class="landing-header">
        <div class="container">
            <nav class="breadcrumb">{breadcrumb_html}</nav>
            <h1>{config['h1']}</h1>
            <p class="lead">{config['description']}</p>
            <div class="landing-stats">
                <div class="landing-stat">
                    <div class="landing-stat-value">{num_jobs}</div>
                    <div class="landing-stat-label">Open Positions</div>
                </div>
                {f'<div class="landing-stat"><div class="landing-stat-value">${int(avg_salary/1000)}K</div><div class="landing-stat-label">Avg. Salary</div></div>' if avg_salary > 0 else ''}
            </div>
        </div>
    </div>

    <main>
        <div class="container">
            <div class="jobs-grid">
                {jobs_html}
            </div>

            {f'<p style="text-align: center; color: var(--text-muted);">Showing {min(50, num_jobs)} of {num_jobs} jobs</p>' if num_jobs > 50 else ''}

            {faq_html}

            {get_cta_box()}

            <section class="related-landing-pages">
                <h2>Browse Jobs by Location</h2>
                <div class="related-pages-grid">
                    {related_html}
                </div>
            </section>
        </div>
    </main>

{get_footer_html()}'''

    # Save page
    page_dir = f'{JOBS_DIR}/{location_slug}'
    os.makedirs(page_dir, exist_ok=True)
    with open(f'{page_dir}/index.html', 'w') as f:
        f.write(html)

    return location_slug, is_thin


# =============================================================================
# SKILL-BASED LANDING PAGES
# =============================================================================

# Key skills to generate pages for
SKILL_CONFIGS = {
    'python': {
        'title': 'Python AI Jobs',
        'h1': 'AI & ML Jobs Requiring Python',
        'description': 'Find AI jobs that require Python programming. Machine learning engineer, data scientist, and AI developer positions.',
        'keywords': ['Python', 'python']
    },
    'pytorch': {
        'title': 'PyTorch AI Jobs',
        'h1': 'AI Jobs Requiring PyTorch',
        'description': 'Discover AI jobs using PyTorch deep learning framework. Research scientist and ML engineer positions.',
        'keywords': ['PyTorch', 'pytorch']
    },
    'tensorflow': {
        'title': 'TensorFlow AI Jobs',
        'h1': 'AI Jobs Requiring TensorFlow',
        'description': 'Find AI jobs using TensorFlow. Machine learning engineer and deep learning researcher positions.',
        'keywords': ['TensorFlow', 'tensorflow']
    },
    'langchain': {
        'title': 'LangChain AI Jobs',
        'h1': 'AI Jobs Requiring LangChain',
        'description': 'Discover AI jobs using LangChain for LLM applications. Prompt engineer and AI developer positions.',
        'keywords': ['LangChain', 'langchain']
    },
    'rag': {
        'title': 'RAG AI Jobs',
        'h1': 'AI Jobs with RAG Experience',
        'description': 'Find AI jobs requiring Retrieval-Augmented Generation (RAG) experience. LLM engineer and AI architect positions.',
        'keywords': ['RAG', 'Retrieval-Augmented Generation', 'retrieval augmented']
    },
    'aws': {
        'title': 'AWS AI Jobs',
        'h1': 'AI Jobs Requiring AWS',
        'description': 'Find AI jobs with AWS cloud experience. ML engineer and MLOps positions on Amazon Web Services.',
        'keywords': ['AWS', 'Amazon Web Services', 'SageMaker']
    },
    'llm': {
        'title': 'LLM Engineer Jobs',
        'h1': 'LLM & Large Language Model Jobs',
        'description': 'Find LLM engineer jobs working with large language models. GPT, Claude, and AI chat application positions.',
        'keywords': ['LLM', 'Large Language Model', 'GPT', 'Claude']
    },
    'fine-tuning': {
        'title': 'Fine-Tuning AI Jobs',
        'h1': 'AI Jobs Requiring Fine-Tuning Experience',
        'description': 'Find AI jobs requiring model fine-tuning expertise. ML engineer and AI researcher positions.',
        'keywords': ['fine-tuning', 'fine tuning', 'finetuning', 'PEFT', 'LoRA']
    },
    'mlops': {
        'title': 'MLOps Jobs',
        'h1': 'MLOps & ML Engineering Jobs',
        'description': 'Find MLOps jobs deploying machine learning models to production. ML infrastructure and platform roles.',
        'keywords': ['MLOps', 'ML Operations', 'model deployment']
    },
    'ai-agents': {
        'title': 'AI Agent Jobs',
        'h1': 'AI Agent & Autonomous Systems Jobs',
        'description': 'Find AI agent jobs building autonomous AI systems. AI developer and research positions.',
        'keywords': ['AI Agents', 'AI Agent', 'autonomous agents', 'agentic']
    },
    'prompt-engineering': {
        'title': 'Prompt Engineering Jobs',
        'h1': 'Prompt Engineering Jobs',
        'description': 'Find prompt engineering jobs crafting effective AI prompts. LLM optimization and AI application roles.',
        'keywords': ['Prompt Engineering', 'prompt engineer', 'prompt design']
    },
    'computer-vision': {
        'title': 'Computer Vision Jobs',
        'h1': 'Computer Vision & Image AI Jobs',
        'description': 'Find computer vision jobs working on image and video AI. ML engineer and research positions.',
        'keywords': ['Computer Vision', 'CV', 'image recognition', 'object detection']
    },
    'nlp': {
        'title': 'NLP Jobs',
        'h1': 'NLP & Natural Language Processing Jobs',
        'description': 'Find NLP jobs working with text and language AI. ML engineer and research positions.',
        'keywords': ['NLP', 'Natural Language Processing', 'text analysis']
    },
}


def job_has_skill(job, keywords):
    """Check if a job mentions any of the skill keywords."""
    # Check skills_tags
    skills = parse_skills(job.get('skills_tags'))
    for skill in skills:
        for keyword in keywords:
            if keyword.lower() in skill.lower():
                return True

    # Check job category
    category = str(job.get('job_category', '')).lower()
    for keyword in keywords:
        if keyword.lower() in category:
            return True

    # Check title
    title = str(job.get('title', '')).lower()
    for keyword in keywords:
        if keyword.lower() in title:
            return True

    return False


def generate_skill_page(skill_slug, config, jobs_df, all_skills):
    """Generate a skill-based landing page."""
    # Filter jobs for this skill
    skill_jobs = jobs_df[jobs_df.apply(lambda job: job_has_skill(job, config['keywords']), axis=1)]
    num_jobs = len(skill_jobs)

    if num_jobs == 0:
        return None, False

    # Determine if thin content
    is_thin = num_jobs < MIN_JOBS_FOR_SKILL_INDEX
    robots = 'noindex, follow' if is_thin else 'index, follow'

    # Calculate stats
    with_salary = skill_jobs['salary_max'].notna().sum() if 'salary_max' in skill_jobs.columns else 0
    avg_salary = skill_jobs['salary_max'].dropna().mean() if 'salary_max' in skill_jobs.columns and with_salary > 0 else 0
    remote_count = skill_jobs.apply(is_remote, axis=1).sum()

    # Breadcrumbs
    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'AI Jobs', 'url': '/jobs/'},
        {'name': 'By Skill', 'url': '/jobs/skills/'},
        {'name': config['title'].replace(' Jobs', ''), 'url': f'/jobs/skills/{skill_slug}/'}
    ]
    breadcrumb_schema = generate_breadcrumb_schema(breadcrumbs)

    # Collection schema
    collection_schema = generate_collectionpage_schema(
        name=config['title'],
        description=config['description'],
        url=f"/jobs/skills/{skill_slug}/",
        item_count=num_jobs,
        keywords=[config['title'], f"{skill_slug} AI jobs", "machine learning jobs"]
    )

    # Generate job cards (limit to 50)
    jobs_html = ""
    for _, job in skill_jobs.head(50).iterrows():
        jobs_html += generate_job_card_html(job)

    # Generate FAQs
    faqs = generate_skill_faqs(skill_slug, config, num_jobs, avg_salary, remote_count)
    faq_html = generate_faq_html(faqs, section_title="Frequently Asked Questions")

    # Related skills
    related_html = ""
    other_skills = [sk for sk in all_skills if sk != skill_slug][:8]
    for sk in other_skills:
        sk_title = SKILL_CONFIGS.get(sk, {}).get('title', sk.replace('-', ' ').title())
        related_html += f'<a href="/jobs/skills/{sk}/" class="related-page-link">{sk_title.replace(" Jobs", "")}</a>'

    # Breadcrumb HTML
    breadcrumb_html = ' / '.join([
        f'<a href="{b["url"]}">{b["name"]}</a>' if i < len(breadcrumbs) - 1 else b['name']
        for i, b in enumerate(breadcrumbs)
    ])

    html = f'''{get_html_head(
        config['title'] + ' 2026',
        config['description'],
        f"jobs/skills/{skill_slug}/",
        robots=robots
    )}
    {breadcrumb_schema}
    {collection_schema}
    <style>{CSS_LANDING}{CSS_FAQ_SECTION}</style>
{get_nav_html('jobs')}

    <div class="landing-header">
        <div class="container">
            <nav class="breadcrumb">{breadcrumb_html}</nav>
            <h1>{config['h1']}</h1>
            <p class="lead">{config['description']}</p>
            <div class="landing-stats">
                <div class="landing-stat">
                    <div class="landing-stat-value">{num_jobs}</div>
                    <div class="landing-stat-label">Open Positions</div>
                </div>
                {f'<div class="landing-stat"><div class="landing-stat-value">${int(avg_salary/1000)}K</div><div class="landing-stat-label">Avg. Salary</div></div>' if avg_salary > 0 else ''}
                <div class="landing-stat">
                    <div class="landing-stat-value">{remote_count}</div>
                    <div class="landing-stat-label">Remote Roles</div>
                </div>
            </div>
        </div>
    </div>

    <main>
        <div class="container">
            <div class="jobs-grid">
                {jobs_html}
            </div>

            {f'<p style="text-align: center; color: var(--text-muted);">Showing {min(50, num_jobs)} of {num_jobs} jobs</p>' if num_jobs > 50 else ''}

            {faq_html}

            {get_cta_box()}

            <section class="related-landing-pages">
                <h2>Browse Jobs by Skill</h2>
                <div class="related-pages-grid">
                    {related_html}
                </div>
            </section>
        </div>
    </main>

{get_footer_html()}'''

    # Save page
    page_dir = f'{JOBS_DIR}/skills/{skill_slug}'
    os.makedirs(page_dir, exist_ok=True)
    with open(f'{page_dir}/index.html', 'w') as f:
        f.write(html)

    return skill_slug, is_thin


def generate_skills_index(jobs_df, skill_pages):
    """Generate the skills index page."""
    os.makedirs(f'{JOBS_DIR}/skills', exist_ok=True)

    # Build skills listing
    skills_html = ""
    for skill_slug in sorted(skill_pages.keys()):
        config = SKILL_CONFIGS.get(skill_slug, {})
        page_info = skill_pages[skill_slug]
        if page_info is None:
            continue

        skills_html += f'''
        <a href="/jobs/skills/{skill_slug}/" class="skill-index-card">
            <h3>{config.get('title', skill_slug.replace('-', ' ').title())}</h3>
            <p>{page_info.get('count', 0)} jobs</p>
        </a>
        '''

    collection_schema = generate_collectionpage_schema(
        name="AI Jobs by Skill",
        description="Browse AI and machine learning jobs by required skill. Find Python, PyTorch, LangChain, and more.",
        url="/jobs/skills/",
        item_count=len(skill_pages),
        keywords=["AI jobs by skill", "ML jobs", "AI skills", "machine learning skills"]
    )

    html = f'''{get_html_head(
        "AI Jobs by Skill",
        "Browse AI and machine learning jobs by required skill. Find Python, PyTorch, LangChain, RAG, and more.",
        "jobs/skills/"
    )}
    {collection_schema}
    <style>
        {CSS_LANDING}
        .skills-index-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 16px;
            padding: 32px 0;
        }}
        .skill-index-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            text-decoration: none;
            transition: all 0.25s;
        }}
        .skill-index-card:hover {{
            border-color: var(--teal-light);
            background: var(--bg-card-hover);
            transform: translateY(-2px);
        }}
        .skill-index-card h3 {{
            color: var(--text-primary);
            margin-bottom: 8px;
        }}
        .skill-index-card p {{
            color: var(--gold);
            font-size: 0.9rem;
        }}
    </style>
{get_nav_html('jobs')}

    <div class="page-header">
        <div class="container">
            <h1>AI Jobs by Skill</h1>
            <p class="lead">Find AI and machine learning jobs by the skills and technologies they require.</p>
        </div>
    </div>

    <main>
        <div class="container">
            <div class="skills-index-grid">
                {skills_html}
            </div>

            {get_cta_box()}
        </div>
    </main>

{get_footer_html()}'''

    with open(f'{JOBS_DIR}/skills/index.html', 'w') as f:
        f.write(html)

    print(f"  Generated skills index page")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    # Load job data
    jobs_df = get_latest_jobs()
    if jobs_df.empty:
        print("  No job data found")
        return

    print(f"\n  Loaded {len(jobs_df)} jobs")

    # === LOCATION PAGES ===
    print(f"\n  Generating location-based landing pages...")
    location_count = 0
    location_thin = 0
    generated_locations = []

    for location_slug, config in LOCATION_CONFIGS.items():
        result, is_thin = generate_location_page(location_slug, config, jobs_df, list(LOCATION_CONFIGS.keys()))
        if result:
            location_count += 1
            generated_locations.append(location_slug)
            if is_thin:
                location_thin += 1
                print(f"    /jobs/{location_slug}/ (noindex: thin content)")
            else:
                print(f"    /jobs/{location_slug}/")

    print(f"\n  Generated {location_count} location pages ({location_thin} noindexed)")

    # === SKILL PAGES ===
    print(f"\n  Generating skill-based landing pages...")
    skill_count = 0
    skill_thin = 0
    skill_pages = {}

    for skill_slug, config in SKILL_CONFIGS.items():
        result, is_thin = generate_skill_page(skill_slug, config, jobs_df, list(SKILL_CONFIGS.keys()))
        if result:
            skill_count += 1
            skill_jobs = jobs_df[jobs_df.apply(lambda job: job_has_skill(job, config['keywords']), axis=1)]
            skill_pages[skill_slug] = {'count': len(skill_jobs), 'is_thin': is_thin}
            if is_thin:
                skill_thin += 1
                print(f"    /jobs/skills/{skill_slug}/ (noindex: thin content)")
            else:
                print(f"    /jobs/skills/{skill_slug}/")
        else:
            skill_pages[skill_slug] = None

    # Generate skills index page
    generate_skills_index(jobs_df, skill_pages)

    print(f"\n  Generated {skill_count} skill pages ({skill_thin} noindexed)")

    print(f"\n{'='*70}")
    print(f"  LANDING PAGES SUMMARY")
    print(f"  - Location pages: {location_count} ({location_count - location_thin} indexed)")
    print(f"  - Skill pages: {skill_count} ({skill_count - skill_thin} indexed)")
    print(f"  - Skills index: 1")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
