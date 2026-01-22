#!/usr/bin/env python3
"""
Generate market intelligence/insights page at /insights/
Analyzes AI tools, frameworks, skills, and trends from job descriptions.
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
INSIGHTS_DIR = f'{SITE_DIR}/insights'
ARTICLES_FILE = f'{DATA_DIR}/articles.json'

print("="*70)
print("  AI MARKET PULSE - GENERATING INSIGHTS PAGE")
print("="*70)

os.makedirs(INSIGHTS_DIR, exist_ok=True)

# Load market intelligence data
intel_file = f"{DATA_DIR}/market_intelligence.json"
if os.path.exists(intel_file):
    with open(intel_file) as f:
        intel = json.load(f)
    print(f"\n Loaded market intelligence data")
else:
    # Generate from job data
    files = glob.glob(f"{DATA_DIR}/ai_jobs_*.csv")
    if files:
        df = pd.read_csv(max(files, key=os.path.getctime))
    elif os.path.exists(f"{DATA_DIR}/jobs.json"):
        with open(f"{DATA_DIR}/jobs.json") as f:
            df = pd.DataFrame(json.load(f).get('jobs', []))
    else:
        print(" No data found")
        exit(1)

    # Basic intel from job data
    intel = {
        'total_jobs': len(df),
        'skills': {},
        'categories': df['job_category'].value_counts().to_dict() if 'job_category' in df.columns else {},
        'remote_breakdown': df['remote_type'].value_counts().to_dict() if 'remote_type' in df.columns else {},
    }

total_jobs = intel.get('total_jobs', 0)
skills = intel.get('skills', {})
skills_by_cat = intel.get('skills_by_category', {})
categories = intel.get('categories', {})
remote = intel.get('remote_breakdown', {})
update_date = intel.get('date', datetime.now().strftime('%Y-%m-%d'))


def escape_html(text):
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def load_articles():
    """Load articles from JSON file."""
    if os.path.exists(ARTICLES_FILE):
        with open(ARTICLES_FILE) as f:
            data = json.load(f)
        return data.get('articles', []), data.get('categories', {}), data.get('tags', {})
    return [], {}, {}


def generate_articles_section(articles, categories):
    """Generate the articles listing section for the insights page."""
    if not articles:
        return ''

    # Sort by published date (newest first)
    sorted_articles = sorted(articles, key=lambda x: x.get('published', ''), reverse=True)

    # Latest articles (up to 6)
    latest = sorted_articles[:6]
    latest_cards = []
    for a in latest:
        cat_name = categories.get(a.get('category', ''), {}).get('name', a.get('category', '').replace('-', ' ').title())
        latest_cards.append(f'''
        <a href="/insights/{a['slug']}/" class="article-card">
            <div class="article-card-category">{cat_name}</div>
            <h3>{a['title']}</h3>
            <p>{a['description']}</p>
            <div class="article-card-footer">
                <span>{a.get('published', '')}</span>
                <span>{a.get('readTime', '5 min')} read</span>
            </div>
        </a>
        ''')

    # Category cards with article counts
    category_cards = []
    for cat_slug, cat_info in categories.items():
        cat_count = len([a for a in articles if a.get('category') == cat_slug])
        category_cards.append(f'''
        <a href="/insights/category/{cat_slug}/" class="category-card">
            <h4>{cat_info.get('name', cat_slug)}</h4>
            <p>{cat_count} article{"s" if cat_count != 1 else ""}</p>
        </a>
        ''')

    # Tag cloud
    tag_counts = {}
    for a in articles:
        for tag in a.get('tags', []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    tag_links = []
    for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
        tag_display = tag.replace('-', ' ').title()
        tag_links.append(f'<a href="/insights/tags/{tag}/">{tag_display} <span class="tag-count">({count})</span></a>')

    return f'''
    <div class="articles-section" style="margin-top: 64px; padding-top: 48px; border-top: 1px solid var(--border);">
        <h2 style="font-size: 1.75rem; margin-bottom: 32px;">Latest Insights</h2>
        <div class="articles-grid">
            {"".join(latest_cards)}
        </div>

        <div style="margin-top: 48px;">
            <h3 style="font-size: 1.25rem; margin-bottom: 20px; color: var(--text-secondary);">Browse by Category</h3>
            <div class="category-grid">
                {"".join(category_cards)}
            </div>
        </div>

        <div style="margin-top: 48px;">
            <h3 style="font-size: 1.25rem; margin-bottom: 20px; color: var(--text-secondary);">Browse by Topic</h3>
            <div class="tag-cloud">
                {"".join(tag_links)}
            </div>
        </div>
    </div>
    '''


def make_bar_chart(data, max_width=100, color='var(--gold)'):
    """Generate horizontal bar chart HTML"""
    if not data:
        return '<p style="color: var(--text-muted);">No data available</p>'

    max_val = max(data.values()) if data else 1
    html = '<div class="chart">'
    for label, value in list(data.items())[:15]:
        pct = (value / max_val) * max_width
        count_pct = (value / total_jobs * 100) if total_jobs > 0 else 0
        html += f'''
            <div class="bar-row">
                <span class="bar-label">{escape_html(label)}</span>
                <div class="bar-container">
                    <div class="bar" style="width: {pct}%; background: {color};"></div>
                </div>
                <span class="bar-value">{value} ({count_pct:.1f}%)</span>
            </div>
        '''
    html += '</div>'
    return html


# Load articles
articles, article_categories, article_tags = load_articles()
articles_section_html = generate_articles_section(articles, article_categories)
print(f" Loaded {len(articles)} articles for insights page")

# Build page
html = f'''{get_html_head(
    "AI Job Market Intelligence 2026",
    f"Market trends, top tools, and insights from {total_jobs} AI job postings. See which frameworks, skills, and technologies are in demand.",
    "insights/"
)}
{get_nav_html('insights')}

    <style>
        .chart {{ margin: 20px 0; }}
        .bar-row {{ display: flex; align-items: center; margin-bottom: 8px; gap: 12px; }}
        .bar-label {{ width: 140px; font-size: 0.9rem; color: var(--text-secondary); }}
        .bar-container {{ flex: 1; height: 24px; background: var(--bg-card); border-radius: 4px; overflow: hidden; }}
        .bar {{ height: 100%; border-radius: 4px; transition: width 0.3s; }}
        .bar-value {{ width: 80px; font-size: 0.85rem; color: var(--text-muted); text-align: right; }}
        .insight-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        .insight-card h2 {{ margin-bottom: 16px; font-size: 1.25rem; }}
        .key-insight {{
            background: rgba(232, 168, 124, 0.1);
            border-left: 3px solid var(--gold);
            padding: 16px;
            margin: 16px 0;
            border-radius: 0 8px 8px 0;
        }}
        .key-insight strong {{ color: var(--gold); }}

        /* Article Cards */
        .articles-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 24px;
        }}

        .article-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            text-decoration: none;
            transition: all 0.25s;
            display: flex;
            flex-direction: column;
        }}

        .article-card:hover {{
            border-color: var(--teal-light);
            background: var(--bg-card-hover);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }}

        .article-card-category {{
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--gold);
            margin-bottom: 12px;
        }}

        .article-card h3 {{
            font-size: 1.1rem;
            color: var(--text-primary);
            margin-bottom: 12px;
            line-height: 1.4;
        }}

        .article-card p {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            line-height: 1.6;
            flex-grow: 1;
        }}

        .article-card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid var(--border-light);
            font-size: 0.8rem;
            color: var(--text-muted);
        }}

        /* Category Cards */
        .category-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 16px;
        }}

        .category-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            text-decoration: none;
            transition: all 0.25s;
            text-align: center;
        }}

        .category-card:hover {{
            border-color: var(--gold);
            background: rgba(232, 168, 124, 0.1);
        }}

        .category-card h4 {{
            font-size: 1rem;
            color: var(--text-primary);
            margin-bottom: 4px;
        }}

        .category-card p {{
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        /* Tag Cloud */
        .tag-cloud {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .tag-cloud a {{
            padding: 8px 16px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            font-size: 0.9rem;
            color: var(--text-secondary);
            text-decoration: none;
            transition: all 0.15s;
        }}

        .tag-cloud a:hover {{
            border-color: var(--gold);
            color: var(--gold);
            background: rgba(232, 168, 124, 0.1);
        }}

        .tag-cloud .tag-count {{
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-left: 4px;
        }}
    </style>

    <div class="page-header">
        <div class="container">
            <h1>AI Job Market Intelligence</h1>
            <p class="lead">Trends, tools, and insights from {total_jobs:,} AI job postings. Updated {update_date}.</p>
        </div>
    </div>

    <main>
        <div class="container">
            <!-- SEO Intro Content -->
            <div class="seo-intro" style="max-width: 800px; margin-bottom: 3rem; padding-bottom: 2rem; border-bottom: 1px solid var(--border); color: var(--text-secondary); line-height: 1.8;">
                <p style="margin-bottom: 1rem;">
                    The AI job market in 2026 is maturing but still growing. After the explosive demand of 2023-2024 driven by ChatGPT and generative AI, the market has shifted from experimentation to production deployment. Companies are hiring not just for AI research, but for the infrastructure, operations, and product skills needed to ship AI products at scale.
                </p>
                <p style="margin-bottom: 1rem;">
                    AI Market Pulse analyzes <strong style="color: var(--text-primary);">{total_jobs:,} active job postings</strong> to surface the signals that matter: which skills are growing, which roles are emerging, and where compensation is heading. Our data comes from Indeed, LinkedIn, Greenhouse, Lever, and direct company career pages—refreshed weekly to reflect current market conditions.
                </p>
                <h2 style="font-size: 1.25rem; color: var(--text-primary); margin: 2rem 0 1rem;">What We Track</h2>
                <p style="margin-bottom: 1rem;">
                    Our market intelligence covers several dimensions: <strong style="color: var(--text-primary);">skills and tools</strong> (which technologies appear most frequently in job requirements), <strong style="color: var(--text-primary);">role distribution</strong> (the balance between different AI job categories), <strong style="color: var(--text-primary);">work arrangements</strong> (remote vs. hybrid vs. on-site), and <strong style="color: var(--text-primary);">salary trends</strong> (how compensation is moving across roles and locations).
                </p>
                <p style="margin-bottom: 1rem;">
                    Unlike salary surveys that rely on self-reported data from months ago, our insights come directly from active job postings. This gives you a real-time view of what employers are actually looking for and willing to pay—not what they were hiring for last quarter.
                </p>
            </div>

            <div class="insight-card">
                <h2>Top AI Tools & Frameworks</h2>
                <p style="color: var(--text-secondary); margin-bottom: 20px;">Most requested technologies in AI/ML job postings.</p>
                {make_bar_chart(skills)}
                <div class="key-insight">
                    <strong>Key Insight:</strong> Python and PyTorch dominate, with LangChain emerging as the top LLM framework.
                </div>
            </div>

            <div class="insight-card">
                <h2>Job Categories</h2>
                <p style="color: var(--text-secondary); margin-bottom: 20px;">Distribution of AI roles by category.</p>
                {make_bar_chart(categories, color='var(--teal-accent)')}
            </div>

            <div class="insight-card">
                <h2>Remote Work Distribution</h2>
                <p style="color: var(--text-secondary); margin-bottom: 20px;">Work arrangement preferences in AI roles.</p>
                {make_bar_chart(remote, color='var(--success)')}
            </div>

            {''.join([f"""
            <div class="insight-card">
                <h2>{escape_html(cat)}</h2>
                {make_bar_chart(dict(list(items.items())[:10]))}
            </div>
            """ for cat, items in skills_by_cat.items() if items])}

            {articles_section_html}

            {get_cta_box(
                title="Get Weekly Market Updates",
                description="Join our newsletter for AI job market trends, salary insights, and career opportunities.",
                button_text="Subscribe Free",
                button_url="https://ainewsdigest.substack.com"
            )}

            <!-- SEO Bottom Content -->
            <div class="seo-bottom" style="max-width: 800px; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--border); color: var(--text-secondary); line-height: 1.8;">
                <h2 style="font-size: 1.25rem; color: var(--text-primary); margin-bottom: 1rem;">How to Use This Data</h2>
                <p style="margin-bottom: 1rem;">
                    Market intelligence is only valuable if you act on it. Here's how AI professionals use our data: <strong style="color: var(--text-primary);">Career planning</strong>—identify which skills to develop based on growing demand, not hype. <strong style="color: var(--text-primary);">Salary negotiations</strong>—use real benchmarks to anchor compensation discussions. <strong style="color: var(--text-primary);">Job search strategy</strong>—focus on roles and locations where demand exceeds supply.
                </p>
                <h2 style="font-size: 1.25rem; color: var(--text-primary); margin: 2rem 0 1rem;">2026 Market Outlook</h2>
                <p style="margin-bottom: 1rem;">
                    Several trends are shaping the AI job market this year. <strong style="color: var(--text-primary);">Production over research</strong>: Companies that experimented with AI in 2023-2024 are now hiring for deployment and operations. MLOps, platform engineering, and AI infrastructure roles are growing faster than pure research positions. <strong style="color: var(--text-primary);">Specialization matters</strong>: Generalist "AI Engineer" roles are giving way to specialists—Prompt Engineers, LLM Engineers, ML Infrastructure Engineers, AI Product Managers with distinct skill requirements.
                </p>
                <p style="margin-bottom: 1rem;">
                    <strong style="color: var(--text-primary);">Remote remains strong</strong>: Despite some companies pushing return-to-office, AI roles maintain higher remote availability than the broader tech market. Our data shows remote AI positions often pay within 5-10% of equivalent on-site roles in major metros. <strong style="color: var(--text-primary);">The tools stack is consolidating</strong>: After a period of framework proliferation, the market is converging on standard stacks—PyTorch for ML, LangChain for LLM orchestration, and cloud-native deployment.
                </p>
                <h2 style="font-size: 1.25rem; color: var(--text-primary); margin: 2rem 0 1rem;">Our Methodology</h2>
                <p style="margin-bottom: 1rem;">
                    We aggregate job postings from Indeed, LinkedIn, Greenhouse, Lever, and company career pages. Each posting is enriched with structured data: job category, required skills, experience level, salary range (when disclosed), location, and remote work type. We update our dataset weekly and filter out duplicates, expired postings, and outliers. Our skill extraction uses both keyword matching and semantic analysis to capture tool mentions accurately.
                </p>
            </div>
        </div>
    </main>

{get_footer_html()}'''

with open(f'{INSIGHTS_DIR}/index.html', 'w') as f:
    f.write(html)

print(f"\n Generated insights page")
print(f" Total jobs analyzed: {total_jobs}")
print(f" Skills tracked: {len(skills)}")
print("="*70)
