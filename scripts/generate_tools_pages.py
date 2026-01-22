#!/usr/bin/env python3
"""
Generate AI Tools directory pages for AI Market Pulse
Creates pages for popular AI tools, frameworks, and platforms
"""

import os
import json
import glob
import pandas as pd
from datetime import datetime
import sys
sys.path.insert(0, 'scripts')

from templates import (
    slugify, BASE_URL, get_html_head, get_nav_html, get_footer_html,
    get_cta_box, get_base_styles, CSS_VARIABLES, CSS_NAV, CSS_LAYOUT,
    CSS_CARDS, CSS_CTA, CSS_FOOTER
)
from nav_config import SITE_NAME

DATA_DIR = 'data'
SITE_DIR = 'site'
TOOLS_DIR = f'{SITE_DIR}/tools'

# AI Tools data - curated list of tools mentioned in AI job postings
# Note: Tools with 'custom_page': True have hand-crafted review pages and won't be overwritten
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
        'skills': ['AI coding', 'Code completion', 'Chat interface', 'Composer', 'Multi-file editing'],
        'use_cases': ['Code writing', 'Refactoring', 'Documentation', 'Multi-file scaffolding'],
        'custom_page': True,  # Has in-depth review page - don't overwrite
    },
    'GitHub Copilot': {
        'category': 'AI Dev Tools',
        'description': 'AI pair programmer from GitHub/Microsoft. Code suggestions powered by OpenAI Codex.',
        'website': 'https://github.com/features/copilot',
        'skills': ['Code completion', 'Code suggestions', 'Chat'],
        'use_cases': ['Code writing', 'Learning new languages', 'Boilerplate reduction'],
    },
}

# Extended SEO content for tool pages
TOOL_SEO_CONTENT = {
    'openai': {
        'overview': '''OpenAI has become synonymous with the AI revolution. Their GPT-4 model powers countless applications, from customer service chatbots to sophisticated coding assistants. For AI professionals, OpenAI API expertise is one of the most in-demand skills, appearing in job postings across every AI role category.''',
        'why_learn': '''OpenAI's API is the de facto standard for LLM integration. Most AI engineering roles expect familiarity with their models, rate limiting strategies, and best practices for prompt engineering. Understanding GPT-4's capabilities and limitations is essential for designing effective AI features.''',
        'career_relevance': '''OpenAI skills are relevant across AI Engineer, Prompt Engineer, LLM Engineer, and even AI Product Manager roles. Companies building with LLMs often start with OpenAI before exploring alternatives, making this expertise a foundation for AI careers.''',
    },
    'anthropic': {
        'overview': '''Anthropic's Claude models have emerged as the primary alternative to OpenAI for enterprise applications. Founded by former OpenAI researchers, Anthropic emphasizes AI safety and constitutional AI approaches. Claude excels at long-context tasks and nuanced reasoning.''',
        'why_learn': '''Many enterprises are diversifying their LLM providers, and Claude's strong performance on coding, analysis, and writing tasks makes Anthropic expertise increasingly valuable. Understanding Claude's unique capabilities—like its 200K context window—enables building applications OpenAI can't match.''',
        'career_relevance': '''Anthropic skills are particularly valued at companies prioritizing AI safety or requiring long-context processing. The API is similar enough to OpenAI that skills transfer easily, but understanding model-specific behaviors is important for optimization.''',
    },
    'google-ai': {
        'overview': '''Google AI offers the Gemini family of models along with Vertex AI for enterprise ML deployment. Their multimodal capabilities and tight integration with Google Cloud make them attractive for companies already in the GCP ecosystem.''',
        'why_learn': '''Google's AI offerings are expanding rapidly. Gemini models offer competitive performance, and Vertex AI provides a comprehensive platform for ML workflows. For companies using Google Cloud, these tools are the natural choice.''',
        'career_relevance': '''Google AI expertise is particularly valuable for roles at Google Cloud customers or companies building multimodal applications. Vertex AI knowledge is relevant for MLOps roles, while Gemini API skills apply to AI engineering positions.''',
    },
    'langchain': {
        'overview': '''LangChain has become the most popular framework for building LLM applications. It provides abstractions for chains, agents, memory, and retrieval, enabling rapid development of sophisticated AI features. The ecosystem includes LangSmith for observability and LangGraph for complex workflows.''',
        'why_learn': '''LangChain is appearing in an increasing number of job postings for AI Engineer and LLM Engineer roles. Its abstractions accelerate development, and understanding its patterns helps even when building custom solutions. LangSmith is becoming standard for LLM observability.''',
        'career_relevance': '''LangChain expertise is directly relevant for AI Engineer, LLM Engineer, and Prompt Engineer roles. Companies building RAG applications, chatbots, or AI agents frequently use LangChain, making it a high-impact skill to develop.''',
    },
    'llamaindex': {
        'overview': '''LlamaIndex specializes in connecting LLMs to data. Originally known as GPT Index, it provides sophisticated indexing, retrieval, and query capabilities for building knowledge-intensive applications. It excels at enterprise RAG and document Q&A use cases.''',
        'why_learn': '''LlamaIndex offers more sophisticated data handling than LangChain for certain use cases. Understanding both frameworks allows choosing the right tool for each project. LlamaIndex's focus on data connections makes it valuable for enterprise applications.''',
        'career_relevance': '''LlamaIndex skills are relevant for AI Engineer and LLM Engineer roles, particularly at companies building document-heavy applications. It's often used alongside LangChain rather than as a replacement.''',
    },
    'hugging-face': {
        'overview': '''Hugging Face is the GitHub of machine learning. Their Hub hosts thousands of models and datasets, while the Transformers library provides easy access to state-of-the-art models. They've become essential infrastructure for the ML community.''',
        'why_learn': '''Hugging Face is ubiquitous in ML workflows. The Transformers library is the standard for working with pre-trained models, and the Hub is where models are shared. Understanding their ecosystem is essential for ML Engineers and Research Engineers.''',
        'career_relevance': '''Hugging Face skills appear in most ML Engineer job postings. Familiarity with the Transformers library, model Hub, and Spaces is expected for roles involving model training, fine-tuning, or deployment.''',
    },
    'pinecone': {
        'overview': '''Pinecone is a managed vector database purpose-built for similarity search. As RAG architectures have become standard for LLM applications, Pinecone has emerged as a leading choice for storing and querying embeddings at scale.''',
        'why_learn': '''Vector databases are essential for RAG applications, and Pinecone's managed service simplifies deployment. Understanding vector search concepts and Pinecone's capabilities enables building production-ready AI applications.''',
        'career_relevance': '''Pinecone expertise is relevant for AI Engineer and LLM Engineer roles building RAG systems. Companies value experience with production vector databases, and Pinecone's popularity makes it a safe choice for skill development.''',
    },
    'weaviate': {
        'overview': '''Weaviate is an open-source vector database with built-in ML model integration. It supports hybrid search combining vector and keyword approaches, making it powerful for enterprise search applications.''',
        'why_learn': '''Weaviate offers more flexibility than managed solutions like Pinecone, with self-hosting options and advanced features. Understanding Weaviate complements Pinecone knowledge and prepares you for different deployment scenarios.''',
        'career_relevance': '''Weaviate skills are valuable for MLOps and AI Engineer roles, particularly at companies preferring self-hosted infrastructure. Its hybrid search capabilities are relevant for enterprise search applications.''',
    },
    'chroma': {
        'overview': '''Chroma is an open-source embedding database designed for simplicity. It's popular for local development and prototyping, with a straightforward API that integrates well with LangChain and other frameworks.''',
        'why_learn': '''Chroma is excellent for learning vector database concepts and rapid prototyping. While not typically used for production at scale, understanding Chroma helps when learning RAG patterns before moving to more robust solutions.''',
        'career_relevance': '''Chroma knowledge demonstrates familiarity with RAG architectures. While production roles often use Pinecone or Weaviate, Chroma experience shows you understand the underlying concepts.''',
    },
    'pytorch': {
        'overview': '''PyTorch has become the dominant deep learning framework, especially for research and LLM work. Developed by Meta, it offers a Pythonic interface, dynamic computation graphs, and excellent GPU support. Most new ML research is implemented in PyTorch.''',
        'why_learn': '''PyTorch is essential for ML Engineer and Research Engineer roles. It's the framework of choice for training custom models, fine-tuning LLMs, and implementing research papers. Strong PyTorch skills are non-negotiable for serious ML work.''',
        'career_relevance': '''PyTorch appears in the majority of ML Engineer job postings. Research Engineer roles essentially require it. Even AI Engineers focused on inference benefit from understanding PyTorch for model optimization and debugging.''',
    },
    'tensorflow': {
        'overview': '''TensorFlow is Google's open-source ML platform with strong production deployment capabilities. While PyTorch has gained research mindshare, TensorFlow remains popular for production ML, especially with TF Serving and TFLite for mobile deployment.''',
        'why_learn': '''TensorFlow's production ecosystem is mature and well-documented. TF Serving, TFLite, and TensorBoard are industry standards. Understanding TensorFlow complements PyTorch skills and prepares you for diverse ML environments.''',
        'career_relevance': '''TensorFlow skills are valuable for MLOps roles and production ML engineering. Companies with existing TensorFlow infrastructure continue to hire for these skills, and mobile ML often requires TFLite knowledge.''',
    },
    'aws-sagemaker': {
        'overview': '''AWS SageMaker is Amazon's managed ML platform, offering tools for the entire ML lifecycle from data labeling to model deployment. Its integration with the AWS ecosystem makes it popular for enterprise ML workloads.''',
        'why_learn': '''SageMaker is the most widely used cloud ML platform. Understanding its capabilities—notebooks, training, inference, pipelines—prepares you for enterprise ML roles. AWS certifications including SageMaker knowledge are valued.''',
        'career_relevance': '''AWS SageMaker expertise is highly relevant for MLOps and ML Engineer roles at AWS-using companies. Enterprise AI roles often require cloud platform experience, and SageMaker is the most common choice.''',
    },
    'azure-ml': {
        'overview': '''Azure ML is Microsoft's cloud ML platform, with strong integration with Azure OpenAI Service and the Microsoft ecosystem. It offers automated ML, responsible AI tools, and enterprise-grade security.''',
        'why_learn': '''Azure ML is common at Microsoft-oriented enterprises. Its responsible AI features and Azure OpenAI integration are differentiators. Understanding Azure ML complements AWS knowledge for cloud-agnostic expertise.''',
        'career_relevance': '''Azure ML skills are valuable for roles at Microsoft ecosystem companies. Enterprise AI roles at large corporations often involve Azure, making this knowledge relevant for corporate AI engineering positions.''',
    },
    'cursor': {
        'overview': '''Cursor is an AI-first code editor that has gained significant traction among developers. Built on VS Code, it integrates LLMs directly into the coding workflow with features like Composer for multi-file editing and natural language code generation.''',
        'why_learn': '''Cursor represents the future of AI-assisted development. Understanding how to leverage AI coding tools effectively is becoming essential for productivity. Cursor's advanced features like multi-file editing push beyond simple code completion.''',
        'career_relevance': '''While Cursor is a tool rather than a skill employers hire for directly, proficiency with AI coding tools demonstrates modern development practices. AI Engineers building coding assistants should understand Cursor's approach.''',
    },
    'github-copilot': {
        'overview': '''GitHub Copilot is the most widely adopted AI coding assistant, integrated directly into VS Code, JetBrains IDEs, and GitHub. Powered by OpenAI Codex, it provides inline code suggestions and chat-based assistance.''',
        'why_learn': '''Copilot has become standard in many development workflows. Learning to use it effectively—knowing when to accept suggestions, how to prompt for better results—improves coding productivity significantly.''',
        'career_relevance': '''Copilot proficiency is increasingly expected in software engineering roles. For AI engineers building similar tools, understanding Copilot's UX and capabilities provides valuable product insight.''',
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


# Tools page specific styles
TOOLS_PAGE_STYLES = '''
    /* Tools Page Specific Styles */
    .tools-hero {
        background: linear-gradient(180deg, var(--bg-darker) 0%, var(--bg-dark) 100%);
        padding: 3rem 0 2rem;
        text-align: center;
        border-bottom: 1px solid var(--border);
    }

    .tools-hero h1 {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        color: var(--text-primary);
    }

    .tools-hero p {
        color: var(--text-secondary);
        font-size: 1.1rem;
        max-width: 600px;
        margin: 0 auto;
    }

    .category-section {
        padding: 2.5rem 0;
        border-bottom: 1px solid var(--border-light);
    }

    .category-section:last-child {
        border-bottom: none;
    }

    .category-section h2 {
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
        color: var(--gold);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .category-section h2::before {
        content: '';
        width: 4px;
        height: 24px;
        background: var(--gold);
        border-radius: 2px;
    }

    .tools-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 1.5rem;
    }

    .tool-card {
        background: var(--bg-card);
        padding: 1.75rem;
        border-radius: 12px;
        border: 1px solid var(--border);
        text-decoration: none;
        color: var(--text-primary);
        transition: all 0.25s;
        display: flex;
        flex-direction: column;
    }

    .tool-card:hover {
        transform: translateY(-4px);
        border-color: var(--gold);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        background: var(--bg-card-hover);
    }

    .tool-card h3 {
        font-size: 1.25rem;
        margin-bottom: 0.75rem;
        color: var(--text-primary);
    }

    .tool-card p {
        color: var(--text-secondary);
        font-size: 0.9rem;
        line-height: 1.6;
        margin-bottom: 1rem;
        flex-grow: 1;
    }

    .tool-card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 1rem;
        border-top: 1px solid var(--border-light);
        margin-top: auto;
    }

    .job-count {
        color: var(--gold);
        font-size: 0.9rem;
        font-weight: 600;
    }

    .tool-card-arrow {
        color: var(--text-muted);
        font-size: 1.25rem;
        transition: transform 0.2s, color 0.2s;
    }

    .tool-card:hover .tool-card-arrow {
        transform: translateX(4px);
        color: var(--gold);
    }

    /* Individual Tool Page Styles */
    .tool-detail-header {
        background: var(--bg-darker);
        padding: 3rem 0;
        border-bottom: 1px solid var(--border);
    }

    .tool-category-badge {
        display: inline-block;
        background: rgba(232, 168, 124, 0.15);
        color: var(--gold);
        padding: 0.35rem 0.85rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
    }

    .tool-detail-header h1 {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }

    .tool-description {
        color: var(--text-secondary);
        font-size: 1.15rem;
        line-height: 1.7;
        max-width: 700px;
    }

    .tool-stats {
        display: flex;
        gap: 1.5rem;
        margin-top: 2rem;
        flex-wrap: wrap;
    }

    .tool-stat {
        background: var(--bg-card);
        border: 1px solid var(--border);
        padding: 1.25rem 1.75rem;
        border-radius: 12px;
        text-align: center;
        min-width: 140px;
    }

    .tool-stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--gold);
        font-family: 'Space Grotesk', sans-serif;
    }

    .tool-stat-label {
        font-size: 0.85rem;
        color: var(--text-muted);
        margin-top: 0.25rem;
    }

    .tool-link-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 1.5rem;
        padding: 0.75rem 1.5rem;
        background: var(--teal-primary);
        color: var(--text-primary);
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }

    .tool-link-btn:hover {
        background: var(--teal-light);
        color: var(--text-primary);
    }

    .tool-content {
        padding: 3rem 0;
    }

    .tool-section {
        margin-bottom: 3rem;
    }

    .tool-section h2 {
        font-size: 1.35rem;
        margin-bottom: 1.25rem;
        color: var(--text-primary);
    }

    .skills-list {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
    }

    .skill-tag {
        background: var(--bg-card);
        color: var(--gold);
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.9rem;
        border: 1px solid var(--border);
        transition: all 0.2s;
    }

    .skill-tag:hover {
        border-color: var(--gold);
        background: var(--bg-card-hover);
    }

    .use-cases {
        list-style: none;
        padding: 0;
    }

    .use-cases li {
        padding: 1rem 1.25rem;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 8px;
        margin-bottom: 0.75rem;
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .use-cases li::before {
        content: '→';
        color: var(--gold);
        font-weight: bold;
    }

    @media (max-width: 768px) {
        .tools-hero h1 { font-size: 2rem; }
        .tools-grid { grid-template-columns: 1fr; }
        .tool-detail-header h1 { font-size: 1.75rem; }
        .tool-stats { flex-direction: column; }
    }
'''


def get_tool_seo_content(slug, tool_name):
    """Get SEO content for a tool page"""
    if slug in TOOL_SEO_CONTENT:
        content = TOOL_SEO_CONTENT[slug]
        return f'''
            <section class="tool-section">
                <h2>Overview</h2>
                <div style="color: var(--text-secondary); line-height: 1.8;">
                    <p style="margin-bottom: 1rem;">{content['overview']}</p>
                </div>
            </section>

            <section class="tool-section">
                <h2>Why Learn {tool_name}</h2>
                <div style="color: var(--text-secondary); line-height: 1.8;">
                    <p style="margin-bottom: 1rem;">{content['why_learn']}</p>
                </div>
            </section>

            <section class="tool-section">
                <h2>Career Relevance</h2>
                <div style="color: var(--text-secondary); line-height: 1.8;">
                    <p style="margin-bottom: 1rem;">{content['career_relevance']}</p>
                </div>
            </section>
        '''
    return ''


def generate_tool_page(tool_name, tool_data, job_count):
    """Generate a page for a single tool"""
    slug = slugify(tool_name)
    if not slug:
        return None

    # Skip tools with custom review pages
    if tool_data.get('custom_page'):
        print(f"  Skipping {tool_name} (has custom review page)")
        return slug

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

    # Get SEO content for this tool
    seo_content = get_tool_seo_content(slug, tool_name)

    # Build extra styles
    extra_styles = f'<style>{TOOLS_PAGE_STYLES}</style>'

    # Use templates for consistent styling
    html = get_html_head(
        title=f'{tool_name} - AI Tools',
        description=f'{tool_data["description"][:150]} Find AI jobs requiring {tool_name} expertise.',
        page_path=f'tools/{slug}/',
        extra_head=extra_styles
    )

    html += get_nav_html(active_page='tools')

    html += f'''
    <div class="tool-detail-header">
        <div class="container">
            <nav class="breadcrumb">
                <a href="/">Home</a> / <a href="/tools/">Tools</a> / {tool_name}
            </nav>
            <span class="tool-category-badge">{tool_data['category']}</span>
            <h1>{tool_name}</h1>
            <p class="tool-description">{tool_data['description']}</p>

            <div class="tool-stats">
                <div class="tool-stat">
                    <div class="tool-stat-value">{job_count}</div>
                    <div class="tool-stat-label">Jobs Mentioning {tool_name}</div>
                </div>
            </div>

            <a href="{tool_data.get('website', '#')}" target="_blank" rel="noopener" class="tool-link-btn">
                Visit {tool_name} →
            </a>
        </div>
    </div>

    <main class="tool-content">
        <div class="container">
            {seo_content}

            <section class="tool-section">
                <h2>Related Skills</h2>
                {skills_html}
            </section>

            <section class="tool-section">
                <h2>Common Use Cases</h2>
                {use_cases_html}
            </section>

            {get_cta_box(
                title=f"Find {tool_name} Jobs",
                description=f"Browse AI roles that require {tool_name} expertise and stay updated on new opportunities.",
                button_text="View All AI Jobs",
                button_url="/jobs/"
            )}
        </div>
    </main>
'''

    html += get_footer_html()

    output_path = f"{tool_dir}/index.html"
    with open(output_path, 'w') as f:
        f.write(html)

    return slug


def generate_tools_index(tools_with_counts):
    """Generate the tools index page"""
    os.makedirs(TOOLS_DIR, exist_ok=True)

    # AI for [Task] Guides section - manual curated comparison pages
    ai_for_task_guides = [
        {'url': '/ai-for-coding/', 'title': 'AI for Coding', 'desc': 'Compare the best AI coding assistants including Cursor, GitHub Copilot, Claude Code, and more.', 'count': '6 tools compared'},
        {'url': '/ai-for-writing/', 'title': 'AI for Writing', 'desc': 'Find the perfect AI writing assistant for content creation, copywriting, and creative writing.', 'count': '8 tools compared'},
        {'url': '/ai-for-video/', 'title': 'AI for Video', 'desc': 'Discover AI video generation, editing, and avatar tools for content creators and marketers.', 'count': '12 tools compared'},
        {'url': '/ai-for-design/', 'title': 'AI for Design', 'desc': 'Explore AI design tools for image generation, UI/UX, graphic design, and 3D creation.', 'count': '18 tools compared'},
        {'url': '/ai-for-sales/', 'title': 'AI for Sales', 'desc': 'Compare AI sales tools for prospecting, call intelligence, engagement, and automation.', 'count': '16 tools compared'},
        {'url': '/ai-for-customer-support/', 'title': 'AI for Customer Support', 'desc': 'Find AI chatbots, help desk automation, and agent assist tools for customer service.', 'count': '14 tools compared'},
        {'url': '/ai-for-hr/', 'title': 'AI for HR', 'desc': 'Compare AI recruiting, performance management, and employee experience platforms.', 'count': '16 tools compared'},
        {'url': '/ai-for-marketing/', 'title': 'AI for Marketing', 'desc': 'Discover AI tools for content creation, SEO, email, social media, and advertising.', 'count': '20 tools compared'},
    ]

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
            job_text = "job" if data['job_count'] == 1 else "jobs"
            tools_cards += f'''
            <a href="/tools/{slug}/" class="tool-card">
                <h3>{tool_name}</h3>
                <p>{data['description'][:120]}...</p>
                <div class="tool-card-footer">
                    <span class="job-count">{data['job_count']} {job_text}</span>
                    <span class="tool-card-arrow">→</span>
                </div>
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

    # Generate AI for [Task] Guides section HTML
    guides_cards = ""
    for guide in ai_for_task_guides:
        guides_cards += f'''
            <a href="{guide['url']}" class="tool-card">
                <h3>{guide['title']}</h3>
                <p>{guide['desc']}</p>
                <div class="tool-card-footer">
                    <span class="job-count">{guide['count']}</span>
                    <span class="tool-card-arrow">→</span>
                </div>
            </a>
'''

    ai_for_task_section = f'''
        <section class="category-section">
            <h2>AI for [Task] Guides</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">Comprehensive comparison guides to find the best AI tools for your specific use case.</p>
            <div class="tools-grid">
{guides_cards}
            </div>
        </section>
'''

    # Build extra styles
    extra_styles = f'<style>{TOOLS_PAGE_STYLES}</style>'

    # Use templates for consistent styling
    html = get_html_head(
        title='AI Tools Directory',
        description='Explore popular AI tools, frameworks, and platforms. Find jobs requiring expertise in LangChain, OpenAI, PyTorch, and more.',
        page_path='tools/',
        extra_head=extra_styles
    )

    html += get_nav_html(active_page='tools')

    html += f'''
    <div class="tools-hero">
        <div class="container">
            <h1>AI Tools Directory</h1>
            <p>Explore popular AI tools, frameworks, and platforms used in AI/ML jobs</p>
        </div>
    </div>

    <main>
        <div class="container">
            <!-- SEO Intro Content -->
            <div class="seo-intro" style="max-width: 800px; margin-bottom: 3rem; color: var(--text-secondary); line-height: 1.8;">
                <p style="margin-bottom: 1rem;">
                    The AI tools landscape is evolving rapidly, and knowing which technologies to learn can make or break your career trajectory. AI Market Pulse tracks tool mentions across thousands of job postings to show you what employers are actually hiring for—not what's trending on Twitter.
                </p>
                <p style="margin-bottom: 1rem;">
                    From foundational frameworks like <strong style="color: var(--text-primary);">PyTorch</strong> and <strong style="color: var(--text-primary);">TensorFlow</strong> to the new wave of LLM tools like <strong style="color: var(--text-primary);">LangChain</strong>, <strong style="color: var(--text-primary);">LlamaIndex</strong>, and vector databases, our directory covers the complete AI/ML technology stack. Each tool page shows how many current job postings require that skill, helping you prioritize your learning investments.
                </p>
                <h2 style="font-size: 1.25rem; color: var(--text-primary); margin: 2rem 0 1rem;">What's in Demand in 2026</h2>
                <p style="margin-bottom: 1rem;">
                    The job market tells a clear story: <strong style="color: var(--text-primary);">Python</strong> remains non-negotiable for AI roles, appearing in 90%+ of postings. <strong style="color: var(--text-primary);">PyTorch</strong> has overtaken TensorFlow as the preferred deep learning framework, especially for research and LLM work. The biggest shift is the emergence of <strong style="color: var(--text-primary);">LLM orchestration tools</strong>—LangChain, LlamaIndex, and similar frameworks—which went from niche to mainstream in 2024-2025.
                </p>
                <p style="margin-bottom: 1rem;">
                    Cloud platforms (<strong style="color: var(--text-primary);">AWS SageMaker</strong>, <strong style="color: var(--text-primary);">Azure ML</strong>, <strong style="color: var(--text-primary);">Google Vertex AI</strong>) remain essential for production ML. Vector databases like <strong style="color: var(--text-primary);">Pinecone</strong>, <strong style="color: var(--text-primary);">Weaviate</strong>, and <strong style="color: var(--text-primary);">Chroma</strong> are increasingly required as RAG architectures become standard for enterprise AI applications.
                </p>
            </div>

            {ai_for_task_section}
            {categories_html}

            {get_cta_box(
                title="Stay Updated on AI Tools",
                description="Get weekly insights on the latest AI tools, frameworks, and job opportunities.",
                button_text="Join the Community",
                button_url="/join/"
            )}

            <!-- SEO Bottom Content -->
            <div class="seo-bottom" style="max-width: 800px; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--border); color: var(--text-secondary); line-height: 1.8;">
                <h2 style="font-size: 1.25rem; color: var(--text-primary); margin-bottom: 1rem;">How to Choose the Right AI Tools</h2>
                <p style="margin-bottom: 1rem;">
                    When deciding which AI tools to learn, consider three factors: <strong style="color: var(--text-primary);">job market demand</strong> (what are employers actually hiring for?), <strong style="color: var(--text-primary);">career trajectory</strong> (where is the industry heading?), and <strong style="color: var(--text-primary);">practical application</strong> (what can you build with it?).
                </p>
                <p style="margin-bottom: 1rem;">
                    For most AI careers, start with the fundamentals: Python, PyTorch or TensorFlow, and cloud platforms (pick one major provider and learn it well). Then specialize based on your target role. Prompt Engineers should focus on LLM APIs (OpenAI, Anthropic, Google), orchestration frameworks (LangChain, LlamaIndex), and evaluation tools. ML Engineers need deeper infrastructure skills: Kubernetes, MLflow, and model serving.
                </p>
                <h2 style="font-size: 1.25rem; color: var(--text-primary); margin: 2rem 0 1rem;">The AI Tools Stack in 2026</h2>
                <p style="margin-bottom: 1rem;">
                    A typical production AI stack in 2026 includes: a <strong style="color: var(--text-primary);">foundation model provider</strong> (OpenAI, Anthropic, or open-source models via Hugging Face), an <strong style="color: var(--text-primary);">orchestration layer</strong> (LangChain or LlamaIndex for complex workflows), a <strong style="color: var(--text-primary);">vector database</strong> (Pinecone for managed, Weaviate or Chroma for self-hosted), <strong style="color: var(--text-primary);">evaluation and observability</strong> (LangSmith, Weights & Biases), and <strong style="color: var(--text-primary);">deployment infrastructure</strong> (cloud ML platforms or Kubernetes).
                </p>
                <p style="margin-bottom: 1rem;">
                    For AI coding tools specifically, the market has consolidated around Cursor and GitHub Copilot, with VS Code + Claude/GPT extensions as a third option. Check our AI for Coding comparison guide for a detailed breakdown.
                </p>
            </div>
        </div>
    </main>
'''

    html += get_footer_html()

    output_path = f"{TOOLS_DIR}/index.html"
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"  Saved tools index: {output_path}")


def main():
    print("="*70)
    print("  AI MARKET PULSE - GENERATING TOOLS PAGES")
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
