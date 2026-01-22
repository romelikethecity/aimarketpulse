#!/usr/bin/env python3
"""
Generate article pages for the Insights section.

This script generates:
1. Individual article pages at /insights/[slug]/
2. Tag pages at /insights/tags/[tag]/
3. Category pages at /insights/category/[category]/

Uses markdown files from /content/insights/ and metadata from /data/articles.json
"""

import json
import os
import sys
import re
from datetime import datetime

# Add scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from templates import (
    get_html_head, get_nav_html, get_footer_html, get_cta_box,
    BASE_URL, SITE_NAME, slugify
)
from seo_core import (
    generate_breadcrumb_schema, generate_faq_schema, generate_faq_html,
    generate_article_schema, generate_article_faqs, CSS_FAQ_SECTION
)

# Directories
DATA_DIR = os.path.join(os.path.dirname(script_dir), 'data')
CONTENT_DIR = os.path.join(os.path.dirname(script_dir), 'content', 'insights')
SITE_DIR = os.path.join(os.path.dirname(script_dir), 'site')
INSIGHTS_DIR = os.path.join(SITE_DIR, 'insights')

print("=" * 70)
print("  AI MARKET PULSE - GENERATING ARTICLE PAGES")
print("=" * 70)


def load_articles_data():
    """Load articles metadata from JSON file."""
    articles_file = os.path.join(DATA_DIR, 'articles.json')
    if os.path.exists(articles_file):
        with open(articles_file, 'r') as f:
            return json.load(f)
    return {"articles": [], "categories": {}, "tags": {}, "author": {}}


def load_market_data():
    """Load market intelligence data for data-driven content."""
    intel_file = os.path.join(DATA_DIR, 'market_intelligence.json')
    if os.path.exists(intel_file):
        with open(intel_file, 'r') as f:
            return json.load(f)
    return {}


def load_markdown_content(slug):
    """Load and parse markdown content for an article."""
    md_file = os.path.join(CONTENT_DIR, f'{slug}.md')
    if os.path.exists(md_file):
        with open(md_file, 'r') as f:
            content = f.read()
        return parse_markdown(content)
    return None


def parse_markdown(content):
    """Convert markdown to HTML with basic formatting."""
    html = content

    # Headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Bold and italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', html)

    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # Blockquotes
    html = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

    # Unordered lists
    def process_ul(match):
        items = match.group(0).strip().split('\n')
        list_items = ''.join([f'<li>{item[2:].strip()}</li>' for item in items if item.startswith('- ')])
        return f'<ul>{list_items}</ul>'

    html = re.sub(r'(^- .+$\n?)+', process_ul, html, flags=re.MULTILINE)

    # Ordered lists
    def process_ol(match):
        items = match.group(0).strip().split('\n')
        list_items = ''.join([f'<li>{re.sub(r"^[0-9]+. ", "", item).strip()}</li>' for item in items if re.match(r'^[0-9]+\.', item)])
        return f'<ol>{list_items}</ol>'

    html = re.sub(r'(^[0-9]+\. .+$\n?)+', process_ol, html, flags=re.MULTILINE)

    # Paragraphs (wrap standalone lines)
    lines = html.split('\n\n')
    processed = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('<'):
            processed.append(f'<p>{line}</p>')
        elif line:
            processed.append(line)
    html = '\n'.join(processed)

    return html


def escape_html(text):
    """Escape HTML special characters."""
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


# =============================================================================
# CSS STYLES FOR ARTICLES
# =============================================================================

CSS_ARTICLE = '''
    /* Article Page Styles */
    .article-header {
        margin-bottom: 32px;
    }

    .article-meta {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 16px;
        margin-bottom: 16px;
        font-size: 0.9rem;
        color: var(--text-muted);
    }

    .article-category {
        display: inline-block;
        padding: 4px 12px;
        background: rgba(232, 168, 124, 0.15);
        color: var(--gold);
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        text-decoration: none;
    }

    .article-category:hover {
        background: rgba(232, 168, 124, 0.25);
        color: var(--gold-light);
    }

    .article-date, .article-read-time {
        color: var(--text-muted);
    }

    .article-author-byline {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid var(--border);
    }

    .article-author-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: var(--teal-primary);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--gold);
    }

    .article-author-info {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .article-author-name {
        font-weight: 600;
        color: var(--text-primary);
    }

    .article-author-title {
        font-size: 0.85rem;
        color: var(--text-muted);
    }

    /* Article Content */
    .article-content {
        max-width: 720px;
        margin: 0 auto;
        font-size: 1.05rem;
        line-height: 1.8;
        color: var(--text-secondary);
    }

    .article-content h2 {
        font-size: 1.5rem;
        color: var(--text-primary);
        margin: 48px 0 20px;
        padding-top: 24px;
        border-top: 1px solid var(--border);
    }

    .article-content h2:first-child {
        margin-top: 0;
        padding-top: 0;
        border-top: none;
    }

    .article-content h3 {
        font-size: 1.25rem;
        color: var(--text-primary);
        margin: 32px 0 16px;
    }

    .article-content p {
        margin-bottom: 20px;
    }

    .article-content ul, .article-content ol {
        margin-bottom: 20px;
        padding-left: 24px;
    }

    .article-content li {
        margin-bottom: 8px;
    }

    .article-content a {
        color: var(--gold);
        text-decoration: underline;
        text-underline-offset: 2px;
    }

    .article-content a:hover {
        color: var(--gold-light);
    }

    .article-content blockquote {
        border-left: 3px solid var(--gold);
        padding-left: 20px;
        margin: 24px 0;
        font-style: italic;
        color: var(--text-secondary);
    }

    .article-content code {
        background: var(--bg-card);
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.9em;
    }

    .article-content strong {
        color: var(--text-primary);
        font-weight: 600;
    }

    /* Methodology Section */
    .methodology-box {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        margin: 32px 0;
    }

    .methodology-box h3 {
        font-size: 1rem;
        color: var(--gold);
        margin-bottom: 12px;
        margin-top: 0;
        border-top: none;
        padding-top: 0;
    }

    .methodology-box p {
        font-size: 0.9rem;
        color: var(--text-muted);
        margin-bottom: 0;
    }

    /* Sources Section */
    .sources-section {
        margin: 48px 0 32px;
        padding-top: 24px;
        border-top: 1px solid var(--border);
    }

    .sources-section h3 {
        font-size: 1rem;
        color: var(--text-secondary);
        margin-bottom: 16px;
        margin-top: 0;
        padding-top: 0;
        border-top: none;
    }

    .sources-list {
        list-style: none;
        padding: 0;
    }

    .sources-list li {
        margin-bottom: 8px;
        font-size: 0.9rem;
    }

    .sources-list a {
        color: var(--gold);
    }

    /* Author Bio Box */
    .author-bio-box {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        margin: 48px 0;
        display: flex;
        gap: 20px;
        align-items: flex-start;
    }

    .author-bio-avatar {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        background: var(--teal-primary);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.75rem;
        font-weight: 600;
        color: var(--gold);
        flex-shrink: 0;
    }

    .author-bio-content h3 {
        font-size: 1.1rem;
        color: var(--text-primary);
        margin-bottom: 4px;
        margin-top: 0;
        padding-top: 0;
        border-top: none;
    }

    .author-bio-content .author-title {
        font-size: 0.85rem;
        color: var(--gold);
        margin-bottom: 12px;
    }

    .author-bio-content p {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin-bottom: 12px;
    }

    .author-bio-content .author-link {
        font-size: 0.85rem;
        color: var(--gold);
        text-decoration: none;
    }

    .author-bio-content .author-link:hover {
        color: var(--gold-light);
        text-decoration: underline;
    }

    /* Tags Section */
    .article-tags {
        margin: 32px 0;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .article-tag {
        display: inline-block;
        padding: 6px 12px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 6px;
        font-size: 0.85rem;
        color: var(--text-secondary);
        text-decoration: none;
        transition: all 0.15s;
    }

    .article-tag:hover {
        border-color: var(--teal-light);
        color: var(--text-primary);
        background: var(--bg-card-hover);
    }

    /* Related Articles */
    .related-articles {
        margin-top: 48px;
        padding-top: 32px;
        border-top: 1px solid var(--border);
    }

    .related-articles h2 {
        font-size: 1.25rem;
        margin-bottom: 24px;
        color: var(--text-primary);
        border-top: none;
        padding-top: 0;
    }

    .related-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 20px;
    }

    .related-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        text-decoration: none;
        transition: all 0.25s;
    }

    .related-card:hover {
        border-color: var(--teal-light);
        background: var(--bg-card-hover);
        transform: translateY(-2px);
    }

    .related-card-category {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--gold);
        margin-bottom: 8px;
    }

    .related-card h3 {
        font-size: 1rem;
        color: var(--text-primary);
        margin-bottom: 8px;
        line-height: 1.4;
    }

    .related-card p {
        font-size: 0.85rem;
        color: var(--text-muted);
        line-height: 1.5;
    }

    /* Tag/Category Page Styles */
    .articles-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 24px;
    }

    .article-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        text-decoration: none;
        transition: all 0.25s;
        display: flex;
        flex-direction: column;
    }

    .article-card:hover {
        border-color: var(--teal-light);
        background: var(--bg-card-hover);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }

    .article-card-category {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--gold);
        margin-bottom: 12px;
    }

    .article-card h3 {
        font-size: 1.1rem;
        color: var(--text-primary);
        margin-bottom: 12px;
        line-height: 1.4;
    }

    .article-card p {
        font-size: 0.9rem;
        color: var(--text-secondary);
        line-height: 1.6;
        flex-grow: 1;
    }

    .article-card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid var(--border-light);
        font-size: 0.8rem;
        color: var(--text-muted);
    }

    /* Tag Cloud */
    .tag-cloud {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 24px 0;
    }

    .tag-cloud a {
        padding: 8px 16px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 20px;
        font-size: 0.9rem;
        color: var(--text-secondary);
        text-decoration: none;
        transition: all 0.15s;
    }

    .tag-cloud a:hover {
        border-color: var(--gold);
        color: var(--gold);
        background: rgba(232, 168, 124, 0.1);
    }

    .tag-cloud .tag-count {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-left: 4px;
    }

    @media (max-width: 768px) {
        .author-bio-box {
            flex-direction: column;
            text-align: center;
        }

        .author-bio-avatar {
            margin: 0 auto;
        }

        .article-content {
            font-size: 1rem;
        }
    }
'''


def generate_article_page(article, author, market_data, all_articles):
    """Generate an individual article page."""
    slug = article['slug']
    title = article['title']
    description = article['description']
    category = article['category']
    tags = article.get('tags', [])
    published = article.get('published', datetime.now().strftime('%Y-%m-%d'))
    updated = article.get('updated', published)
    read_time = article.get('readTime', '5 min')
    sources = article.get('sources', [])

    # Load markdown content
    content_html = load_markdown_content(slug)
    if not content_html:
        content_html = f'<p>{description}</p><p><em>Full article content coming soon.</em></p>'

    # Get category info
    categories_data = load_articles_data().get('categories', {})
    category_info = categories_data.get(category, {'name': category.replace('-', ' ').title()})
    category_name = category_info.get('name', category)

    # Generate breadcrumbs
    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'Insights', 'url': '/insights/'},
        {'name': title, 'url': f'/insights/{slug}/'}
    ]
    breadcrumb_html = ' / '.join([
        f'<a href="{b["url"]}">{b["name"]}</a>' if i < len(breadcrumbs) - 1 else b['name']
        for i, b in enumerate(breadcrumbs)
    ])

    # Generate schemas
    article_schema = generate_article_schema(article, author)
    breadcrumb_schema = generate_breadcrumb_schema(breadcrumbs)

    # Generate FAQs
    faqs = generate_article_faqs(article, market_data)
    # Add custom FAQs from article if present
    if article.get('faqs'):
        faqs.extend(article['faqs'])
    faq_html = generate_faq_html(faqs) if faqs else ''

    # Author initials for avatar
    author_initials = ''.join([n[0].upper() for n in author.get('name', 'RT').split()[:2]])

    # Tags HTML
    tags_html = ''
    if tags:
        tag_links = [f'<a href="/insights/tags/{t}/" class="article-tag">{t.replace("-", " ").title()}</a>' for t in tags]
        tags_html = f'<div class="article-tags">{" ".join(tag_links)}</div>'

    # Sources HTML
    sources_html = ''
    if sources:
        source_items = []
        for src in sources:
            if src.get('url'):
                source_items.append(f'<li><a href="{src["url"]}" target="_blank" rel="noopener">{src["name"]}</a></li>')
            else:
                source_items.append(f'<li>{src["name"]}</li>')
        sources_html = f'''
        <div class="sources-section">
            <h3>Sources</h3>
            <ul class="sources-list">
                {"".join(source_items)}
            </ul>
        </div>
        '''

    # Methodology box for data-heavy articles
    methodology_html = ''
    if category in ['salary-intel', 'hiring-trends'] or any(t in tags for t in ['salary', 'data', 'market']):
        total_jobs = market_data.get('total_jobs', 1969)
        methodology_html = f'''
        <div class="methodology-box">
            <h3>About This Data</h3>
            <p>Analysis based on {total_jobs:,} AI job postings tracked by AI Market Pulse.
               Our database is updated weekly and includes roles from major job boards and company career pages.
               Salary data reflects disclosed compensation ranges only.</p>
        </div>
        '''

    # Related articles
    related_html = ''
    related = [a for a in all_articles if a['slug'] != slug][:4]
    if related:
        related_cards = []
        for r in related:
            r_cat = categories_data.get(r['category'], {}).get('name', r['category'])
            related_cards.append(f'''
            <a href="/insights/{r['slug']}/" class="related-card">
                <div class="related-card-category">{r_cat}</div>
                <h3>{r['title']}</h3>
                <p>{r['description'][:100]}...</p>
            </a>
            ''')
        related_html = f'''
        <div class="related-articles">
            <h2>Related Insights</h2>
            <div class="related-grid">
                {"".join(related_cards)}
            </div>
        </div>
        '''

    # Build page
    html = f'''{get_html_head(
        title,
        description,
        f"insights/{slug}/",
        extra_head=f'<style>{CSS_ARTICLE}{CSS_FAQ_SECTION}</style>'
    )}
    {article_schema}
    {breadcrumb_schema}
    {get_nav_html('insights')}

    <div class="page-header">
        <div class="container">
            <div class="breadcrumb">{breadcrumb_html}</div>
            <div class="article-header">
                <div class="article-meta">
                    <a href="/insights/category/{category}/" class="article-category">{category_name}</a>
                    <span class="article-date">{published}</span>
                    <span class="article-read-time">{read_time} read</span>
                </div>
                <h1>{title}</h1>
                <div class="article-author-byline">
                    <div class="article-author-avatar">{author_initials}</div>
                    <div class="article-author-info">
                        <span class="article-author-name">{author.get('name', 'Rome Thorndike')}</span>
                        <span class="article-author-title">{author.get('title', 'Founder')}, {SITE_NAME}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <main>
        <div class="container">
            <article class="article-content">
                {content_html}

                {methodology_html}

                {tags_html}

                {sources_html}
            </article>

            {faq_html}

            <div class="author-bio-box">
                <div class="author-bio-avatar">{author_initials}</div>
                <div class="author-bio-content">
                    <h3>About the Author</h3>
                    <div class="author-title">{author.get('title', 'Founder')}, {SITE_NAME}</div>
                    <p>{author.get('bio', '')}</p>
                    <a href="{author.get('linkedin', '#')}" target="_blank" rel="noopener" class="author-link">
                        Connect on LinkedIn →
                    </a>
                </div>
            </div>

            {related_html}

            {get_cta_box(
                title="Get Weekly AI Career Insights",
                description="Join our newsletter for AI job market trends, salary data, and career guidance.",
                button_text="Subscribe Free",
                button_url="https://ainewsdigest.substack.com"
            )}
        </div>
    </main>

    {get_footer_html()}'''

    # Write file
    article_dir = os.path.join(INSIGHTS_DIR, slug)
    os.makedirs(article_dir, exist_ok=True)
    with open(os.path.join(article_dir, 'index.html'), 'w') as f:
        f.write(html)

    return True


def generate_tag_page(tag, articles, categories_data):
    """Generate a tag landing page."""
    tag_display = tag.replace('-', ' ').title()
    article_count = len(articles)

    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'Insights', 'url': '/insights/'},
        {'name': f'Tag: {tag_display}', 'url': f'/insights/tags/{tag}/'}
    ]
    breadcrumb_html = ' / '.join([
        f'<a href="{b["url"]}">{b["name"]}</a>' if i < len(breadcrumbs) - 1 else b['name']
        for i, b in enumerate(breadcrumbs)
    ])
    breadcrumb_schema = generate_breadcrumb_schema(breadcrumbs)

    # Article cards
    article_cards = []
    for a in articles:
        cat_name = categories_data.get(a['category'], {}).get('name', a['category'])
        article_cards.append(f'''
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

    html = f'''{get_html_head(
        f"{tag_display} - AI Career Insights",
        f"Articles about {tag_display.lower()} in AI careers. {article_count} insights on jobs, salaries, and skills.",
        f"insights/tags/{tag}/",
        extra_head=f'<style>{CSS_ARTICLE}</style>'
    )}
    {breadcrumb_schema}
    {get_nav_html('insights')}

    <div class="page-header">
        <div class="container">
            <div class="breadcrumb">{breadcrumb_html}</div>
            <h1>Articles tagged "{tag_display}"</h1>
            <p class="lead">{article_count} article{"s" if article_count != 1 else ""} about {tag_display.lower()}</p>
        </div>
    </div>

    <main>
        <div class="container">
            <div class="articles-grid">
                {"".join(article_cards)}
            </div>

            {get_cta_box(
                title="Get Weekly AI Career Insights",
                description="Join our newsletter for AI job market trends, salary data, and career guidance.",
                button_text="Subscribe Free",
                button_url="https://ainewsdigest.substack.com"
            )}
        </div>
    </main>

    {get_footer_html()}'''

    # Write file
    tag_dir = os.path.join(INSIGHTS_DIR, 'tags', tag)
    os.makedirs(tag_dir, exist_ok=True)
    with open(os.path.join(tag_dir, 'index.html'), 'w') as f:
        f.write(html)


def generate_category_page(category, category_info, articles, all_categories):
    """Generate a category landing page."""
    category_name = category_info.get('name', category.replace('-', ' ').title())
    category_desc = category_info.get('description', '')
    article_count = len(articles)

    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'Insights', 'url': '/insights/'},
        {'name': category_name, 'url': f'/insights/category/{category}/'}
    ]
    breadcrumb_html = ' / '.join([
        f'<a href="{b["url"]}">{b["name"]}</a>' if i < len(breadcrumbs) - 1 else b['name']
        for i, b in enumerate(breadcrumbs)
    ])
    breadcrumb_schema = generate_breadcrumb_schema(breadcrumbs)

    # Article cards
    article_cards = []
    for a in articles:
        article_cards.append(f'''
        <a href="/insights/{a['slug']}/" class="article-card">
            <h3>{a['title']}</h3>
            <p>{a['description']}</p>
            <div class="article-card-footer">
                <span>{a.get('published', '')}</span>
                <span>{a.get('readTime', '5 min')} read</span>
            </div>
        </a>
        ''')

    # Other categories
    other_cats = []
    for cat_slug, cat_info in all_categories.items():
        if cat_slug != category:
            other_cats.append(f'<a href="/insights/category/{cat_slug}/">{cat_info.get("name", cat_slug)}</a>')
    other_cats_html = ' · '.join(other_cats) if other_cats else ''

    html = f'''{get_html_head(
        f"{category_name} - AI Market Pulse",
        category_desc or f"AI career {category_name.lower()}. {article_count} insights on the AI job market.",
        f"insights/category/{category}/",
        extra_head=f'<style>{CSS_ARTICLE}</style>'
    )}
    {breadcrumb_schema}
    {get_nav_html('insights')}

    <div class="page-header">
        <div class="container">
            <div class="breadcrumb">{breadcrumb_html}</div>
            <h1>{category_name}</h1>
            <p class="lead">{category_desc}</p>
        </div>
    </div>

    <main>
        <div class="container">
            <p style="color: var(--text-muted); margin-bottom: 32px;">
                {article_count} article{"s" if article_count != 1 else ""} in this category
            </p>

            <div class="articles-grid">
                {"".join(article_cards) if article_cards else '<p style="color: var(--text-muted);">No articles yet. Check back soon!</p>'}
            </div>

            {f'<div style="margin-top: 48px; padding-top: 32px; border-top: 1px solid var(--border);"><h3 style="margin-bottom: 16px; color: var(--text-secondary);">Browse Other Categories</h3><p style="color: var(--text-muted);">{other_cats_html}</p></div>' if other_cats_html else ''}

            {get_cta_box(
                title="Get Weekly AI Career Insights",
                description="Join our newsletter for AI job market trends, salary data, and career guidance.",
                button_text="Subscribe Free",
                button_url="https://ainewsdigest.substack.com"
            )}
        </div>
    </main>

    {get_footer_html()}'''

    # Write file
    cat_dir = os.path.join(INSIGHTS_DIR, 'category', category)
    os.makedirs(cat_dir, exist_ok=True)
    with open(os.path.join(cat_dir, 'index.html'), 'w') as f:
        f.write(html)


def main():
    """Main generation function."""
    # Load data
    data = load_articles_data()
    articles = data.get('articles', [])
    categories = data.get('categories', {})
    author = data.get('author', {})
    market_data = load_market_data()

    print(f"\n  Loaded {len(articles)} articles")
    print(f"  Loaded {len(categories)} categories")

    # Create directories
    os.makedirs(INSIGHTS_DIR, exist_ok=True)
    os.makedirs(os.path.join(INSIGHTS_DIR, 'tags'), exist_ok=True)
    os.makedirs(os.path.join(INSIGHTS_DIR, 'category'), exist_ok=True)

    # Generate individual article pages
    article_count = 0
    for article in articles:
        if generate_article_page(article, author, market_data, articles):
            article_count += 1
            print(f"    Generated: /insights/{article['slug']}/")

    # Build tag index
    tag_index = {}
    for article in articles:
        for tag in article.get('tags', []):
            if tag not in tag_index:
                tag_index[tag] = []
            tag_index[tag].append(article)

    # Generate tag pages
    tag_count = 0
    for tag, tag_articles in tag_index.items():
        generate_tag_page(tag, tag_articles, categories)
        tag_count += 1
        print(f"    Generated: /insights/tags/{tag}/")

    # Generate category pages
    cat_count = 0
    for category, category_info in categories.items():
        cat_articles = [a for a in articles if a.get('category') == category]
        generate_category_page(category, category_info, cat_articles, categories)
        cat_count += 1
        print(f"    Generated: /insights/category/{category}/")

    print(f"\n  Generated {article_count} article pages")
    print(f"  Generated {tag_count} tag pages")
    print(f"  Generated {cat_count} category pages")
    print("=" * 70)


if __name__ == '__main__':
    main()
