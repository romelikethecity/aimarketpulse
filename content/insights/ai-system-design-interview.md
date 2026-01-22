System design interviews for AI roles are different from traditional software engineering. You'll be asked to design RAG systems, agent architectures, and ML pipelines. Here's how to prepare and ace these interviews.

## How AI System Design Differs

**Traditional SWE system design:**
- Scale a web service to 1M users
- Design a messaging system
- Build a distributed cache

**AI system design:**
- Design a RAG system for customer support
- Build an AI agent that can book travel
- Architect an ML pipeline for fraud detection
- Create a multi-modal content moderation system

The principles (scalability, reliability, tradeoffs) apply, but the components and considerations are different.

## The AI System Design Framework

Use this framework for any AI system design question:

### 1. Clarify Requirements (5 minutes)

**Functional requirements:**
- What exactly should the system do?
- What are the inputs and outputs?
- What quality level is acceptable?
- Who are the users?

**Non-functional requirements:**
- Scale (queries per second, data volume)
- Latency (real-time? async OK?)
- Accuracy (what error rate is acceptable?)
- Cost constraints
- Availability requirements

**Key questions to ask:**
> "What's the expected query volume?"
> "Is this real-time or can it be async?"
> "What accuracy level do we need?"
> "What's the latency budget?"
> "What are the cost constraints?"

### 2. High-Level Design (10 minutes)

Draw the major components:
- Data ingestion
- Processing pipeline
- Storage systems
- Serving layer
- Monitoring

**For AI systems, always include:**
- Where the AI/ML happens
- Data flow through the system
- Evaluation/feedback loop

### 3. Deep Dive (15-20 minutes)

Pick 2-3 components to detail:
- Model selection and why
- Data pipeline specifics
- Scaling approach
- Reliability mechanisms

### 4. Tradeoffs and Extensions (5-10 minutes)

Discuss:
- What would you do differently with more time/resources?
- How would this scale 10x? 100x?
- What are the failure modes?
- How would you monitor and improve it?

## Common AI System Design Questions

### RAG System Design

**Question:** "Design a customer support system that can answer questions about our product documentation."

**Key components:**

```
[Documents] → [Ingestion Pipeline] → [Vector DB]
                                          ↓
[User Query] → [Embedding] → [Retrieval] → [LLM] → [Response]
```

**Clarifying questions:**
- How many documents? How often do they update?
- Expected QPS?
- What latency is acceptable?
- What accuracy/hallucination rate is tolerable?
- Multi-language support?

**Key design decisions:**
- Chunking strategy (size, overlap, method)
- Embedding model (OpenAI vs open source)
- Vector database (Pinecone, Weaviate, pgvector)
- Retrieval strategy (simple vs hybrid vs re-rank)
- LLM choice and prompt design

**Tradeoffs to discuss:**
- Chunking size: smaller = more precise, more retrieval calls
- Hybrid search: better recall, more complexity
- Re-ranking: better precision, added latency
- Caching: faster responses, stale content risk

### Agent System Design

**Question:** "Design an AI agent that can research topics and produce comprehensive reports."

**Key components:**

```
[User Request] → [Planning Agent] → [Research Agents] → [Synthesis] → [Report]
                        ↓
              [Tools: Search, Docs, APIs]
```

**Key design decisions:**
- Single agent vs multi-agent
- Tool design and orchestration
- State management (memory)
- Error handling and recovery
- Human-in-the-loop checkpoints

**Tradeoffs to discuss:**
- Autonomy vs control
- Breadth vs depth of research
- Cost vs comprehensiveness
- Latency vs quality

### ML Pipeline Design

**Question:** "Design a fraud detection system for a payments company."

**Key components:**

```
[Transactions] → [Feature Engineering] → [Model Inference] → [Decision]
                         ↓                        ↓
                   [Feature Store]          [Model Registry]
```

**Key design decisions:**
- Real-time vs batch features
- Model type (rule-based, ML, hybrid)
- Training pipeline and retraining frequency
- Threshold tuning and human review
- Feedback loop from decisions

**Tradeoffs to discuss:**
- Precision vs recall (false positives vs fraud)
- Latency vs accuracy
- Automation vs human review
- Cost of false positives vs missed fraud

### Content Moderation Design

**Question:** "Design a content moderation system for a social media platform."

**Key components:**

```
[Content] → [Multi-Modal Analysis] → [Classification] → [Action]
                   ↓                        ↓
            [Images, Video, Text]    [Human Review Queue]
```

**Key design decisions:**
- Modality-specific models vs unified
- Threshold tuning for different harm types
- Appeals and human review process
- Real-time vs queued processing
- Edge cases and context

## Key Concepts to Know

### Evaluation and Metrics

Always discuss how you'd measure success:

**RAG systems:**
- Retrieval: recall@k, precision@k
- Generation: accuracy, hallucination rate
- End-to-end: user satisfaction, task completion

**Agent systems:**
- Task success rate
- Cost per task
- Time to completion
- Error rate

**ML systems:**
- Precision, recall, F1
- AUC-ROC
- Business metrics (fraud caught, false positive rate)

### Scaling Considerations

**For AI systems:**
- Token/embedding throughput
- GPU/TPU utilization
- Caching strategies
- Batching for efficiency

**Common scaling patterns:**
- Embedding caching (avoid re-computing)
- Response caching (same queries)
- Async processing for non-real-time
- Model distillation for faster inference

### Cost Management

AI systems have unique cost considerations:

**LLM API costs:**
- Model selection (GPT-4 vs GPT-3.5 vs open source)
- Token optimization (shorter prompts, efficient retrieval)
- Caching (avoid redundant calls)
- Tiering (expensive model for hard cases)

**Infrastructure costs:**
- GPU instances for inference
- Vector database storage and queries
- Data storage and processing

### Reliability Patterns

**For AI systems:**
- Fallback models (if primary fails)
- Graceful degradation (return cached/default response)
- Human escalation (for uncertain cases)
- Retry with backoff (for transient failures)

## Interview Tips

### Structure Your Answer

Use clear headings as you talk:
> "First, let me clarify the requirements..."
> "Now I'll draw the high-level architecture..."
> "Let me dive deeper into the retrieval system..."
> "Here are the key tradeoffs to consider..."

### Think Aloud

Explain your reasoning:
> "I'm choosing Pinecone here because we need low-latency retrieval and they handle scaling..."
> "The tradeoff is between cost and quality—let me explain why I'd optimize for quality first..."

### Ask Questions

Don't assume. Clarify:
> "Before I design, can I ask about the expected scale?"
> "Is this real-time critical, or can we batch some processing?"

### Discuss Tradeoffs

Every decision has tradeoffs. Show you understand them:
> "We could use a larger model for better quality, but that increases latency and cost. Given the requirements, I'd start with..."

### Draw Diagrams

Even virtual interviews support diagrams. Use them:
- Boxes for components
- Arrows for data flow
- Labels for key details

### Handle What You Don't Know

If asked about something unfamiliar:
> "I'm not deeply familiar with that specific tool, but based on what I know about similar systems, I'd approach it like..."

## Practice Problems

Try designing these systems:

1. **Document Q&A:** Legal document search and question answering
2. **Code Review Agent:** Automated code review with suggestions
3. **Multimodal Search:** Search across text, images, and video
4. **Recommendation System:** AI-powered product recommendations
5. **Meeting Assistant:** Transcription, summarization, and action items

For each:
- Define requirements (make assumptions)
- Draw high-level architecture
- Deep dive on 2-3 components
- Discuss tradeoffs and extensions

## The Bottom Line

AI system design interviews test whether you can architect complete AI systems, not just build components. Practice the framework: clarify requirements, draw high-level design, deep dive on key components, discuss tradeoffs.

Know the common patterns for RAG, agents, and ML pipelines. Understand cost, scale, and reliability considerations unique to AI systems. Always discuss evaluation and how you'd measure success.

Preparation matters. Practice designing systems out loud, explaining your reasoning as you go. The best candidates demonstrate both technical depth and clear thinking under ambiguity.
