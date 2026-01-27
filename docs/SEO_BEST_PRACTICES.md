# AI Market Pulse SEO Best Practices

Reference guide for SEO implementation across all page generators.

## Table of Contents
1. [Head Section Structure](#head-section-structure)
2. [Core Web Vitals](#core-web-vitals)
3. [Schema.org Markup](#schemaorg-markup)
4. [Internal Linking](#internal-linking)
5. [Content Guidelines](#content-guidelines)
6. [Thin Content Handling](#thin-content-handling)
7. [International SEO](#international-seo)

---

## Head Section Structure

Use `get_html_head()` from `templates.py` for consistent implementation:

```python
from templates import get_html_head

html = get_html_head(
    title="Page Title",           # 60 chars max (before " | AI Market Pulse")
    description="Meta desc",      # 155 chars max
    page_path="jobs/remote/",     # Path after BASE_URL
    robots="index, follow"        # or "noindex, follow" for thin content
)
```

### Required Meta Tags
- `<title>` - Unique, keyword-rich, under 60 chars
- `<meta name="description">` - Unique, under 155 chars
- `<link rel="canonical">` - Full absolute URL
- `<meta name="robots">` - Index status

### Social Tags (auto-included)
- Open Graph (og:title, og:description, og:image, og:locale)
- Twitter Cards (twitter:card, twitter:title, twitter:image)

---

## Core Web Vitals

### LCP (Largest Contentful Paint)
```html
<!-- Preconnect EARLY in <head> -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- Use font-display: swap to prevent FOIT -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=...&display=swap">
```

### CLS (Cumulative Layout Shift)
```css
/* Reserve space for images */
.logo img {
    width: 36px;
    height: 36px;
    aspect-ratio: 1;
    object-fit: cover;
}

/* Explicit dimensions prevent reflow */
img[width][height] {
    height: auto;
}
```

### FID/INP (First Input Delay / Interaction to Next Paint)
```javascript
// Use passive listeners for scroll-related events
element.addEventListener('click', handler, {passive: true});

// Defer non-critical JS
document.addEventListener('DOMContentLoaded', function() {
    // Initialize interactive elements
}, {once: true});
```

### CSS Performance
```css
/* Specify transitions explicitly (not 'all') */
.card {
    transition: border-color 0.25s, background-color 0.25s, transform 0.25s;
}

/* Use contain for isolated components */
.card {
    contain: layout style;
    will-change: transform;
}
```

### Analytics Placement
```html
<!-- Place at END of <head> to not block rendering -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXX"></script>
```

---

## Schema.org Markup

### Available Generators (seo_core.py)

| Function | Use Case |
|----------|----------|
| `generate_breadcrumb_schema()` | All pages with breadcrumbs |
| `generate_faq_schema()` | FAQ sections |
| `generate_jobposting_schema()` | Job detail pages |
| `generate_article_schema()` | Blog/insight articles |
| `generate_organization_schema()` | Company pages |
| `generate_dataset_schema()` | Salary data pages |
| `generate_software_schema()` | Tool review pages |
| `generate_collectionpage_schema()` | Landing pages, indexes |

### Breadcrumbs Example
```python
from seo_core import generate_breadcrumb_schema

breadcrumbs = [
    {'name': 'Home', 'url': '/'},
    {'name': 'Jobs', 'url': '/jobs/'},
    {'name': 'Remote', 'url': '/jobs/remote/'}
]
schema_html = generate_breadcrumb_schema(breadcrumbs)
```

### FAQ Schema
```python
from seo_core import generate_faq_schema, generate_faq_html

faqs = [
    {'question': 'How many AI jobs...?', 'answer': 'We track 1969...'},
    {'question': 'What is average salary?', 'answer': 'Based on...'}
]
faq_schema = generate_faq_schema(faqs)  # JSON-LD
faq_html = generate_faq_html(faqs)       # Visible HTML
```

---

## Internal Linking

### Page-Level Linking

| Page Type | Internal Links |
|-----------|---------------|
| Job pages | Related jobs (4), company link |
| Company pages | Similar companies (6), job links |
| Articles | Related resources (4), auto-linked terms |
| Landing pages | Related locations/skills (6-8) |
| Salary pages | Role-specific job links |

### Auto-Linking Content
```python
from seo_core import auto_link_content

# Automatically links tool names, salary references
content = auto_link_content(
    html_content,
    exclude_links=['/current-page/'],  # Don't link to self
    max_links=5                         # Limit for readability
)
```

### Cross-Linking Patterns
- Articles → Jobs, Salaries, Tools (via TAG_TO_RESOURCES mapping)
- Jobs → Company pages, similar jobs
- Companies → Similar companies by category/skills
- Salaries → Job landing pages by role

---

## Content Guidelines

### Title Tags
- Include primary keyword near beginning
- Keep under 60 characters (before site name suffix)
- Use year for time-sensitive content: "Remote AI Jobs 2026"
- Pattern: `{Primary Keyword} - {Modifier} | AI Market Pulse`

### Meta Descriptions
- Include primary keyword naturally
- Add a call-to-action or value proposition
- Keep under 155 characters
- Include numbers when available: "1969 open roles tracked"

### Headings
- One `<h1>` per page (matches page topic)
- Use `<h2>` for major sections
- Use `<h3>` for subsections
- Include keywords naturally

### URL Structure
```
/jobs/                          # Job index
/jobs/remote/                   # Location landing
/jobs/skills/python/            # Skill landing
/jobs/{company}-{title}-{hash}/ # Individual job
/salaries/ai-engineer/          # Role salary
/companies/{slug}/              # Company page
/insights/{slug}/               # Article
/tools/{slug}/                  # Tool review
```

---

## Thin Content Handling

### Thresholds
| Page Type | Index Threshold | Noindex Below |
|-----------|-----------------|---------------|
| Location landing | 5 jobs | < 5 jobs |
| Skill landing | 10 jobs | < 10 jobs |
| Company page | 3 jobs | < 3 jobs |
| Salary role | 10 samples | < 10 samples |
| Tag page | 3 articles | < 3 articles |

### Implementation
```python
# Set noindex for thin content
robots = "noindex, follow" if num_items < THRESHOLD else "index, follow"

html = get_html_head(
    title=title,
    description=desc,
    page_path=path,
    robots=robots  # Pass robot directive
)
```

### Why Keep Noindexed Pages
- Internal linking value (PageRank flow)
- User navigation (complete site structure)
- Future indexing (when content threshold met)

---

## International SEO

### Hreflang Tags (auto-included via get_html_head)
```html
<link rel="alternate" hreflang="en-US" href="https://theaimarketpulse.com/...">
<link rel="alternate" hreflang="en" href="https://theaimarketpulse.com/...">
<link rel="alternate" hreflang="x-default" href="https://theaimarketpulse.com/...">
```

### og:locale
```html
<meta property="og:locale" content="en_US">
```

### Future Expansion
When adding new languages/regions:
1. Create separate URL structure (/es/, /uk/, etc.)
2. Add hreflang alternates pointing to all versions
3. Ensure x-default points to primary version
4. Translate meta descriptions and titles

---

## Checklist for New Pages

- [ ] Use `get_html_head()` from templates.py
- [ ] Title under 60 chars with primary keyword
- [ ] Meta description under 155 chars
- [ ] Canonical URL set correctly
- [ ] Breadcrumb schema included
- [ ] Page-specific schema (FAQ, JobPosting, etc.)
- [ ] Internal links to related pages (4-8)
- [ ] Thin content check with appropriate robots directive
- [ ] Images have explicit width/height or aspect-ratio
- [ ] Interactive JS uses passive listeners
- [ ] Test with Chrome Lighthouse

---

## Key Files

| File | Purpose |
|------|---------|
| `scripts/templates.py` | HTML generators, CSS, utility functions |
| `scripts/seo_core.py` | Schema generators, FAQ generators, auto-linking |
| `scripts/nav_config.py` | Navigation items, site-wide config |
| `scripts/validate_seo.py` | SEO validation tool |

---

*Last updated: Phase 9 (Core Web Vitals + hreflang)*
