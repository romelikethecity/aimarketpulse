#!/usr/bin/env python3
"""
Shared templates and utilities for PE Collective page generators.

This module consolidates common HTML, CSS, and utility functions used across
multiple page generators to eliminate duplication and centralize maintenance.

Design System: Dark teal + gold accent theme
"""

import re
import pandas as pd
import sys
import os

# Add scripts directory to path using absolute path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    from nav_config import NAV_ITEMS, FOOTER_ITEMS, SUBSCRIBE_LINK, SUBSCRIBE_LABEL, NEWSLETTER_LINK, NEWSLETTER_LABEL, SITE_NAME, COPYRIGHT_YEAR
except Exception as e:
    # Fallback if nav_config not found
    NAV_ITEMS = [
        {"href": "/jobs/", "label": "AI Jobs"},
        {"href": "/salaries/", "label": "Salaries"},
        {"href": "/tools/", "label": "Tools"},
        {"href": "/insights/", "label": "Market Intel"},
        {"href": "/about/", "label": "About"},
    ]
    FOOTER_ITEMS = NAV_ITEMS + [{"href": "/join/", "label": "Community"}]
    SUBSCRIBE_LINK = "/join/"
    SUBSCRIBE_LABEL = "Join Community"
    NEWSLETTER_LINK = "https://ainewsdigest.substack.com"
    NEWSLETTER_LABEL = "Newsletter"
    SITE_NAME = "PE Collective"
    COPYRIGHT_YEAR = "2026"

# SEO: Canonical domain
BASE_URL = 'https://theaimarketpulse.com'


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def slugify(text, max_length=60):
    """Convert text to URL-safe slug"""
    if pd.isna(text) or not text:
        return None
    slug = str(text).lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug[:max_length] if slug else None


def format_salary(min_amount, max_amount):
    """Format salary range for display"""
    try:
        min_sal = float(min_amount) if pd.notna(min_amount) else 0
        max_sal = float(max_amount) if pd.notna(max_amount) else 0
    except (ValueError, TypeError):
        return ""

    if min_sal > 0 and max_sal > 0:
        return f"${int(min_sal/1000)}K - ${int(max_sal/1000)}K"
    elif max_sal > 0:
        return f"Up to ${int(max_sal/1000)}K"
    elif min_sal > 0:
        return f"${int(min_sal/1000)}K+"
    return ""


def is_remote(job_data):
    """Check if job is remote based on job data dict or series"""
    if isinstance(job_data, dict):
        remote_type = job_data.get('remote_type', '')
        if remote_type and str(remote_type).lower() == 'remote':
            return True
        if job_data.get('is_remote'):
            return True
        location = job_data.get('location', '')
    else:
        # pandas Series
        remote_type = job_data.get('remote_type', '')
        if pd.notna(remote_type) and str(remote_type).lower() == 'remote':
            return True
        if 'is_remote' in job_data and job_data['is_remote']:
            return True
        location = job_data.get('location', '')

    if pd.notna(location):
        return 'remote' in str(location).lower()
    return False


def get_experience_display(level):
    """Convert experience level to display text"""
    mapping = {
        'entry': 'Entry Level',
        'mid': 'Mid Level',
        'senior': 'Senior',
        'lead': 'Lead/Principal',
    }
    if pd.isna(level):
        return ''
    return mapping.get(str(level).lower(), str(level).title())


# =============================================================================
# CSS CONSTANTS - PE Collective Dark Teal + Gold Theme
# =============================================================================

CSS_VARIABLES = '''
    :root {
        /* Core colors - dark theme */
        --bg-dark: #0f2d35;
        --bg-darker: #0a1f25;
        --bg-card: #132f38;
        --bg-card-hover: #1a3d48;

        --teal-primary: #1a4a56;
        --teal-light: #2a6a7a;
        --teal-accent: #3d8a9a;

        --gold: #e8a87c;
        --gold-light: #f0c4a8;
        --gold-hover: #d4956a;

        --text-primary: #ffffff;
        --text-secondary: #a8c5cc;
        --text-muted: #6a8a94;

        --success: #4ade80;
        --warning: #fbbf24;
        --error: #f87171;

        --border: rgba(255, 255, 255, 0.1);
        --border-light: rgba(255, 255, 255, 0.05);

        /* Legacy compatibility mappings */
        --navy: #0f2d35;
        --navy-light: #132f38;
        --navy-medium: #1a4a56;
        --navy-hover: #2a6a7a;
        --gold-muted: #d4956a;
        --gold-dark: #c4855c;
        --green: #4ade80;
        --green-dark: #22c55e;
        --red: #f87171;
        --gray-50: #0f2d35;
        --gray-100: #132f38;
        --gray-200: rgba(255, 255, 255, 0.1);
        --gray-300: #6a8a94;
        --gray-500: #6a8a94;
        --gray-600: #a8c5cc;
        --gray-700: #a8c5cc;
        --gray-800: #ffffff;
        --white: #ffffff;
    }

    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        background: var(--bg-dark);
        color: var(--text-primary);
        line-height: 1.6;
        -webkit-font-smoothing: antialiased;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        line-height: 1.2;
        letter-spacing: -0.02em;
    }

    a {
        color: var(--gold);
        text-decoration: none;
        transition: color 0.15s ease;
    }

    a:hover {
        color: var(--gold-light);
    }
'''

CSS_NAV = '''
    /* Navigation */
    .site-header {
        background: rgba(15, 45, 53, 0.95);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid var(--border);
        padding: 16px 0;
        position: sticky;
        top: 0;
        z-index: 100;
    }

    .header-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .logo {
        display: flex;
        align-items: center;
        gap: 12px;
        text-decoration: none;
        color: var(--text-primary);
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.125rem;
    }

    .logo img, .logo-img {
        width: 36px;
        height: 36px;
        border-radius: 8px;
    }

    .logo:hover {
        color: var(--text-primary);
    }

    .nav, .nav-links {
        display: flex;
        gap: 32px;
        align-items: center;
        list-style: none;
        margin: 0;
        padding: 0;
    }

    .nav a, .nav-links a {
        color: var(--text-secondary);
        text-decoration: none;
        font-size: 0.9375rem;
        font-weight: 500;
        transition: color 0.15s;
    }

    .nav a:hover, .nav-links a:hover { color: var(--text-primary); }
    .nav a.active { color: var(--text-primary); font-weight: 600; }

    .nav-cta, .btn-subscribe {
        background: var(--gold) !important;
        color: var(--bg-darker) !important;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 600;
    }
    .nav-cta:hover, .btn-subscribe:hover {
        background: var(--gold-hover) !important;
        transform: translateY(-1px);
    }

    .btn-secondary {
        background: transparent;
        color: var(--text-primary);
        border: 1px solid var(--border);
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 500;
    }
    .btn-secondary:hover {
        background: var(--bg-card);
        border-color: var(--teal-light);
    }

    /* Mobile Navigation */
    .mobile-menu-btn {
        display: none;
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: var(--text-primary);
    }
    .mobile-nav-overlay {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 999;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .mobile-nav-overlay.active { opacity: 1; }
    .mobile-nav {
        position: fixed;
        top: 0;
        right: -100%;
        width: 280px;
        max-width: 85%;
        height: 100vh;
        background: var(--bg-darker);
        z-index: 1000;
        padding: 1.5rem;
        box-shadow: -4px 0 20px rgba(0, 0, 0, 0.3);
        transition: right 0.3s ease;
        overflow-y: auto;
    }
    .mobile-nav.active { right: 0; }
    .mobile-nav-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border);
    }
    .mobile-nav-header .logo-text {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-primary);
        font-family: 'Space Grotesk', sans-serif;
    }
    .mobile-nav-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: var(--text-muted);
    }
    .mobile-nav-links {
        list-style: none;
        margin: 0 0 2rem 0;
        padding: 0;
    }
    .mobile-nav-links li { border-bottom: 1px solid var(--border-light); }
    .mobile-nav-links a {
        display: block;
        padding: 1rem 0;
        font-size: 1rem;
        font-weight: 500;
        color: var(--text-secondary);
        text-decoration: none;
    }
    .mobile-nav-links a:hover { color: var(--text-primary); }
    .mobile-nav-subscribe {
        display: block;
        width: 100%;
        padding: 1rem;
        background: var(--gold);
        color: var(--bg-darker);
        text-align: center;
        font-weight: 600;
        border-radius: 8px;
        text-decoration: none;
    }
    .mobile-nav-subscribe:hover {
        background: var(--gold-hover);
        color: var(--bg-darker);
    }

    @media (max-width: 768px) {
        .nav, .nav-links { display: none; }
        .mobile-menu-btn { display: block; }
        .mobile-nav-overlay { display: block; pointer-events: none; }
        .mobile-nav-overlay.active { pointer-events: auto; }
    }
'''

CSS_LAYOUT = '''
    /* Layout */
    .container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
    .container-narrow { max-width: 900px; margin: 0 auto; padding: 0 24px; }

    main { padding: 48px 0; }
    .section { margin-bottom: 56px; }

    /* Page Header */
    .page-header {
        background: var(--bg-darker);
        padding: 48px 0 40px;
        border-bottom: 1px solid var(--border);
    }

    .breadcrumb {
        font-size: 0.85rem;
        color: var(--text-muted);
        margin-bottom: 16px;
    }
    .breadcrumb a { color: var(--gold); text-decoration: none; }
    .breadcrumb a:hover { color: var(--gold-light); }

    .page-label {
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: var(--gold);
        margin-bottom: 12px;
    }

    .page-header h1 {
        font-size: 2.25rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 12px;
    }

    .page-header .lead {
        font-size: 1.1rem;
        color: var(--text-secondary);
        max-width: 700px;
        line-height: 1.7;
    }
'''

CSS_CARDS = '''
    /* Cards */
    .tool-card, .job-card, .company-card, .salary-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        text-decoration: none;
        color: inherit;
        transition: all 0.25s;
    }

    .tool-card:hover, .job-card:hover, .company-card:hover, .salary-card:hover {
        border-color: var(--teal-light);
        background: var(--bg-card-hover);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }

    .card-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 14px;
        width: fit-content;
    }

    .badge-live { background: rgba(74, 222, 128, 0.15); color: var(--success); }
    .badge-soon { background: rgba(106, 138, 148, 0.2); color: var(--text-muted); }
    .badge-comparison { background: rgba(232, 168, 124, 0.15); color: var(--gold); }
    .badge-remote { background: rgba(74, 222, 128, 0.15); color: var(--success); }
    .badge-salary { background: rgba(232, 168, 124, 0.15); color: var(--gold); }

    /* Skill Tags */
    .skill-tag {
        display: inline-block;
        padding: 2px 8px;
        background: var(--bg-darker);
        border-radius: 4px;
        font-size: 0.8125rem;
        color: var(--text-secondary);
        margin-right: 6px;
        margin-bottom: 6px;
    }

    /* Stats */
    .stats-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-top: 32px;
    }

    @media (max-width: 768px) { .stats-row { grid-template-columns: repeat(2, 1fr); } }

    .stat-box {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        transition: all 0.25s;
    }

    .stat-box:hover {
        border-color: var(--teal-light);
        transform: translateY(-2px);
    }

    .stat-number {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--gold);
        line-height: 1;
    }

    .stat-number.green { color: var(--success); }
    .stat-number.red { color: var(--error); }

    .stat-label {
        font-size: 0.875rem;
        color: var(--text-muted);
        margin-top: 8px;
    }
'''

CSS_CTA = '''
    /* CTA Box */
    .cta-box {
        background: linear-gradient(135deg, var(--teal-primary) 0%, var(--bg-darker) 100%);
        color: var(--text-primary);
        border-radius: 16px;
        padding: 40px;
        text-align: center;
        margin: 40px 0;
        border: 1px solid var(--border);
        position: relative;
        overflow: hidden;
    }

    .cta-box::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 60%;
        height: 200%;
        background: radial-gradient(ellipse, rgba(232, 168, 124, 0.1) 0%, transparent 60%);
        pointer-events: none;
    }

    .cta-box h3 {
        font-size: 1.5rem;
        margin-bottom: 12px;
        position: relative;
    }

    .cta-box p {
        color: var(--text-secondary);
        margin-bottom: 24px;
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
        position: relative;
    }

    .btn {
        display: inline-block;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        text-decoration: none;
        font-size: 0.95rem;
        transition: all 0.15s;
    }

    .btn-gold {
        background: var(--gold);
        color: var(--bg-darker);
    }
    .btn-gold:hover {
        background: var(--gold-hover);
        color: var(--bg-darker);
        transform: translateY(-1px);
        box-shadow: 0 0 20px rgba(232, 168, 124, 0.3);
    }

    .btn-outline {
        background: transparent;
        color: var(--text-primary);
        border: 1px solid var(--border);
    }
    .btn-outline:hover {
        background: var(--bg-card);
        border-color: var(--teal-light);
        color: var(--text-primary);
    }
'''

CSS_FOOTER = '''
    /* Footer */
    .site-footer, .footer {
        background: var(--bg-darker);
        border-top: 1px solid var(--border);
        padding: 48px 0 24px;
        margin-top: 64px;
    }

    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.875rem;
        color: var(--text-muted);
    }

    .footer-content a, .footer a {
        color: var(--text-muted);
        text-decoration: none;
        transition: color 0.15s;
    }
    .footer-content a:hover, .footer a:hover { color: var(--text-primary); }
    .footer-links a { margin-left: 24px; }

    @media (max-width: 768px) {
        .footer-content { flex-direction: column; gap: 12px; text-align: center; }
        .footer-links a { margin: 0 12px; }
    }
'''

CSS_JOB_PAGE = '''
    /* Individual Job Page Styles */
    .job-detail-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 24px;
        margin-bottom: 32px;
    }

    .job-detail-header h1 {
        font-size: 2rem;
        margin-bottom: 8px;
    }

    .job-company {
        font-size: 1.25rem;
        color: var(--text-secondary);
        margin-bottom: 16px;
    }

    .job-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 24px;
    }

    .job-meta-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 6px;
        font-size: 0.875rem;
        color: var(--text-secondary);
    }

    .job-meta-badge.salary {
        background: rgba(232, 168, 124, 0.15);
        border-color: rgba(232, 168, 124, 0.3);
        color: var(--gold);
    }

    .job-meta-badge.remote {
        background: rgba(74, 222, 128, 0.15);
        border-color: rgba(74, 222, 128, 0.3);
        color: var(--success);
    }

    .apply-btn {
        display: inline-block;
        padding: 16px 32px;
        background: var(--gold);
        color: var(--bg-darker);
        font-size: 1rem;
        font-weight: 700;
        border-radius: 8px;
        text-decoration: none;
        transition: all 0.15s;
    }

    .apply-btn:hover {
        background: var(--gold-hover);
        color: var(--bg-darker);
        transform: translateY(-2px);
        box-shadow: 0 0 20px rgba(232, 168, 124, 0.3);
    }

    .job-skills {
        margin: 24px 0;
    }

    .job-skills h3 {
        font-size: 1rem;
        color: var(--text-secondary);
        margin-bottom: 12px;
    }

    .job-details-table {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        margin: 24px 0;
    }

    .job-details-row {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid var(--border-light);
    }

    .job-details-row:last-child {
        border-bottom: none;
    }

    .job-details-label {
        color: var(--text-muted);
        font-weight: 500;
    }

    .job-details-value {
        color: var(--text-primary);
        font-weight: 600;
    }

    /* Expired/Stale Job Styles */
    .job-expired-notice {
        background: rgba(248, 113, 113, 0.1);
        border: 1px solid rgba(248, 113, 113, 0.3);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 32px;
        text-align: center;
    }

    .job-expired-notice h2 {
        color: var(--error);
        font-size: 1.25rem;
        margin-bottom: 8px;
    }

    .job-expired-notice p {
        color: var(--text-secondary);
    }

    .similar-jobs-section h3 {
        margin-bottom: 20px;
        color: var(--text-primary);
    }

    .similar-jobs-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 16px;
    }

    @media (max-width: 768px) {
        .job-detail-header {
            flex-direction: column;
        }
        .apply-btn {
            width: 100%;
            text-align: center;
        }
    }
'''


def get_base_styles():
    """Get all base CSS styles"""
    return f'''
    <style>
        {CSS_VARIABLES}
        {CSS_NAV}
        {CSS_LAYOUT}
        {CSS_CARDS}
        {CSS_CTA}
        {CSS_FOOTER}
        {CSS_JOB_PAGE}
    </style>
'''


# =============================================================================
# HTML GENERATORS
# =============================================================================

def get_html_head(title, description, page_path, include_styles=True, extra_head=''):
    """Generate SEO-compliant head section"""
    styles = get_base_styles() if include_styles else ''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | {SITE_NAME}</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="{BASE_URL}/{page_path}">

    <!-- Open Graph Tags -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{BASE_URL}/{page_path}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:site_name" content="{SITE_NAME}">
    <meta property="og:image" content="{BASE_URL}/assets/social-preview.png">

    <!-- Twitter Card Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@pe_collective">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{BASE_URL}/assets/social-preview.png">

    <link rel="icon" type="image/jpeg" href="/assets/logo.jpeg">
    <link rel="apple-touch-icon" sizes="180x180" href="/assets/logo.jpeg">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    {styles}
    {extra_head}
</head>
'''


def get_nav_html(active_page=None):
    """Generate site navigation including mobile nav and JS.

    Uses NAV_ITEMS from nav_config.py for centralized nav management.
    """
    # Build desktop nav links
    nav_links = []
    for item in NAV_ITEMS:
        page_id = item['href'].strip('/')
        active = ' class="active"' if page_id == active_page else ''
        nav_links.append(f'<a href="{item["href"]}"{active}>{item["label"]}</a>')
    nav_html = '\n                '.join(nav_links)

    # Build mobile nav links
    mobile_links = []
    for item in NAV_ITEMS:
        mobile_links.append(f'<li><a href="{item["href"]}">{item["label"]}</a></li>')
    mobile_nav_html = '\n            '.join(mobile_links)

    return f'''
<body>
    <header class="site-header">
        <div class="header-container">
            <a href="/" class="logo">
                <img src="/assets/logo.jpeg" alt="{SITE_NAME}">
                {SITE_NAME}
            </a>
            <nav class="nav">
                {nav_html}
            </nav>
            <div style="display: flex; gap: 8px; align-items: center;">
                <a href="{SUBSCRIBE_LINK}" class="btn-secondary">{SUBSCRIBE_LABEL}</a>
                <a href="{NEWSLETTER_LINK}" target="_blank" rel="noopener" class="nav-cta">{NEWSLETTER_LABEL}</a>
            </div>
            <button class="mobile-menu-btn" aria-label="Open menu">☰</button>
        </div>
    </header>

    <!-- Mobile Navigation -->
    <div class="mobile-nav-overlay"></div>
    <nav class="mobile-nav">
        <div class="mobile-nav-header">
            <span class="logo-text">{SITE_NAME}</span>
            <button class="mobile-nav-close" aria-label="Close menu">✕</button>
        </div>
        <ul class="mobile-nav-links">
            {mobile_nav_html}
        </ul>
        <a href="{SUBSCRIBE_LINK}" class="mobile-nav-subscribe">{SUBSCRIBE_LABEL}</a>
    </nav>

    <script>
        (function() {{
            const menuBtn = document.querySelector('.mobile-menu-btn');
            const closeBtn = document.querySelector('.mobile-nav-close');
            const overlay = document.querySelector('.mobile-nav-overlay');
            const mobileNav = document.querySelector('.mobile-nav');
            const mobileLinks = document.querySelectorAll('.mobile-nav-links a, .mobile-nav-subscribe');
            function openMenu() {{
                mobileNav.classList.add('active');
                overlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            }}
            function closeMenu() {{
                mobileNav.classList.remove('active');
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            }}
            if (menuBtn) menuBtn.addEventListener('click', openMenu);
            if (closeBtn) closeBtn.addEventListener('click', closeMenu);
            if (overlay) overlay.addEventListener('click', closeMenu);
            mobileLinks.forEach(link => {{ link.addEventListener('click', closeMenu); }});
        }})();
    </script>
'''


def get_footer_html():
    """Generate site footer.

    Uses FOOTER_ITEMS from nav_config.py for centralized nav management.
    """
    # Build footer links
    footer_links = []
    for item in FOOTER_ITEMS:
        footer_links.append(f'<a href="{item["href"]}">{item["label"]}</a>')
    footer_html = '\n                '.join(footer_links)

    return f'''
    <footer class="site-footer">
        <div class="footer-content">
            <span>&copy; {COPYRIGHT_YEAR} <a href="/">{SITE_NAME}</a></span>
            <div class="footer-links">
                {footer_html}
            </div>
        </div>
    </footer>
</body>
</html>
'''


def get_cta_box(title="Join the AI Community",
                description="Connect with prompt engineers and AI professionals. Get job alerts, salary insights, and market intelligence.",
                button_text="Join Community",
                button_url="/join/"):
    """Generate a CTA box"""
    return f'''
    <div class="cta-box">
        <h3>{title}</h3>
        <p>{description}</p>
        <a href="{button_url}" class="btn btn-gold">{button_text} →</a>
    </div>
'''


def get_job_posting_schema(job_data):
    """Generate JobPosting JSON-LD schema for a job"""
    import json
    from datetime import datetime, timedelta

    # Parse dates
    date_posted = job_data.get('date_posted', datetime.now().strftime('%Y-%m-%d'))
    if pd.isna(date_posted):
        date_posted = datetime.now().strftime('%Y-%m-%d')

    # Valid through (60 days from posting)
    try:
        posted_dt = datetime.strptime(str(date_posted)[:10], '%Y-%m-%d')
        valid_through = (posted_dt + timedelta(days=60)).strftime('%Y-%m-%d')
    except:
        valid_through = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')

    # Build schema
    schema = {
        "@context": "https://schema.org",
        "@type": "JobPosting",
        "title": job_data.get('title', ''),
        "datePosted": str(date_posted)[:10],
        "validThrough": valid_through,
        "employmentType": "FULL_TIME",
        "hiringOrganization": {
            "@type": "Organization",
            "name": job_data.get('company', job_data.get('company_name', ''))
        }
    }

    # Location
    location = job_data.get('location', '')
    remote_type = job_data.get('remote_type', '')

    if is_remote(job_data):
        schema["jobLocationType"] = "TELECOMMUTE"

    if pd.notna(location) and location:
        # Try to parse city, state
        parts = str(location).split(',')
        if len(parts) >= 2:
            schema["jobLocation"] = {
                "@type": "Place",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": parts[0].strip(),
                    "addressRegion": parts[1].strip()[:2] if len(parts[1].strip()) >= 2 else parts[1].strip(),
                    "addressCountry": "US"
                }
            }

    # Salary
    min_sal = job_data.get('salary_min', job_data.get('min_amount', 0))
    max_sal = job_data.get('salary_max', job_data.get('max_amount', 0))

    try:
        min_sal = float(min_sal) if pd.notna(min_sal) else 0
        max_sal = float(max_sal) if pd.notna(max_sal) else 0
    except:
        min_sal = max_sal = 0

    if min_sal > 0 or max_sal > 0:
        schema["baseSalary"] = {
            "@type": "MonetaryAmount",
            "currency": "USD",
            "value": {
                "@type": "QuantitativeValue",
                "unitText": "YEAR"
            }
        }
        if min_sal > 0:
            schema["baseSalary"]["value"]["minValue"] = int(min_sal)
        if max_sal > 0:
            schema["baseSalary"]["value"]["maxValue"] = int(max_sal)

    # Skills
    skills = job_data.get('skills_tags', [])
    if isinstance(skills, str):
        try:
            skills = json.loads(skills.replace("'", '"'))
        except:
            skills = [s.strip() for s in skills.split(',') if s.strip()]
    if skills:
        schema["skills"] = skills

    return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'
