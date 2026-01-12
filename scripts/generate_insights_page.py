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

print("="*70)
print("  PE COLLECTIVE - GENERATING INSIGHTS PAGE")
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
    </style>

    <div class="page-header">
        <div class="container">
            <h1>AI Job Market Intelligence</h1>
            <p class="lead">Trends, tools, and insights from {total_jobs:,} AI job postings. Updated {update_date}.</p>
        </div>
    </div>

    <main>
        <div class="container">
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

            {get_cta_box(
                title="Get Weekly Market Updates",
                description="Join our newsletter for AI job market trends, salary insights, and career opportunities.",
                button_text="Subscribe Free",
                button_url="https://ainewsdigest.substack.com"
            )}
        </div>
    </main>

{get_footer_html()}'''

with open(f'{INSIGHTS_DIR}/index.html', 'w') as f:
    f.write(html)

print(f"\n Generated insights page")
print(f" Total jobs analyzed: {total_jobs}")
print(f" Skills tracked: {len(skills)}")
print("="*70)
