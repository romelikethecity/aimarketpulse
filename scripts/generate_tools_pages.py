#!/usr/bin/env python3
"""
Generate AI Tools directory pages for AI Market Pulse
Creates in-depth review pages following best practices:
- Hero with logo, verdict, key stats
- Company overview with background
- Pricing section with tiers
- Core features with icons
- Honest limitations
- Pros/Cons summary
- Decision framework (Buy If / Skip If)
- Alternatives comparison table
- Questions to ask
- Bottom line verdict
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
    get_cta_box, get_base_styles, get_breadcrumb_html, get_img_tag,
    CSS_VARIABLES, CSS_NAV, CSS_LAYOUT, CSS_CARDS, CSS_CTA, CSS_FOOTER
)
from seo_core import generate_collectionpage_schema, generate_itemlist_schema, generate_review_schema, generate_breadcrumb_schema, generate_faq_schema
from nav_config import SITE_NAME

DATA_DIR = 'data'
SITE_DIR = 'site'
TOOLS_DIR = f'{SITE_DIR}/tools'

# Comprehensive tool review data following CRO Report best practices
# Each tool has full review content for in-depth pages
TOOL_REVIEWS = {
    'openai': {
        'name': 'OpenAI',
        'category': 'LLM Providers',
        'tagline': 'The API that started the LLM revolution',
        'website': 'https://openai.com',
        'logo_placeholder': '/assets/logos/openai_logo.png',
        'rating': '4.6',
        'rating_count': '500+',
        'stats': [
            {'value': '4.6/5', 'label': 'G2 Rating'},
            {'value': '200M+', 'label': 'ChatGPT Users'},
            {'value': 'GPT-4o', 'label': 'Latest Model'},
            {'value': '$20', 'label': 'ChatGPT Plus/mo'},
        ],
        'verdict': '''OpenAI's GPT-4 remains the benchmark that other LLMs are measured against. For most AI engineering teams, starting with OpenAI is still the pragmatic choice—best documentation, widest ecosystem support, and most reliable API. But the competitive landscape is tightening fast, and smart teams are building provider-agnostic architectures.''',
        'overview': '''OpenAI has become synonymous with the AI revolution. Founded in 2015 as a nonprofit research lab, the company pivoted to a "capped profit" model in 2019 and launched ChatGPT in November 2022, triggering the current AI boom. Their GPT-4 model powers countless applications, from customer service chatbots to sophisticated coding assistants.

For AI professionals, OpenAI API expertise is one of the most in-demand skills, appearing in job postings across every AI role category. The company's models—GPT-4, GPT-4o, GPT-4 Turbo, and the newer o1 reasoning models—form the foundation of most enterprise LLM deployments.''',
        'pricing': '''OpenAI uses usage-based pricing for API access:

| Model | Input | Output | Context |
|-------|-------|--------|---------|
| GPT-4o | $2.50/1M tokens | $10/1M tokens | 128K |
| GPT-4 Turbo | $10/1M tokens | $30/1M tokens | 128K |
| GPT-3.5 Turbo | $0.50/1M tokens | $1.50/1M tokens | 16K |
| o1-preview | $15/1M tokens | $60/1M tokens | 128K |

ChatGPT Plus costs $20/month for individuals. Team plans start at $25/user/month. Enterprise pricing is custom.

For most production use cases, expect to spend $100-500/month at moderate scale. High-volume applications can easily reach $10K+/month.''',
        'pricing_note': '''API costs can escalate quickly with high-context conversations. The o1 reasoning models are 6x more expensive than GPT-4o. Always implement token counting and cost monitoring before going to production.''',
        'features': [
            {'icon': '🧠', 'title': 'GPT-4 & GPT-4o', 'desc': 'State-of-the-art language models with strong reasoning and coding capabilities.'},
            {'icon': '🔗', 'title': 'Function Calling', 'desc': 'Structured output and tool use for building AI agents and workflows.'},
            {'icon': '👁️', 'title': 'Vision Capabilities', 'desc': 'Analyze images with GPT-4o for multimodal applications.'},
            {'icon': '🎨', 'title': 'DALL-E 3', 'desc': 'Text-to-image generation integrated with ChatGPT and API.'},
            {'icon': '🎤', 'title': 'Whisper', 'desc': 'Industry-leading speech-to-text transcription API.'},
            {'icon': '📊', 'title': 'Fine-tuning', 'desc': 'Customize GPT-3.5 Turbo and GPT-4 for your specific use case.'},
        ],
        'limitations': '''**Rate Limits and Reliability**
OpenAI's API has experienced significant outages during high-demand periods. Rate limits can be restrictive for new accounts, requiring gradual scaling. Enterprise customers get priority, but even they report occasional latency spikes.

**Cost at Scale**
Token costs add up quickly for high-volume applications. A customer service bot handling 10,000 conversations/day can easily cost $5K-15K/month depending on conversation length.

**Data Privacy Concerns**
Some enterprises are hesitant to send sensitive data through OpenAI's API due to unclear data usage policies (though they don't train on API data by default). This drives interest in self-hosted alternatives.

**Model Deprecation**
OpenAI regularly deprecates older models, requiring code updates. GPT-3 was sunset, and older GPT-4 versions get retired with 6-12 months notice.''',
        'pros': [
            'Best-in-class model quality (still the benchmark)',
            'Excellent documentation and developer experience',
            'Widest ecosystem integration (every framework supports OpenAI)',
            'Fastest iteration on new features',
            'Strong function calling and structured output',
            'ChatGPT provides immediate testing environment',
        ],
        'cons': [
            'Premium pricing compared to alternatives',
            'Rate limits can bottleneck scaling',
            'Occasional reliability issues during high demand',
            'Data privacy concerns for regulated industries',
            'Model deprecation requires ongoing maintenance',
            'Closed-source limits customization options',
        ],
        'buy_if': [
            'You need the most capable models for complex reasoning tasks',
            'Developer experience and documentation quality matter to you',
            'You want the widest selection of framework integrations',
            'You\'re building prototypes and need to move fast',
            'Your team is new to LLMs and wants the gentlest learning curve',
        ],
        'skip_if': [
            'Cost is your primary concern (Claude or open-source may be cheaper)',
            'You need guaranteed uptime for mission-critical applications',
            'Data privacy requirements prevent cloud API usage',
            'You want to fine-tune models with sensitive proprietary data',
            'You need very long context windows (Anthropic offers 200K)',
        ],
        'alternatives': [
            {'name': 'Anthropic Claude', 'strength': 'Longer context, better safety', 'pricing': 'Competitive with GPT-4'},
            {'name': 'Google Gemini', 'strength': 'Multimodal, GCP integration', 'pricing': 'Similar to OpenAI'},
            {'name': 'Llama 3 (Meta)', 'strength': 'Open source, self-hostable', 'pricing': 'Compute costs only'},
            {'name': 'Mistral', 'strength': 'European, efficient models', 'pricing': 'Lower than GPT-4'},
        ],
        'questions': [
            'What are our expected monthly token volumes, and have we modeled API costs?',
            'Do we need to implement fallback providers for reliability?',
            'Are there data residency or privacy requirements that affect API usage?',
            'Which model tier (GPT-4o vs GPT-4 Turbo vs GPT-3.5) fits our quality/cost trade-off?',
            'Have we set up cost monitoring and alerting before going to production?',
            'Do we need fine-tuning, or will prompt engineering suffice?',
        ],
        'bottom_line': '''**OpenAI remains the default choice for most AI engineering teams**, and for good reason—the models are excellent, the developer experience is best-in-class, and the ecosystem support is unmatched. If you're new to LLMs, start here.

But the market is maturing. Anthropic's Claude offers compelling advantages for long-context and safety-critical applications. Open-source models are closing the gap. Smart teams are building provider-agnostic architectures and evaluating alternatives for cost and reliability reasons.

For production applications, implement cost monitoring from day one, build in provider fallback capability, and stay current on the rapidly evolving model landscape.''',
        'skills': ['GPT-4', 'ChatGPT', 'OpenAI API', 'DALL-E', 'Whisper', 'Function Calling'],
        'use_cases': ['Chatbots', 'Content generation', 'Code assistance', 'Image generation', 'RAG applications'],
    },

    'anthropic': {
        'name': 'Anthropic',
        'category': 'LLM Providers',
        'tagline': 'Constitutional AI and the Claude model family',
        'website': 'https://anthropic.com',
        'logo_placeholder': '/assets/logos/anthropic_logo.png',
        'rating': '4.7',
        'rating_count': '200+',
        'stats': [
            {'value': '4.7/5', 'label': 'G2 Rating'},
            {'value': '200K', 'label': 'Context Window'},
            {'value': 'Claude 3.5', 'label': 'Latest Model'},
            {'value': '$20', 'label': 'Claude Pro/mo'},
        ],
        'verdict': '''Anthropic's Claude has emerged as the primary alternative to OpenAI for enterprises. The 200K context window is genuinely differentiating for document-heavy use cases. Claude Sonnet 3.5 matches or beats GPT-4 on many benchmarks at lower cost. For teams already on OpenAI, Claude is the natural second provider to add for redundancy and capability diversification.''',
        'overview': '''Anthropic was founded in 2021 by former OpenAI researchers, including Dario and Daniela Amodei. The company has raised over $7 billion and is valued at $18+ billion, making it one of the most well-funded AI startups. Anthropic's focus on AI safety through "Constitutional AI" has resonated with enterprise customers concerned about responsible deployment.

Claude 3.5 Sonnet, released in 2024, matches or exceeds GPT-4 performance on most benchmarks while being faster and cheaper. The 200K context window—roughly 150,000 words—enables processing entire codebases or document collections in a single prompt.''',
        'pricing': '''Anthropic uses usage-based pricing similar to OpenAI:

| Model | Input | Output | Context |
|-------|-------|--------|---------|
| Claude 3.5 Sonnet | $3/1M tokens | $15/1M tokens | 200K |
| Claude 3 Opus | $15/1M tokens | $75/1M tokens | 200K |
| Claude 3 Haiku | $0.25/1M tokens | $1.25/1M tokens | 200K |

Claude Pro costs $20/month for individuals. Team plans start at $25/user/month. Enterprise pricing is custom and includes enhanced security features.

For most applications, Claude Sonnet offers the best quality-to-cost ratio. Opus is reserved for the most demanding reasoning tasks.''',
        'pricing_note': '''Claude Sonnet at $3/$15 per million tokens is cheaper than GPT-4 Turbo ($10/$30) for equivalent capability. The cost advantage is significant at scale.''',
        'features': [
            {'icon': '📚', 'title': '200K Context Window', 'desc': 'Process entire books, codebases, or document collections in a single prompt.'},
            {'icon': '🛡️', 'title': 'Constitutional AI', 'desc': 'Built-in safety training reduces harmful outputs without excessive refusals.'},
            {'icon': '💻', 'title': 'Code Excellence', 'desc': 'Claude excels at code generation, review, and explanation tasks.'},
            {'icon': '🔧', 'title': 'Tool Use', 'desc': 'Function calling and structured output for building AI agents.'},
            {'icon': '👁️', 'title': 'Vision', 'desc': 'Analyze images and documents with Claude 3 models.'},
            {'icon': '📊', 'title': 'Artifacts', 'desc': 'Claude can generate interactive visualizations and code demos.'},
        ],
        'limitations': '''**Availability and Rate Limits**
Anthropic's API has faced capacity constraints during high-demand periods. Rate limits are more restrictive than OpenAI for new accounts. Some features (like vision) were slower to roll out than competitors.

**Ecosystem Maturity**
While improving rapidly, Anthropic's ecosystem is less developed than OpenAI's. Fewer tutorials, integrations, and community resources. LangChain and other frameworks support Claude, but OpenAI often gets features first.

**No Fine-tuning (Yet)**
Unlike OpenAI, Anthropic doesn't offer fine-tuning for Claude models. You can't train on your proprietary data to create a specialized model.

**Over-Cautious Refusals**
Claude's safety training occasionally leads to unnecessary refusals on benign requests. This has improved significantly in Claude 3.5, but some users still find it more restrictive than GPT-4.''',
        'pros': [
            '200K context window (50% larger than GPT-4)',
            'Excellent performance on coding and analysis tasks',
            'Lower cost than GPT-4 for equivalent capability',
            'Strong safety profile without excessive restrictions',
            'Growing enterprise adoption and AWS partnership',
            'Artifacts feature for interactive outputs',
        ],
        'cons': [
            'Smaller ecosystem than OpenAI',
            'No fine-tuning available yet',
            'Rate limits can be restrictive',
            'Occasional over-cautious refusals',
            'Fewer tutorials and community resources',
            'API capacity constraints during peak demand',
        ],
        'buy_if': [
            'You need very long context windows (documents, codebases)',
            'You want lower costs than GPT-4 without sacrificing quality',
            'AI safety and responsible deployment matter to your organization',
            'You\'re building a coding assistant or code analysis tool',
            'You want to diversify LLM providers beyond OpenAI',
        ],
        'skip_if': [
            'You need fine-tuning on proprietary data',
            'You want the largest possible ecosystem of integrations',
            'Your team relies heavily on OpenAI-specific features',
            'You\'re in a regulated industry requiring audit trails (check compliance first)',
            'You need guaranteed SLA for mission-critical applications',
        ],
        'alternatives': [
            {'name': 'OpenAI GPT-4', 'strength': 'Largest ecosystem, most integrations', 'pricing': 'Premium tier'},
            {'name': 'Google Gemini', 'strength': '1M context window (Gemini Pro)', 'pricing': 'Competitive'},
            {'name': 'Cohere', 'strength': 'Enterprise focus, RAG specialization', 'pricing': 'Custom'},
            {'name': 'Llama 3', 'strength': 'Open source, self-hostable', 'pricing': 'Compute only'},
        ],
        'questions': [
            'Do we have use cases that benefit from 200K context windows?',
            'Are we currently over-paying for GPT-4 where Claude Sonnet would suffice?',
            'How important is fine-tuning capability for our roadmap?',
            'Can we handle the smaller ecosystem and fewer community resources?',
            'Have we tested Claude on our specific use cases to validate quality?',
            'Do we need AWS Bedrock integration (Anthropic is a featured partner)?',
        ],
        'bottom_line': '''**Anthropic's Claude has become a legitimate first-choice option, not just an OpenAI alternative.** Claude Sonnet 3.5 offers GPT-4-class performance at lower cost, and the 200K context window enables use cases that simply aren't possible with other providers.

For document-heavy applications (legal, financial, research), Claude's context advantage is decisive. For coding tools, Claude consistently matches or beats GPT-4. The safety-focused approach appeals to enterprises worried about AI risk.

The main gaps are ecosystem maturity and fine-tuning capability. If you need either, OpenAI remains the pragmatic choice. But for many teams, Claude should be your primary or secondary LLM provider.''',
        'skills': ['Claude', 'Constitutional AI', 'Anthropic API', 'Claude 3.5'],
        'use_cases': ['Long document analysis', 'Code generation', 'Enterprise AI', 'Content moderation', 'Research assistance'],
    },

    'langchain': {
        'name': 'LangChain',
        'category': 'LLM Frameworks',
        'tagline': 'The most popular framework for building LLM applications',
        'website': 'https://langchain.com',
        'logo_placeholder': '/assets/logos/langchain_logo.png',
        'rating': '4.5',
        'rating_count': '400+',
        'stats': [
            {'value': '4.5/5', 'label': 'G2 Rating'},
            {'value': '85K+', 'label': 'GitHub Stars'},
            {'value': '2022', 'label': 'Founded'},
            {'value': 'Free', 'label': 'Open Source'},
        ],
        'verdict': '''LangChain is the de facto standard for building LLM applications. It's appearing in more AI Engineer job postings than any other framework. The abstractions aren't perfect—some developers find them over-engineered—but the ecosystem, documentation, and community support are unmatched. For most teams starting with RAG or agents, LangChain is the pragmatic choice.''',
        'overview': '''LangChain was created by Harrison Chase in late 2022 and quickly became the most popular framework for LLM application development. The company raised $25M from Sequoia and now employs 50+ people. The ecosystem includes LangChain (the framework), LangSmith (observability), LangServe (deployment), and LangGraph (complex workflows).

LangChain provides abstractions for common LLM patterns: chains (sequences of calls), agents (autonomous decision-making), memory (conversation state), and retrieval (RAG). These building blocks accelerate development, especially for teams new to LLMs.''',
        'pricing': '''LangChain (the framework) is **free and open source** under MIT license.

LangSmith (observability platform) pricing:
| Tier | Cost | Includes |
|------|------|----------|
| Free | $0 | 5K traces/month, 1 seat |
| Plus | $39/seat/month | 100K traces, team features |
| Enterprise | Custom | Unlimited, SSO, support |

Most teams start with free LangChain + free LangSmith tier, upgrading to Plus as trace volume grows.''',
        'pricing_note': '''LangChain itself is completely free. The commercial play is LangSmith for observability. You can use LangChain without ever paying LangSmith—many teams use alternative observability tools.''',
        'features': [
            {'icon': '🔗', 'title': 'Chains', 'desc': 'Compose sequences of LLM calls, prompts, and tools into reusable pipelines.'},
            {'icon': '🤖', 'title': 'Agents', 'desc': 'Build autonomous systems that decide which tools to use and in what order.'},
            {'icon': '🧠', 'title': 'Memory', 'desc': 'Manage conversation history and context across multi-turn interactions.'},
            {'icon': '📚', 'title': 'Retrieval (RAG)', 'desc': 'Connect LLMs to your data with vector stores, embeddings, and document loaders.'},
            {'icon': '🔍', 'title': 'LangSmith', 'desc': 'Debug, test, and monitor LLM applications with detailed tracing.'},
            {'icon': '📊', 'title': 'LangGraph', 'desc': 'Build complex multi-agent workflows with state management.'},
        ],
        'limitations': '''**Abstraction Overhead**
LangChain's abstractions can feel over-engineered for simple use cases. Some developers find the learning curve steep and prefer calling LLM APIs directly. The "magic" can make debugging harder.

**Rapid API Changes**
The framework evolves quickly, with frequent breaking changes. Code written 6 months ago may not work with current versions. This velocity is both a strength (fast iteration) and a weakness (maintenance burden).

**Performance Overhead**
For high-performance applications, LangChain's abstractions add latency and complexity. Some teams "graduate" to custom implementations after prototyping with LangChain.

**Documentation Gaps**
Despite being extensive, the documentation doesn't always keep up with the rapidly evolving codebase. Stack Overflow and Discord become essential for edge cases.''',
        'pros': [
            'Largest ecosystem of integrations (every LLM, vector DB, tool)',
            'Excellent for rapid prototyping and learning LLM patterns',
            'Strong community with abundant tutorials and examples',
            'LangSmith provides best-in-class LLM observability',
            'LangGraph enables complex multi-agent workflows',
            'High demand in job market (appears in most AI Engineer postings)',
        ],
        'cons': [
            'Abstractions can feel over-engineered',
            'Frequent breaking changes require maintenance',
            'Performance overhead for high-throughput applications',
            'Learning curve steeper than calling APIs directly',
            'Documentation gaps for advanced use cases',
            'Some developers prefer simpler alternatives',
        ],
        'buy_if': [
            'You\'re building RAG applications and want batteries-included',
            'Your team is new to LLMs and needs structured patterns to follow',
            'You want maximum integration options (any LLM, any vector DB)',
            'LLM observability matters and you want LangSmith',
            'You\'re building complex agent workflows (LangGraph)',
        ],
        'skip_if': [
            'You prefer minimal abstractions and direct API calls',
            'You\'re building a high-performance application where latency matters',
            'You don\'t want to deal with frequent framework updates',
            'Your use case is simple enough that a framework adds unnecessary complexity',
            'You need production stability over cutting-edge features',
        ],
        'alternatives': [
            {'name': 'LlamaIndex', 'strength': 'Better for data-intensive RAG', 'pricing': 'Free / LlamaCloud'},
            {'name': 'Haystack', 'strength': 'Production-focused, stable APIs', 'pricing': 'Free + deepset Cloud'},
            {'name': 'Semantic Kernel', 'strength': 'Microsoft ecosystem, C#/.NET', 'pricing': 'Free'},
            {'name': 'Direct API calls', 'strength': 'Maximum control, no overhead', 'pricing': 'N/A'},
        ],
        'questions': [
            'Is the abstraction overhead worth it for our use case complexity?',
            'Can our team handle frequent framework updates and breaking changes?',
            'Do we need LangSmith, or will another observability tool work?',
            'Should we prototype in LangChain and potentially migrate later?',
            'Have we evaluated LlamaIndex for our RAG-specific needs?',
            'Is our team experienced enough to benefit from abstractions, or would direct API calls teach more?',
        ],
        'bottom_line': '''**LangChain is the right choice for most teams building their first LLM applications.** The ecosystem is unmatched, the patterns are well-documented, and the job market rewards LangChain expertise.

But be aware of the trade-offs. The abstractions add overhead—both cognitive and computational. Some experienced teams skip LangChain entirely, preferring direct API calls. Others prototype in LangChain and migrate to custom code for production.

For RAG applications specifically, also evaluate LlamaIndex, which has more sophisticated data handling. For simple chatbots, you may not need a framework at all.

**The pragmatic approach:** Start with LangChain to learn the patterns and move fast. Plan to potentially simplify or migrate as your understanding deepens.''',
        'skills': ['Chains', 'Agents', 'Memory', 'RAG', 'LangSmith', 'LangGraph'],
        'use_cases': ['RAG applications', 'AI agents', 'Chatbots', 'Document Q&A', 'LLM observability'],
    },

    'hugging-face': {
        'name': 'Hugging Face',
        'category': 'ML Platforms',
        'tagline': 'The GitHub of machine learning',
        'website': 'https://huggingface.co',
        'logo_placeholder': '/assets/logos/huggingface_logo.png',
        'rating': '4.8',
        'rating_count': '300+',
        'stats': [
            {'value': '4.8/5', 'label': 'G2 Rating'},
            {'value': '500K+', 'label': 'Models on Hub'},
            {'value': '100K+', 'label': 'Datasets'},
            {'value': 'Free', 'label': 'Open Source'},
        ],
        'verdict': '''Hugging Face has become essential infrastructure for the ML community—like GitHub, but for models. The Transformers library is the standard way to work with pretrained models. ML Engineers are expected to be fluent with the Hub and core libraries. If you work in ML, you'll use Hugging Face.''',
        'overview': '''Hugging Face was founded in 2016 as a chatbot company before pivoting to become the central hub for ML models and datasets. The company has raised over $400M and is valued at $4.5B. Their open-source libraries—Transformers, Datasets, Accelerate, PEFT—power most ML workflows.

The Hugging Face Hub hosts 500K+ models and 100K+ datasets, including most state-of-the-art open models (Llama, Mistral, Falcon). Spaces allows hosting ML demos. The Inference API provides managed model serving.''',
        'pricing': '''Hugging Face Hub and open-source libraries are **free**.

Paid services:
| Service | Cost |
|---------|------|
| Inference Endpoints | From $0.032/hour (CPU) |
| Pro Account | $9/month (private models, more compute) |
| Enterprise Hub | Custom (SSO, security, compliance) |
| Spaces | Free tier + paid GPU options |

Most users never pay—the open-source ecosystem is fully functional. Paid services are for production deployment and enterprise needs.''',
        'pricing_note': '''The free tier is generous. You only pay when you need managed deployment (Inference Endpoints) or enterprise features. Most ML engineers use Hugging Face daily without ever paying.''',
        'features': [
            {'icon': '🤗', 'title': 'Model Hub', 'desc': '500K+ pretrained models with version control, model cards, and easy downloading.'},
            {'icon': '📚', 'title': 'Datasets', 'desc': '100K+ datasets with streaming, preprocessing, and integration with training loops.'},
            {'icon': '🔧', 'title': 'Transformers', 'desc': 'The standard library for working with transformer models in PyTorch and TensorFlow.'},
            {'icon': '🚀', 'title': 'Inference Endpoints', 'desc': 'Deploy any Hub model to dedicated infrastructure with autoscaling.'},
            {'icon': '💻', 'title': 'Spaces', 'desc': 'Host Gradio and Streamlit demos directly from the Hub.'},
            {'icon': '⚡', 'title': 'Accelerate', 'desc': 'Simplify distributed training and mixed-precision across hardware.'},
        ],
        'limitations': '''**Not a Full ML Platform**
Hugging Face provides models and libraries, not a complete ML platform. You still need experiment tracking (Weights & Biases), feature stores, and production infrastructure elsewhere.

**Inference Endpoint Costs**
GPU inference endpoints are expensive for high-volume production use. Many teams use Hugging Face for development but deploy elsewhere (AWS SageMaker, custom infrastructure).

**Model Quality Varies**
The Hub hosts everything—not all models are high quality. Due diligence is required before using community models in production. Stick to verified organizations and popular models.

**API Complexity**
The Transformers library has a steep learning curve. The API is powerful but can be overwhelming for newcomers. Many models have subtle differences in usage.''',
        'pros': [
            'Essential infrastructure for ML community',
            'Largest collection of open models and datasets',
            'Transformers library is the industry standard',
            'Excellent documentation and course materials',
            'Free for most use cases',
            'Strong community and active development',
        ],
        'cons': [
            'Not a full ML platform (need other tools)',
            'Inference endpoints can be expensive at scale',
            'Model quality varies (community uploads)',
            'Learning curve for Transformers library',
            'Hub can be overwhelming to navigate',
            'Some advanced features require paid tier',
        ],
        'buy_if': [
            'You work with pretrained models and transformers',
            'You need access to open-source models (Llama, Mistral, etc.)',
            'You want managed model deployment without infrastructure work',
            'You\'re building demos with Gradio/Streamlit',
            'You want to share models and collaborate with the ML community',
        ],
        'skip_if': [
            'You only use proprietary APIs (OpenAI, Anthropic)',
            'You need a complete MLOps platform (try AWS SageMaker, Vertex AI)',
            'You\'re doing purely classical ML without transformers',
            'You need enterprise compliance features (evaluate Enterprise Hub)',
            'You want turnkey production deployment (consider managed platforms)',
        ],
        'alternatives': [
            {'name': 'AWS SageMaker', 'strength': 'Full MLOps platform', 'pricing': 'Usage-based'},
            {'name': 'Replicate', 'strength': 'Simple model hosting', 'pricing': 'Per-prediction'},
            {'name': 'Modal', 'strength': 'Serverless ML compute', 'pricing': 'Usage-based'},
            {'name': 'Weights & Biases', 'strength': 'Experiment tracking (complementary)', 'pricing': 'Free + paid'},
        ],
        'questions': [
            'Are we primarily using open-source models or proprietary APIs?',
            'Do we need managed inference, or can we deploy ourselves?',
            'Have we evaluated the Transformers library for our use case?',
            'Do we need enterprise security features (SSO, compliance)?',
            'Are we sharing models publicly or keeping them private?',
            'How does Hugging Face fit with our existing MLOps stack?',
        ],
        'bottom_line': '''**Hugging Face is non-negotiable for ML engineers.** The Hub and Transformers library are so central to modern ML workflows that "fluent with Hugging Face" is an implicit requirement for most ML roles.

Use the free tier for model access, experimentation, and learning. Consider paid Inference Endpoints when you need managed deployment without infrastructure work. Enterprise Hub is for organizations with compliance requirements.

The ecosystem continues to expand: Spaces for demos, Accelerate for distributed training, PEFT for efficient fine-tuning. Learning Hugging Face isn't just about one tool—it's about accessing the entire open ML ecosystem.''',
        'skills': ['Transformers', 'Datasets', 'Model Hub', 'Spaces', 'Inference API', 'Accelerate'],
        'use_cases': ['Model hosting', 'Fine-tuning', 'ML collaboration', 'Demo deployment', 'Dataset management'],
    },

    'pinecone': {
        'name': 'Pinecone',
        'category': 'Vector Databases',
        'tagline': 'Managed vector database for AI applications',
        'website': 'https://pinecone.io',
        'logo_placeholder': '/assets/logos/pinecone_logo.png',
        'rating': '4.6',
        'rating_count': '150+',
        'stats': [
            {'value': '4.6/5', 'label': 'G2 Rating'},
            {'value': '2019', 'label': 'Founded'},
            {'value': '$100M+', 'label': 'Funding'},
            {'value': 'Free', 'label': 'Starter Tier'},
        ],
        'verdict': '''Pinecone is the default choice for teams that want a managed vector database without infrastructure overhead. The serverless pricing model makes it cost-effective to start, and it scales well. For RAG applications in production, Pinecone is the safe, pragmatic choice. But self-hosted alternatives are catching up.''',
        'overview': '''Pinecone was founded in 2019 by Edo Liberty, former head of Amazon's AI Labs. The company raised $138M and pioneered the "managed vector database" category. As RAG (Retrieval Augmented Generation) became the dominant pattern for LLM applications, Pinecone emerged as the go-to solution.

The product is laser-focused on vector similarity search. You upload embeddings (from OpenAI, Cohere, etc.), and Pinecone handles indexing, querying, and scaling. The serverless architecture means you pay for queries, not reserved compute.''',
        'pricing': '''Pinecone uses serverless pricing based on storage and queries:

| Component | Free Tier | Paid |
|-----------|-----------|------|
| Storage | 100K vectors | $0.33/1M vectors/month |
| Writes | 2M/month | $2/1M writes |
| Reads | 10M/month | $8/1M reads |
| Indexes | 1 | Unlimited |

The free tier is generous for development. Production costs depend on index size and query volume—expect $50-500/month for moderate applications.''',
        'pricing_note': '''Pinecone's serverless model means you don't pay for idle compute. This makes it cheaper than self-hosting for many use cases, especially with variable traffic.''',
        'features': [
            {'icon': '🔍', 'title': 'Vector Search', 'desc': 'Millisecond-latency similarity search across billions of vectors.'},
            {'icon': '🏷️', 'title': 'Metadata Filtering', 'desc': 'Filter search results by metadata attributes like category, date, or source.'},
            {'icon': '☁️', 'title': 'Serverless', 'desc': 'Pay per query with automatic scaling. No infrastructure to manage.'},
            {'icon': '🔗', 'title': 'Integrations', 'desc': 'Native connectors for LangChain, LlamaIndex, and major embedding providers.'},
            {'icon': '📊', 'title': 'Namespaces', 'desc': 'Organize vectors into namespaces for multi-tenant applications.'},
            {'icon': '🔄', 'title': 'Hybrid Search', 'desc': 'Combine vector similarity with keyword search for better relevance.'},
        ],
        'limitations': '''**Vendor Lock-in**
Pinecone uses a proprietary architecture. Migrating to another vector database requires re-indexing your entire dataset. Some teams prefer open-source options for flexibility.

**Cost at Scale**
While serverless is efficient for small-medium workloads, costs can escalate with high query volumes. Some enterprises find self-hosting cheaper at scale.

**Limited Control**
As a managed service, you can't tune low-level parameters. For advanced use cases requiring custom similarity metrics or index structures, self-hosted options offer more flexibility.

**Geographic Limitations**
Index regions are limited. If you need data residency in specific countries, verify Pinecone supports your region.''',
        'pros': [
            'Fully managed—no infrastructure to maintain',
            'Serverless pricing efficient for variable traffic',
            'Excellent performance and reliability',
            'Strong LangChain/LlamaIndex integration',
            'Good documentation and developer experience',
            'Free tier generous for development',
        ],
        'cons': [
            'Proprietary—harder to migrate away',
            'Can get expensive at high query volumes',
            'Limited low-level customization',
            'Some features (hybrid search) are newer',
            'Geographic availability varies',
            'Self-hosting may be cheaper at scale',
        ],
        'buy_if': [
            'You want a managed vector database without infrastructure work',
            'Your traffic is variable (serverless makes sense)',
            'You\'re building RAG and want the default, well-supported option',
            'Fast time-to-production matters more than long-term flexibility',
            'Your scale is moderate (millions, not billions, of vectors)',
        ],
        'skip_if': [
            'You want to avoid vendor lock-in',
            'You have very high query volumes where self-hosting is cheaper',
            'You need custom similarity metrics or index configurations',
            'You have strict data residency requirements Pinecone doesn\'t support',
            'Your team has infrastructure expertise and prefers control',
        ],
        'alternatives': [
            {'name': 'Weaviate', 'strength': 'Open source, hybrid search', 'pricing': 'Free + Cloud options'},
            {'name': 'Chroma', 'strength': 'Simplest to start, open source', 'pricing': 'Free'},
            {'name': 'Qdrant', 'strength': 'Rust-based, high performance', 'pricing': 'Free + Cloud'},
            {'name': 'Milvus', 'strength': 'Enterprise features, Apache 2.0', 'pricing': 'Free + Zilliz Cloud'},
        ],
        'questions': [
            'How many vectors will we store, and what\'s our query volume?',
            'Is serverless pricing cheaper than self-hosted for our usage pattern?',
            'Can we accept the vendor lock-in, or do we need portability?',
            'Does Pinecone support our required regions for data residency?',
            'Have we compared costs to Weaviate Cloud or self-hosted options?',
            'Do we need features Pinecone doesn\'t offer (custom metrics, etc.)?',
        ],
        'bottom_line': '''**Pinecone is the pragmatic default for most RAG applications.** The managed service eliminates infrastructure burden, the serverless pricing is efficient for typical workloads, and the ecosystem support is excellent.

But evaluate alternatives if you have concerns about vendor lock-in, operate at very high scale, or need capabilities Pinecone doesn't offer. Weaviate is the strongest open-source competitor with cloud and self-hosted options.

For most teams building their first RAG system: start with Pinecone, launch quickly, and reconsider infrastructure choices once you have real usage data.''',
        'skills': ['Vector embeddings', 'Similarity search', 'Metadata filtering', 'RAG'],
        'use_cases': ['Semantic search', 'RAG', 'Recommendation systems', 'Duplicate detection'],
    },

    'pytorch': {
        'name': 'PyTorch',
        'category': 'ML Frameworks',
        'tagline': 'The dominant deep learning framework',
        'website': 'https://pytorch.org',
        'logo_placeholder': '/assets/logos/pytorch_logo.png',
        'rating': '4.8',
        'rating_count': '500+',
        'stats': [
            {'value': '4.8/5', 'label': 'G2 Rating'},
            {'value': '80K+', 'label': 'GitHub Stars'},
            {'value': '2016', 'label': 'Released'},
            {'value': 'Free', 'label': 'Open Source'},
        ],
        'verdict': '''PyTorch has won the framework wars. It's the default choice for ML research and increasingly for production. Most new papers are implemented in PyTorch. Most LLMs are trained in PyTorch. ML Engineer job postings mention PyTorch more than any other framework. If you're serious about ML, PyTorch proficiency is non-negotiable.''',
        'overview': '''PyTorch was released by Meta AI (then Facebook) in 2016 and quickly gained adoption for its Pythonic interface and dynamic computation graphs. While TensorFlow dominated early deep learning, PyTorch became the research standard by 2020 and has since expanded into production.

The framework is now governed by the PyTorch Foundation under the Linux Foundation, with contributions from Meta, Microsoft, AWS, Google, and others. The ecosystem includes PyTorch Lightning for training abstractions, TorchServe for deployment, and extensive Hugging Face integration.''',
        'pricing': '''PyTorch is **completely free and open source** under the BSD license.

You pay for compute:
- Training: GPU instances ($0.50-5/hour depending on GPU)
- Inference: Model serving infrastructure
- Cloud ML platforms (SageMaker, Vertex AI) often include PyTorch runtimes

The framework itself has no licensing costs.''',
        'pricing_note': '''PyTorch is free. Your costs are compute (GPUs for training/inference) and optionally managed platforms that simplify deployment.''',
        'features': [
            {'icon': '🐍', 'title': 'Pythonic API', 'desc': 'Natural Python interface with imperative execution. Debug with standard Python tools.'},
            {'icon': '📊', 'title': 'Dynamic Graphs', 'desc': 'Define-by-run computation graphs enable flexible architectures and easy debugging.'},
            {'icon': '⚡', 'title': 'CUDA Integration', 'desc': 'First-class GPU support with seamless tensor movement between CPU and GPU.'},
            {'icon': '🔧', 'title': 'Autograd', 'desc': 'Automatic differentiation for gradient computation in neural networks.'},
            {'icon': '📦', 'title': 'TorchScript', 'desc': 'Compile models for production deployment and mobile.'},
            {'icon': '🤗', 'title': 'Ecosystem', 'desc': 'Hugging Face Transformers, Lightning, TorchVision, TorchAudio, and more.'},
        ],
        'limitations': '''**Mobile/Edge Deployment**
While TorchScript and PyTorch Mobile exist, TensorFlow Lite is more mature for mobile deployment. Edge ML is an area where TensorFlow still has advantages.

**Learning Curve**
PyTorch requires understanding tensors, autograd, and neural network fundamentals. It's not a high-level "AutoML" tool—you need to understand what you're building.

**Production Tooling**
PyTorch's production ecosystem has improved but still trails TensorFlow Serving for some enterprise use cases. Many teams use ONNX to export PyTorch models for production serving.

**Memory Management**
GPU memory management in PyTorch can be tricky. Large models require careful attention to batch sizes, gradient accumulation, and mixed-precision training.''',
        'pros': [
            'Industry standard for ML research and LLMs',
            'Intuitive, Pythonic API',
            'Dynamic graphs enable flexible architectures',
            'Excellent debugging experience',
            'Massive ecosystem (Hugging Face, Lightning, etc.)',
            'Strong community and documentation',
        ],
        'cons': [
            'Steeper learning curve than high-level tools',
            'Mobile deployment less mature than TensorFlow',
            'Production serving requires additional tooling',
            'GPU memory management complexity',
            'Not ideal for classical ML (use scikit-learn)',
            'Requires understanding of fundamentals',
        ],
        'buy_if': [
            'You\'re doing deep learning research or development',
            'You work with transformer models and LLMs',
            'You want the framework most papers are implemented in',
            'You value debugging experience and Pythonic code',
            'You\'re targeting ML Engineer or Research Engineer roles',
        ],
        'skip_if': [
            'You\'re doing classical ML without deep learning (use scikit-learn)',
            'You need turnkey mobile deployment (consider TensorFlow Lite)',
            'You prefer high-level abstractions over framework control',
            'You\'re working in a TensorFlow-heavy codebase and can\'t switch',
            'You need enterprise production serving (evaluate ONNX Runtime)',
        ],
        'alternatives': [
            {'name': 'TensorFlow', 'strength': 'Mobile deployment, TF Serving', 'pricing': 'Free'},
            {'name': 'JAX', 'strength': 'Functional style, TPU optimization', 'pricing': 'Free'},
            {'name': 'Keras', 'strength': 'High-level API, easier to start', 'pricing': 'Free'},
            {'name': 'scikit-learn', 'strength': 'Classical ML, simpler models', 'pricing': 'Free'},
        ],
        'questions': [
            'Are we doing deep learning, or would simpler tools (scikit-learn) suffice?',
            'Do we need mobile/edge deployment (TensorFlow may be better)?',
            'Is our team comfortable with lower-level frameworks?',
            'Do we have access to GPU compute for training?',
            'How will we serve models in production (TorchServe, ONNX, custom)?',
            'Should we use PyTorch Lightning for training abstractions?',
        ],
        'bottom_line': '''**PyTorch is the default choice for serious ML work.** The research community has standardized on it, most LLMs are trained in it, and job postings reflect this reality. ML Engineer candidates who aren't proficient in PyTorch are at a significant disadvantage.

For production deployment, you'll likely combine PyTorch with additional tooling—ONNX for model export, TorchServe or a custom solution for serving. The production story is improving but still requires more setup than TensorFlow Serving.

If you're new to deep learning, PyTorch's intuitive API and excellent debugging make it the best framework to learn. The skills transfer to understanding ML fundamentals, reading papers, and contributing to the open-source ecosystem.''',
        'skills': ['Tensors', 'Autograd', 'Neural networks', 'CUDA', 'TorchScript', 'PyTorch Lightning'],
        'use_cases': ['Deep learning research', 'Model training', 'LLM fine-tuning', 'Computer vision', 'NLP'],
    },
}

# Add remaining tools with shorter content (to be expanded)
TOOL_REVIEWS.update({
    'google-gemini': {
        'name': 'Google Gemini',
        'category': 'LLM Providers',
        'tagline': 'Google\'s frontier AI model family with industry-leading context windows',
        'website': 'https://deepmind.google/technologies/gemini/',
        'logo_placeholder': '/assets/logos/google_gemini_logo.png',
        'rating': '4.4',
        'rating_count': '250+',
        'stats': [
            {'value': '4.4/5', 'label': 'G2 Rating'},
            {'value': '2M', 'label': 'Token Context'},
            {'value': 'Gemini 2.0', 'label': 'Latest Model'},
            {'value': 'Free', 'label': 'AI Studio Tier'},
        ],
        'verdict': '''Google Gemini has evolved from "also-ran" to genuine contender. Gemini 2.0 Flash matches or exceeds GPT-4o on many benchmarks at a fraction of the cost, and no one else offers 2M token context windows. For long-document analysis, video understanding, or cost-sensitive applications, Gemini deserves serious evaluation alongside OpenAI and Anthropic.''',
        'overview': '''Google Gemini is Google DeepMind's flagship AI model family, launched in December 2023 and rapidly iterated since. The Gemini lineup includes Gemini 2.0 Flash (fast and cheap), Gemini 1.5 Pro (balanced), and Gemini Ultra (most capable). The standout feature is context length: Gemini 1.5 Pro supports up to 2 million tokens—enough to process entire codebases, books, or hours of video in a single prompt.

Google offers Gemini through multiple channels: the consumer Gemini app (formerly Bard), Google AI Studio for developers, and Vertex AI for enterprise deployment. The models are natively multimodal, processing text, images, audio, and video without separate vision or audio models.

For AI engineers, Gemini expertise is increasingly valuable as enterprises diversify beyond OpenAI. Job postings mentioning Gemini have grown 3x year-over-year.''',
        'pricing': '''Gemini API pricing through Google AI Studio (per million tokens):

| Model | Input | Output | Context |
|-------|-------|--------|---------|
| Gemini 2.0 Flash | $0.10 | $0.40 | 1M |
| Gemini 1.5 Pro | $1.25 | $5.00 | 2M |
| Gemini 1.5 Flash | $0.075 | $0.30 | 1M |

**Free tier**: 15 requests/minute, 1M tokens/day on Gemini Flash in AI Studio—generous for prototyping.

**Vertex AI pricing** is slightly higher but includes enterprise features (SLAs, VPC, compliance). Enterprise agreements available for high-volume users.

**Gemini Advanced**: $20/month consumer subscription includes Gemini Ultra, 2TB Google One storage, and Workspace integration.''',
        'pricing_note': '''Gemini Flash is 10-50x cheaper than GPT-4o for comparable quality on many tasks. The free tier in AI Studio is the most generous in the industry—use it for prototyping before committing to any provider.''',
        'features': [
            {'icon': '📚', 'title': '2M Token Context', 'desc': 'Process entire codebases, books, or hours of video in a single prompt. No chunking required.'},
            {'icon': '👁️', 'title': 'Native Multimodal', 'desc': 'Single model handles text, images, audio, and video—no separate vision APIs needed.'},
            {'icon': '⚡', 'title': 'Gemini Flash', 'desc': 'Best price-to-performance ratio in the market. Sub-second responses at minimal cost.'},
            {'icon': '🔧', 'title': 'Google AI Studio', 'desc': 'Free development environment with prompt testing, API keys, and model comparison tools.'},
            {'icon': '🏢', 'title': 'Vertex AI Integration', 'desc': 'Enterprise deployment with grounding, RAG, fine-tuning, and Google Cloud security.'},
            {'icon': '🌐', 'title': 'Workspace Integration', 'desc': 'Gemini built into Gmail, Docs, Sheets, and Meet for enterprise productivity.'},
        ],
        'limitations': '''**Ecosystem Maturity**
The Gemini API ecosystem is younger than OpenAI\'s. Fewer third-party libraries, templates, and community resources. LangChain and LlamaIndex support exists but OpenAI examples are more abundant.

**Function Calling Reliability**
Gemini\'s function calling works but is less refined than OpenAI\'s. Complex tool-use patterns may require more prompt engineering. Structured output can be inconsistent.

**Rate Limits and Availability**
Free tier rate limits are restrictive for production use. Paid tier limits are reasonable but lower than OpenAI Enterprise. Some regions have limited availability.

**Model Versioning**
Google iterates quickly, which means model behavior can change. Less predictable versioning than OpenAI\'s dated snapshots. Test thoroughly before production updates.''',
        'pros': [
            'Industry-leading 2M token context window',
            'Best price-to-performance with Gemini Flash',
            'Native multimodal (no separate vision model)',
            'Generous free tier for prototyping',
            'Strong Workspace and GCP integration',
            'Rapid model improvements (Gemini 2.0 is impressive)',
        ],
        'cons': [
            'Smaller developer ecosystem than OpenAI',
            'Function calling less mature',
            'Model versioning less predictable',
            'Some features GCP-only',
        ],
        'buy_if': [
            'You need to process very long documents (legal, research, code)',
            'Cost efficiency is a priority (Flash is incredibly cheap)',
            'You\'re already in the Google Cloud ecosystem',
            'You need native video or audio understanding',
            'You want multimodal without managing separate models',
        ],
        'skip_if': [
            'You need the largest third-party ecosystem',
            'Complex function calling is core to your use case',
            'You want maximum API stability and predictability',
            'Your team has deep OpenAI expertise you want to leverage',
        ],
        'alternatives': [
            {'name': 'OpenAI GPT-4o', 'strength': 'Largest ecosystem, best function calling', 'pricing': '$2.50-10/M tokens'},
            {'name': 'Anthropic Claude', 'strength': '200K context, strong reasoning', 'pricing': '$3-15/M tokens'},
            {'name': 'Mistral Large', 'strength': 'EU-hosted, open weights available', 'pricing': '$2-6/M tokens'},
        ],
        'questions': [
            'What\'s our average document/context length? (If >100K tokens, Gemini has a significant advantage)',
            'How price-sensitive is our application? (Gemini Flash could cut costs 80%+)',
            'Do we need multimodal capabilities? (Gemini\'s native approach is cleaner)',
            'Are we already using Google Cloud? (Vertex AI integration is seamless)',
            'How complex is our function calling? (OpenAI is still ahead here)',
            'Can we tolerate some API instability during rapid iteration?',
        ],
        'bottom_line': '''**Gemini has earned a seat at the table.** The 2M token context window is genuinely differentiated—no one else comes close. Gemini Flash offers the best price-to-performance in the industry. For cost-sensitive applications or long-context use cases, Gemini should be your first evaluation, not your fallback. For complex agentic applications with heavy function calling, OpenAI still has the edge, but that gap is closing fast.''',
        'skills': ['Google Gemini', 'Gemini API', 'Vertex AI', 'Google AI Studio', 'Multimodal AI', 'Long Context LLMs'],
        'use_cases': ['Long document analysis', 'Video understanding', 'Codebase Q&A', 'Cost-optimized chatbots', 'Multimodal applications', 'Enterprise search'],
    },

    'llamaindex': {
        'name': 'LlamaIndex',
        'category': 'LLM Frameworks',
        'tagline': 'Data framework for LLM applications',
        'website': 'https://llamaindex.ai',
        'logo_placeholder': '/assets/logos/llamaindex_logo.png',
        'rating': '4.5',
        'rating_count': '100+',
        'stats': [
            {'value': '4.5/5', 'label': 'G2 Rating'},
            {'value': '32K+', 'label': 'GitHub Stars'},
            {'value': '2022', 'label': 'Founded'},
            {'value': 'Free', 'label': 'Open Source'},
        ],
        'verdict': '''LlamaIndex is LangChain\'s closest competitor, with a stronger focus on data ingestion and indexing. For RAG applications with complex document processing needs, LlamaIndex often provides better abstractions. Many teams use both.''',
        'overview': '''LlamaIndex (originally GPT Index) specializes in connecting LLMs to data. It provides sophisticated document processing, indexing strategies, and query engines. The LlamaHub community contributes data loaders for hundreds of sources.''',
        'pricing': '''LlamaIndex (framework) is free and open source.

LlamaCloud pricing:
- Managed parsing and indexing
- Custom pricing based on usage

Most teams use the free framework.''',
        'pricing_note': '''LlamaCloud is a newer offering for managed RAG infrastructure.''',
        'features': [
            {'icon': '📄', 'title': 'Document Loaders', 'desc': 'Ingest PDFs, Word docs, databases, APIs, and 100+ sources via LlamaHub.'},
            {'icon': '🗂️', 'title': 'Index Types', 'desc': 'Multiple indexing strategies optimized for different query patterns.'},
            {'icon': '🔍', 'title': 'Query Engines', 'desc': 'Sophisticated retrieval with synthesis, routing, and multi-step reasoning.'},
            {'icon': '📊', 'title': 'Evaluation', 'desc': 'Built-in RAG evaluation metrics and testing tools.'},
            {'icon': '🔗', 'title': 'LlamaHub', 'desc': 'Community repository of data loaders, tools, and integrations.'},
            {'icon': '☁️', 'title': 'LlamaCloud', 'desc': 'Managed parsing and indexing service (in development).'},
        ],
        'limitations': '''Smaller ecosystem than LangChain. Documentation can be overwhelming. Some abstractions are complex. Less community support and tutorials.''',
        'pros': ['Excellent for complex RAG', 'Strong document processing', 'Multiple index types', 'Good evaluation tools'],
        'cons': ['Smaller ecosystem', 'Steeper learning curve', 'Complex abstractions', 'Fewer tutorials'],
        'buy_if': ['You\'re building document-heavy RAG applications', 'You need sophisticated retrieval strategies', 'Data ingestion is a major challenge'],
        'skip_if': ['You want the largest ecosystem', 'Simple RAG is sufficient', 'You prefer more tutorials and examples'],
        'alternatives': [
            {'name': 'LangChain', 'strength': 'Larger ecosystem, more integrations', 'pricing': 'Free'},
            {'name': 'Haystack', 'strength': 'Production-focused', 'pricing': 'Free'},
        ],
        'questions': ['Is our primary challenge data ingestion and indexing?', 'Do we need sophisticated retrieval strategies?', 'Can we handle the smaller ecosystem?'],
        'bottom_line': '''LlamaIndex excels at data-intensive RAG applications. Consider using it alongside LangChain, or as your primary framework if document processing is your main challenge.''',
        'skills': ['Data connectors', 'Indexing', 'Query engines', 'RAG', 'Document processing'],
        'use_cases': ['Knowledge bases', 'Document search', 'Enterprise RAG', 'Complex retrieval'],
    },

    'weaviate': {
        'name': 'Weaviate',
        'category': 'Vector Databases',
        'tagline': 'Open-source vector database with hybrid search',
        'website': 'https://weaviate.io',
        'logo_placeholder': '/assets/logos/weaviate_logo.png',
        'rating': '4.5',
        'rating_count': '100+',
        'stats': [
            {'value': '4.5/5', 'label': 'G2 Rating'},
            {'value': '10K+', 'label': 'GitHub Stars'},
            {'value': '2019', 'label': 'Founded'},
            {'value': 'Free', 'label': 'Open Source'},
        ],
        'verdict': '''Weaviate is the leading open-source alternative to Pinecone. Hybrid search (combining vector and keyword) is a standout feature. Self-hosting gives more control, while Weaviate Cloud offers managed convenience. Strong choice for teams wanting flexibility.''',
        'overview': '''Weaviate is an open-source vector database built in Go. It supports hybrid search combining vector similarity with BM25 keyword search. Built-in ML model integration allows automatic embedding generation.''',
        'pricing': '''Self-hosted is free. Weaviate Cloud pricing:
- Serverless: Pay per use
- Dedicated: From $135/month for basic clusters

Self-hosting requires infrastructure costs.''',
        'pricing_note': '''Self-hosting may be cheaper at scale but requires DevOps expertise.''',
        'features': [
            {'icon': '🔍', 'title': 'Hybrid Search', 'desc': 'Combine vector and keyword search for better relevance.'},
            {'icon': '🤖', 'title': 'Built-in ML', 'desc': 'Automatic embedding generation with integrated models.'},
            {'icon': '📊', 'title': 'GraphQL API', 'desc': 'Query with GraphQL for complex filtering and aggregations.'},
            {'icon': '☁️', 'title': 'Cloud + Self-hosted', 'desc': 'Choose between managed cloud or self-hosted deployment.'},
            {'icon': '🔗', 'title': 'Integrations', 'desc': 'LangChain, LlamaIndex, and embedding provider support.'},
            {'icon': '📦', 'title': 'Modules', 'desc': 'Extensible with text2vec, img2vec, and other modules.'},
        ],
        'limitations': '''Self-hosting requires infrastructure expertise. GraphQL API has a learning curve. Smaller community than Pinecone.''',
        'pros': ['Open source and self-hostable', 'Hybrid search capability', 'Built-in ML models', 'Strong feature set'],
        'cons': ['Self-hosting complexity', 'GraphQL learning curve', 'Smaller community'],
        'buy_if': ['You want open source with self-hosting option', 'You need hybrid search', 'You have DevOps resources'],
        'skip_if': ['You want purely managed service', 'You prefer simpler APIs', 'No infrastructure expertise'],
        'alternatives': [
            {'name': 'Pinecone', 'strength': 'Fully managed, no ops', 'pricing': 'Serverless'},
            {'name': 'Qdrant', 'strength': 'Rust-based, high performance', 'pricing': 'Free + Cloud'},
        ],
        'questions': ['Do we want self-hosted or managed?', 'Do we need hybrid search?', 'Do we have DevOps resources?'],
        'bottom_line': '''Weaviate is the best open-source vector database for teams wanting flexibility and control. Hybrid search is genuinely useful for many RAG applications.''',
        'skills': ['Vector search', 'Hybrid search', 'GraphQL API', 'Self-hosted infrastructure'],
        'use_cases': ['Multimodal search', 'Enterprise RAG', 'Self-hosted vector search'],
    },

    'chroma': {
        'name': 'Chroma',
        'category': 'Vector Databases',
        'tagline': 'The AI-native open-source embedding database',
        'website': 'https://trychroma.com',
        'logo_placeholder': '/assets/logos/chroma_logo.png',
        'rating': '4.4',
        'rating_count': '50+',
        'stats': [
            {'value': '4.4/5', 'label': 'G2 Rating'},
            {'value': '12K+', 'label': 'GitHub Stars'},
            {'value': '2022', 'label': 'Founded'},
            {'value': 'Free', 'label': 'Open Source'},
        ],
        'verdict': '''Chroma is the simplest vector database to get started with—perfect for learning RAG patterns and local development. Not recommended for production at scale, but excellent for prototyping and small applications.''',
        'overview': '''Chroma is an open-source embedding database designed for simplicity. It runs in-process or as a server, making it easy to get started without infrastructure. Popular for tutorials, prototyping, and learning RAG.''',
        'pricing': '''Free and open source. Chroma Cloud (managed) is in development.''',
        'pricing_note': '''Currently free. Managed cloud offering coming soon.''',
        'features': [
            {'icon': '🚀', 'title': 'Simple API', 'desc': 'Minimal API that\'s easy to learn and use.'},
            {'icon': '💻', 'title': 'Local First', 'desc': 'Runs in-process for development without infrastructure.'},
            {'icon': '🔗', 'title': 'LangChain Native', 'desc': 'First-class LangChain integration out of the box.'},
            {'icon': '📊', 'title': 'Metadata', 'desc': 'Store and filter on metadata alongside embeddings.'},
            {'icon': '🐍', 'title': 'Python Native', 'desc': 'Designed for Python developers with Pythonic API.'},
            {'icon': '⚡', 'title': 'Fast Start', 'desc': 'pip install chromadb and you\'re running.'},
        ],
        'limitations': '''Not designed for production scale. Limited persistence options. Fewer features than Pinecone or Weaviate. No managed cloud (yet).''',
        'pros': ['Simplest to start with', 'Great for learning RAG', 'Local development friendly', 'Excellent LangChain integration'],
        'cons': ['Not production-ready at scale', 'Limited features', 'No managed offering yet'],
        'buy_if': ['You\'re learning RAG', 'You need a quick prototype', 'You want the simplest possible setup'],
        'skip_if': ['You need production scale', 'You want managed infrastructure', 'You need advanced features'],
        'alternatives': [
            {'name': 'Pinecone', 'strength': 'Production-ready, managed', 'pricing': 'Serverless'},
            {'name': 'Weaviate', 'strength': 'More features, self-hostable', 'pricing': 'Free + Cloud'},
        ],
        'questions': ['Is this for prototyping or production?', 'Can we migrate to another database later?', 'Do we need scale beyond what Chroma offers?'],
        'bottom_line': '''Chroma is the best choice for learning and prototyping. Start here, then migrate to Pinecone or Weaviate when you need production scale.''',
        'skills': ['Embeddings', 'Local storage', 'Collections', 'RAG prototyping'],
        'use_cases': ['Local development', 'Prototyping', 'Learning RAG', 'Small-scale applications'],
    },

    'tensorflow': {
        'name': 'TensorFlow',
        'category': 'ML Frameworks',
        'tagline': 'Google\'s production ML platform',
        'website': 'https://tensorflow.org',
        'logo_placeholder': '/assets/logos/tensorflow_logo.png',
        'rating': '4.5',
        'rating_count': '400+',
        'stats': [
            {'value': '4.5/5', 'label': 'G2 Rating'},
            {'value': '180K+', 'label': 'GitHub Stars'},
            {'value': '2015', 'label': 'Released'},
            {'value': 'Free', 'label': 'Open Source'},
        ],
        'verdict': '''TensorFlow remains strong for production ML, especially mobile deployment with TFLite. But PyTorch has won mindshare for research and LLMs. Learn TensorFlow if you\'re targeting mobile/edge deployment or working in a TensorFlow-heavy codebase.''',
        'overview': '''TensorFlow is Google\'s open-source ML platform with a comprehensive ecosystem for production deployment. TF Serving provides robust model serving. TFLite enables mobile and edge deployment. TensorBoard offers visualization.''',
        'pricing': '''Free and open source under Apache 2.0 license.''',
        'pricing_note': '''Framework is free. You pay for compute and optionally cloud platforms.''',
        'features': [
            {'icon': '📱', 'title': 'TFLite', 'desc': 'Deploy models on mobile and edge devices.'},
            {'icon': '🚀', 'title': 'TF Serving', 'desc': 'Production-grade model serving with batching and versioning.'},
            {'icon': '📊', 'title': 'TensorBoard', 'desc': 'Visualization for training metrics, graphs, and embeddings.'},
            {'icon': '🔧', 'title': 'Keras', 'desc': 'High-level API for easy model building.'},
            {'icon': '⚡', 'title': 'XLA', 'desc': 'Compiler optimization for performance.'},
            {'icon': '☁️', 'title': 'Cloud TPU', 'desc': 'Optimized for Google\'s custom TPU hardware.'},
        ],
        'limitations': '''Steeper learning curve than PyTorch. Less used in research. Static graphs can be harder to debug. Ecosystem fragmented between TF 1.x and 2.x.''',
        'pros': ['Strong production ecosystem', 'Best mobile deployment (TFLite)', 'TF Serving is robust', 'TPU optimization'],
        'cons': ['Lost research mindshare to PyTorch', 'Steeper learning curve', 'Static graph debugging harder'],
        'buy_if': ['You need mobile/edge deployment', 'You\'re in a TensorFlow codebase', 'You want TF Serving for production'],
        'skip_if': ['You\'re doing research or LLM work', 'You want the framework with most tutorials', 'You prefer Pythonic APIs'],
        'alternatives': [
            {'name': 'PyTorch', 'strength': 'Research standard, Pythonic', 'pricing': 'Free'},
            {'name': 'JAX', 'strength': 'Functional, TPU optimized', 'pricing': 'Free'},
        ],
        'questions': ['Do we need mobile deployment?', 'Are we already using TensorFlow?', 'Is PyTorch better for our use case?'],
        'bottom_line': '''TensorFlow\'s strength is production deployment, especially mobile. For new projects, evaluate whether PyTorch (research, LLMs) or TensorFlow (production, mobile) better fits your needs.''',
        'skills': ['Keras', 'TF Serving', 'TensorBoard', 'TFLite', 'XLA'],
        'use_cases': ['Production ML', 'Mobile deployment', 'Edge AI', 'Model serving'],
    },

    'aws-sagemaker': {
        'name': 'AWS SageMaker',
        'category': 'Cloud ML',
        'tagline': 'Amazon\'s managed ML platform',
        'website': 'https://aws.amazon.com/sagemaker',
        'logo_placeholder': '/assets/logos/aws_sagemaker_logo.png',
        'rating': '4.3',
        'rating_count': '300+',
        'stats': [
            {'value': '4.3/5', 'label': 'G2 Rating'},
            {'value': '#1', 'label': 'Cloud ML Platform'},
            {'value': '2017', 'label': 'Launched'},
            {'value': 'Pay-per-use', 'label': 'Pricing'},
        ],
        'verdict': '''SageMaker is the most widely used cloud ML platform. If you\'re on AWS, it\'s the default choice for managed ML infrastructure. Comprehensive but complex—expect a learning curve. Essential knowledge for MLOps roles.''',
        'overview': '''AWS SageMaker provides a complete ML platform: notebooks, training, inference, pipelines, feature store, and model registry. It integrates deeply with AWS services and supports most ML frameworks.''',
        'pricing': '''Usage-based pricing. Key components:
- Notebooks: ~$0.05-2/hour depending on instance
- Training: GPU instances $0.50-30/hour
- Inference: $0.05-5/hour for endpoints

Costs vary widely based on usage. Expect $100-1000+/month for typical workloads.''',
        'pricing_note': '''SageMaker costs can escalate quickly. Monitor usage and set budgets.''',
        'features': [
            {'icon': '📓', 'title': 'Studio', 'desc': 'Integrated IDE for ML development with notebooks.'},
            {'icon': '🏋️', 'title': 'Training', 'desc': 'Managed training on any instance type with spot support.'},
            {'icon': '🚀', 'title': 'Inference', 'desc': 'Real-time and batch inference endpoints.'},
            {'icon': '📊', 'title': 'Pipelines', 'desc': 'MLOps workflow orchestration.'},
            {'icon': '🗃️', 'title': 'Feature Store', 'desc': 'Managed feature engineering and storage.'},
            {'icon': '📋', 'title': 'Model Registry', 'desc': 'Version control and deployment for models.'},
        ],
        'limitations': '''Complex and overwhelming. Steep learning curve. Can be expensive at scale. AWS-specific—no portability.''',
        'pros': ['Comprehensive ML platform', 'Deep AWS integration', 'Most widely used', 'Supports all frameworks'],
        'cons': ['Complex and overwhelming', 'Expensive at scale', 'Steep learning curve', 'AWS lock-in'],
        'buy_if': ['You\'re on AWS', 'You need managed ML infrastructure', 'You want enterprise features'],
        'skip_if': ['You want simplicity', 'You\'re multi-cloud', 'You prefer open-source MLOps'],
        'alternatives': [
            {'name': 'Google Vertex AI', 'strength': 'GCP integration', 'pricing': 'Similar'},
            {'name': 'Azure ML', 'strength': 'Microsoft ecosystem', 'pricing': 'Similar'},
            {'name': 'Databricks', 'strength': 'Data + ML unified', 'pricing': 'Premium'},
        ],
        'questions': ['Are we committed to AWS?', 'Do we need all SageMaker features?', 'Have we estimated costs?'],
        'bottom_line': '''SageMaker is the default for AWS shops. Essential for MLOps roles. But evaluate if you need the full platform or simpler alternatives.''',
        'skills': ['Notebooks', 'Training', 'Inference', 'Pipelines', 'MLOps', 'Feature Store'],
        'use_cases': ['Enterprise ML', 'Model deployment', 'MLOps', 'Automated training'],
    },

    'azure-ml': {
        'name': 'Azure ML',
        'category': 'Cloud ML',
        'tagline': 'Microsoft\'s cloud ML platform',
        'website': 'https://azure.microsoft.com/en-us/products/machine-learning',
        'logo_placeholder': '/assets/logos/azure_ml_logo.png',
        'rating': '4.2',
        'rating_count': '200+',
        'stats': [
            {'value': '4.2/5', 'label': 'G2 Rating'},
            {'value': 'Azure', 'label': 'Cloud'},
            {'value': '2018', 'label': 'Launched'},
            {'value': 'Pay-per-use', 'label': 'Pricing'},
        ],
        'verdict': '''Azure ML makes sense for organizations in the Microsoft ecosystem. Strong integration with Azure OpenAI Service and responsible AI tools. Similar capability to SageMaker with different strengths.''',
        'overview': '''Azure Machine Learning provides managed ML infrastructure with strong integration with Microsoft services. Azure OpenAI Service access is a unique advantage. Responsible AI tools address enterprise compliance needs.''',
        'pricing': '''Usage-based like SageMaker. Key costs:
- Compute instances for training and inference
- Storage for datasets and models
- Azure OpenAI Service usage

Similar price range to SageMaker.''',
        'pricing_note': '''Evaluate total cost including Azure OpenAI Service if using GPT models.''',
        'features': [
            {'icon': '🤖', 'title': 'Azure OpenAI', 'desc': 'Exclusive access to OpenAI models through Azure.'},
            {'icon': '🛡️', 'title': 'Responsible AI', 'desc': 'Built-in fairness, interpretability, and error analysis.'},
            {'icon': '📓', 'title': 'Studio', 'desc': 'Visual designer for building ML pipelines.'},
            {'icon': '🔧', 'title': 'AutoML', 'desc': 'Automated model selection and hyperparameter tuning.'},
            {'icon': '📊', 'title': 'MLflow', 'desc': 'Native MLflow integration for experiment tracking.'},
            {'icon': '🔗', 'title': 'Microsoft 365', 'desc': 'Integration with Microsoft productivity suite.'},
        ],
        'limitations': '''Less widely used than SageMaker. Smaller community. Some features less mature than AWS equivalent.''',
        'pros': ['Azure OpenAI access', 'Responsible AI tools', 'Microsoft ecosystem integration', 'Strong AutoML'],
        'cons': ['Smaller community', 'Less widely adopted', 'Some features less mature'],
        'buy_if': ['You\'re in the Microsoft ecosystem', 'You need Azure OpenAI Service', 'Responsible AI features matter'],
        'skip_if': ['You\'re on AWS or GCP', 'You want the largest community', 'You prefer open-source MLOps'],
        'alternatives': [
            {'name': 'AWS SageMaker', 'strength': 'Largest adoption', 'pricing': 'Similar'},
            {'name': 'Google Vertex AI', 'strength': 'GCP, Gemini integration', 'pricing': 'Similar'},
        ],
        'questions': ['Are we committed to Azure?', 'Do we need Azure OpenAI Service?', 'How important are responsible AI tools?'],
        'bottom_line': '''Azure ML is the natural choice for Microsoft shops. Azure OpenAI Service integration is a unique advantage. But SageMaker remains more widely adopted.''',
        'skills': ['Azure OpenAI', 'ML Studio', 'Automated ML', 'Responsible AI', 'MLflow'],
        'use_cases': ['Enterprise AI', 'Microsoft ecosystem', 'Responsible AI', 'Azure OpenAI deployment'],
    },

    'cursor': {
        'name': 'Cursor',
        'category': 'AI Dev Tools',
        'tagline': 'AI-first code editor',
        'website': 'https://cursor.sh',
        'logo_placeholder': '/assets/logos/cursor_logo.png',
        'rating': '4.7',
        'rating_count': '200+',
        'stats': [
            {'value': '4.7/5', 'label': 'User Rating'},
            {'value': 'VSCode', 'label': 'Based On'},
            {'value': '2023', 'label': 'Launched'},
            {'value': '$20', 'label': 'Pro/month'},
        ],
        'verdict': '''Cursor represents the future of AI-assisted development. The Composer feature for multi-file editing and natural language code generation goes beyond simple autocomplete. Worth trying for any developer—the productivity gains can be substantial.''',
        'overview': '''Cursor is an AI-first code editor built on VS Code. It integrates GPT-4 and Claude directly into the coding workflow with features like Composer for multi-file editing, inline AI commands, and codebase-aware chat.''',
        'pricing': '''- Free: Basic AI features
- Pro ($20/month): GPT-4, more requests
- Business ($40/user/month): Team features, admin controls''',
        'pricing_note': '''The free tier is useful but limited. Pro is worth it for heavy users.''',
        'features': [
            {'icon': '🎼', 'title': 'Composer', 'desc': 'AI-powered multi-file editing from natural language.'},
            {'icon': '💬', 'title': 'Codebase Chat', 'desc': 'Ask questions about your entire codebase.'},
            {'icon': '⚡', 'title': 'Inline Edits', 'desc': 'Quick AI edits with Cmd+K inline commands.'},
            {'icon': '🔗', 'title': 'VS Code Compatible', 'desc': 'All your VS Code extensions work.'},
            {'icon': '🧠', 'title': 'Model Choice', 'desc': 'Use GPT-4, Claude, or other models.'},
            {'icon': '📚', 'title': '@-mentions', 'desc': 'Reference files, docs, and web in prompts.'},
        ],
        'limitations': '''Subscription required for full features. Privacy concerns for some codebases. Learning curve for advanced features.''',
        'pros': ['Best-in-class AI coding experience', 'Multi-file editing', 'Codebase-aware', 'VS Code compatible'],
        'cons': ['Monthly subscription', 'Privacy concerns', 'Learning curve for advanced features'],
        'buy_if': ['You want the best AI coding experience', 'You do multi-file refactoring', 'You\'re already on VS Code'],
        'skip_if': ['You can\'t send code to cloud', 'You prefer minimal tooling', 'Free tools are sufficient'],
        'alternatives': [
            {'name': 'GitHub Copilot', 'strength': 'Wider IDE support, GitHub integration', 'pricing': '$10-19/month'},
            {'name': 'VS Code + Continue', 'strength': 'Open source, self-hosted option', 'pricing': 'Free'},
        ],
        'questions': ['Are we comfortable sending code to AI providers?', 'Is the subscription worth the productivity gains?', 'Should we evaluate vs GitHub Copilot?'],
        'bottom_line': '''Cursor is the leading AI code editor. The multi-file editing and codebase chat features justify the subscription for most developers.''',
        'skills': ['AI coding', 'Code completion', 'Chat interface', 'Composer', 'Multi-file editing'],
        'use_cases': ['Code writing', 'Refactoring', 'Documentation', 'Multi-file scaffolding'],
        'custom_page': True,  # Has dedicated review page
    },

    'github-copilot': {
        'name': 'GitHub Copilot',
        'category': 'AI Dev Tools',
        'tagline': 'AI pair programmer from GitHub',
        'website': 'https://github.com/features/copilot',
        'logo_placeholder': '/assets/logos/github_copilot_logo.png',
        'rating': '4.5',
        'rating_count': '500+',
        'stats': [
            {'value': '4.5/5', 'label': 'G2 Rating'},
            {'value': '1M+', 'label': 'Users'},
            {'value': '2021', 'label': 'Launched'},
            {'value': '$10-19', 'label': 'Per month'},
        ],
        'verdict': '''GitHub Copilot is the most widely adopted AI coding assistant. It\'s reliable, well-integrated, and continuously improving. The safe choice for teams that want AI coding assistance without switching editors.''',
        'overview': '''GitHub Copilot provides AI code suggestions powered by OpenAI. It works in VS Code, JetBrains IDEs, and GitHub.com. Copilot Chat adds conversational coding assistance.''',
        'pricing': '''- Individual: $10/month or $100/year
- Business: $19/user/month
- Enterprise: $39/user/month

Free for verified students and open source maintainers.''',
        'pricing_note': '''Business tier required for company use with IP protection features.''',
        'features': [
            {'icon': '✨', 'title': 'Code Completion', 'desc': 'Real-time suggestions as you type.'},
            {'icon': '💬', 'title': 'Copilot Chat', 'desc': 'Conversational AI in your editor.'},
            {'icon': '🔌', 'title': 'IDE Support', 'desc': 'Works in VS Code, JetBrains, Neovim, and more.'},
            {'icon': '🔗', 'title': 'GitHub Integration', 'desc': 'Copilot on GitHub.com for PRs and issues.'},
            {'icon': '📄', 'title': 'Docs', 'desc': 'Generate documentation from code.'},
            {'icon': '🧪', 'title': 'Tests', 'desc': 'Generate unit tests for functions.'},
        ],
        'limitations': '''Suggestions aren\'t always accurate. Less powerful than Cursor for multi-file editing. Chat is newer and less polished.''',
        'pros': ['Most widely adopted', 'Works in any major IDE', 'Reliable suggestions', 'GitHub integration'],
        'cons': ['Less powerful than Cursor', 'Chat feature less mature', 'Suggestions need review'],
        'buy_if': ['You want AI coding in your existing IDE', 'You\'re already using GitHub', 'You want the safe, mainstream choice'],
        'skip_if': ['You want the most advanced AI features', 'You prefer Cursor\'s approach', 'You need enterprise features on budget'],
        'alternatives': [
            {'name': 'Cursor', 'strength': 'More powerful multi-file editing', 'pricing': '$20/month'},
            {'name': 'Codeium', 'strength': 'Free tier, good quality', 'pricing': 'Free + paid'},
        ],
        'questions': ['Is Copilot powerful enough, or should we try Cursor?', 'Do we need Business tier for IP protection?', 'Are we getting value from the subscription?'],
        'bottom_line': '''GitHub Copilot is the safe, reliable choice for AI coding assistance. Not the most powerful, but the most widely supported and trusted.''',
        'skills': ['Code completion', 'Code suggestions', 'Chat', 'Test generation'],
        'use_cases': ['Code writing', 'Learning new languages', 'Boilerplate reduction', 'Documentation'],
    },
})


# CSS for review pages
REVIEW_PAGE_STYLES = '''
    /* Review Page Styles - Based on CRO Report best practices */

    .hero {
        background: linear-gradient(135deg, var(--bg-darker) 0%, var(--bg-dark) 100%);
        padding: 64px 0 48px;
        border-bottom: 1px solid var(--border);
    }

    .breadcrumb {
        font-size: 0.85rem;
        color: var(--text-muted);
        margin-bottom: 20px;
    }
    .breadcrumb a { color: var(--gold); text-decoration: none; }
    .breadcrumb a:hover { text-decoration: underline; }

    .badge {
        display: inline-block;
        background: rgba(232, 168, 124, 0.15);
        color: var(--gold);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 20px;
    }

    .hero-header {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 20px;
    }

    .hero-logo {
        width: 72px;
        height: 72px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
    }

    .hero-logo img {
        max-width: 56px;
        max-height: 56px;
        object-fit: contain;
    }

    .hero h1 {
        font-size: clamp(2rem, 4vw, 2.75rem);
        font-weight: 700;
        line-height: 1.2;
        color: var(--text-primary);
    }

    .hero .lead {
        font-size: 1.15rem;
        color: var(--text-secondary);
        max-width: 650px;
        margin-bottom: 32px;
        line-height: 1.7;
    }

    .verdict-box {
        background: rgba(232, 168, 124, 0.08);
        border: 1px solid rgba(232, 168, 124, 0.3);
        border-radius: 12px;
        padding: 24px;
        display: flex;
        gap: 16px;
    }

    .verdict-icon {
        width: 44px;
        height: 44px;
        background: var(--gold);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        flex-shrink: 0;
        color: var(--bg-dark);
    }

    .verdict-text {
        font-size: 0.95rem;
        line-height: 1.6;
        color: var(--text-secondary);
    }
    .verdict-text strong { color: var(--gold); }

    /* Stats Section */
    .stats-section {
        padding: 40px 0;
        background: var(--bg-card);
        border-bottom: 1px solid var(--border);
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
    }

    @media (max-width: 768px) {
        .stats-grid { grid-template-columns: repeat(2, 1fr); }
    }

    .stat-card {
        text-align: center;
        padding: 24px 16px;
        background: var(--bg-darker);
        border: 1px solid var(--border);
        border-radius: 10px;
    }

    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: var(--gold);
        line-height: 1;
        margin-bottom: 6px;
    }

    .stat-label {
        font-size: 0.8rem;
        color: var(--text-muted);
    }

    /* Content Sections */
    .content-section {
        padding: 48px 0;
        border-bottom: 1px solid var(--border-light);
    }

    .content-section:last-child { border-bottom: none; }

    .section-label {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--gold);
        margin-bottom: 10px;
    }

    .content-section h2 {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 20px;
    }

    .content-section h3 {
        font-size: 1.15rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 28px 0 14px;
    }

    .content-section p {
        margin-bottom: 16px;
        color: var(--text-secondary);
        line-height: 1.7;
    }

    .content-section ul {
        margin: 16px 0;
        padding-left: 24px;
        color: var(--text-secondary);
    }

    .content-section li {
        margin-bottom: 8px;
        line-height: 1.6;
    }

    /* Feature Grid */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin: 24px 0;
    }

    @media (max-width: 768px) {
        .feature-grid { grid-template-columns: 1fr; }
    }

    .feature-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 20px;
    }

    .feature-card h4 {
        font-size: 0.95rem;
        color: var(--text-primary);
        margin-bottom: 8px;
    }

    .feature-card p {
        font-size: 0.85rem;
        color: var(--text-muted);
        margin: 0;
    }

    .feature-icon {
        font-size: 1.5rem;
        margin-bottom: 12px;
    }

    /* Pros/Cons */
    .rec-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
        margin: 24px 0;
    }

    @media (max-width: 768px) {
        .rec-grid { grid-template-columns: 1fr; }
    }

    .rec-box {
        padding: 22px;
        border-radius: 10px;
        border: 2px solid;
    }

    .rec-box.use {
        background: rgba(40, 167, 69, 0.08);
        border-color: var(--green);
    }

    .rec-box.skip {
        background: rgba(220, 53, 69, 0.08);
        border-color: var(--red);
    }

    .rec-box h4 {
        font-size: 0.95rem;
        margin-bottom: 12px;
    }

    .rec-box.use h4 { color: var(--green); }
    .rec-box.skip h4 { color: var(--red); }

    .rec-box ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .rec-box li {
        padding: 5px 0 5px 18px;
        position: relative;
        font-size: 0.88rem;
        color: var(--text-secondary);
    }

    .rec-box li::before {
        content: '→';
        position: absolute;
        left: 0;
        color: var(--text-muted);
    }

    /* Decision Framework */
    .stage-section { margin: 28px 0; }

    .stage-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 14px;
    }

    .stage-badge {
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.75rem;
        text-transform: uppercase;
    }

    .stage-badge.buy { background: rgba(40, 167, 69, 0.15); color: var(--green); }
    .stage-badge.skip { background: rgba(220, 53, 69, 0.15); color: var(--red); }

    /* Alert Boxes */
    .alert {
        padding: 18px 20px;
        border-radius: 8px;
        margin: 20px 0;
        display: flex;
        gap: 14px;
        border-left: 4px solid;
    }

    .alert-icon {
        font-size: 1.3rem;
        flex-shrink: 0;
    }

    .alert-success {
        background: rgba(40, 167, 69, 0.08);
        border-left-color: var(--green);
    }

    .alert-danger {
        background: rgba(220, 53, 69, 0.08);
        border-left-color: var(--red);
    }

    .alert-warning {
        background: rgba(232, 168, 124, 0.1);
        border-left-color: var(--gold);
    }

    .alert h4 {
        font-weight: 700;
        margin-bottom: 6px;
        color: var(--text-primary);
        font-size: 0.95rem;
    }

    .alert p {
        margin: 0;
        font-size: 0.9rem;
    }

    /* Comparison Table */
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin: 24px 0;
        font-size: 0.9rem;
    }

    .comparison-table th {
        background: var(--bg-darker);
        color: var(--text-primary);
        padding: 12px 16px;
        text-align: left;
        font-weight: 600;
        border: 1px solid var(--border);
    }

    .comparison-table td {
        padding: 12px 16px;
        border: 1px solid var(--border);
        vertical-align: top;
        color: var(--text-secondary);
    }

    .comparison-table tr:nth-child(even) { background: var(--bg-card); }

    /* Questions List */
    .questions-list {
        background: var(--bg-darker);
        padding: 28px;
        border-radius: 12px;
        margin: 28px 0;
        border: 1px solid var(--border);
    }

    .questions-list h3 {
        color: var(--gold);
        margin-bottom: 18px;
        font-size: 1.1rem;
    }

    .questions-list ol {
        padding-left: 20px;
        margin: 0;
    }

    .questions-list li {
        padding: 10px 0;
        border-bottom: 1px solid var(--border-light);
        font-size: 0.95rem;
        color: var(--text-secondary);
    }

    .questions-list li:last-child { border-bottom: none; }

    /* Bottom Line */
    .bottom-line {
        background: linear-gradient(135deg, var(--bg-darker) 0%, var(--bg-dark) 100%);
        border: 1px solid var(--border);
        padding: 36px;
        border-radius: 12px;
        margin: 32px 0;
    }

    .bottom-line h3 {
        color: var(--gold);
        font-size: 1.35rem;
        margin-bottom: 18px;
    }

    .bottom-line p {
        font-size: 1rem;
        line-height: 1.7;
    }

    .bottom-line ul {
        margin: 14px 0 0 18px;
    }

    .bottom-line li {
        margin-bottom: 8px;
    }

    /* CTA Section */
    .cta-section {
        text-align: center;
        padding: 48px 24px;
        background: var(--bg-card);
        border-radius: 12px;
        margin: 32px 0;
    }

    .cta-section h2 { margin-bottom: 12px; }
    .cta-section p { color: var(--text-secondary); margin-bottom: 24px; }

    .btn {
        display: inline-block;
        padding: 14px 28px;
        border-radius: 8px;
        font-weight: 600;
        text-decoration: none;
        font-size: 0.95rem;
    }

    .btn-primary { background: var(--gold); color: var(--bg-dark); }
    .btn-secondary {
        background: transparent;
        color: var(--text-primary);
        border: 2px solid var(--border);
        margin-left: 12px;
    }

    /* Mobile */
    @media (max-width: 768px) {
        .hero-header { flex-direction: column; text-align: center; }
        .verdict-box { flex-direction: column; text-align: center; }
    }
'''

# Tools Index Page Styles
TOOLS_INDEX_STYLES = '''
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

    .stats-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-top: 32px;
    }

    @media (max-width: 768px) {
        .stats-row { grid-template-columns: repeat(2, 1fr); }
    }

    .stat-box {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 18px;
        text-align: center;
    }

    .stat-number {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--gold);
        line-height: 1;
    }

    .stat-label {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 6px;
    }

    .category-section {
        padding: 2.5rem 0;
        border-bottom: 1px solid var(--border-light);
    }

    .category-section:last-child { border-bottom: none; }

    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }

    .section-header h2 {
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    .section-icon { font-size: 1.4rem; }

    .section-description {
        color: var(--text-secondary);
        margin-bottom: 24px;
        font-size: 0.95rem;
    }

    .tools-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 20px;
    }

    @media (max-width: 768px) {
        .tools-grid { grid-template-columns: 1fr; }
    }

    .tool-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        text-decoration: none;
        color: inherit;
        transition: all 0.2s;
        display: flex;
        flex-direction: column;
    }

    .tool-card:hover {
        border-color: var(--gold);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transform: translateY(-2px);
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
        background: rgba(232, 168, 124, 0.15);
        color: var(--gold);
    }

    .card-logos {
        display: flex;
        gap: 10px;
        margin-bottom: 16px;
    }

    .card-logo {
        width: 40px;
        height: 40px;
        background: var(--bg-darker);
        border: 1px solid var(--border);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        font-size: 1.25rem;
    }

    .card-logo img {
        max-width: 32px;
        max-height: 32px;
        object-fit: contain;
    }

    .tool-card h3 {
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 8px;
    }

    .tool-card p {
        font-size: 0.9rem;
        color: var(--text-secondary);
        line-height: 1.55;
        flex-grow: 1;
        margin-bottom: 0;
    }

    .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid var(--border-light);
    }

    .card-meta { font-size: 0.8rem; color: var(--text-muted); }
    .card-link { font-size: 0.85rem; font-weight: 600; color: var(--gold); }
'''


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


def generate_tool_review_page(slug, tool_data, job_count):
    """Generate a full review page following CRO Report best practices"""

    # Skip if it has a custom page (like Cursor review)
    if tool_data.get('custom_page'):
        print(f"  Skipping {tool_data['name']} (has custom review page)")
        return slug

    tool_dir = f"{TOOLS_DIR}/{slug}"
    os.makedirs(tool_dir, exist_ok=True)

    # Build stats HTML
    stats_html = ""
    for stat in tool_data.get('stats', []):
        stats_html += f'''
            <div class="stat-card">
                <div class="stat-number">{stat['value']}</div>
                <div class="stat-label">{stat['label']}</div>
            </div>
        '''

    # Build features HTML
    features_html = ""
    for feature in tool_data.get('features', []):
        features_html += f'''
            <div class="feature-card">
                <div class="feature-icon">{feature['icon']}</div>
                <h4>{feature['title']}</h4>
                <p>{feature['desc']}</p>
            </div>
        '''

    # Build pros HTML
    pros_html = ""
    for pro in tool_data.get('pros', []):
        pros_html += f"<li>{pro}</li>"

    # Build cons HTML
    cons_html = ""
    for con in tool_data.get('cons', []):
        cons_html += f"<li>{con}</li>"

    # Build buy_if HTML
    buy_if_html = ""
    for item in tool_data.get('buy_if', []):
        buy_if_html += f"<li>{item}</li>"

    # Build skip_if HTML
    skip_if_html = ""
    for item in tool_data.get('skip_if', []):
        skip_if_html += f"<li>{item}</li>"

    # Build alternatives table HTML
    alternatives_html = ""
    for alt in tool_data.get('alternatives', []):
        alternatives_html += f'''
            <tr>
                <td><strong>{alt['name']}</strong></td>
                <td>{alt['strength']}</td>
                <td>{alt['pricing']}</td>
            </tr>
        '''

    # Build questions HTML
    questions_html = ""
    for q in tool_data.get('questions', []):
        questions_html += f"<li>{q}</li>"

    # Get logo placeholder with proper alt text
    logo_alt = f"{tool_data['name']} logo - {tool_data.get('category', 'AI tool')}"
    logo_html = get_img_tag(tool_data.get("logo_placeholder", ""), logo_alt, loading="eager") if tool_data.get('logo_placeholder') else '🔧'

    # Generate Review schema for rich snippets
    tool_for_schema = {
        'name': tool_data['name'],
        'slug': slug,
        'rating': tool_data.get('rating', '0'),
        'rating_count': tool_data.get('rating_count', '0'),
        'tagline': tool_data.get('tagline', ''),
        'verdict': tool_data.get('verdict', ''),
        'category': tool_data.get('category', 'DeveloperApplication'),
        'website': tool_data.get('website', '')
    }
    review_schema = generate_review_schema(tool_for_schema)

    # Generate breadcrumbs with schema
    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'AI Tools', 'url': '/tools/'},
        {'name': tool_data['name'], 'url': f'/tools/{slug}/'}
    ]
    breadcrumb_html_block = get_breadcrumb_html(breadcrumbs)

    # Generate FAQ schema from tool data
    faqs = []
    # Add pricing FAQ if pricing data exists
    if tool_data.get('pricing_tiers'):
        pricing_summary = ", ".join([f"{t['name']}: {t['price']}" for t in tool_data['pricing_tiers'][:3]])
        faqs.append({
            'question': f"What does {tool_data['name']} cost?",
            'answer': f"{tool_data['name']} offers these pricing tiers: {pricing_summary}. See the full pricing section above for details on what each tier includes."
        })
    # Add key features FAQ
    if tool_data.get('features'):
        feature_names = [f['title'] for f in tool_data['features'][:4]]
        faqs.append({
            'question': f"What are the main features of {tool_data['name']}?",
            'answer': f"Key features include: {', '.join(feature_names)}. {tool_data['name']} is known for: {tool_data.get('tagline', '')}."
        })
    # Add alternatives FAQ
    if tool_data.get('alternatives'):
        alt_names = [a['name'] for a in tool_data['alternatives'][:3]]
        faqs.append({
            'question': f"What are the best alternatives to {tool_data['name']}?",
            'answer': f"Top alternatives include: {', '.join(alt_names)}. Each has different strengths - see the alternatives comparison table above for detailed analysis."
        })
    # Add verdict FAQ
    if tool_data.get('verdict'):
        faqs.append({
            'question': f"Is {tool_data['name']} worth it in 2026?",
            'answer': tool_data['verdict']
        })
    faq_schema = generate_faq_schema(faqs) if faqs else ''

    extra_styles = f'<style>{REVIEW_PAGE_STYLES}</style>\n    {review_schema}\n    {faq_schema}'

    # SEO-optimized title (max 60 chars for SERP display)
    page_title = f'{tool_data["name"]} Review 2026: Pricing & Pros/Cons'

    html = get_html_head(
        title=page_title,
        description=f'{tool_data["name"]} review for 2026. {tool_data.get("tagline", "")}. Honest assessment with pricing, pros/cons, and alternatives.',
        page_path=f'tools/{slug}/',
        extra_head=extra_styles
    )

    html += get_nav_html(active_page='tools')

    html += f'''
    <header class="hero">
        <div class="container">
            {breadcrumb_html_block}
            <span class="badge">{tool_data['category'].upper()}</span>
            <div class="hero-header">
                <div class="hero-logo">{logo_html}</div>
                <h1>{tool_data['name']} Review 2026</h1>
            </div>
            <p class="lead">{tool_data.get('tagline', tool_data['name'])}. {job_count} jobs currently require this skill.</p>

            <div class="verdict-box">
                <div class="verdict-icon">⚡</div>
                <div class="verdict-text">
                    <strong>The Verdict:</strong> {tool_data.get('verdict', '')}
                </div>
            </div>
        </div>
    </header>

    <section class="stats-section">
        <div class="container">
            <div class="stats-grid">
                {stats_html}
            </div>
        </div>
    </section>

    <main>
        <section class="content-section">
            <div class="container">
                <div class="section-label">Company Overview</div>
                <h2>What Is {tool_data['name']}?</h2>
                <p>{tool_data.get('overview', '').replace(chr(10)+chr(10), '</p><p>')}</p>
            </div>
        </section>

        <section class="content-section">
            <div class="container">
                <div class="section-label">Pricing</div>
                <h2>What {tool_data['name']} Costs</h2>
                <p>{tool_data.get('pricing', '').replace(chr(10)+chr(10), '</p><p>')}</p>

                {f'<div class="alert alert-warning"><div class="alert-icon">💰</div><div><h4>Pricing Note</h4><p>{tool_data.get("pricing_note", "")}</p></div></div>' if tool_data.get('pricing_note') else ''}
            </div>
        </section>

        <section class="content-section">
            <div class="container">
                <div class="section-label">Core Features</div>
                <h2>What {tool_data['name']} Does Well</h2>

                <div class="feature-grid">
                    {features_html}
                </div>
            </div>
        </section>

        <section class="content-section">
            <div class="container">
                <div class="section-label">Limitations</div>
                <h2>Where {tool_data['name']} Falls Short</h2>
                <p>{tool_data.get('limitations', '').replace(chr(10)+chr(10), '</p><p>')}</p>
            </div>
        </section>

        <section class="content-section">
            <div class="container">
                <div class="section-label">Evaluation</div>
                <h2>Pros and Cons Summary</h2>

                <div class="rec-grid">
                    <div class="rec-box use">
                        <h4>✓ The Good Stuff</h4>
                        <ul>{pros_html}</ul>
                    </div>
                    <div class="rec-box skip">
                        <h4>✗ The Problems</h4>
                        <ul>{cons_html}</ul>
                    </div>
                </div>
            </div>
        </section>

        <section class="content-section">
            <div class="container">
                <div class="section-label">Decision Framework</div>
                <h2>Should You Use {tool_data['name']}?</h2>

                <div class="stage-section">
                    <div class="stage-header">
                        <span class="stage-badge buy">USE {tool_data['name'].upper()} IF</span>
                    </div>
                    <div class="alert alert-success">
                        <div class="alert-icon">✅</div>
                        <div>
                            <ul style="margin: 0; padding-left: 18px;">{buy_if_html}</ul>
                        </div>
                    </div>
                </div>

                <div class="stage-section">
                    <div class="stage-header">
                        <span class="stage-badge skip">SKIP {tool_data['name'].upper()} IF</span>
                    </div>
                    <div class="alert alert-danger">
                        <div class="alert-icon">❌</div>
                        <div>
                            <ul style="margin: 0; padding-left: 18px;">{skip_if_html}</ul>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section class="content-section">
            <div class="container">
                <div class="section-label">Alternatives</div>
                <h2>{tool_data['name']} Alternatives</h2>

                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Tool</th>
                            <th>Strength</th>
                            <th>Pricing</th>
                        </tr>
                    </thead>
                    <tbody>
                        {alternatives_html}
                    </tbody>
                </table>
            </div>
        </section>

        <section class="content-section">
            <div class="container">
                <div class="questions-list">
                    <h3>🔍 Questions to Ask Before Committing</h3>
                    <ol>{questions_html}</ol>
                </div>
            </div>
        </section>

        <section class="content-section">
            <div class="container">
                <div class="bottom-line">
                    <h3>The Bottom Line</h3>
                    <p>{tool_data.get('bottom_line', '').replace(chr(10)+chr(10), '</p><p>')}</p>
                </div>
            </div>
        </section>

        <section class="content-section">
            <div class="container">
                <div class="cta-section">
                    <h2>Find {tool_data['name']} Jobs</h2>
                    <p>Browse AI roles that require {tool_data['name']} expertise.</p>
                    <a href="/jobs/" class="btn btn-primary">View All AI Jobs →</a>
                    <a href="/tools/" class="btn btn-secondary">Browse All Tools</a>
                </div>
            </div>
        </section>
    </main>
    '''

    html += get_footer_html()

    output_path = f"{tool_dir}/index.html"
    with open(output_path, 'w') as f:
        f.write(html)

    return slug


def generate_tools_index(tools_with_counts):
    """Generate the tools index page with logo placeholders"""
    os.makedirs(TOOLS_DIR, exist_ok=True)

    # Category icon mapping
    category_icons = {
        'LLM Providers': '🤖',
        'LLM Frameworks': '🔗',
        'ML Platforms': '🤗',
        'Vector Databases': '🗄️',
        'ML Frameworks': '🧠',
        'Cloud ML': '☁️',
        'AI Dev Tools': '💻',
    }

    # AI Guides section
    ai_guides = [
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
    for slug, data in tools_with_counts.items():
        category = data['category']
        if category not in categories:
            categories[category] = []
        categories[category].append((slug, data))

    # Count totals
    total_reviews = len(tools_with_counts)

    # Generate categories HTML
    categories_html = ""
    for category, tools in sorted(categories.items()):
        tools_sorted = sorted(tools, key=lambda x: x[1].get('job_count', 0), reverse=True)
        icon = category_icons.get(category, '🔧')

        tools_cards = ""
        for slug, data in tools_sorted:
            logo_html = get_img_tag(data.get("logo_placeholder", ""), f"{data['name']} logo", loading="lazy") if data.get('logo_placeholder') else '🔧'
            job_count = data.get('job_count', 0)
            job_text = "job" if job_count == 1 else "jobs"

            tools_cards += f'''
            <a href="/tools/{slug}/" class="tool-card">
                <span class="card-badge">In-Depth</span>
                <div class="card-logos">
                    <div class="card-logo">{logo_html}</div>
                </div>
                <h3>{data['name']}</h3>
                <p>{data.get('tagline', '')}</p>
                <div class="card-footer">
                    <span class="card-meta">{job_count} {job_text}</span>
                    <span class="card-link">Read Analysis →</span>
                </div>
            </a>
            '''

        categories_html += f'''
        <div class="category-section">
            <div class="section-header">
                <span class="section-icon">{icon}</span>
                <h2>{category}</h2>
            </div>
            <div class="tools-grid">
                {tools_cards}
            </div>
        </div>
        '''

    # Generate AI Guides section
    guides_cards = ""
    for guide in ai_guides:
        guides_cards += f'''
            <a href="{guide['url']}" class="tool-card">
                <h3>{guide['title']}</h3>
                <p>{guide['desc']}</p>
                <div class="card-footer">
                    <span class="card-meta">{guide['count']}</span>
                    <span class="card-link">Read Guide →</span>
                </div>
            </a>
        '''

    ai_guides_section = f'''
        <div class="category-section">
            <div class="section-header">
                <span class="section-icon">📚</span>
                <h2>AI Guides</h2>
            </div>
            <p class="section-description">Comprehensive comparison guides to find the best AI tools for your specific use case.</p>
            <div class="tools-grid">
                {guides_cards}
            </div>
        </div>
    '''

    # Generate JSON-LD schemas for tools hub
    tools_for_schema = []
    for slug, data in list(tools_with_counts.items())[:10]:
        tools_for_schema.append({
            'name': data['name'],
            'url': f"/tools/{slug}/",
            'description': data.get('tagline', '')
        })

    collection_schema = generate_collectionpage_schema(
        name="AI Tools Directory",
        description="Honest reviews of AI tools, LLM frameworks, and ML platforms for AI professionals.",
        url="/tools/",
        item_count=total_reviews,
        keywords=["AI tools", "LLM frameworks", "ML platforms", "AI development tools", "LangChain", "OpenAI"]
    )
    itemlist_schema = generate_itemlist_schema(
        items=tools_for_schema,
        list_name="AI Tools & Reviews",
        url="/tools/"
    )
    schemas_html = f"{collection_schema}\n    {itemlist_schema}"

    extra_styles = f'<style>{TOOLS_INDEX_STYLES}</style>\n    {schemas_html}'

    html = get_html_head(
        title='AI Tools Directory | In-Depth Reviews & Comparisons',
        description='Honest reviews of AI tools, LLM frameworks, and ML platforms for AI professionals. Real pricing, limitations, and recommendations.',
        page_path='tools/',
        extra_head=extra_styles
    )

    html += get_nav_html(active_page='tools')

    html += f'''
    <section class="tools-hero">
        <div class="container">
            <h1>AI Tools & Reviews</h1>
            <p>Honest assessments of AI tools from a practitioner perspective. Real pricing, limitations, and recommendations.</p>

            <div class="stats-row">
                <div class="stat-box">
                    <div class="stat-number">{total_reviews}</div>
                    <div class="stat-label">In-Depth Reviews</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">8</div>
                    <div class="stat-label">AI Guides</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{len(categories)}</div>
                    <div class="stat-label">Categories</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">Weekly</div>
                    <div class="stat-label">Updates</div>
                </div>
            </div>
        </div>
    </section>

    <main>
        <div class="container">
            <div class="seo-intro" style="max-width: 800px; margin-bottom: 3rem; color: var(--text-secondary); line-height: 1.8;">
                <p style="margin-bottom: 1rem;">
                    The AI tools landscape is evolving rapidly. AI Market Pulse provides honest, practitioner-written reviews—not vendor marketing. We dig into real pricing, actual limitations, and who each tool is really for.
                </p>
                <p style="margin-bottom: 1rem;">
                    From foundational frameworks like <strong style="color: var(--text-primary);">PyTorch</strong> to LLM tools like <strong style="color: var(--text-primary);">LangChain</strong> and <strong style="color: var(--text-primary);">LlamaIndex</strong>, our directory covers the complete AI/ML stack. Each review includes pricing, pros/cons, decision frameworks, and alternatives.
                </p>
            </div>

            {ai_guides_section}
            {categories_html}

            {get_cta_box(
                title="Stay Updated on AI Tools",
                description="Get weekly insights on the latest AI tools, frameworks, and job opportunities.",
                button_text="Join the Community",
                button_url="/join/"
            )}
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
    print("  AI MARKET PULSE - GENERATING TOOL REVIEW PAGES")
    print("="*70)

    # Load job data for counting
    jobs_df = pd.DataFrame()
    job_files = glob.glob(f"{DATA_DIR}/ai_jobs_*.csv")
    if job_files:
        latest_file = sorted(job_files)[-1]
        jobs_df = pd.read_csv(latest_file)
        print(f"  Loaded {len(jobs_df)} jobs for tool counting")

    # Generate pages
    tools_with_counts = {}
    generated = 0

    for slug, tool_data in TOOL_REVIEWS.items():
        job_count = get_tool_job_count(tool_data['name'], jobs_df)
        tool_data['job_count'] = job_count
        tools_with_counts[slug] = tool_data

        result = generate_tool_review_page(slug, tool_data, job_count)
        if result:
            generated += 1
            print(f"  Generated: /tools/{slug}/")

    # Generate index
    generate_tools_index(tools_with_counts)

    print(f"\n{'='*70}")
    print(f"  Generated {generated} tool review pages")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
