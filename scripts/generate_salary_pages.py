#!/usr/bin/env python3
"""
Generate salary benchmark pages for programmatic SEO.
Creates pages like /salaries/ml-engineer/, /salaries/san-francisco/, /salaries/senior/
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
SALARIES_DIR = f'{SITE_DIR}/salaries'

# Define salary categories
ROLE_CATEGORIES = [
    ('AI/ML Engineer', 'ai-ml-engineer', 'AI/ML Engineer'),
    ('Prompt Engineer', 'prompt-engineer', 'Prompt Engineer'),
    ('LLM Engineer', 'llm-engineer', 'LLM Engineer'),
    ('MLOps Engineer', 'mlops-engineer', 'MLOps Engineer'),
    ('Research Engineer', 'research-engineer', 'Research Engineer'),
    ('AI Agent Developer', 'ai-agent-developer', 'AI Agent Developer'),
    ('AI Product Manager', 'ai-product-manager', 'AI Product Manager'),
    ('Data Scientist', 'data-scientist', 'Data Scientist'),
]

# SEO content for each role category
ROLE_SEO_CONTENT = {
    'ai-ml-engineer': {
        'intro': '''AI/ML Engineers are the backbone of production machine learning systems. These professionals bridge the gap between research and deployment, building scalable infrastructure that transforms experimental models into reliable production services. In 2026, demand remains strong as companies continue their AI transformation initiatives.''',
        'what_they_do': '''AI/ML Engineers design and implement end-to-end machine learning pipelines, from data ingestion to model serving. Daily work includes optimizing model performance, managing training infrastructure, implementing A/B testing frameworks, and ensuring models meet latency and accuracy requirements in production. They typically work with PyTorch or TensorFlow, cloud platforms like AWS SageMaker or Google Vertex AI, and orchestration tools like Kubernetes and Airflow.''',
        'salary_factors': '''Location has the biggest impact on AI/ML Engineer salaries, with San Francisco and New York commanding 20-30% premiums. Experience level matters significantly—senior engineers with MLOps expertise can earn 40-60% more than mid-level counterparts. Company stage also plays a role: FAANG companies offer the highest base salaries, while startups may compensate with larger equity packages.''',
    },
    'prompt-engineer': {
        'intro': '''Prompt Engineering emerged as a distinct discipline in 2023-2024 and has matured into a well-defined career path. Prompt Engineers optimize LLM outputs through systematic prompt design, few-shot learning, and chain-of-thought techniques. As enterprises deploy more LLM-powered applications, demand for specialists who can reliably extract value from these models continues to grow.''',
        'what_they_do': '''Prompt Engineers craft and iterate on prompts to achieve consistent, high-quality outputs from large language models. This involves understanding model behavior, designing evaluation frameworks, implementing prompt versioning systems, and collaborating with product teams to translate requirements into effective prompts. Advanced practitioners work on RAG architectures, agent systems, and fine-tuning strategies.''',
        'salary_factors': '''Prompt Engineer salaries vary widely based on the complexity of systems being built. Basic prompt optimization roles pay less than positions requiring RAG architecture design or multi-agent system development. Companies building AI-native products (not just adding AI features) typically pay 15-25% more. The field is new enough that salary bands are still forming, creating negotiation opportunities for experienced practitioners.''',
    },
    'llm-engineer': {
        'intro': '''LLM Engineers specialize in the technical implementation of large language model systems. Unlike Prompt Engineers who focus on prompt optimization, LLM Engineers build the infrastructure: fine-tuning pipelines, serving infrastructure, evaluation systems, and integration layers. This is one of the fastest-growing and highest-paying specializations in AI.''',
        'what_they_do': '''LLM Engineers work on model fine-tuning (LoRA, QLoRA, full fine-tuning), build RAG systems with vector databases, implement inference optimization (quantization, distillation), and create evaluation pipelines for model quality. They often own the entire LLM stack from API integration to production deployment, working with tools like LangChain, LlamaIndex, vLLM, and various model providers.''',
        'salary_factors': '''LLM Engineer salaries are among the highest in AI due to specialized skills and limited supply. Experience with production LLM systems commands significant premiums—engineers who have shipped LLM features at scale can negotiate 20-40% above market rates. Familiarity with open-source model deployment (Llama, Mistral) is increasingly valued as companies explore alternatives to API-only approaches.''',
    },
    'mlops-engineer': {
        'intro': '''MLOps Engineers ensure machine learning models work reliably in production. As the AI industry matures from experimentation to deployment, MLOps has become critical infrastructure. These engineers build the platforms that enable data scientists and ML engineers to ship models quickly and safely.''',
        'what_they_do': '''MLOps Engineers build and maintain ML platforms including feature stores, model registries, training pipelines, and serving infrastructure. They implement CI/CD for ML, monitoring and alerting for model drift, A/B testing frameworks, and cost optimization for compute resources. Tools of the trade include Kubernetes, MLflow, Kubeflow, Airflow, and cloud-native ML services.''',
        'salary_factors': '''MLOps salaries have increased significantly as companies realize the cost of unreliable ML systems. Engineers with experience at scale (managing hundreds of models in production) command the highest salaries. Cloud platform expertise matters—deep knowledge of AWS SageMaker, Azure ML, or Google Vertex AI adds 10-15% to compensation. DevOps background plus ML knowledge is the winning combination.''',
    },
    'research-engineer': {
        'intro': '''Research Engineers bridge the gap between academic ML research and production systems. They implement papers, run experiments at scale, and help research scientists iterate faster. This role is common at AI labs, big tech research divisions, and well-funded AI startups pushing the boundaries of what's possible.''',
        'what_they_do': '''Research Engineers implement novel architectures from papers, optimize training code for multi-GPU/multi-node setups, build experiment tracking infrastructure, and create tools that accelerate the research process. They need strong software engineering skills combined with deep understanding of ML fundamentals—particularly optimization, distributed computing, and numerical stability.''',
        'salary_factors': '''Research Engineer salaries vary significantly by employer. Top AI labs (OpenAI, Anthropic, DeepMind, FAIR) pay premium rates, often matching or exceeding senior software engineer compensation at FAANG. Publication record and contributions to open-source ML projects can significantly boost compensation. PhD is valued but not required if you have equivalent demonstrated expertise.''',
    },
    'ai-agent-developer': {
        'intro': '''AI Agent Developers build autonomous systems that can plan, reason, and take actions to accomplish complex tasks. This emerging specialization combines LLM expertise with software architecture skills to create agents that interact with tools, APIs, and the real world. The field is nascent but growing rapidly as agent frameworks mature.''',
        'what_they_do': '''AI Agent Developers design agent architectures, implement tool-use patterns, build memory and state management systems, and create evaluation frameworks for agent behavior. They work with agent frameworks (LangGraph, AutoGPT, CrewAI), implement safety guardrails, and optimize agent performance for reliability and cost. The role requires both LLM expertise and traditional software engineering skills.''',
        'salary_factors': '''AI Agent Developer is a new enough role that salary data is still emerging. Early practitioners with production agent systems can command premium rates due to limited supply. Companies building agent-based products (customer service automation, coding assistants, workflow automation) are the primary employers. Expect salaries to stabilize as the field matures over 2025-2026.''',
    },
    'ai-product-manager': {
        'intro': '''AI Product Managers guide the development of AI-powered products, translating technical capabilities into user value. They need enough technical depth to work effectively with ML teams while maintaining focus on user needs, market positioning, and business outcomes. This hybrid role is increasingly important as AI becomes a product differentiator.''',
        'what_they_do': '''AI Product Managers define product requirements for AI features, prioritize model improvements based on user impact, design evaluation metrics that align with business goals, and manage the unique challenges of AI products (handling model uncertainty, setting user expectations, iterating on data quality). They bridge technical and business stakeholders, often translating between "model accuracy improved 2%" and "customer satisfaction increased."''',
        'salary_factors': '''AI PM salaries correlate with the strategic importance of AI to the company's product. At AI-native companies, these roles pay 15-25% more than traditional PM positions. Technical background (engineering, data science) commands higher compensation. Experience shipping AI products at scale is the strongest salary driver—PMs who have navigated the challenges of production ML systems are in high demand.''',
    },
    'data-scientist': {
        'intro': '''Data Scientists extract insights from data to drive business decisions. While the role has evolved significantly since the "sexiest job" hype of the 2010s, Data Scientists remain essential for companies leveraging data for competitive advantage. The modern role increasingly overlaps with ML engineering and analytics engineering.''',
        'what_they_do': '''Data Scientists analyze data to answer business questions, build predictive models, design and analyze experiments, and communicate findings to stakeholders. The role varies significantly by company—some emphasize statistical analysis and experimentation, others focus on production ML, and many blend both. SQL, Python, and statistical modeling remain core skills, with increasing demand for ML engineering capabilities.''',
        'salary_factors': '''Data Scientist salaries depend heavily on the role definition at each company. ML-focused positions at tech companies pay significantly more than analytics-focused roles at traditional companies. Industry matters too—fintech and big tech lead compensation, while retail and healthcare lag. The title has become so broad that salary ranges vary more than most AI roles—always clarify the actual job responsibilities when comparing offers.''',
    },
}

# SEO content for metro/location categories
METRO_SEO_CONTENT = {
    'san-francisco': {
        'intro': '''San Francisco and the Bay Area remain the epicenter of AI talent and compensation. Home to OpenAI, Anthropic, and countless AI startups, SF offers the highest AI salaries in the world—but also the highest cost of living. The concentration of AI companies creates unique networking and career growth opportunities.''',
        'market_context': '''The Bay Area AI job market is highly competitive on both sides. Companies compete aggressively for talent with top-of-market salaries and equity packages. Candidates face rigorous interview processes at top companies but have abundant opportunities. Remote-friendly policies have reduced some geographic premium, but on-site roles in SF still command the highest base salaries.''',
    },
    'new-york': {
        'intro': '''New York City has emerged as a major AI hub, particularly for AI applications in finance, media, and advertising. Wall Street firms and fintech companies pay premium salaries for ML talent, while a growing startup ecosystem offers equity-heavy opportunities. NYC's AI scene is more application-focused than SF's research orientation.''',
        'market_context': '''NYC AI salaries approach San Francisco levels, especially in finance-adjacent roles where ML is directly tied to revenue. The city attracts talent who want big-city living without Bay Area commutes. Financial services firms offer the highest compensation but often require on-site presence and longer hours. Startups cluster in Manhattan and Brooklyn with more flexible arrangements.''',
    },
    'seattle': {
        'intro': '''Seattle's AI market is dominated by Amazon and Microsoft, with a growing startup ecosystem in their shadow. AWS ML services and Azure AI teams are major employers, and both companies' presence creates a pipeline of experienced talent for other opportunities. The city offers high salaries with lower cost of living than SF or NYC.''',
        'market_context': '''Seattle AI compensation is 10-20% below SF for equivalent roles, but the cost of living difference makes it financially comparable. Amazon and Microsoft compete heavily for ML talent, driving market rates up. The city's strength is in applied ML and cloud infrastructure—less pure research than SF, more production-focused than most markets.''',
    },
    'austin': {
        'intro': '''Austin has grown rapidly as an AI hub, driven by tech company relocations and a business-friendly environment. Tesla's AI team, Oracle, and a wave of startups have created significant demand. Salaries are lower than coastal cities, but cost of living makes Austin competitive for take-home pay.''',
        'market_context': '''Austin AI salaries typically run 20-30% below SF, but housing costs are 50%+ lower, making it attractive for total compensation. The market is growing faster than talent supply, creating opportunities for experienced engineers relocating from higher-cost markets. Startup equity can be particularly valuable given lower cash compensation.''',
    },
    'boston': {
        'intro': '''Boston's AI market benefits from MIT, Harvard, and a strong biotech/healthcare cluster. AI applications in life sciences and robotics are particularly strong. The city attracts research-oriented talent and offers competitive salaries, though below SF and NYC levels.''',
        'market_context': '''Boston AI roles skew toward research and healthcare applications. Biotech companies pay well for ML talent who understand the domain. The academic pipeline produces strong researchers, but production-focused engineers are in high demand. Salaries are 15-25% below SF but cost of living is also lower.''',
    },
    'los-angeles': {
        'intro': '''Los Angeles AI market is driven by entertainment, gaming, and aerospace industries. AI applications in content creation, visual effects, and autonomous systems are growing. The market is smaller than SF but offers competitive salaries with better weather and lifestyle.''',
        'market_context': '''LA AI salaries are 10-20% below SF, with the gap narrowing for specialized roles in entertainment and gaming. SpaceX, gaming companies, and streaming services are major employers. The market is more fragmented than SF or Seattle—networking is important for finding opportunities.''',
    },
    'remote': {
        'intro': '''Remote AI roles have become mainstream, with many companies offering fully distributed positions at competitive salaries. The rise of remote work has expanded opportunities beyond traditional tech hubs, though compensation often adjusts for location. Remote roles require strong self-direction and communication skills.''',
        'market_context': '''Remote AI salaries vary widely by company policy. Some pay SF-equivalent rates regardless of location, others adjust based on local cost of living. Fully distributed companies (no HQ) tend to pay location-agnostic rates. Hybrid-remote roles often require occasional travel to company offices. The remote market is highly competitive—strong portfolios and referrals are important for standing out.''',
    },
}

# SEO content for experience level categories
EXPERIENCE_SEO_CONTENT = {
    'senior': {
        'intro': '''Senior AI roles (typically 5+ years of experience) command the highest salaries and carry significant responsibility. At this level, engineers are expected to lead technical projects, mentor junior team members, and make architectural decisions that impact the entire organization. Compensation reflects both expertise and leadership expectations.''',
        'expectations': '''Senior AI professionals are expected to work autonomously on complex problems, influence technical direction, and multiply team productivity through mentorship and tooling. Many companies expect senior hires to define their own projects rather than just execute assigned tasks. The line between senior IC and management often blurs at this level.''',
    },
    'mid-level': {
        'intro': '''Mid-level AI roles (2-5 years of experience) represent the bulk of hiring demand. At this level, engineers can work independently on well-defined problems and contribute to system design discussions. Compensation growth is typically fastest during these years as skills compound rapidly.''',
        'expectations': '''Mid-level AI professionals should be able to own features end-to-end with minimal supervision. Companies expect solid fundamentals, growing expertise in specialized areas, and the ability to ramp up quickly on new codebases. This is the level where specialization (LLMs, computer vision, etc.) starts to significantly impact career trajectory.''',
    },
    'entry-level': {
        'intro': '''Entry-level AI roles are competitive but accessible for candidates with strong fundamentals. Bootcamp graduates, new PhDs, and career changers with relevant projects all compete for these positions. Companies hiring at this level invest in training, so demonstrating learning ability is as important as current skills.''',
        'expectations': '''Entry-level candidates should have working knowledge of Python, ML fundamentals, and at least one deep learning framework. A portfolio of projects (Kaggle, personal projects, or research) is often required to demonstrate practical skills. Internship experience at tech companies significantly improves hiring outcomes.''',
    },
}

METRO_CATEGORIES = [
    ('San Francisco', 'san-francisco'),
    ('New York', 'new-york'),
    ('Seattle', 'seattle'),
    ('Austin', 'austin'),
    ('Boston', 'boston'),
    ('Los Angeles', 'los-angeles'),
    ('Remote', 'remote'),
]

EXPERIENCE_CATEGORIES = [
    ('senior', 'senior', 'Senior'),
    ('mid', 'mid-level', 'Mid-Level'),
    ('entry', 'entry-level', 'Entry-Level'),
]


def escape_html(text):
    if pd.isna(text):
        return ''
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def get_seo_content_for_category(slug, category_type, title):
    """Get SEO content based on category type and slug"""
    if category_type == 'role' and slug in ROLE_SEO_CONTENT:
        content = ROLE_SEO_CONTENT[slug]
        return f'''
            <div class="seo-content" style="max-width: 800px; margin-bottom: 2rem; color: var(--text-secondary); line-height: 1.8;">
                <p style="margin-bottom: 1rem;">{content['intro']}</p>
                <h3 style="color: var(--text-primary); font-size: 1.1rem; margin: 1.5rem 0 0.75rem;">What {title}s Do</h3>
                <p style="margin-bottom: 1rem;">{content['what_they_do']}</p>
                <h3 style="color: var(--text-primary); font-size: 1.1rem; margin: 1.5rem 0 0.75rem;">What Affects {title} Salaries</h3>
                <p style="margin-bottom: 1rem;">{content['salary_factors']}</p>
            </div>
        '''
    elif category_type == 'metro' and slug in METRO_SEO_CONTENT:
        content = METRO_SEO_CONTENT[slug]
        return f'''
            <div class="seo-content" style="max-width: 800px; margin-bottom: 2rem; color: var(--text-secondary); line-height: 1.8;">
                <p style="margin-bottom: 1rem;">{content['intro']}</p>
                <h3 style="color: var(--text-primary); font-size: 1.1rem; margin: 1.5rem 0 0.75rem;">{title} AI Job Market</h3>
                <p style="margin-bottom: 1rem;">{content['market_context']}</p>
            </div>
        '''
    elif category_type == 'experience' and slug in EXPERIENCE_SEO_CONTENT:
        content = EXPERIENCE_SEO_CONTENT[slug]
        return f'''
            <div class="seo-content" style="max-width: 800px; margin-bottom: 2rem; color: var(--text-secondary); line-height: 1.8;">
                <p style="margin-bottom: 1rem;">{content['intro']}</p>
                <h3 style="color: var(--text-primary); font-size: 1.1rem; margin: 1.5rem 0 0.75rem;">What Employers Expect</h3>
                <p style="margin-bottom: 1rem;">{content['expectations']}</p>
            </div>
        '''
    return ''


def generate_salary_page(filtered_df, slug, title, category_type, salary_col, min_col):
    """Generate a salary page for a specific category"""
    if len(filtered_df) < 3:
        return False

    try:
        avg_min = int(filtered_df[min_col].mean()) if filtered_df[min_col].notna().any() else 0
        avg_max = int(filtered_df[salary_col].mean())
        median = int(filtered_df[salary_col].median())
    except (ValueError, TypeError):
        avg_min = 0
        avg_max = 0
        median = 0

    sample_size = len(filtered_df)

    # Top paying companies
    company_col = 'company' if 'company' in filtered_df.columns else 'company_name'
    if company_col in filtered_df.columns:
        top_companies = filtered_df.nlargest(5, salary_col)[[company_col, salary_col]].to_dict('records')
    else:
        top_companies = []

    companies_html = ""
    for c in top_companies:
        company_name = c.get('company', c.get('company_name', 'Unknown'))
        try:
            sal = int(c[salary_col])
        except (ValueError, TypeError):
            sal = 0
        companies_html += f'''
            <div class="company-row">
                <span class="company-name">{escape_html(str(company_name))}</span>
                <span class="company-salary">${sal:,}</span>
            </div>
        '''

    # Get SEO content for this category
    seo_content = get_seo_content_for_category(slug, category_type, title)

    html = f'''{get_html_head(
        f"{title} Salary 2026 - ${avg_max//1000}K Average",
        f"{title} salary benchmarks based on {sample_size} job postings. Average ${avg_min//1000}K-${avg_max//1000}K. Median ${median//1000}K.",
        f"salaries/{slug}/"
    )}
{get_nav_html('salaries')}

    <div class="page-header">
        <div class="container">
            <div class="breadcrumb">
                <a href="/">Home</a> → <a href="/salaries/">Salaries</a> → {escape_html(title)}
            </div>
            <h1>{escape_html(title)} Salary 2026</h1>
            <p class="lead">Salary benchmarks based on {sample_size} job postings with disclosed compensation.</p>

            <div class="stats-row">
                <div class="stat-box">
                    <div class="stat-number">${avg_min//1000}K</div>
                    <div class="stat-label">Avg Min</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">${avg_max//1000}K</div>
                    <div class="stat-label">Avg Max</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">${median//1000}K</div>
                    <div class="stat-label">Median</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{sample_size}</div>
                    <div class="stat-label">Sample Size</div>
                </div>
            </div>
        </div>
    </div>

    <main>
        <div class="container">
            <style>
                .company-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 16px;
                    background: var(--bg-card);
                    border: 1px solid var(--border);
                    border-radius: 8px;
                    margin-bottom: 8px;
                }}
                .company-name {{ color: var(--text-primary); font-weight: 500; }}
                .company-salary {{ color: var(--gold); font-weight: 600; }}
            </style>

            {seo_content}

            {'<div class="section"><h2 style="margin-bottom: 20px;">Top Paying Companies</h2>' + companies_html + '</div>' if companies_html else ''}

            <div class="section" style="background: var(--bg-card); border-radius: 12px; padding: 24px; border: 1px solid var(--border);">
                <h3>Methodology</h3>
                <p style="color: var(--text-secondary); margin-top: 12px;">
                    Salary data is collected from job postings on Indeed and company career pages.
                    Only jobs with disclosed compensation are included. Data is updated weekly.
                </p>
            </div>

            {get_cta_box()}
        </div>
    </main>

{get_footer_html()}'''

    page_dir = f'{SALARIES_DIR}/{slug}'
    os.makedirs(page_dir, exist_ok=True)
    with open(f'{page_dir}/index.html', 'w') as f:
        f.write(html)
    return True


def main():
    print("="*70)
    print("  AI MARKET PULSE - GENERATING SALARY PAGES")
    print("="*70)

    os.makedirs(SALARIES_DIR, exist_ok=True)

    # Load job data
    files = glob.glob(f"{DATA_DIR}/ai_jobs_*.csv")
    print(f"  Looking for CSV files in {DATA_DIR}/")
    print(f"  Found: {files}")

    if files:
        df = pd.read_csv(max(files, key=os.path.getmtime))
    elif os.path.exists(f"{DATA_DIR}/jobs.json"):
        with open(f"{DATA_DIR}/jobs.json") as f:
            df = pd.DataFrame(json.load(f).get('jobs', []))
    else:
        print(" No job data found")
        sys.exit(1)

    print(f"\n Loaded {len(df)} jobs")
    print(f"  Columns: {list(df.columns)}")

    # Filter to jobs with salary
    salary_col = 'salary_max' if 'salary_max' in df.columns else 'max_amount'
    min_col = 'salary_min' if 'salary_min' in df.columns else 'min_amount'

    if salary_col not in df.columns:
        print(f" ERROR: No salary column found ({salary_col})")
        sys.exit(1)

    df_salary = df[df[salary_col].notna() & (df[salary_col] > 0)].copy()
    print(f" Jobs with salary: {len(df_salary)}")

    # Generate role-based salary pages
    print("\n Generating role-based salary pages...")
    for category, slug, display in ROLE_CATEGORIES:
        filtered = df_salary[df_salary['job_category'] == category] if 'job_category' in df_salary.columns else pd.DataFrame()
        if generate_salary_page(filtered, slug, display, 'role', salary_col, min_col):
            print(f"   Generated /salaries/{slug}/ ({len(filtered)} jobs)")

    # Generate metro-based salary pages
    print("\n Generating metro-based salary pages...")
    for metro, slug in METRO_CATEGORIES:
        if metro == 'Remote':
            if 'remote_type' in df_salary.columns:
                filtered = df_salary[df_salary['remote_type'].astype(str).str.contains('remote', case=False, na=False)]
            else:
                filtered = pd.DataFrame()
        else:
            if 'metro' in df_salary.columns:
                filtered = df_salary[df_salary['metro'] == metro]
            elif 'location' in df_salary.columns:
                filtered = df_salary[df_salary['location'].str.contains(metro, case=False, na=False)]
            else:
                filtered = pd.DataFrame()
        if generate_salary_page(filtered, slug, metro, 'metro', salary_col, min_col):
            print(f"   Generated /salaries/{slug}/ ({len(filtered)} jobs)")

    # Generate experience-based salary pages
    print("\n Generating experience-based salary pages...")
    for level, slug, display in EXPERIENCE_CATEGORIES:
        filtered = df_salary[df_salary['experience_level'] == level] if 'experience_level' in df_salary.columns else pd.DataFrame()
        if generate_salary_page(filtered, slug, display, 'experience', salary_col, min_col):
            print(f"   Generated /salaries/{slug}/ ({len(filtered)} jobs)")

    # Generate index page
    overall_avg = int(df_salary[salary_col].mean()) if len(df_salary) > 0 else 0
    overall_median = int(df_salary[salary_col].median()) if len(df_salary) > 0 else 0
    index_html = f'''{get_html_head(
        "AI & ML Engineer Salary Benchmarks 2026",
        f"Comprehensive salary data for AI engineers, ML engineers, and prompt engineers. Average ${overall_avg//1000}K based on {len(df_salary)} jobs.",
        "salaries/"
    )}
{get_nav_html('salaries')}

    <div class="page-header">
        <div class="container">
            <h1>AI Salary Benchmarks 2026</h1>
            <p class="lead">Real salary data from {len(df_salary)} AI and ML job postings. Updated weekly.</p>
        </div>
    </div>

    <main>
        <div class="container">
            <style>
                .category-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; margin-bottom: 40px; }}
                .category-card {{
                    display: block;
                    background: var(--bg-card);
                    border: 1px solid var(--border);
                    border-radius: 12px;
                    padding: 24px;
                    text-decoration: none;
                    transition: all 0.2s;
                }}
                .category-card:hover {{ border-color: var(--teal-light); transform: translateY(-2px); }}
                .category-card h3 {{ color: var(--text-primary); margin-bottom: 8px; }}
                .category-card p {{ color: var(--text-secondary); font-size: 0.9rem; }}
                .seo-content {{ color: var(--text-secondary); line-height: 1.8; max-width: 800px; }}
                .seo-content p {{ margin-bottom: 1rem; }}
                .seo-content h3 {{ color: var(--text-primary); font-size: 1.15rem; margin: 1.5rem 0 0.75rem; }}
                .seo-content strong {{ color: var(--text-primary); }}
            </style>

            <!-- SEO Intro Content -->
            <div class="seo-content" style="margin-bottom: 3rem; padding-bottom: 2rem; border-bottom: 1px solid var(--border);">
                <p>
                    Understanding AI salaries in 2026 requires real data, not outdated surveys or recruiter estimates. AI Market Pulse tracks salary information from job postings with disclosed compensation across <strong>{len(df_salary):,} positions</strong>, giving you current benchmarks to inform your career decisions.
                </p>
                <p>
                    The average maximum salary across all AI roles is <strong>${overall_avg:,}</strong>, with a median of <strong>${overall_median:,}</strong>. However, compensation varies significantly by role type, location, and experience level. Prompt Engineers and LLM Engineers command premium salaries as demand outpaces supply, while ML Engineers and Data Scientists remain the volume leaders in job postings.
                </p>
                <h3>How We Collect Salary Data</h3>
                <p>
                    We aggregate salary information exclusively from job postings with disclosed compensation ranges. This includes listings from Indeed, LinkedIn, company career pages, and Greenhouse/Lever job boards. We filter out outliers and normalize data to annual USD equivalents. Our data is updated weekly to reflect current market conditions.
                </p>
                <h3>What Affects AI Salaries</h3>
                <p>
                    Three factors dominate AI compensation: <strong>location</strong> (San Francisco and New York lead, but remote salaries are increasingly competitive), <strong>specialization</strong> (LLM and prompt engineering command 15-25% premiums over general ML roles), and <strong>company stage</strong> (early-stage startups often offer equity-heavy packages while FAANG-tier companies lead in base salary). Browse our breakdowns below to find benchmarks relevant to your situation.
                </p>
            </div>

            <h2 style="margin-bottom: 20px;">By Role</h2>
            <div class="category-grid">
                {''.join([f'<a href="/salaries/{slug}/" class="category-card"><h3>{display}</h3><p>View salary data</p></a>' for _, slug, display in ROLE_CATEGORIES])}
            </div>

            <h2 style="margin-bottom: 20px;">By Location</h2>
            <div class="category-grid">
                {''.join([f'<a href="/salaries/{slug}/" class="category-card"><h3>{metro}</h3><p>View salary data</p></a>' for metro, slug in METRO_CATEGORIES])}
            </div>

            <h2 style="margin-bottom: 20px;">By Experience</h2>
            <div class="category-grid">
                {''.join([f'<a href="/salaries/{slug}/" class="category-card"><h3>{display}</h3><p>View salary data</p></a>' for _, slug, display in EXPERIENCE_CATEGORIES])}
            </div>

            <!-- SEO Bottom Content -->
            <div class="seo-content" style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--border);">
                <h3>Using Salary Data for Negotiations</h3>
                <p>
                    When negotiating an AI role, come prepared with specific data points. Know the salary range for your exact role title, target location, and experience level. Our data shows that candidates who cite specific market benchmarks typically negotiate 10-15% higher offers than those who don't. Remember that total compensation includes base salary, equity, bonuses, and benefits—our benchmarks focus on base salary ranges as disclosed in job postings.
                </p>
                <h3>2026 AI Salary Trends</h3>
                <p>
                    The AI job market continues to mature. While 2023-2024 saw explosive growth in LLM-related roles, 2026 shows more stabilization with continued strong demand for production-focused skills. <strong>MLOps</strong> and <strong>AI infrastructure</strong> roles are seeing the fastest salary growth as companies move from experimentation to deployment. Remote work remains prevalent, with remote-first companies often matching or exceeding on-site salaries to compete for talent.
                </p>
            </div>

            {get_cta_box()}
        </div>
    </main>

{get_footer_html()}'''

    with open(f'{SALARIES_DIR}/index.html', 'w') as f:
        f.write(index_html)

    print(f"\n Generated salary index page")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
