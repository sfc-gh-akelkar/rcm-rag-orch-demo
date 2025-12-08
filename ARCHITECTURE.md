# RCM Intelligence Hub - Technical Architecture

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│                      (Streamlit Chat UI)                            │
│                                                                     │
│  • Single chat window (no tool selection)                           │
│  • Debug panel (cost & routing visibility)                          │
│  • Session statistics dashboard                                     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                              │
│                    (orchestrator.py)                                │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │         SUPERVISOR AGENT (Router)                             │ │
│  │                                                               │ │
│  │  1. Intent Classification                                     │ │
│  │     • Model: llama3.2-3b (lightweight, fast)                 │ │
│  │     • Output: ANALYTICS | KNOWLEDGE_BASE | GENERAL           │ │
│  │                                                               │ │
│  │  2. RCM Terminology Enhancement                               │ │
│  │     • Detect domain terms (remit, write-off, codes)          │ │
│  │     • Add context definitions                                 │ │
│  │     • Expand abbreviations (A/R, ERA, COB)                   │ │
│  │                                                               │ │
│  │  3. Cost Tracking                                             │ │
│  │     • Count input/output tokens                               │ │
│  │     • Estimate cost per query                                 │ │
│  │     • Aggregate session statistics                            │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                             │                                       │
│              ┌──────────────┼──────────────┐                        │
│              │              │              │                        │
└──────────────┼──────────────┼──────────────┼────────────────────────┘
               │              │              │
               ▼              ▼              ▼
┌──────────────────┐ ┌────────────────┐ ┌──────────────────┐
│   ANALYTICS      │ │ KNOWLEDGE BASE │ │    GENERAL       │
│   ROUTE          │ │    ROUTE       │ │    ROUTE         │
│                  │ │                │ │                  │
│ Cortex Analyst   │ │ Cortex Search  │ │ Cortex Complete  │
│ (mistral-large)  │ │ (RAG Pattern)  │ │ (llama3.2-3b)    │
│                  │ │                │ │                  │
│ • SQL generation │ │ • Doc retrieval│ │ • Conversation   │
│ • Metric calc    │ │ • Context build│ │ • Help/guidance  │
│ • Trend analysis │ │ • Answer gen   │ │ • Clarification  │
└────────┬─────────┘ └────────┬───────┘ └────────┬─────────┘
         │                    │                   │
         ▼                    ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   SNOWFLAKE DATA LAYER                      │
│                                                             │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────┐ │
│  │  Semantic Views │  │  Cortex Search   │  │   Tables  │ │
│  │                 │  │    Services      │  │           │ │
│  │ • Claims        │  │  • Finance Docs  │  │ • Claims  │ │
│  │   Processing    │  │  • Operations    │  │ • Denials │ │
│  │ • Denials       │  │  • Compliance    │  │ • Payers  │ │
│  │   Management    │  │  • Strategy      │  │ • Providers│ │
│  │                 │  │  • Knowledge Base│  │           │ │
│  └─────────────────┘  └──────────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. User Interface Layer (`app.py`)

**Purpose**: Single, unified chat interface

**Key Features**:
- Chat-based interaction (no tool selection menus)
- Real-time session statistics
- Optional debug panel for transparency
- Sample question buttons for discovery

**Technology**: Streamlit

**User Experience Flow**:
```
1. User types question in chat
2. System shows "Analyzing query and routing..."
3. Response appears with answer
4. (Optional) Debug panel shows routing & cost
```

---

### 2. Orchestration Layer

#### 2.1 Supervisor Agent (`orchestrator.py`)

**Purpose**: Central intelligence that routes queries

**Process Flow**:
```python
def process_query(user_query):
    # Step 1: Classify intent
    intent, reasoning = determine_intent(user_query)
    
    # Step 2: Route to appropriate handler
    if intent == ANALYTICS:
        result = execute_analytics_query(user_query)
    elif intent == KNOWLEDGE_BASE:
        result = execute_knowledge_base_query(user_query)
    else:
        result = execute_general_query(user_query)
    
    # Step 3: Track cost
    track_query_cost(intent, result)
    
    return result
```

**Intent Classification**:
- Uses lightweight LLM (llama3.2-3b) for fast classification
- Prompt engineered for RCM domain
- Fallback to keyword-based classification if LLM fails

**Routing Logic**:

| Intent | Trigger Patterns | Route To | Use Case |
|--------|-----------------|----------|----------|
| ANALYTICS | "what is", "show me", "calculate", "rate", "total" | Cortex Analyst | Metrics, trends, calculations |
| KNOWLEDGE_BASE | "how do i", "policy", "procedure", "compliance" | Cortex Search | Documentation, procedures |
| GENERAL | "hello", "help", "explain", "what can you" | Cortex Complete | Conversation, guidance |

#### 2.2 RCM Terminology Enhancement (`rcm_terminology.py`)

**Purpose**: Add domain context for healthcare terms

**Terminology Handled**:

| User Term | Enhanced Context |
|-----------|------------------|
| "remit" | "remittance advice (ERA - Electronic Remittance Advice)" |
| "write-off" | "contractual adjustment or bad debt (CO-45, PR-1 codes)" |
| "A/R" | "accounts receivable (days since claim submission)" |
| "clean claim" | "claim accepted on first submission without errors" |
| "CO-45" | "Contractual Obligation code 45: charge exceeds fee schedule" |
| "PR-1" | "Patient Responsibility code 1: patient deductible amount" |

**Enhancement Process**:
```python
def enhance_query(query):
    # Detect RCM terms in query
    detected_terms = detect_rcm_terms(query)
    
    # Build context
    context = "RCM Terminology:\n"
    for term, definition in detected_terms:
        context += f"- {term}: {definition}\n"
    
    # Prepend to query
    enhanced_query = f"{context}\n\nUser Query: {query}"
    
    return enhanced_query
```

#### 2.3 Cost Tracker (`cost_tracker.py`)

**Purpose**: Monitor token usage and estimate costs

**Tracking Metrics**:
- Input tokens (query + context)
- Output tokens (response)
- Total tokens per query
- Estimated cost (based on model pricing)
- Session aggregates

**Cost Estimation**:
```python
def estimate_cost(input_tokens, output_tokens, model):
    pricing = MODEL_COSTS[model]
    input_cost = (input_tokens / 1M) * pricing["input"]
    output_cost = (output_tokens / 1M) * pricing["output"]
    return input_cost + output_cost
```

**Model Pricing (per million tokens)**:
| Model | Input | Output |
|-------|-------|--------|
| llama3.2-3b | $0.20 | $0.20 |
| llama3-70b | $0.90 | $0.90 |
| mistral-large | $2.00 | $6.00 |

**Cost Warnings**:
- 🟡 Yellow warning at 15,000 tokens
- 🔴 Red alert at 25,000 tokens
- 💡 Suggestions to optimize query

---

### 3. Execution Routes

#### 3.1 Analytics Route

**Trigger**: Questions about metrics, calculations, trends

**Examples**:
- "What is the clean claim rate?"
- "Show me denial trends by payer"
- "Which providers have the highest revenue?"

**Execution Flow**:
```
1. Enhance query with RCM terminology
2. Build analytics-focused prompt
3. Call Cortex Analyst (or Complete with analytics context)
4. Generate SQL against semantic views
5. Execute SQL and format results
6. Return answer with visualizations
```

**Semantic Views Used**:
- `CLAIMS_PROCESSING_VIEW`: Claims, providers, payers, procedures
- `DENIALS_MANAGEMENT_VIEW`: Denials, appeals, reasons, outcomes

**Optimization**:
- Uses cached semantic model for faster SQL generation
- Pre-defined metrics reduce prompt engineering
- Focused schema reduces context window

#### 3.2 Knowledge Base Route (RAG)

**Trigger**: Questions about procedures, policies, documentation

**Examples**:
- "How do I resolve Code 45 denial?"
- "What are HIPAA compliance requirements?"
- "Find our appeal filing procedures"

**Execution Flow**:
```
1. Enhance query with RCM terminology
2. Execute Cortex Search (vector similarity)
3. Retrieve top 5 relevant documents
4. Build RAG context (limit to 2,500 chars)
5. Enhance context with terminology definitions
6. Generate response using mistral-large
7. Return answer with source citations
```

**Search Services**:
- `RCM_FINANCE_DOCS_SEARCH`: Financial policies, contracts
- `RCM_OPERATIONS_DOCS_SEARCH`: Procedures, handbooks
- `RCM_COMPLIANCE_DOCS_SEARCH`: Compliance, audits
- `RCM_STRATEGY_DOCS_SEARCH`: Strategic plans
- `RCM_KNOWLEDGE_BASE_SEARCH`: All documents (default)

**Optimization**:
- Limit to 5 documents (vs 10-20)
- Truncate chunks to 500 chars each
- Total context capped at ~2,500 chars
- Result: ~2,000 tokens vs 30,000+

#### 3.3 General Route

**Trigger**: Greetings, help requests, general conversation

**Examples**:
- "Hello"
- "What can you help me with?"
- "Explain RCM metrics"

**Execution Flow**:
```
1. Build conversational prompt
2. Call Cortex Complete (llama3.2-3b)
3. Generate helpful, friendly response
4. Guide user to ask specific questions
```

**Optimization**:
- Uses smallest model (llama3.2-3b)
- Minimal context (no RAG or semantic views)
- Fast response (~200-300 tokens)

---

## Data Flow Diagrams

### Query Processing Flow

```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│ RCM Enhancement      │
│ (Terminology)        │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Intent Classification│
│ (Router LLM)         │
└──────┬───────────────┘
       │
       ├─────────┬─────────────┬──────────┐
       │         │             │          │
       ▼         ▼             ▼          ▼
┌──────────┐ ┌──────┐ ┌─────────────┐ ┌────────┐
│ANALYTICS │ │  KB  │ │  GENERAL    │ │ ERROR  │
└────┬─────┘ └───┬──┘ └──────┬──────┘ └───┬────┘
     │           │            │            │
     ▼           ▼            ▼            ▼
┌──────────────────────────────────────────────┐
│           Cost Tracking                      │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
            ┌─────────────┐
            │  Response   │
            │  + Metadata │
            └─────────────┘
```

### Analytics Route Detail

```
User Query: "What is the denial rate?"
     │
     ▼
┌─────────────────────────┐
│ Terminology Enhancement │
│ • Detect: "denial rate" │
│ • Add: Definition       │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Build Analytics Prompt  │
│ • System context        │
│ • RCM metric definitions│
│ • User query            │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Cortex Analyst          │
│ • Access semantic view  │
│ • Generate SQL          │
│ • Execute query         │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Format Response         │
│ • Metric values         │
│ • Trend analysis        │
│ • Visualizations        │
└───────────┬─────────────┘
            │
            ▼
    Return to User
```

### Knowledge Base Route Detail

```
User Query: "How do I resolve Code 45?"
     │
     ▼
┌─────────────────────────┐
│ Terminology Enhancement │
│ • Detect: "Code 45"     │
│ • Add: "CO-45 = charge  │
│   exceeds fee schedule" │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Cortex Search           │
│ • Vector search         │
│ • Top 5 documents       │
│ • Filter by relevance   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Build RAG Context       │
│ • Concatenate chunks    │
│ • Limit to 2,500 chars  │
│ • Add terminology       │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Generate Response       │
│ • mistral-large         │
│ • Use RAG context       │
│ • Cite sources          │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Return with Metadata    │
│ • Response text         │
│ • Source documents      │
│ • Cost/tokens           │
└─────────────────────────┘
```

---

## Configuration Architecture

### Model Selection Strategy

```python
# config.py

# ROUTER: Lightweight for fast classification
ROUTER_MODEL = "llama3.2-3b"
→ Use case: Intent classification only
→ Tokens: ~200-300 per classification
→ Cost: ~$0.0001 per call

# ANALYTICS: Best for SQL generation
ANALYST_MODEL = "mistral-large"
→ Use case: Structured data analysis
→ Tokens: ~1,000-2,000 per query
→ Cost: ~$0.003-$0.012 per call

# RAG: Balance quality and cost
RAG_MODEL = "mistral-large"
→ Use case: Document-based Q&A
→ Tokens: ~2,000-4,000 per query (with context)
→ Cost: ~$0.004-$0.024 per call

# GENERAL: Lightweight conversation
GENERAL_MODEL = "llama3.2-3b"
→ Use case: Simple conversation
→ Tokens: ~200-500 per query
→ Cost: ~$0.0001-$0.0002 per call
```

### Cost Optimization Settings

```python
# Limit context retrieval
MAX_SEARCH_RESULTS = 5
→ 5 docs × 500 chars = 2,500 chars = ~625 tokens
→ vs 10 docs = 5,000 chars = ~1,250 tokens (50% savings)

# Token warning thresholds
MODERATE_USAGE = 15,000 tokens
HIGH_USAGE = 25,000 tokens
→ Alert users before hitting 30k+ problem
```

---

## Security & Performance

### Security Considerations

**Credentials Management**:
- Secrets stored in `.streamlit/secrets.toml` (gitignored)
- No hardcoded credentials in code
- Role-based access control (RBAC) in Snowflake

**Data Access**:
- Semantic views limit data exposure
- Search services filtered by document type
- No direct table access from UI

**Cost Controls**:
- Token limits per query
- Session-level budgets (configurable)
- Warnings before expensive operations

### Performance Optimizations

**Caching**:
- Snowflake connection cached (Streamlit `@cache_resource`)
- Terminology enhancer singleton pattern
- Session state for chat history

**Model Selection**:
- Lightweight router (200-300 tokens)
- Targeted retrieval (5 docs max)
- Smart context building (truncation)

**Expected Performance**:
| Route | Avg Tokens | Avg Cost | Response Time |
|-------|-----------|----------|---------------|
| Analytics | 1,500 | $0.003 | 2-3 seconds |
| Knowledge Base | 2,500 | $0.006 | 3-5 seconds |
| General | 300 | $0.0001 | 1-2 seconds |

**vs Quadax's Current State**:
- Was: 30,000+ tokens per query
- Now: 1,500-2,500 tokens average
- Savings: 90%+ reduction in token usage

---

## Deployment Architecture

### Local Development

```
Local Machine
├── Python 3.9+
├── Streamlit (localhost:8501)
└── Direct Snowflake connection
    └── RCM_AI_DEMO database
```

### Production Deployment Options

**Option 1: Streamlit Community Cloud**
```
GitHub Repo → Streamlit Cloud
└── Secrets managed in Streamlit UI
```

**Option 2: Snowflake Native App**
```
Snowpark Container Services
└── Streamlit in Snowflake
    └── No external connections needed
```

**Option 3: Enterprise Deployment**
```
Kubernetes Cluster
├── Streamlit pod
├── Load balancer
└── Snowflake connector pool
```

---

## Monitoring & Observability

### Built-in Metrics

**Session Level**:
- Total queries processed
- Total tokens consumed
- Total estimated cost
- Average tokens per query
- Route distribution (Analytics/KB/General %)

**Query Level**:
- Intent classification accuracy
- Model used
- Token counts (input/output/total)
- Estimated cost
- Response time (future enhancement)

### Future Enhancements

**Proposed Monitoring**:
- [ ] Export metrics to Snowflake table
- [ ] Grafana dashboard for trends
- [ ] Alert on cost thresholds
- [ ] User satisfaction ratings
- [ ] A/B testing different models

**Proposed Features**:
- [ ] Multi-turn conversation context
- [ ] Query refinement suggestions
- [ ] Automated report generation
- [ ] Integration with ServiceNow
- [ ] Mobile-responsive UI

---

## Scaling Considerations

### Current Limitations

- Single Streamlit instance (1 user at a time for local dev)
- No persistent chat history (session-based only)
- Manual credential management

### Scaling Solutions

**Horizontal Scaling**:
- Deploy multiple Streamlit instances
- Use load balancer
- Share session state via Redis

**Vertical Scaling**:
- Larger Snowflake warehouse for complex queries
- Cached embeddings for faster search
- Pre-computed aggregates for common metrics

**Cost Scaling**:
- Implement query budgets per user
- Cache frequent query results
- Use smaller models for simple queries

---

## Comparison: Before vs After

### Before (Point Solutions)

```
Tool Selection UI
├── [Button] Search Documents → Cortex Search only
├── [Button] Analyze Data → Cortex Analyst only
└── [Button] Chat → Cortex Complete only

User Experience:
❌ Must choose correct tool
❌ No cost visibility
❌ RCM terms not handled
❌ No unified history
❌ 30k+ tokens per query
```

### After (Orchestrated)

```
Single Chat Interface
└── Natural language query → Auto-routed

User Experience:
✅ No tool selection needed
✅ Full cost transparency
✅ RCM terminology built-in
✅ Unified chat history
✅ 1,500-2,500 avg tokens per query
```

---

## Summary

This architecture solves Quadax's three key problems:

1. **Point Solution Fatigue**
   - Before: 3 separate tools, manual selection
   - After: 1 unified interface, automatic routing

2. **Domain Specificity**
   - Before: Generic LLMs don't understand RCM slang
   - After: Terminology enhancement layer adds context

3. **Cost & Token Control**
   - Before: 30k+ tokens per query, no visibility
   - After: 1,500-2,500 tokens, full transparency

**Technical Foundation**: Supervisor Agent Pattern + RCM Domain Intelligence + Cost Monitoring

