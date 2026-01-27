# SEO Best Practices Checklist

**Use this checklist when creating new page generators or modifying existing ones.**

---

## Required for Every Page

### 1. Meta Tags
- [ ] `<title>` - Max 60 characters, include primary keyword near start
- [ ] `<meta name="description">` - Max 155 characters, compelling with CTA
- [ ] `<meta name="robots">` - Use `noindex, follow` for thin content (<3 items)
- [ ] Canonical URL - Always set, use trailing slashes consistently

### 2. Images
- [ ] **Always use `get_img_tag()` helper** from templates.py
- [ ] Every image MUST have descriptive `alt` text (not just filename)
- [ ] Use `loading="lazy"` for below-fold images
- [ ] Use `loading="eager"` only for above-fold critical images (logo, hero)
- [ ] Include `width` and `height` to prevent layout shift

```python
from templates import get_img_tag

# Good - uses helper with descriptive alt
logo_html = get_img_tag(src, f"{company_name} logo", loading="eager")

# Bad - inline img without alt or lazy loading
logo_html = f'<img src="{src}">'
```

### 3. Breadcrumbs
- [ ] **Always include breadcrumbs** on all pages except homepage
- [ ] Use `get_breadcrumb_html()` - includes BreadcrumbList schema automatically
- [ ] Structure: Home > Section > Current Page

```python
from templates import get_breadcrumb_html

breadcrumbs = [
    {'name': 'Home', 'url': '/'},
    {'name': 'Jobs', 'url': '/jobs/'},
    {'name': page_title, 'url': f'/jobs/{slug}/'}
]
breadcrumb_html = get_breadcrumb_html(breadcrumbs)
```

### 4. Structured Data (JSON-LD)
- [ ] BreadcrumbList schema (via `get_breadcrumb_html`)
- [ ] Page-specific schema based on content type:

| Page Type | Required Schema |
|-----------|-----------------|
| Job listing | JobPosting |
| Product/tool review | Review + SoftwareApplication |
| Company page | Organization |
| Article | Article or BlogPosting |
| FAQ content | FAQPage |
| Data/stats page | Dataset |
| List/index page | CollectionPage + ItemList |

### 5. Open Graph & Twitter Cards
- [ ] `og:title`, `og:description`, `og:url`, `og:image`
- [ ] `og:type` (website, article, product)
- [ ] `twitter:card` (summary_large_image)
- [ ] `twitter:image:alt` - Same as og:image alt text

---

## Pagination (for list pages with 50+ items)

- [ ] Implement server-side pagination (50 items per page recommended)
- [ ] Use clean URLs: `/jobs/`, `/jobs/page/2/`, `/jobs/page/3/`
- [ ] Include `rel="prev"` and `rel="next"` link tags
- [ ] Each page has unique canonical URL
- [ ] First page canonical is `/jobs/` not `/jobs/page/1/`

---

## Content Quality Signals

### Thin Content Handling
- [ ] Pages with <3 items should be `noindex, follow`
- [ ] Add "similar items" section to thin pages for user value
- [ ] Consider consolidating very thin pages

### Title Optimization
- [ ] Primary keyword within first 60 characters
- [ ] Brand name at end if space allows
- [ ] Unique across all pages

### Internal Linking
- [ ] Link to related content within body text
- [ ] Use descriptive anchor text (not "click here")
- [ ] Footer should link to main sections
- [ ] **Add "Related Items" section** on detail pages (jobs → related jobs, companies → similar companies)
- [ ] Use `auto_link_content()` from seo_core.py to automatically link tool names and salary pages

```python
from seo_core import auto_link_content

# Auto-link mentions of tools and salary pages in article content
content_html = auto_link_content(
    content_html,
    exclude_links=[f'/insights/{slug}/'],  # Don't link to self
    max_links=5  # Limit to avoid over-optimization
)
```

### FAQ Schema
- [ ] Add FAQPage schema on pages with Q&A content
- [ ] Use `generate_faq_schema()` + `generate_faq_html()` from seo_core.py
- [ ] Good FAQ candidates: tool pages, salary pages, category pages

```python
from seo_core import generate_faq_schema, generate_faq_html

faqs = [
    {'question': 'What is X?', 'answer': 'X is...'},
    {'question': 'How much does X cost?', 'answer': 'Pricing starts at...'}
]
faq_schema = generate_faq_schema(faqs)
faq_html = generate_faq_html(faqs)
```

---

## Performance

- [ ] Inline critical CSS in `<head>`
- [ ] Preconnect to external domains (fonts.googleapis.com, etc.)
- [ ] No render-blocking resources
- [ ] Lazy load below-fold images

---

## Existing Helpers in templates.py

| Function | Purpose |
|----------|---------|
| `get_html_head()` | Full `<head>` with meta tags, OG, Twitter |
| `get_nav_html()` | Consistent navigation with logo alt text |
| `get_footer_html()` | Footer with internal links |
| `get_img_tag()` | SEO-optimized images with alt + lazy loading |
| `get_breadcrumb_html()` | Breadcrumbs with BreadcrumbList schema |
| `get_cta_box()` | Call-to-action sections |

## Schema Helpers in seo_core.py

| Function | Purpose |
|----------|---------|
| `generate_breadcrumb_schema()` | BreadcrumbList JSON-LD |
| `generate_faq_schema()` | FAQPage JSON-LD |
| `generate_review_schema()` | Review JSON-LD |
| `generate_collectionpage_schema()` | CollectionPage JSON-LD |
| `generate_itemlist_schema()` | ItemList JSON-LD |
| `generate_dataset_schema()` | Dataset JSON-LD |

---

## Quick Audit Commands

```bash
# Check for images without alt text
grep -r '<img ' site/ | grep -v 'alt='

# Check title lengths
grep -r '<title>' site/ | awk -F'[<>]' '{print length($3), $3}' | sort -rn | head -20

# Find pages without breadcrumbs
for f in site/**/*.html; do grep -L 'BreadcrumbList' "$f"; done

# Check for noindex pages
grep -r 'noindex' site/ | wc -l
```

---

## Common Pitfalls to Avoid

### Title Tags
- **Double suffix bug**: If using `get_html_head()`, don't append `| {SITE_NAME}` yourself - the helper already does this
- **Truncation**: Google truncates at ~60 chars. Check lengths with: `grep -r '<title>' site/ | awk -F'[<>]' '{print length($3), $3}' | sort -rn | head -20`

### Data Structure Mismatches
- **Feature dicts use 'title' not 'name'**: `[f['title'] for f in tool_data['features']]`
- **Always check dict keys**: When iterating data structures, verify the actual key names before using them

### Schema Markup
- **Multiple schemas are fine**: A page can have BreadcrumbList + CollectionPage + ItemList
- **Pass schemas via `extra_head`**: `get_html_head(..., extra_head=f"{schema1}\n{schema2}")`

### Related Content Sections
- **Score-based matching works well**: Score by category overlap, skill overlap, company match, salary presence
- **Limit to 4-6 items**: Too many dilutes the signal
- **Exclude current page**: Always filter out the page you're generating

```python
def find_related_jobs(current_job, all_jobs, num_related=4):
    """Score each job by relevance, return top N."""
    scored = []
    for job in all_jobs:
        if job == current_job:
            continue
        score = 0
        if job['category'] == current_job['category']:
            score += 30
        if job['company'] == current_job['company']:
            score += 50
        # ... more scoring logic
        scored.append((job, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [j for j, _ in scored[:num_related]]
```

---

## New Page Generator Template

When creating a new page generator, start with this skeleton:

```python
import sys
sys.path.insert(0, 'scripts')

from templates import (
    get_html_head, get_nav_html, get_footer_html, get_cta_box,
    get_breadcrumb_html, get_img_tag, slugify, BASE_URL, SITE_NAME
)
from seo_core import (
    generate_breadcrumb_schema, generate_collectionpage_schema,
    generate_itemlist_schema, generate_faq_schema, auto_link_content
)

def generate_page(item, all_items):
    slug = slugify(item['name'])

    # Determine if thin content
    is_thin = len(item.get('sub_items', [])) < 3
    robots = 'noindex, follow' if is_thin else 'index, follow'

    # Breadcrumbs
    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'Section', 'url': '/section/'},
        {'name': item['name'], 'url': f'/section/{slug}/'}
    ]
    breadcrumb_html = get_breadcrumb_html(breadcrumbs)

    # Schemas
    collection_schema = generate_collectionpage_schema(...)
    itemlist_schema = generate_itemlist_schema(...)
    schemas = f"{collection_schema}\\n{itemlist_schema}"

    # Related items
    related = find_related_items(item, all_items)
    related_html = generate_related_html(related)

    # Build page
    html = f'''{get_html_head(
        f"{item['name']} - Primary Keyword",
        "Meta description under 155 chars",
        f"section/{slug}/",
        extra_head=schemas,
        robots=robots
    )}
    {get_nav_html('section')}

    <main class="container">
        {breadcrumb_html}
        <!-- content -->
        {get_cta_box()}
        {related_html}
    </main>

    {get_footer_html()}'''

    return html
```

---

*Last updated: January 2026*
*After SEO Phase 10 implementation*
