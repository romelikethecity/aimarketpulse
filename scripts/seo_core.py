#!/usr/bin/env python3
"""
SEO Core Module for AI Market Pulse

Centralized SEO logic including:
- Schema.org JSON-LD generators (JobPosting, FAQPage, BreadcrumbList, Dataset, SoftwareApplication)
- FAQ content generators with data-driven answers
- Internal linking engine for AI tools and companies
- Content enrichment and validation utilities
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Optional, Any

# Site configuration
SITE_URL = "https://theaimarketpulse.com"
SITE_NAME = "AI Market Pulse"


# =============================================================================
# SCHEMA.ORG GENERATORS
# =============================================================================

def generate_breadcrumb_schema(breadcrumbs: List[Dict[str, str]]) -> str:
    """
    Generate BreadcrumbList schema markup.

    Args:
        breadcrumbs: List of dicts with 'name' and 'url' keys
        Example: [{'name': 'Home', 'url': '/'}, {'name': 'Jobs', 'url': '/jobs/'}]

    Returns:
        JSON-LD script tag
    """
    items = []
    for i, crumb in enumerate(breadcrumbs, 1):
        items.append({
            "@type": "ListItem",
            "position": i,
            "name": crumb['name'],
            "item": f"{SITE_URL}{crumb['url']}"
        })

    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }

    return f'<script type="application/ld+json">{json.dumps(schema, indent=2)}</script>'


def generate_faq_schema(faqs: List[Dict[str, str]]) -> str:
    """
    Generate FAQPage schema markup.

    Args:
        faqs: List of dicts with 'question' and 'answer' keys

    Returns:
        JSON-LD script tag or empty string if no FAQs
    """
    if not faqs:
        return ''

    main_entity = []
    for faq in faqs:
        main_entity.append({
            "@type": "Question",
            "name": faq['question'],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": faq['answer']
            }
        })

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": main_entity
    }

    return f'<script type="application/ld+json">{json.dumps(schema, indent=2)}</script>'


def generate_dataset_schema(title: str, description: str, record_count: int, url: str,
                            keywords: List[str] = None, date_modified: str = None) -> str:
    """
    Generate Dataset schema for salary/market data pages.

    Args:
        title: Dataset name
        description: Dataset description
        record_count: Number of records
        url: Page URL (relative path)
        keywords: Optional list of keywords
        date_modified: Optional date string (YYYY-MM-DD)

    Returns:
        JSON-LD script tag
    """
    if date_modified is None:
        date_modified = datetime.now().strftime('%Y-%m-%d')

    if keywords is None:
        keywords = ["AI jobs", "prompt engineer salary", "AI salary", "ML engineer compensation"]

    schema = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": title,
        "description": description,
        "url": f"{SITE_URL}{url}",
        "keywords": keywords,
        "creator": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": SITE_URL
        },
        "dateModified": date_modified,
        "temporalCoverage": str(datetime.now().year),
        "spatialCoverage": "United States"
    }

    return f'<script type="application/ld+json">{json.dumps(schema, indent=2)}</script>'


def generate_software_schema(tool: Dict[str, Any]) -> str:
    """
    Generate SoftwareApplication schema for AI tool pages.

    Args:
        tool: Dict with name, slug, description, pricing, category

    Returns:
        JSON-LD script tag
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": tool.get('name'),
        "description": tool.get('description', tool.get('tagline', '')),
        "applicationCategory": tool.get('category', 'DeveloperApplication'),
        "operatingSystem": "Web, macOS, Windows, Linux",
        "url": f"{SITE_URL}/tools/{tool.get('slug')}/"
    }

    if tool.get('pricing'):
        schema["offers"] = {
            "@type": "Offer",
            "description": tool['pricing']
        }

    return f'<script type="application/ld+json">{json.dumps(schema, indent=2)}</script>'


def generate_organization_schema() -> str:
    """Generate Organization schema for the site."""
    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": SITE_NAME,
        "url": SITE_URL,
        "logo": f"{SITE_URL}/assets/logo.jpeg",
        "description": "AI jobs, salary benchmarks, and market intelligence for AI professionals",
        "sameAs": [
            "https://twitter.com/pe_collective",
            "https://ainewsdigest.substack.com"
        ]
    }
    return f'<script type="application/ld+json">{json.dumps(schema, indent=2)}</script>'


# =============================================================================
# FAQ CONTENT GENERATORS (Data-driven)
# =============================================================================

def generate_salary_faqs(role_title: str, location: str = None, category: str = None,
                         avg_min: float = None, avg_max: float = None,
                         sample_count: int = None, comparison_data: Dict = None) -> List[Dict[str, str]]:
    """
    Generate substantive FAQ content for AI salary pages based on actual data.

    Args:
        role_title: Job role (e.g., "Prompt Engineer", "AI Engineer")
        location: Optional location filter
        category: Optional category (e.g., "Remote", "Senior")
        avg_min: Average minimum salary
        avg_max: Average maximum salary
        sample_count: Number of job postings analyzed
        comparison_data: Dict with comparison metrics (national_avg, etc.)

    Returns:
        List of FAQ dicts with 'question' and 'answer' keys
    """
    faqs = []

    def fmt_salary(amount):
        return f"${int(amount/1000)}K" if amount else "N/A"

    # Base salary question
    if avg_min and avg_max:
        range_spread = ((avg_max - avg_min) / avg_min) * 100 if avg_min > 0 else 0

        if location:
            faqs.append({
                "question": f"What is the average {role_title} salary in {location}?",
                "answer": f"Based on {sample_count or 'our'} job postings with disclosed compensation, {role_title} roles in {location} pay between {fmt_salary(avg_min)} and {fmt_salary(avg_max)} base salary. This {int(range_spread)}% spread reflects differences in company stage, required skills, and specific responsibilities."
            })
        elif category:
            faqs.append({
                "question": f"What do {category} {role_title} roles pay?",
                "answer": f"{category} {role_title} positions pay between {fmt_salary(avg_min)} and {fmt_salary(avg_max)} based on {sample_count or 'analyzed'} job postings with disclosed compensation."
            })
        else:
            faqs.append({
                "question": f"What is the average {role_title} salary in 2026?",
                "answer": f"The average {role_title} salary ranges from {fmt_salary(avg_min)} to {fmt_salary(avg_max)} base, based on {sample_count or 'analyzed'} job postings with disclosed compensation. Actual offers depend on experience, skills (especially with specific LLM frameworks), and company stage."
            })

        # Why such a wide range?
        if range_spread > 30:
            faqs.append({
                "question": f"Why is the {role_title} salary range so wide?",
                "answer": f"The {int(range_spread)}% salary spread reflects real market variation. Key factors include: (1) Company stage - startups often pay less base but offer equity; (2) Specific skills - expertise in LangChain, RAG, or fine-tuning commands premiums; (3) Industry - fintech and healthtech AI roles pay 15-25% above average; (4) Scope - building production systems vs research roles have different compensation."
            })

    # Location comparison
    if location and comparison_data:
        national_avg = comparison_data.get('national_avg_max')
        if national_avg and avg_max:
            diff_pct = ((avg_max - national_avg) / national_avg) * 100
            direction = "above" if diff_pct > 0 else "below"

            col_note = ""
            if location in ['San Francisco', 'New York']:
                col_note = f" Keep in mind that cost of living in {location} is 40-60% higher than the national average."
            elif location == 'Remote':
                col_note = " Some companies use geographic pay bands, adjusting remote salaries based on candidate location."

            faqs.append({
                "question": f"How do {location} {role_title} salaries compare nationally?",
                "answer": f"{location} {role_title} salaries average {fmt_salary(avg_max)}, which is {abs(int(diff_pct))}% {direction} the national average of {fmt_salary(national_avg)}.{col_note}"
            })

    # Required skills question
    faqs.append({
        "question": f"What skills increase {role_title} salary?",
        "answer": f"Skills that command higher {role_title} salaries include: LangChain/LlamaIndex expertise (+10-15%), production RAG systems experience (+15-20%), fine-tuning experience (+10-20%), MLOps/deployment skills (+10-15%), and domain expertise in high-paying industries like finance or healthcare. Multiple LLM platform experience (OpenAI + Claude + open-source) also adds value."
    })

    # Data accuracy
    if sample_count:
        faqs.append({
            "question": "How accurate is this AI salary data?",
            "answer": f"Our data comes from {sample_count} actual job postings with disclosed compensation ranges, not self-reported surveys. We track AI, ML, and prompt engineering roles weekly. Limitations: not all companies disclose salary ranges, and posted ranges may differ from final negotiated offers."
        })

    return faqs


def generate_tool_faqs(tool_name: str, category: str, pricing: str = None,
                       pros: List[str] = None, cons: List[str] = None,
                       best_for: str = None, alternatives: List[str] = None) -> List[Dict[str, str]]:
    """
    Generate FAQ content for AI tool pages.

    Args:
        tool_name: Name of the tool
        category: Tool category
        pricing: Pricing description
        pros: List of advantages
        cons: List of disadvantages
        best_for: Description of ideal use case
        alternatives: List of alternative tool names

    Returns:
        List of FAQ dicts
    """
    faqs = []

    if pricing:
        faqs.append({
            "question": f"How much does {tool_name} cost?",
            "answer": f"{tool_name} pricing: {pricing}. Most {category} tools offer free tiers for individual developers and team pricing for organizations. Compare pricing carefully based on your expected usage."
        })

    if best_for:
        faqs.append({
            "question": f"Is {tool_name} right for my project?",
            "answer": f"{tool_name} is best for: {best_for}. Consider your team's experience level, project requirements, and integration needs when evaluating."
        })

    if alternatives and len(alternatives) > 0:
        alt_list = ", ".join(alternatives[:4])
        faqs.append({
            "question": f"What are the best {tool_name} alternatives?",
            "answer": f"Top {tool_name} alternatives include: {alt_list}. The best choice depends on your specific needs - some prioritize features, others focus on pricing, ease of use, or specific integrations."
        })

    if pros and cons:
        pros_text = "; ".join(pros[:3])
        cons_text = "; ".join(cons[:3])
        faqs.append({
            "question": f"What are the pros and cons of {tool_name}?",
            "answer": f"Pros: {pros_text}. Cons: {cons_text}. Every tool has tradeoffs - evaluate based on your team's workflow and project requirements."
        })

    return faqs


# =============================================================================
# INTERNAL LINKING ENGINE
# =============================================================================

# AI tools to auto-link
AI_TOOLS_LINKS = {
    'langchain': '/tools/langchain/',
    'llamaindex': '/tools/llamaindex/',
    'openai': '/tools/openai-api/',
    'gpt-4': '/tools/openai-api/',
    'gpt-4o': '/tools/openai-api/',
    'claude': '/tools/anthropic-claude/',
    'anthropic': '/tools/anthropic-claude/',
    'pinecone': '/tools/pinecone/',
    'weaviate': '/tools/weaviate/',
    'chroma': '/tools/chromadb/',
    'hugging face': '/tools/hugging-face/',
    'huggingface': '/tools/hugging-face/',
    'cursor': '/tools/cursor/',
    'github copilot': '/tools/github-copilot/',
    'copilot': '/tools/github-copilot/',
    'mlflow': '/tools/mlflow/',
    'weights & biases': '/tools/weights-biases/',
    'wandb': '/tools/weights-biases/',
}

# Salary page links
SALARY_LINKS = {
    'prompt engineer': '/salaries/prompt-engineer/',
    'ai engineer': '/salaries/ai-engineer/',
    'ml engineer': '/salaries/ml-engineer/',
    'machine learning engineer': '/salaries/ml-engineer/',
    'data scientist': '/salaries/data-scientist/',
}


def auto_link_content(text: str, exclude_links: List[str] = None, max_links: int = 5) -> str:
    """
    Automatically add internal links to AI tools and salary pages mentioned in text.

    Args:
        text: HTML content to process
        exclude_links: List of URLs to exclude (e.g., the current page)
        max_links: Maximum number of links to add

    Returns:
        Text with auto-linked terms
    """
    if exclude_links is None:
        exclude_links = []

    links_added = 0

    # Combine all link mappings
    all_links = {**AI_TOOLS_LINKS, **SALARY_LINKS}

    for term, url in all_links.items():
        if links_added >= max_links:
            break
        if url in exclude_links:
            continue

        # Case-insensitive search, but only replace if not already in a link
        pattern = rf'(?<![">])(?<!/)\b({re.escape(term)})\b(?![^<]*</a>)'

        if re.search(pattern, text, re.IGNORECASE):
            # Only link first occurrence
            replacement = rf'<a href="{url}">\1</a>'
            text = re.sub(pattern, replacement, text, count=1, flags=re.IGNORECASE)
            links_added += 1

    return text


def get_related_pages(current_page: Dict[str, Any], all_pages: List[Dict[str, Any]],
                      max_links: int = 6) -> List[Dict[str, str]]:
    """
    Generate related page suggestions for internal linking.

    Args:
        current_page: Dict with current page info (type, slug, category, etc.)
        all_pages: List of all pages
        max_links: Maximum related pages to return

    Returns:
        List of dicts with 'title', 'url', and 'context' keys
    """
    related = []
    current_type = current_page.get('type')
    current_slug = current_page.get('slug')

    # Always include parent section
    type_map = {
        'salary': {'title': 'All Salary Data', 'url': '/salaries/'},
        'job': {'title': 'All AI Jobs', 'url': '/jobs/'},
        'tool': {'title': 'All AI Tools', 'url': '/tools/'},
        'company': {'title': 'All Companies', 'url': '/companies/'},
    }

    if current_type in type_map:
        related.append({
            'title': type_map[current_type]['title'],
            'url': type_map[current_type]['url'],
            'context': 'Browse all'
        })

    # Find similar pages (same type, different slug)
    siblings = [p for p in all_pages if p.get('type') == current_type and p.get('slug') != current_slug]

    # Sort by relevance (could be job count, salary, etc.)
    siblings.sort(key=lambda x: x.get('count', x.get('avg_max', 0)), reverse=True)

    for sib in siblings[:3]:
        url_prefix = type_map.get(current_type, {}).get('url', '/')
        related.append({
            'title': sib.get('title', sib.get('name', '')),
            'url': f"{url_prefix}{sib.get('slug')}/",
            'context': f"{sib.get('count', 0)} roles" if sib.get('count') else ''
        })

    # Cross-link to other sections
    if current_type != 'job':
        related.append({
            'title': 'Browse AI Jobs',
            'url': '/jobs/',
            'context': 'Latest openings'
        })
    if current_type != 'salary':
        related.append({
            'title': 'Salary Benchmarks',
            'url': '/salaries/',
            'context': 'Compensation data'
        })

    return related[:max_links]


# =============================================================================
# CONTENT VALIDATION
# =============================================================================

# Quality thresholds
MIN_WORD_COUNT = 250
MIN_FAQ_COUNT = 2
MAX_TITLE_LENGTH = 70
MIN_TITLE_LENGTH = 20
MAX_DESCRIPTION_LENGTH = 160
MIN_DESCRIPTION_LENGTH = 50


def validate_page_content(page_data: Dict[str, Any], all_pages: List[Dict[str, Any]] = None) -> List[str]:
    """
    Validate page meets quality thresholds for programmatic SEO.

    Args:
        page_data: Dict containing title, content/html, faqs, description, slug
        all_pages: Optional list of all pages for uniqueness checking

    Returns:
        List of validation issues (empty list if valid)
    """
    issues = []

    # 1. Word count check
    content = page_data.get('content', '') or page_data.get('html', '')
    # Strip HTML tags for word count
    text_only = re.sub(r'<[^>]+>', ' ', content)
    text_only = re.sub(r'\s+', ' ', text_only).strip()
    word_count = len(text_only.split())

    if word_count < MIN_WORD_COUNT:
        issues.append(f"Thin content: {word_count} words (minimum: {MIN_WORD_COUNT})")

    # 2. FAQ count check
    faqs = page_data.get('faqs', [])
    faq_count = len(faqs) if faqs else 0
    if faq_count < MIN_FAQ_COUNT:
        issues.append(f"Low FAQ count: {faq_count} (minimum: {MIN_FAQ_COUNT})")

    # 3. Title validation
    title = page_data.get('title', '')
    if not title:
        issues.append("Missing title")
    elif len(title) > MAX_TITLE_LENGTH:
        issues.append(f"Title too long: {len(title)} chars (max: {MAX_TITLE_LENGTH})")
    elif len(title) < MIN_TITLE_LENGTH:
        issues.append(f"Title too short: {len(title)} chars (min: {MIN_TITLE_LENGTH})")

    # 4. Description validation
    description = page_data.get('description', '')
    if not description:
        issues.append("Missing meta description")
    elif len(description) > MAX_DESCRIPTION_LENGTH:
        issues.append(f"Description too long: {len(description)} chars (max: {MAX_DESCRIPTION_LENGTH})")
    elif len(description) < MIN_DESCRIPTION_LENGTH:
        issues.append(f"Description too short: {len(description)} chars (min: {MIN_DESCRIPTION_LENGTH})")

    # 5. Title uniqueness check
    if all_pages:
        existing_titles = [p.get('title') for p in all_pages if p.get('title') != title]
        if title in existing_titles:
            issues.append(f"Duplicate title: {title}")

    # 6. Slug/URL present
    if not page_data.get('slug') and not page_data.get('url'):
        issues.append("Missing slug/URL")

    return issues


def validate_all_pages(pages: List[Dict[str, Any]], strict: bool = False) -> Dict[str, Any]:
    """
    Validate all pages and return summary report.

    Args:
        pages: List of page data dicts
        strict: If True, raise exception on any issues

    Returns:
        Dict with validation summary and issues by page
    """
    results = {
        'total_pages': len(pages),
        'valid_pages': 0,
        'pages_with_issues': 0,
        'issues_by_page': {},
        'issue_summary': {}
    }

    for page in pages:
        slug = page.get('slug', page.get('url', 'unknown'))
        issues = validate_page_content(page, pages)

        if issues:
            results['pages_with_issues'] += 1
            results['issues_by_page'][slug] = issues

            # Track issue types
            for issue in issues:
                issue_type = issue.split(':')[0]
                results['issue_summary'][issue_type] = results['issue_summary'].get(issue_type, 0) + 1
        else:
            results['valid_pages'] += 1

    if strict and results['pages_with_issues'] > 0:
        raise ValueError(f"Validation failed: {results['pages_with_issues']} pages have issues")

    return results


# =============================================================================
# FAQ HTML GENERATOR
# =============================================================================

CSS_FAQ_SECTION = '''
    .faq-section {
        margin: 48px 0;
    }

    .faq-section h2 {
        font-size: 1.5rem;
        margin-bottom: 24px;
        color: var(--text-primary);
    }

    .faq-item {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        margin-bottom: 16px;
        overflow: hidden;
    }

    .faq-question {
        width: 100%;
        padding: 20px 24px;
        background: transparent;
        border: none;
        text-align: left;
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: background 0.2s;
    }

    .faq-question:hover {
        background: var(--bg-card-hover);
    }

    .faq-icon {
        font-size: 1.25rem;
        color: var(--gold);
        transition: transform 0.3s;
    }

    .faq-item.active .faq-icon {
        transform: rotate(45deg);
    }

    .faq-answer {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease;
    }

    .faq-item.active .faq-answer {
        max-height: 500px;
    }

    .faq-answer-content {
        padding: 0 24px 20px;
        color: var(--text-secondary);
        line-height: 1.7;
    }
'''


def generate_faq_html(faqs: List[Dict[str, str]], section_title: str = "Frequently Asked Questions") -> str:
    """
    Generate expandable FAQ HTML with schema markup.

    Args:
        faqs: List of FAQ dicts with 'question' and 'answer' keys
        section_title: Optional section heading

    Returns:
        HTML string with FAQ section and embedded schema
    """
    if not faqs:
        return ''

    schema = generate_faq_schema(faqs)

    faq_items = []
    for faq in faqs:
        faq_items.append(f'''
        <div class="faq-item">
            <button class="faq-question" onclick="this.parentElement.classList.toggle('active')">
                <span>{faq['question']}</span>
                <span class="faq-icon">+</span>
            </button>
            <div class="faq-answer">
                <div class="faq-answer-content">{faq['answer']}</div>
            </div>
        </div>
        ''')

    return f'''
    {schema}
    <section class="faq-section">
        <h2>{section_title}</h2>
        {''.join(faq_items)}
    </section>
    '''


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def generate_meta_tags(title: str, description: str, url: str,
                       image_url: str = None, article_type: str = "website") -> str:
    """
    Generate comprehensive meta tags for a page.

    Args:
        title: Page title
        description: Meta description
        url: Page URL (relative path)
        image_url: Optional social image URL
        article_type: Open Graph type (website, article, etc.)

    Returns:
        HTML meta tags string
    """
    if image_url is None:
        image_url = f"{SITE_URL}/assets/social-preview.png"
    elif not image_url.startswith('http'):
        image_url = f"{SITE_URL}{image_url}"

    full_url = f"{SITE_URL}{url}"

    return f'''
    <meta name="description" content="{description}">
    <link rel="canonical" href="{full_url}">

    <!-- Open Graph -->
    <meta property="og:type" content="{article_type}">
    <meta property="og:url" content="{full_url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:site_name" content="{SITE_NAME}">
    <meta property="og:image" content="{image_url}">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@pe_collective">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{image_url}">
    '''


def get_page_last_modified(file_path: str = None) -> str:
    """Get last modified date for sitemap."""
    if file_path:
        try:
            import os
            mtime = os.path.getmtime(file_path)
            return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        except:
            pass
    return datetime.now().strftime('%Y-%m-%d')
