#!/usr/bin/env python3
"""
SEO Content Validation Script

Scans generated pages to identify thin content and SEO issues
that could cause Google to flag the site for spamming.

Usage:
    python scripts/validate_seo.py [--fix]
"""

import os
import re
import sys
import glob
from collections import defaultdict
from bs4 import BeautifulSoup

# Add scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

SITE_DIR = 'site'

# Validation thresholds
MIN_WORD_COUNT = 250
MIN_TITLE_LENGTH = 20
MAX_TITLE_LENGTH = 70
MIN_DESCRIPTION_LENGTH = 50
MAX_DESCRIPTION_LENGTH = 160

# Pages that should have noindex if thin
THIN_CONTENT_THRESHOLD = 150  # words


def extract_page_data(html_path):
    """Extract SEO-relevant data from an HTML file"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')

        # Get title
        title_tag = soup.find('title')
        title = title_tag.get_text() if title_tag else ''

        # Get meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        description = desc_tag.get('content', '') if desc_tag else ''

        # Get canonical
        canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
        canonical = canonical_tag.get('href', '') if canonical_tag else ''

        # Check for noindex
        robots_tag = soup.find('meta', attrs={'name': 'robots'})
        is_noindex = robots_tag and 'noindex' in robots_tag.get('content', '').lower() if robots_tag else False

        # Count JSON-LD schemas
        schemas = soup.find_all('script', attrs={'type': 'application/ld+json'})
        schema_count = len(schemas)
        schema_types = []
        for s in schemas:
            try:
                import json
                data = json.loads(s.string)
                if isinstance(data, dict):
                    if '@type' in data:
                        schema_types.append(data['@type'])
                    elif '@graph' in data:
                        for item in data['@graph']:
                            if '@type' in item:
                                schema_types.append(item['@type'])
            except:
                pass

        # Get main content word count (excluding nav, footer, scripts, styles)
        for tag in soup.find_all(['nav', 'footer', 'script', 'style', 'head']):
            tag.decompose()

        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        word_count = len(text.split())

        # Check for OG tags
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        has_og_tags = bool(og_title and og_desc)

        # Check for Twitter cards
        tw_card = soup.find('meta', attrs={'name': 'twitter:card'})
        has_twitter_card = bool(tw_card)

        return {
            'path': html_path,
            'title': title,
            'title_length': len(title),
            'description': description,
            'description_length': len(description),
            'canonical': canonical,
            'word_count': word_count,
            'schema_count': schema_count,
            'schema_types': schema_types,
            'is_noindex': is_noindex,
            'has_og_tags': has_og_tags,
            'has_twitter_card': has_twitter_card,
        }
    except Exception as e:
        return {'path': html_path, 'error': str(e)}


def validate_page(page_data):
    """Validate a single page and return issues"""
    issues = []
    warnings = []

    if 'error' in page_data:
        issues.append(f"Parse error: {page_data['error']}")
        return issues, warnings

    path = page_data['path']

    # Skip validation for noindexed pages (they're already protected)
    if page_data['is_noindex']:
        return issues, warnings

    # 1. Thin content check
    if page_data['word_count'] < MIN_WORD_COUNT:
        severity = 'CRITICAL' if page_data['word_count'] < THIN_CONTENT_THRESHOLD else 'WARNING'
        issues.append(f"[{severity}] Thin content: {page_data['word_count']} words (minimum: {MIN_WORD_COUNT})")

    # 2. Title validation
    if not page_data['title']:
        issues.append("[CRITICAL] Missing title tag")
    elif page_data['title_length'] > MAX_TITLE_LENGTH:
        warnings.append(f"Title too long: {page_data['title_length']} chars (max: {MAX_TITLE_LENGTH})")
    elif page_data['title_length'] < MIN_TITLE_LENGTH:
        warnings.append(f"Title too short: {page_data['title_length']} chars (min: {MIN_TITLE_LENGTH})")

    # 3. Description validation
    if not page_data['description']:
        issues.append("[CRITICAL] Missing meta description")
    elif page_data['description_length'] > MAX_DESCRIPTION_LENGTH:
        warnings.append(f"Description too long: {page_data['description_length']} chars")
    elif page_data['description_length'] < MIN_DESCRIPTION_LENGTH:
        warnings.append(f"Description too short: {page_data['description_length']} chars")

    # 4. Canonical URL check
    if not page_data['canonical']:
        issues.append("[CRITICAL] Missing canonical URL")

    # 5. Schema markup check
    if page_data['schema_count'] == 0:
        warnings.append("No JSON-LD schema markup found")

    # 6. Social meta tags check
    if not page_data['has_og_tags']:
        warnings.append("Missing Open Graph tags")
    if not page_data['has_twitter_card']:
        warnings.append("Missing Twitter Card tags")

    return issues, warnings


def scan_directory(directory, pattern='**/index.html'):
    """Scan a directory for HTML files and validate them"""
    html_files = glob.glob(os.path.join(directory, pattern), recursive=True)
    return html_files


def main():
    print("=" * 70)
    print("  AI MARKET PULSE - SEO VALIDATION REPORT")
    print("=" * 70)

    # Track results
    results = {
        'total': 0,
        'valid': 0,
        'with_issues': 0,
        'with_warnings': 0,
        'noindexed': 0,
        'issues_by_type': defaultdict(int),
        'thin_pages': [],
        'critical_issues': [],
    }

    # Scan different page types
    page_types = [
        ('Jobs', f'{SITE_DIR}/jobs'),
        ('Companies', f'{SITE_DIR}/companies'),
        ('Salaries', f'{SITE_DIR}/salaries'),
        ('Tools', f'{SITE_DIR}/tools'),
        ('Insights', f'{SITE_DIR}/insights'),
    ]

    for page_type, directory in page_types:
        if not os.path.exists(directory):
            print(f"\n  Skipping {page_type} (directory not found: {directory})")
            continue

        print(f"\n  Scanning {page_type} pages...")
        html_files = scan_directory(directory)
        print(f"    Found {len(html_files)} pages")

        type_results = {'valid': 0, 'issues': 0, 'noindex': 0}

        for html_path in html_files:
            results['total'] += 1
            page_data = extract_page_data(html_path)
            issues, warnings = validate_page(page_data)

            if page_data.get('is_noindex'):
                results['noindexed'] += 1
                type_results['noindex'] += 1
                continue

            if issues:
                results['with_issues'] += 1
                type_results['issues'] += 1

                # Track issue types
                for issue in issues:
                    if 'Thin content' in issue:
                        results['issues_by_type']['thin_content'] += 1
                        results['thin_pages'].append({
                            'path': page_data['path'],
                            'word_count': page_data['word_count']
                        })
                    elif 'CRITICAL' in issue:
                        results['critical_issues'].append({
                            'path': page_data['path'],
                            'issue': issue
                        })
                        results['issues_by_type']['critical'] += 1
            else:
                results['valid'] += 1
                type_results['valid'] += 1

            if warnings:
                results['with_warnings'] += 1

        print(f"    Valid: {type_results['valid']}, Issues: {type_results['issues']}, Noindex: {type_results['noindex']}")

    # Print summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Total pages scanned: {results['total']}")
    print(f"  Valid pages: {results['valid']}")
    print(f"  Pages with issues: {results['with_issues']}")
    print(f"  Noindexed pages (protected): {results['noindexed']}")

    if results['issues_by_type']:
        print("\n  Issue breakdown:")
        for issue_type, count in sorted(results['issues_by_type'].items()):
            print(f"    - {issue_type}: {count}")

    if results['thin_pages']:
        print(f"\n  THIN CONTENT WARNING: {len(results['thin_pages'])} pages below {MIN_WORD_COUNT} words")
        print("  These pages are at risk of being flagged as spam by Google.")
        print("\n  Top 10 thinnest pages:")
        sorted_thin = sorted(results['thin_pages'], key=lambda x: x['word_count'])[:10]
        for p in sorted_thin:
            rel_path = p['path'].replace(SITE_DIR + '/', '')
            print(f"    - {rel_path}: {p['word_count']} words")

    if results['critical_issues']:
        print(f"\n  CRITICAL ISSUES: {len(results['critical_issues'])} pages need immediate attention")
        for p in results['critical_issues'][:10]:
            rel_path = p['path'].replace(SITE_DIR + '/', '')
            print(f"    - {rel_path}: {p['issue']}")

    # Exit with error code if critical issues found
    if results['critical_issues'] or len(results['thin_pages']) > 50:
        print("\n  ACTION REQUIRED: Fix critical issues before deploying.")
        sys.exit(1)
    else:
        print("\n  SEO validation passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
