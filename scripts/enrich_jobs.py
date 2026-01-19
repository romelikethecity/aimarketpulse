#!/usr/bin/env python3
"""
Enrich raw AI job data and prepare for page generation.

This script processes raw job scrape data and outputs:
1. data/jobs.json - For the live job board
2. data/ai_jobs_YYYYMMDD.csv - Weekly enriched data for page generators
3. data/market_intelligence.json - Skills/tools analysis for insights page
"""

import pandas as pd
import json
import re
import os
from datetime import datetime, date
import glob
from collections import Counter

# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = "data"

# Skills to extract from job descriptions
SKILL_KEYWORDS = {
    # LLM Frameworks
    "langchain": "LangChain",
    "llamaindex": "LlamaIndex",
    "llama index": "LlamaIndex",
    "semantic kernel": "Semantic Kernel",
    "haystack": "Haystack",
    "autogen": "AutoGen",
    "crewai": "CrewAI",
    "dspy": "DSPy",

    # LLM Providers / Models
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "claude": "Claude",
    "gpt-4": "GPT-4",
    "gpt-3": "GPT-3",
    "gpt4": "GPT-4",
    "llama": "Llama",
    "mistral": "Mistral",
    "gemini": "Gemini",
    "cohere": "Cohere",
    "hugging face": "Hugging Face",
    "huggingface": "Hugging Face",

    # Techniques
    "rag": "RAG",
    "retrieval augmented": "RAG",
    "fine-tuning": "Fine-tuning",
    "fine tuning": "Fine-tuning",
    "prompt engineering": "Prompt Engineering",
    "embeddings": "Embeddings",
    "vector search": "Vector Search",
    "rlhf": "RLHF",
    "chain of thought": "Chain of Thought",
    "multimodal": "Multimodal",
    "agentic": "AI Agents",
    "ai agent": "AI Agents",

    # Vector DBs
    "pinecone": "Pinecone",
    "weaviate": "Weaviate",
    "milvus": "Milvus",
    "qdrant": "Qdrant",
    "chroma": "Chroma",
    "pgvector": "pgvector",
    "faiss": "FAISS",

    # ML Frameworks
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "transformers": "Transformers",
    "jax": "JAX",
    "keras": "Keras",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",

    # Languages
    "python": "Python",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "rust": "Rust",
    "golang": "Go",
    " go ": "Go",

    # Infrastructure
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "mlflow": "MLflow",
    "wandb": "Weights & Biases",
    "weights & biases": "Weights & Biases",
    "sagemaker": "SageMaker",
    "bedrock": "Bedrock",
    "vertex ai": "Vertex AI",
}

# Categories for grouping skills in insights
SKILL_CATEGORIES = {
    "LangChain": "LLM Frameworks",
    "LlamaIndex": "LLM Frameworks",
    "Semantic Kernel": "LLM Frameworks",
    "Haystack": "LLM Frameworks",
    "AutoGen": "LLM Frameworks",
    "CrewAI": "LLM Frameworks",
    "DSPy": "LLM Frameworks",
    "OpenAI": "LLM Providers",
    "Anthropic": "LLM Providers",
    "Claude": "LLM Providers",
    "GPT-4": "LLM Providers",
    "GPT-3": "LLM Providers",
    "Llama": "LLM Providers",
    "Mistral": "LLM Providers",
    "Gemini": "LLM Providers",
    "Cohere": "LLM Providers",
    "Hugging Face": "LLM Providers",
    "RAG": "Techniques",
    "Fine-tuning": "Techniques",
    "Prompt Engineering": "Techniques",
    "Embeddings": "Techniques",
    "Vector Search": "Techniques",
    "RLHF": "Techniques",
    "Chain of Thought": "Techniques",
    "Multimodal": "Techniques",
    "AI Agents": "Techniques",
    "Pinecone": "Vector Databases",
    "Weaviate": "Vector Databases",
    "Milvus": "Vector Databases",
    "Qdrant": "Vector Databases",
    "Chroma": "Vector Databases",
    "pgvector": "Vector Databases",
    "FAISS": "Vector Databases",
    "PyTorch": "ML Frameworks",
    "TensorFlow": "ML Frameworks",
    "Transformers": "ML Frameworks",
    "JAX": "ML Frameworks",
    "Keras": "ML Frameworks",
    "scikit-learn": "ML Frameworks",
    "Python": "Languages",
    "TypeScript": "Languages",
    "JavaScript": "Languages",
    "Rust": "Languages",
    "Go": "Languages",
    "AWS": "Cloud/Infrastructure",
    "Azure": "Cloud/Infrastructure",
    "GCP": "Cloud/Infrastructure",
    "Kubernetes": "Cloud/Infrastructure",
    "Docker": "Cloud/Infrastructure",
    "MLflow": "Cloud/Infrastructure",
    "Weights & Biases": "Cloud/Infrastructure",
    "SageMaker": "Cloud/Infrastructure",
    "Bedrock": "Cloud/Infrastructure",
    "Vertex AI": "Cloud/Infrastructure",
}

# Job categorization rules (first match wins)
# More specific rules should come before general ones
CATEGORY_RULES = [
    # Prompt Engineering
    ("prompt engineer", "Prompt Engineer"),
    ("prompt specialist", "Prompt Engineer"),

    # AI Agents / LLM Specialists
    ("ai agent", "AI Agent Developer"),
    ("agent developer", "AI Agent Developer"),
    ("agent engineer", "AI Agent Developer"),
    ("rag engineer", "RAG Engineer"),
    ("rag developer", "RAG Engineer"),
    ("llm engineer", "LLM Engineer"),
    ("llm developer", "LLM Engineer"),
    ("llm specialist", "LLM Engineer"),
    ("large language model", "LLM Engineer"),

    # MLOps / Infrastructure
    ("mlops", "MLOps Engineer"),
    ("ml ops", "MLOps Engineer"),
    ("ml infrastructure", "MLOps Engineer"),
    ("ml platform", "MLOps Engineer"),
    ("machine learning platform", "MLOps Engineer"),
    ("ai infrastructure", "MLOps Engineer"),
    ("ai platform engineer", "MLOps Engineer"),

    # AI Safety & Ethics
    ("ai safety", "AI Safety"),
    ("ai ethics", "AI Safety"),
    ("responsible ai", "AI Safety"),
    ("ai governance", "AI Safety"),

    # Product Management
    ("ai product manager", "AI Product Manager"),
    ("product manager ai", "AI Product Manager"),
    ("product manager ml", "AI Product Manager"),
    ("product manager, ai", "AI Product Manager"),
    ("product manager, ml", "AI Product Manager"),
    ("ml product manager", "AI Product Manager"),
    ("ai pm", "AI Product Manager"),

    # Research / Science
    ("applied scientist", "Research Scientist"),
    ("research scientist", "Research Scientist"),
    ("staff scientist", "Research Scientist"),
    ("ml scientist", "Research Scientist"),
    ("ai scientist", "Research Scientist"),
    ("research engineer", "Research Engineer"),
    ("ml research", "Research Engineer"),
    ("ai research", "Research Engineer"),

    # AI/ML Engineering - Specific
    ("artificial intelligence engineer", "AI/ML Engineer"),
    ("machine learning engineer", "AI/ML Engineer"),
    ("ml engineer", "AI/ML Engineer"),
    ("ai engineer", "AI/ML Engineer"),
    ("ai/ml engineer", "AI/ML Engineer"),
    ("ai developer", "AI/ML Engineer"),
    ("ml developer", "AI/ML Engineer"),
    ("nlp engineer", "AI/ML Engineer"),
    ("natural language", "AI/ML Engineer"),
    ("deep learning engineer", "AI/ML Engineer"),
    ("deep learning", "AI/ML Engineer"),
    ("generative ai", "AI/ML Engineer"),
    ("gen ai", "AI/ML Engineer"),
    ("genai", "AI/ML Engineer"),
    ("computer vision engineer", "AI/ML Engineer"),
    ("computer vision", "AI/ML Engineer"),
    ("cv engineer", "AI/ML Engineer"),
    ("speech recognition", "AI/ML Engineer"),
    ("speech engineer", "AI/ML Engineer"),
    ("recommendation system", "AI/ML Engineer"),
    ("recommendations engineer", "AI/ML Engineer"),

    # Software Engineering with AI focus
    ("software engineer, ai", "AI Software Engineer"),
    ("software engineer, ml", "AI Software Engineer"),
    ("software engineer - ai", "AI Software Engineer"),
    ("software engineer - ml", "AI Software Engineer"),
    ("sr. software engineer, ai", "AI Software Engineer"),
    ("senior software engineer, ai", "AI Software Engineer"),
    ("ai software engineer", "AI Software Engineer"),
    ("ai full-stack", "AI Software Engineer"),
    ("ai-native", "AI Software Engineer"),
    ("ai backend", "AI Software Engineer"),

    # Engineering Management
    ("engineering manager, ai", "AI Engineering Manager"),
    ("engineering manager, ml", "AI Engineering Manager"),
    ("engineering manager - ai", "AI Engineering Manager"),
    ("ai engineering manager", "AI Engineering Manager"),
    ("ml engineering manager", "AI Engineering Manager"),
    ("manager, ai", "AI Engineering Manager"),
    ("manager, ml", "AI Engineering Manager"),
    ("manager, applied ai", "AI Engineering Manager"),
    ("head of ai", "AI Engineering Manager"),
    ("head of ml", "AI Engineering Manager"),
    ("director of ai", "AI Engineering Manager"),
    ("director of ml", "AI Engineering Manager"),
    ("vp of ai", "AI Engineering Manager"),
    ("vp, ai", "AI Engineering Manager"),

    # Architecture
    ("ai architect", "AI Architect"),
    ("ml architect", "AI Architect"),
    ("ai enterprise architect", "AI Architect"),
    ("cloud ai architect", "AI Architect"),
    ("solutions architect, ai", "AI Architect"),
    ("solutions architect ai", "AI Architect"),

    # Data Science
    ("data scientist", "Data Scientist"),
    ("senior data scientist", "Data Scientist"),
    ("staff data scientist", "Data Scientist"),
    ("principal data scientist", "Data Scientist"),
    ("lead data scientist", "Data Scientist"),

    # Data Engineering
    ("data engineer", "Data Engineer"),
    ("senior data engineer", "Data Engineer"),
    ("lead data engineer", "Data Engineer"),
    ("staff data engineer", "Data Engineer"),
    ("data engineering", "Data Engineer"),
    ("analytics engineer", "Data Engineer"),

    # AI DevOps / Cloud
    ("ai devops", "AI/ML Engineer"),
    ("ai cloud", "AI/ML Engineer"),
    ("ai infrastructure engineer", "AI/ML Engineer"),

    # AI Consultants / Specialists
    ("ai consultant", "AI Consultant"),
    ("ai specialist", "AI Consultant"),
    ("ai functional", "AI Consultant"),
    ("ai advisor", "AI Consultant"),

    # AI Product roles
    ("ai product architect", "AI Product Manager"),
    ("ai/ml product", "AI Product Manager"),
    ("product architect, ai", "AI Product Manager"),

    # AI-Native roles
    ("ai native", "AI Software Engineer"),
    ("ai-native", "AI Software Engineer"),
    ("sr. developer ai", "AI Software Engineer"),
    ("developer ai", "AI Software Engineer"),
    ("developer, ai", "AI Software Engineer"),

    # Language / AGI roles
    ("language engineer", "AI/ML Engineer"),
    ("agi ", "AI/ML Engineer"),
    ("artificial general intelligence", "AI/ML Engineer"),

    # Catch-all AI mentions in title (lower priority)
    (", ai", "AI/ML Engineer"),  # "Software Engineer, AI"
    ("- ai", "AI/ML Engineer"),  # "Engineer - AI"
    (" ai ", "AI/ML Engineer"),  # Contains " AI " surrounded by spaces
    (" ai/", "AI/ML Engineer"),  # "Senior AI/ML"
    ("/ai ", "AI/ML Engineer"),  # "ML/AI Engineer"
]

# Metro areas for location normalization
METRO_MAPPING = {
    "san francisco": "San Francisco",
    "sf": "San Francisco",
    "bay area": "San Francisco",
    "palo alto": "San Francisco",
    "menlo park": "San Francisco",
    "mountain view": "San Francisco",
    "sunnyvale": "San Francisco",
    "san jose": "San Francisco",
    "new york": "New York",
    "nyc": "New York",
    "manhattan": "New York",
    "brooklyn": "New York",
    "seattle": "Seattle",
    "austin": "Austin",
    "boston": "Boston",
    "los angeles": "Los Angeles",
    "la": "Los Angeles",
    "chicago": "Chicago",
    "denver": "Denver",
    "atlanta": "Atlanta",
    "remote": "Remote",
}

# Seniority classification keywords
SENIORITY_PATTERNS = {
    'C-Level': ['chief', 'cto', 'cio', 'cao', 'cdo', 'head of ai', 'vp of ai'],
    'VP': ['vice president', 'vp ', ' vp,', 'vp,'],
    'Director': ['director', 'head of'],
    'Senior': ['senior', 'sr.', 'sr ', 'staff', 'principal', 'lead'],
    'Mid': ['mid', 'ii', 'iii'],
    'Entry': ['junior', 'jr.', 'jr ', 'entry', 'associate', ' i ', ' 1 '],
}

# Tech company indicators
TECH_COMPANY_KEYWORDS = [
    'software', 'saas', 'tech', 'ai', 'cloud', 'data', 'platform',
    'digital', 'cyber', 'fintech', 'analytics', 'machine learning',
    'automation', 'api', 'infrastructure', 'labs', 'systems',
    'intelligence', 'robotics', 'computing', 'neural', 'cognitive'
]

# Company stage indicators (from funding/description)
COMPANY_STAGE_PATTERNS = {
    'Startup (Seed)': ['seed', 'pre-seed', 'angel'],
    'Startup (Series A-B)': ['series a', 'series b', 'early stage', 'early-stage'],
    'Growth (Series C+)': ['series c', 'series d', 'series e', 'growth stage', 'growth-stage', 'late stage'],
    'Enterprise/Public': ['fortune 500', 'fortune500', 'public company', 'nasdaq', 'nyse', 'enterprise'],
}

# Buzzwords to track for insights
AI_BUZZWORDS = [
    'production-ready', 'scalable', 'enterprise-grade', 'state-of-the-art',
    'cutting-edge', 'innovative', 'groundbreaking', 'revolutionary',
    'next-generation', 'world-class', 'fast-paced', 'dynamic',
    'collaborative', 'cross-functional', 'end-to-end', 'full-stack'
]

# Red flag patterns for job postings
RED_FLAG_PATTERNS = {
    'vague_compensation': ['competitive salary', 'competitive compensation', 'commensurate with experience'],
    'unrealistic_requirements': ['10+ years', '10 years', 'phd required', 'must have phd'],
    'overwork_signals': ['wear many hats', 'fast-paced', 'startup mentality', 'hustle', '24/7'],
    'vague_role': ['various duties', 'other duties as assigned', 'jack of all trades'],
}


def extract_skills(text):
    """Extract skills from job description"""
    if not text or pd.isna(text):
        return []

    text_lower = str(text).lower()
    found_skills = set()

    for keyword, canonical in SKILL_KEYWORDS.items():
        if keyword in text_lower:
            found_skills.add(canonical)

    return sorted(list(found_skills))


def categorize_job(title):
    """Categorize job based on title"""
    if not title or pd.isna(title):
        return "Other AI Role"

    title_lower = str(title).lower()

    for keyword, category in CATEGORY_RULES:
        if keyword in title_lower:
            return category

    return "Other AI Role"


def determine_remote_type(row):
    """Determine if job is remote, hybrid, or onsite"""
    is_remote = row.get('is_remote', False)
    location = str(row.get('location', '')).lower()

    if is_remote or 'remote' in location:
        return 'remote'
    elif 'hybrid' in location:
        return 'hybrid'
    else:
        return 'onsite'


def determine_experience_level(title, description=''):
    """Determine experience level from title/description"""
    text = f"{title} {description}".lower()

    if any(word in text for word in ['senior', 'sr.', 'sr ', 'lead', 'principal', 'staff', 'head of', 'director']):
        return 'senior'
    elif any(word in text for word in ['junior', 'jr.', 'jr ', 'entry', 'associate', ' i ', ' ii ']):
        return 'entry'
    else:
        return 'mid'


def normalize_metro(location):
    """Normalize location to metro area"""
    if not location or pd.isna(location):
        return None

    location_lower = str(location).lower()

    for pattern, metro in METRO_MAPPING.items():
        if pattern in location_lower:
            return metro

    return None


def classify_seniority(title):
    """Classify job seniority level from title"""
    if not title or pd.isna(title):
        return 'Mid'

    title_lower = str(title).lower()

    for level, patterns in SENIORITY_PATTERNS.items():
        for pattern in patterns:
            if pattern in title_lower:
                return level

    return 'Mid'


def detect_tech_company(company, description=''):
    """Detect if company is a tech company"""
    if not company:
        return False

    text = f"{company} {description}".lower()
    return any(keyword in text for keyword in TECH_COMPANY_KEYWORDS)


def detect_company_stage(description):
    """Detect company stage from job description"""
    if not description or pd.isna(description):
        return 'Unknown'

    desc_lower = str(description).lower()

    for stage, patterns in COMPANY_STAGE_PATTERNS.items():
        for pattern in patterns:
            if pattern in desc_lower:
                return stage

    return 'Unknown'


def calculate_data_quality(row):
    """Calculate data quality score (0-100)"""
    score = 0

    # Has description (40 points)
    if pd.notna(row.get('description')) and len(str(row.get('description', ''))) > 100:
        score += 40

    # Has salary (30 points)
    if pd.notna(row.get('min_amount')) or pd.notna(row.get('max_amount')):
        score += 30

    # Has location (15 points)
    if pd.notna(row.get('location')) and str(row.get('location', '')) not in ['', 'nan', 'None']:
        score += 15

    # Has company (15 points)
    if pd.notna(row.get('company')) and str(row.get('company', '')) not in ['', 'nan', 'None', 'Unknown']:
        score += 15

    return score


def get_data_quality_label(score):
    """Convert quality score to label"""
    if score >= 85:
        return 'Premium'
    elif score >= 55:
        return 'Good'
    else:
        return 'Basic'


def extract_red_flags(description):
    """Extract red flags from job description"""
    if not description or pd.isna(description):
        return []

    desc_lower = str(description).lower()
    flags = []

    for flag_type, patterns in RED_FLAG_PATTERNS.items():
        for pattern in patterns:
            if pattern in desc_lower:
                flags.append(flag_type)
                break

    return flags


def extract_buzzwords(description):
    """Extract buzzwords from job description"""
    if not description or pd.isna(description):
        return []

    desc_lower = str(description).lower()
    found = []

    for buzzword in AI_BUZZWORDS:
        if buzzword in desc_lower:
            found.append(buzzword)

    return found


def process_jobs(df):
    """Process raw job data into enriched format"""
    jobs = []
    today = date.today()
    import_date = today.isoformat()
    import_week = today.strftime('%Y-W%W')

    for _, row in df.iterrows():
        # Skip if no title
        if pd.isna(row.get('title')):
            continue

        # Extract salary
        salary_min = None
        salary_max = None
        salary_type = 'annual'

        if pd.notna(row.get('min_amount')):
            try:
                salary_min = int(float(row['min_amount']))
            except:
                pass
        if pd.notna(row.get('max_amount')):
            try:
                salary_max = int(float(row['max_amount']))
            except:
                pass
        if pd.notna(row.get('interval')):
            interval = str(row['interval']).lower()
            if 'hour' in interval:
                salary_type = 'hourly'
                # Convert hourly to annual estimate for comparison
                if salary_min and salary_min < 500:
                    salary_min = int(salary_min * 2080)
                if salary_max and salary_max < 500:
                    salary_max = int(salary_max * 2080)

        # Build job object
        description = str(row.get('description', '')) if pd.notna(row.get('description')) else ''
        location = str(row.get('location', '')) if pd.notna(row.get('location')) else ''
        title = str(row.get('title', ''))
        company = str(row.get('company', '')) if pd.notna(row.get('company')) else 'Unknown'

        # Calculate data quality
        row_dict = row.to_dict()
        data_quality_score = calculate_data_quality(row_dict)

        job = {
            'job_id': str(row.get('id', ''))[:12] if pd.notna(row.get('id')) else '',
            'title': title,
            'company': company,
            'location': location,
            'metro': normalize_metro(location),
            'remote_type': determine_remote_type(row),
            'is_remote': determine_remote_type(row) == 'remote',
            'salary_min': salary_min,
            'salary_max': salary_max,
            'min_amount': salary_min,  # Alias for compatibility
            'max_amount': salary_max,  # Alias for compatibility
            'salary_type': salary_type,
            'experience_level': determine_experience_level(title, description),
            'seniority': classify_seniority(title),
            'job_category': categorize_job(title),
            'skills_tags': extract_skills(description),
            'is_tech': detect_tech_company(company, description),
            'company_stage': detect_company_stage(description),
            'data_quality_score': data_quality_score,
            'data_quality': get_data_quality_label(data_quality_score),
            'has_description': bool(description and len(description) > 100),
            'has_salary': bool(salary_min or salary_max),
            'red_flags': extract_red_flags(description),
            'buzzwords': extract_buzzwords(description),
            'date_posted': str(row.get('date_posted', ''))[:10] if pd.notna(row.get('date_posted')) else None,
            'date_scraped': date.today().isoformat(),
            'import_date': import_date,
            'import_week': import_week,
            'week_added': import_date,
            'source': str(row.get('site', 'indeed')),
            'source_url': str(row.get('job_url', row.get('job_url_direct', ''))) if pd.notna(row.get('job_url', row.get('job_url_direct'))) else '',
            'job_url_direct': str(row.get('job_url', row.get('job_url_direct', ''))) if pd.notna(row.get('job_url', row.get('job_url_direct'))) else '',
            'description': description,
            'description_snippet': description[:500] if description else '',
        }

        jobs.append(job)

    return jobs


def generate_market_intelligence(jobs):
    """Generate market intelligence data from jobs"""
    all_skills = []
    all_buzzwords = []
    all_red_flags = []
    categories_count = Counter()
    experience_count = Counter()
    seniority_count = Counter()
    remote_count = Counter()
    metro_count = Counter()
    company_stage_count = Counter()
    tech_count = 0
    data_quality_count = Counter()

    # Salary stats
    salaries = []
    salaries_by_category = {}
    salaries_by_seniority = {}

    for job in jobs:
        # Skills
        all_skills.extend(job.get('skills_tags', []))

        # Buzzwords
        all_buzzwords.extend(job.get('buzzwords', []))

        # Red flags
        all_red_flags.extend(job.get('red_flags', []))

        # Category
        cat = job.get('job_category', 'Other')
        categories_count[cat] += 1

        # Experience
        experience_count[job.get('experience_level', 'mid')] += 1

        # Seniority
        seniority = job.get('seniority', 'Mid')
        seniority_count[seniority] += 1

        # Remote
        remote_count[job.get('remote_type', 'onsite')] += 1

        # Metro
        if job.get('metro'):
            metro_count[job['metro']] += 1

        # Company stage
        stage = job.get('company_stage', 'Unknown')
        company_stage_count[stage] += 1

        # Tech company
        if job.get('is_tech'):
            tech_count += 1

        # Data quality
        quality = job.get('data_quality', 'Basic')
        data_quality_count[quality] += 1

        # Salary
        if job.get('salary_max'):
            sal = job['salary_max']
            salaries.append(sal)

            # By category
            if cat not in salaries_by_category:
                salaries_by_category[cat] = []
            salaries_by_category[cat].append(sal)

            # By seniority
            if seniority not in salaries_by_seniority:
                salaries_by_seniority[seniority] = []
            salaries_by_seniority[seniority].append(sal)

    # Skill counts
    skill_counts = Counter(all_skills)
    buzzword_counts = Counter(all_buzzwords)
    red_flag_counts = Counter(all_red_flags)

    # Group by category
    skills_by_category = {}
    for skill, count in skill_counts.items():
        category = SKILL_CATEGORIES.get(skill, 'Other')
        if category not in skills_by_category:
            skills_by_category[category] = {}
        skills_by_category[category][skill] = count

    # Calculate salary stats
    salary_stats = {}
    if salaries:
        salaries.sort()
        salary_stats = {
            'min': min(salaries),
            'max': max(salaries),
            'median': salaries[len(salaries)//2],
            'avg': sum(salaries) // len(salaries),
            'count_with_salary': len(salaries),
        }

    # Salary by category
    salary_by_category = {}
    for cat, sals in salaries_by_category.items():
        if sals:
            sals.sort()
            salary_by_category[cat] = {
                'median': sals[len(sals)//2],
                'avg': sum(sals) // len(sals),
                'count': len(sals),
            }

    # Salary by seniority
    salary_by_seniority = {}
    for sen, sals in salaries_by_seniority.items():
        if sals:
            sals.sort()
            salary_by_seniority[sen] = {
                'median': sals[len(sals)//2],
                'avg': sum(sals) // len(sals),
                'count': len(sals),
            }

    intel = {
        'date': date.today().isoformat(),
        'total_jobs': len(jobs),
        'skills': dict(skill_counts.most_common(50)),
        'skills_by_category': skills_by_category,
        'categories': dict(categories_count.most_common()),
        'experience_levels': dict(experience_count),
        'seniority_breakdown': dict(seniority_count),
        'remote_breakdown': dict(remote_count),
        'top_metros': dict(metro_count.most_common(10)),
        'company_stages': dict(company_stage_count.most_common()),
        'tech_companies': tech_count,
        'tech_percentage': round(tech_count / len(jobs) * 100, 1) if jobs else 0,
        'data_quality_breakdown': dict(data_quality_count),
        'salary_stats': salary_stats,
        'salary_by_category': salary_by_category,
        'salary_by_seniority': salary_by_seniority,
        'buzzwords': dict(buzzword_counts.most_common(20)),
        'red_flags': dict(red_flag_counts.most_common()),
    }

    return intel


def main():
    print("="*70)
    print("  PE COLLECTIVE - JOB ENRICHMENT")
    print("="*70)

    # Find raw job files
    raw_files = glob.glob(f"{DATA_DIR}/raw_ai_jobs_*.csv")
    if not raw_files:
        # Check if enriched data already exists
        existing_csv = glob.glob(f"{DATA_DIR}/ai_jobs_*.csv")
        if existing_csv:
            print("\n No raw files to process, using existing enriched data")
            print(f"   Found: {existing_csv}")
            print("   Skipping enrichment.")
            return

        # Try loading from jobs.json if no raw files and no existing CSV
        jobs_json = f"{DATA_DIR}/jobs.json"
        if os.path.exists(jobs_json):
            print(f"\n Loading from existing jobs.json")
            with open(jobs_json) as f:
                data = json.load(f)
            jobs = data.get('jobs', [])
            print(f" Jobs loaded: {len(jobs)}")
        else:
            print(" No raw job files or jobs.json found")
            print("   Run the AI jobs scraper first or add jobs.json to data/")
            exit(1)
    else:
        # Load most recent raw file
        latest_file = max(raw_files, key=os.path.getctime)
        print(f"\n Loading: {latest_file}")

        df = pd.read_csv(latest_file)
        print(f" Raw jobs loaded: {len(df)}")

        # Deduplicate
        url_col = 'job_url' if 'job_url' in df.columns else 'job_url_direct'
        df = df.drop_duplicates(subset=[url_col], keep='first')
        print(f" After deduplication: {len(df)}")

        # Process jobs
        jobs = process_jobs(df)
        print(f" Jobs processed: {len(jobs)}")

    # Print category breakdown
    categories = Counter(job['job_category'] for job in jobs)
    print("\n By category:")
    for cat, count in categories.most_common():
        print(f"   {cat}: {count}")

    # Seniority breakdown
    seniority = Counter(job['seniority'] for job in jobs)
    print("\n By seniority:")
    for level, count in seniority.most_common():
        pct = (count / len(jobs) * 100) if jobs else 0
        print(f"   {level}: {count} ({pct:.1f}%)")

    # Remote breakdown
    remote = Counter(job['remote_type'] for job in jobs)
    print("\n Remote breakdown:")
    for rtype, count in remote.items():
        pct = (count / len(jobs) * 100) if jobs else 0
        print(f"   {rtype}: {count} ({pct:.1f}%)")

    # Data quality breakdown
    quality = Counter(job['data_quality'] for job in jobs)
    print("\n Data quality:")
    for q, count in quality.most_common():
        pct = (count / len(jobs) * 100) if jobs else 0
        print(f"   {q}: {count} ({pct:.1f}%)")

    # Tech company stats
    tech_count = sum(1 for job in jobs if job.get('is_tech'))
    print(f"\n Tech companies: {tech_count} ({tech_count/len(jobs)*100:.1f}%)")

    # Salary stats
    salaries = [j['salary_max'] for j in jobs if j.get('salary_max')]
    if salaries:
        avg_sal = sum(salaries) // len(salaries)
        print(f"\n Salary data: {len(salaries)} jobs with salary")
        print(f"   Average max: ${avg_sal:,}")

    # Generate market intelligence
    intel = generate_market_intelligence(jobs)

    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # Save jobs.json (for live job board)
    output_json = {
        'last_updated': date.today().isoformat(),
        'total_jobs': len(jobs),
        'jobs': jobs
    }
    with open(f'{DATA_DIR}/jobs.json', 'w') as f:
        json.dump(output_json, f, indent=2)
    print(f"\n Saved: {DATA_DIR}/jobs.json")

    # Save CSV for page generators
    csv_filename = f"{DATA_DIR}/ai_jobs_{date.today().strftime('%Y%m%d')}.csv"
    df_output = pd.DataFrame(jobs)

    # Convert list fields to strings for CSV
    list_columns = ['skills_tags', 'red_flags', 'buzzwords']
    for col in list_columns:
        if col in df_output.columns:
            df_output[col] = df_output[col].apply(lambda x: ','.join(x) if isinstance(x, list) else x)

    df_output.to_csv(csv_filename, index=False)
    print(f" Saved: {csv_filename}")

    # Save market intelligence
    with open(f'{DATA_DIR}/market_intelligence.json', 'w') as f:
        json.dump(intel, f, indent=2)
    print(f" Saved: {DATA_DIR}/market_intelligence.json")

    print(f"\n{'='*70}")
    print(" ENRICHMENT COMPLETE!")
    print(f"{'='*70}")
    print(f" Total jobs: {len(jobs)}")
    print(f" Jobs with salary: {len(salaries)}")
    print(f"\n Ready for page generation!")
    print("="*70)


if __name__ == "__main__":
    main()
