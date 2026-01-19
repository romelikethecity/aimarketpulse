#!/usr/bin/env python3
"""
Generate AI Tools directory pages for PE Collective
Creates pages for popular AI tools, frameworks, and platforms
"""

import os
import json
import glob
import pandas as pd
from datetime import datetime
import sys
sys.path.insert(0, 'scripts')

from templates import slugify, BASE_URL

DATA_DIR = 'data'
SITE_DIR = 'site'
TOOLS_DIR = f'{SITE_DIR}/tools'

# AI Tools data - curated list of tools mentioned in AI job postings
AI_TOOLS = {
    # LLM Providers
    'OpenAI': {
        'category': 'LLM Providers',
        'description': 'Creator of GPT-4, ChatGPT, and the OpenAI API. Leading provider of large language models for enterprise and consumer applications.',
        'website': 'https://openai.com',
        'skills': ['GPT-4', 'ChatGPT', 'OpenAI API', 'DALL-E', 'Whisper'],
        'use_cases': ['Chatbots', 'Content generation', 'Code assistance', 'Image generation'],
    },
    'Anthropic': {
        'category': 'LLM Providers',
        'description': 'AI safety company behind Claude, known for constitutional AI and responsible development practices.',
        'website': 'https://anthropic.com',
        'skills': ['Claude', 'Constitutional AI', 'Anthropic API'],
        'use_cases': ['Enterprise AI', 'Content moderation', 'Research assistance'],
    },
    'Google AI': {
        'category': 'LLM Providers',
        'description': 'Google\'s AI division offering Gemini models, Vertex AI, and various ML services.',
        'website': 'https://ai.google',
        'skills': ['Gemini', 'Vertex AI', 'Google Cloud AI', 'PaLM'],
        'use_cases': ['Multimodal AI', 'Enterprise search', 'Code generation'],
    },

    # Frameworks
    'LangChain': {
        'category': 'LLM Frameworks',
        'description': 'Popular framework for building applications with large language models. Provides chains, agents, and memory components.',
        'website': 'https://langchain.com',
        'skills': ['Chains', 'Agents', 'Memory', 'RAG', 'LangSmith'],
        'use_cases': ['RAG applications', 'AI agents', 'Chatbots', 'Document Q&A'],
    },
    'LlamaIndex': {
        'category': 'LLM Frameworks',
        'description': 'Data framework for LLM applications. Specializes in connecting custom data sources to large language models.',
        'website': 'https://llamaindex.ai',
        'skills': ['Data connectors', 'Indexing', 'Query engines', 'RAG'],
        'use_cases': ['Knowledge bases', 'Document search', 'Enterprise RAG'],
    },
    'Hugging Face': {
        'category': 'ML Platforms',
        'description': 'The GitHub of machine learning. Hub for models, datasets, and ML collaboration.',
        'website': 'https://huggingface.co',
        'skills': ['Transformers', 'Datasets', 'Model Hub', 'Spaces', 'Inference API'],
        'use_cases': ['Model hosting', 'Fine-tuning', 'ML collaboration'],
    },

    # Vector Databases
    'Pinecone': {
        'category': 'Vector Databases',
        'description': 'Managed vector database for similarity search. Popular choice for RAG applications.',
        'website': 'https://pinecone.io',
        'skills': ['Vector embeddings', 'Similarity search', 'Metadata filtering'],
        'use_cases': ['Semantic search', 'RAG', 'Recommendation systems'],
    },
    'Weaviate': {
        'category': 'Vector Databases',
        'description': 'Open-source vector database with built-in ML model integration.',
        'website': 'https://weaviate.io',
        'skills': ['Vector search', 'Hybrid search', 'GraphQL API'],
        'use_cases': ['Multimodal search', 'Knowledge graphs', 'RAG'],
    },
    'Chroma': {
        'category': 'Vector Databases',
        'description': 'Open-source embedding database. Simple to use and integrate with LangChain.',
        'website': 'https://trychroma.com',
        'skills': ['Embeddings', 'Local storage', 'Collections'],
        'use_cases': ['Local development', 'Prototyping', 'Small-scale RAG'],
    },

    # ML Frameworks
    'PyTorch': {
        'category': 'ML Frameworks',
        'description': 'Open-source machine learning framework developed by Meta. Preferred for research and production.',
        'website': 'https://pytorch.org',
        'skills': ['Tensors', 'Autograd', 'Neural networks', 'CUDA'],
        'use_cases': ['Deep learning research', 'Model training', 'Production ML'],
    },
    'TensorFlow': {
        'category': 'ML Frameworks',
        'description': 'Google\'s open-source ML platform. Strong ecosystem for production deployment.',
        'website': 'https://tensorflow.org',
        'skills': ['Keras', 'TF Serving', 'TensorBoard', 'TFLite'],
        'use_cases': ['Production ML', 'Mobile deployment', 'Edge AI'],
    },

    # Cloud Platforms
    'AWS SageMaker': {
        'category': 'Cloud ML',
        'description': 'Amazon\'s managed ML platform. Full suite of tools for building, training, and deploying models.',
        'website': 'https://aws.amazon.com/sagemaker',
        'skills': ['Notebooks', 'Training', 'Inference', 'MLOps'],
        'use_cases': ['Enterprise ML', 'Model deployment', 'Automated training'],
    },
    'Azure ML': {
        'category': 'Cloud ML',
        'description': 'Microsoft\'s cloud ML platform. Integrates with Azure OpenAI Service.',
        'website': 'https://azure.microsoft.com/en-us/products/machine-learning',
        'skills': ['Azure OpenAI', 'ML Studio', 'Automated ML'],
        'use_cases': ['Enterprise AI', 'Microsoft ecosystem', 'Responsible AI'],
    },

    # Development Tools
    'Cursor': {
        'category': 'AI Dev Tools',
        'description': 'AI-first code editor built on VS Code. Integrates LLMs directly into the coding workflow.',
        'website': 'https://cursor.sh',
        'skills': ['AI coding', 'Code completion', 'Chat interface'],
        'use_cases': ['Code writing', 'Refactoring', 'Documentation'],
    },
    'GitHub Copilot': {
        'category': 'AI Dev Tools',
        'description': 'AI pair programmer from GitHub/Microsoft. Code suggestions powered by OpenAI Codex.',
        'website': 'https://github.com/features/copilot',
        'skills': ['Code completion', 'Code suggestions', 'Chat'],
        'use_cases': ['Code writing', 'Learning new languages', 'Boilerplate reduction'],
    },
}


def get_tool_job_count(tool_name, jobs_df):
    """Count jobs mentioning a tool"""
    if jobs_df.empty or 'skills_tags' not in jobs_df.columns:
        return 0

    count = 0
    tool_lower = tool_name.lower()
    for skills in jobs_df['skills_tags'].dropna():
        if isinstance(skills, str) and tool_lower in skills.lower():
            count += 1
    return count


def generate_tool_page(tool_name, tool_data, job_count):
    """Generate a page for a single tool"""
    slug = slugify(tool_name)
    if not slug:
        return None

    tool_dir = f"{TOOLS_DIR}/{slug}"
    os.makedirs(tool_dir, exist_ok=True)

    # Generate skills HTML
    skills_html = ""
    if tool_data.get('skills'):
        skills_html = '<div class="skills-list">'
        for skill in tool_data['skills']:
            skills_html += f'<span class="skill-tag">{skill}</span>'
        skills_html += '</div>'

    # Generate use cases HTML
    use_cases_html = ""
    if tool_data.get('use_cases'):
        use_cases_html = '<ul class="use-cases">'
        for use_case in tool_data['use_cases']:
            use_cases_html += f'<li>{use_case}</li>'
        use_cases_html += '</ul>'

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tool_name} - AI Tools | PE Collective</title>
    <meta name="description" content="{tool_data['description'][:150]} Find AI jobs requiring {tool_name} expertise.">

    <link rel="canonical" href="{BASE_URL}/tools/{slug}/">

    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #334155;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --accent: #22d3ee;
            --accent-gold: #f5a623;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }}

        .container {{ max-width: 800px; margin: 0 auto; padding: 0 20px; }}

        nav {{
            background: var(--bg-secondary);
            padding: 1rem 0;
            border-bottom: 1px solid var(--bg-card);
        }}
        nav .container {{ display: flex; justify-content: space-between; align-items: center; max-width: 1200px; }}
        .nav-brand {{ font-size: 1.5rem; font-weight: 700; color: var(--accent); text-decoration: none; }}

        .breadcrumb {{
            padding: 1rem 0;
            color: var(--text-secondary);
            font-size: 0.875rem;
        }}
        .breadcrumb a {{ color: var(--accent); text-decoration: none; }}

        .tool-header {{
            padding: 2rem 0;
        }}
        .tool-category {{
            color: var(--accent);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}
        .tool-header h1 {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        .tool-description {{
            color: var(--text-secondary);
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
        }}
        .tool-stats {{
            display: flex;
            gap: 2rem;
            margin-bottom: 1.5rem;
        }}
        .stat {{
            background: var(--bg-secondary);
            padding: 1rem 1.5rem;
            border-radius: 8px;
        }}
        .stat-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--accent);
        }}
        .stat-label {{
            font-size: 0.875rem;
            color: var(--text-secondary);
        }}
        .tool-link {{
            display: inline-block;
            color: var(--accent);
            text-decoration: none;
            margin-top: 1rem;
        }}

        .section {{
            padding: 2rem 0;
            border-top: 1px solid var(--bg-card);
        }}
        .section h2 {{
            font-size: 1.25rem;
            margin-bottom: 1rem;
        }}
        .skills-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        .skill-tag {{
            background: var(--bg-card);
            color: var(--accent);
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
        }}
        .use-cases {{
            list-style: none;
            padding: 0;
        }}
        .use-cases li {{
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--bg-card);
            color: var(--text-secondary);
        }}

        .cta-box {{
            background: var(--bg-secondary);
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            margin-top: 2rem;
        }}
        .cta-box h3 {{
            margin-bottom: 0.5rem;
        }}
        .cta-box p {{
            color: var(--text-secondary);
            margin-bottom: 1rem;
        }}
        .cta-button {{
            display: inline-block;
            background: var(--accent);
            color: var(--bg-primary);
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
        }}

        footer {{
            background: var(--bg-secondary);
            padding: 2rem 0;
            margin-top: 3rem;
            text-align: center;
            color: var(--text-secondary);
        }}

        @media (max-width: 768px) {{
            .tool-header h1 {{ font-size: 1.75rem; }}
            .tool-stats {{ flex-direction: column; gap: 1rem; }}
        }}
    </style>
</head>
<body>
    <nav>
        <div class="container">
            <a href="/" class="nav-brand">PE Collective</a>
        </div>
    </nav>

    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> / <a href="/tools/">Tools</a> / {tool_name}
        </div>

        <header class="tool-header">
            <div class="tool-category">{tool_data['category']}</div>
            <h1>{tool_name}</h1>
            <p class="tool-description">{tool_data['description']}</p>

            <div class="tool-stats">
                <div class="stat">
                    <div class="stat-value">{job_count}</div>
                    <div class="stat-label">Jobs Mentioning {tool_name}</div>
                </div>
            </div>

            <a href="{tool_data.get('website', '#')}" target="_blank" rel="noopener" class="tool-link">
                Visit {tool_name} →
            </a>
        </header>

        <section class="section">
            <h2>Related Skills</h2>
            {skills_html}
        </section>

        <section class="section">
            <h2>Common Use Cases</h2>
            {use_cases_html}
        </section>

        <div class="cta-box">
            <h3>Find {tool_name} Jobs</h3>
            <p>Browse AI roles that require {tool_name} expertise</p>
            <a href="/jobs/" class="cta-button">View All AI Jobs</a>
        </div>
    </div>

    <footer>
        <p>© 2026 PE Collective</p>
    </footer>
</body>
</html>
'''

    output_path = f"{tool_dir}/index.html"
    with open(output_path, 'w') as f:
        f.write(html)

    return slug


def generate_tools_index(tools_with_counts):
    """Generate the tools index page"""
    os.makedirs(TOOLS_DIR, exist_ok=True)

    # Group by category
    categories = {}
    for tool_name, data in tools_with_counts.items():
        category = data['category']
        if category not in categories:
            categories[category] = []
        categories[category].append((tool_name, data))

    # Generate HTML for each category
    categories_html = ""
    for category, tools in sorted(categories.items()):
        tools_sorted = sorted(tools, key=lambda x: x[1]['job_count'], reverse=True)

        tools_cards = ""
        for tool_name, data in tools_sorted:
            slug = slugify(tool_name)
            tools_cards += f'''
            <a href="/tools/{slug}/" class="tool-card">
                <h3>{tool_name}</h3>
                <p>{data['description'][:100]}...</p>
                <span class="job-count">{data['job_count']} jobs</span>
            </a>
            '''

        categories_html += f'''
        <section class="category-section">
            <h2>{category}</h2>
            <div class="tools-grid">
                {tools_cards}
            </div>
        </section>
        '''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Tools Directory | PE Collective</title>
    <meta name="description" content="Explore popular AI tools, frameworks, and platforms. Find jobs requiring expertise in LangChain, OpenAI, PyTorch, and more.">

    <link rel="canonical" href="{BASE_URL}/tools/">

    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #334155;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --accent: #22d3ee;
            --accent-gold: #f5a623;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }}

        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}

        nav {{
            background: var(--bg-secondary);
            padding: 1rem 0;
            border-bottom: 1px solid var(--bg-card);
        }}
        nav .container {{ display: flex; justify-content: space-between; align-items: center; }}
        .nav-brand {{ font-size: 1.5rem; font-weight: 700; color: var(--accent); text-decoration: none; }}

        .page-header {{
            padding: 3rem 0;
            text-align: center;
        }}
        .page-header h1 {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        .page-header p {{
            color: var(--text-secondary);
            font-size: 1.1rem;
        }}

        .category-section {{
            padding: 2rem 0;
        }}
        .category-section h2 {{
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            color: var(--accent);
        }}
        .tools-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.5rem;
        }}
        .tool-card {{
            background: var(--bg-secondary);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--bg-card);
            text-decoration: none;
            color: var(--text-primary);
            transition: transform 0.2s, border-color 0.2s;
        }}
        .tool-card:hover {{
            transform: translateY(-4px);
            border-color: var(--accent);
        }}
        .tool-card h3 {{
            margin-bottom: 0.5rem;
        }}
        .tool-card p {{
            color: var(--text-secondary);
            font-size: 0.875rem;
            margin-bottom: 1rem;
        }}
        .job-count {{
            color: var(--accent-gold);
            font-size: 0.875rem;
            font-weight: 600;
        }}

        footer {{
            background: var(--bg-secondary);
            padding: 2rem 0;
            margin-top: 3rem;
            text-align: center;
            color: var(--text-secondary);
        }}
    </style>
</head>
<body>
    <nav>
        <div class="container">
            <a href="/" class="nav-brand">PE Collective</a>
        </div>
    </nav>

    <div class="container">
        <header class="page-header">
            <h1>AI Tools Directory</h1>
            <p>Explore popular AI tools, frameworks, and platforms used in AI/ML jobs</p>
        </header>

        {categories_html}
    </div>

    <footer>
        <p>© 2026 PE Collective</p>
    </footer>
</body>
</html>
'''

    output_path = f"{TOOLS_DIR}/index.html"
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"  Saved tools index: {output_path}")


def main():
    print("="*70)
    print("  GENERATING TOOLS PAGES")
    print("="*70)

    # Load job data for counting
    jobs_df = pd.DataFrame()
    job_files = glob.glob(f"{DATA_DIR}/ai_jobs_*.csv")
    if job_files:
        latest_file = sorted(job_files)[-1]
        jobs_df = pd.read_csv(latest_file)
        print(f"  Loaded {len(jobs_df)} jobs for tool counting")

    # Generate pages and collect counts
    tools_with_counts = {}
    generated = 0

    for tool_name, tool_data in AI_TOOLS.items():
        job_count = get_tool_job_count(tool_name, jobs_df)
        tool_data['job_count'] = job_count
        tools_with_counts[tool_name] = tool_data

        slug = generate_tool_page(tool_name, tool_data, job_count)
        if slug:
            generated += 1

    # Generate index
    generate_tools_index(tools_with_counts)

    print(f"\n{'='*70}")
    print(f"  Generated {generated} tool pages")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
