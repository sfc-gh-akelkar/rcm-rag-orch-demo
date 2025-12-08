# RCM Intelligence Hub - Orchestrated AI Demo

## 🎯 Executive Summary

This application demonstrates a **Supervisor Agent Pattern** that solves Quadax's "Point Solution Fatigue" by providing a **unified AI orchestration layer** for Healthcare Revenue Cycle Management (RCM).

### Key Business Problems Solved

1. ✅ **Point Solution Fatigue**: Single interface replaces multiple isolated tools
2. ✅ **Domain Specificity**: Handles RCM "slang" and terminology automatically
3. ✅ **Cost & Token Control**: Provides full visibility into token usage and costs

---

## 🏗️ Architecture Overview

### The Supervisor Agent Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                      USER QUERY                            │
│              "What is our denial rate?"                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              SUPERVISOR AGENT (Router)                      │
│                                                             │
│  • Intent Classification (llama3.2-3b)                      │
│  • RCM Terminology Enhancement                              │
│  • Cost Tracking & Monitoring                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
┌───────────────┐ ┌──────────┐ ┌──────────┐
│  ANALYTICS    │ │KNOWLEDGE │ │ GENERAL  │
│               │ │   BASE   │ │          │
│ Cortex        │ │ Cortex   │ │ Cortex   │
│ Analyst       │ │ Search   │ │ Complete │
│               │ │ (RAG)    │ │          │
│ • Claims      │ │ • Docs   │ │ • Help   │
│ • Denials     │ │ • Policies│ │ • Chat  │
│ • Metrics     │ │ • Guides │ │          │
└───────────────┘ └──────────┘ └──────────┘
```

### Why This Architecture Solves "One vs. Many Models"

**Traditional Approach (Point Solutions):**
- ❌ User must choose: "Is this a SQL question or document question?"
- ❌ Each tool has different interfaces and workflows
- ❌ No unified cost tracking
- ❌ Domain terminology not handled consistently

**Orchestrated Approach (This Solution):**
- ✅ User asks naturally: "What is our denial rate?"
- ✅ Supervisor routes automatically to Cortex Analyst
- ✅ All queries tracked for cost and performance
- ✅ RCM terminology enhanced before sending to any model

---

## 🚀 Quick Start

### 1. Prerequisites

- Snowflake account with Cortex enabled
- Python 3.9+
- Completed RCM demo setup (all 6 SQL scripts executed)

### 2. Installation

```bash
# Clone or navigate to the demo directory
cd RCM_RAG_ORCH_DEMO

# Install dependencies
pip install -r requirements.txt

# Configure Snowflake credentials
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your Snowflake credentials
```

### 3. Configure Snowflake Credentials

Edit `.streamlit/secrets.toml`:

```toml
[snowflake]
user = "your_user"
password = "your_password"
account = "your_account"  # Format: orgname-accountname
warehouse = "RCM_INTELLIGENCE_WH"
database = "RCM_AI_DEMO"
schema = "RCM_SCHEMA"
role = "SF_INTELLIGENCE_DEMO"
```

### 4. Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 💡 How It Works

### Intent Classification (The Router)

The orchestrator uses a **lightweight LLM (llama3.2-3b)** to classify user intent:

```python
def determine_intent(user_query: str) -> str:
    """
    Classifies query into:
    - ANALYTICS: Metrics, numbers, trends (→ Cortex Analyst)
    - KNOWLEDGE_BASE: Policies, procedures (→ Cortex Search)
    - GENERAL: Conversation, help (→ Cortex Complete)
    """
```

**Example Classifications:**

| User Query | Intent | Routed To | Reasoning |
|-----------|--------|-----------|-----------|
| "What is the denial rate?" | ANALYTICS | Cortex Analyst | Requires metric calculation |
| "How do I resolve Code 45?" | KNOWLEDGE_BASE | Cortex Search | Asking about procedures |
| "What can you help with?" | GENERAL | Cortex Complete | General conversation |

### RCM Terminology Enhancement

Before sending queries to any model, we enhance them with domain-specific context:

```python
# User query: "Show me remits for Anthem"
# Enhanced query:
"""
RCM Terminology Context:
- remits: remittance advice (ERA - Electronic Remittance Advice)

User Query: Show me remits for Anthem
"""
```

**Common RCM Terms Handled:**
- "Remit" → "Remittance Advice (ERA)"
- "Write-off" → "Contractual adjustment (CO-45, PR-1)"
- "A/R" → "Accounts Receivable"
- "Clean claim" → "First-pass acceptance without errors"
- Denial codes (CO-45, PR-1, etc.)

### Cost Tracking & Visibility

Every query tracks:
- Input tokens (query + context)
- Output tokens (response)
- Estimated cost (based on model pricing)
- Route taken (Analytics/KB/General)

**Addressing the 30k+ Token Problem:**

The orchestrator implements several optimizations:

1. **Limited Context Retrieval**: Only top 5 documents (configurable)
2. **Lightweight Router**: Uses smallest model (llama3.2-3b) for classification
3. **Smart Context Building**: Truncates large documents intelligently
4. **Cost Warnings**: Alerts when queries exceed 15k or 25k tokens

---

## 📊 Demo Scenarios

### Scenario 1: Analytics Query

**User asks:** *"What is the clean claim rate by provider?"*

```
1. Router classifies as: ANALYTICS
2. Routes to: Cortex Analyst
3. Uses semantic view: CLAIMS_PROCESSING_VIEW
4. Generates SQL and returns metrics
5. Tracks: ~500 input tokens, ~300 output tokens, $0.002 cost
```

### Scenario 2: Knowledge Base Query

**User asks:** *"How do I resolve a Code 45 denial in ServiceNow?"*

```
1. Router classifies as: KNOWLEDGE_BASE
2. Detects terminology: "Code 45" = CO-45 denial code
3. Routes to: Cortex Search (RCM_COMPLIANCE_DOCS_SEARCH)
4. Retrieves top 5 relevant document chunks
5. Enhances context with: "CO-45 = Charge exceeds fee schedule"
6. Generates response using: mistral-large with enhanced context
7. Tracks: ~2,000 input tokens, ~400 output tokens, $0.006 cost
```

### Scenario 3: General Conversation

**User asks:** *"What can you help me with?"*

```
1. Router classifies as: GENERAL
2. Routes to: Cortex Complete (llama3.2-3b)
3. Provides overview of capabilities
4. Tracks: ~200 input tokens, ~150 output tokens, $0.0001 cost
```

---

## 🎛️ Configuration

### Model Selection

Edit `config.py` to customize models for each route:

```python
# Router - Keep lightweight for speed
ROUTER_MODEL = "llama3.2-3b"  # Fast classification

# Analytics - Best for SQL generation
ANALYST_MODEL = "mistral-large"

# RAG - Balance quality and cost
RAG_MODEL = "mistral-large"

# General - Lightweight for conversation
GENERAL_MODEL = "llama3.2-3b"
```

### Cost Optimization

Adjust these settings in `config.py`:

```python
# Reduce context window
MAX_SEARCH_RESULTS = 5  # Default: 5 (was 10+)

# Set token warning thresholds
# Warns at 15k, alerts at 25k
```

### RCM Terminology

Add custom terminology in `config.py`:

```python
RCM_TERMINOLOGY = {
    "your_term": "definition and context",
    # Add company-specific terms here
}
```

---

## 📈 Cost & Performance Monitoring

### Session Statistics

The app tracks:
- Total queries processed
- Total tokens consumed (input + output)
- Total estimated cost
- Average tokens/cost per query
- Breakdown by route (Analytics/KB/General)

### Debug Panel

Enable in sidebar to see per-query:
- ✅ Intent classification reasoning
- ✅ Model used
- ✅ Token counts (input/output/total)
- ✅ Estimated cost
- ✅ Source documents (for RAG)
- ✅ SQL generated (for Analytics)

**Example Output:**

```
🔍 AIOps & Cost Visibility

Routing Decision:
- Intent: ANALYTICS
- Reasoning: Query requires data analysis
- Route: ANALYTICS
- Model: mistral-large

Cost Analysis:
- Input Tokens: 1,234
- Output Tokens: 456
- Total Tokens: 1,690
- Estimated Cost: $0.0034
```

---

## 🏥 RCM-Specific Features

### 1. Terminology Detection

Automatically detects and defines:
- RCM abbreviations (CCR, NCR, A/R, ERA, EDI)
- Denial codes (CO-45, PR-1, etc.)
- Industry terms (remit, write-off, scrub, aging)

### 2. Query Enhancement

Before sending to models, adds context:
```
"Show me the remit for claim 12345"
→
"Show me the remittance advice (ERA - Electronic Remittance Advice) 
for claim 12345"
```

### 3. Smart Routing for Mixed Queries

```
"What is our denial rate and what are the policies for appeals?"
→ Routes to ANALYTICS first, then suggests KB search for policies
```

---

## 🔒 Security & Best Practices

### Credentials Management

- ✅ Uses Streamlit secrets (not committed to git)
- ✅ `.gitignore` configured to exclude `secrets.toml`
- ✅ Example file provided for setup

### Cost Controls

- ✅ Token limits configurable per route
- ✅ Warnings for high-cost queries
- ✅ Session-level budget tracking

### Error Handling

- ✅ Graceful fallback if classification fails
- ✅ Keyword-based routing as backup
- ✅ Clear error messages to users

---

## 📝 File Structure

```
RCM_RAG_ORCH_DEMO/
│
├── app.py                      # Main Streamlit UI
├── orchestrator.py             # Supervisor Agent logic
├── cost_tracker.py             # Token & cost tracking
├── rcm_terminology.py          # Domain terminology enhancement
├── config.py                   # Configuration settings
│
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
│
├── .streamlit/
│   ├── config.toml             # Streamlit UI config
│   ├── secrets.toml.example    # Credentials template
│   └── secrets.toml            # (Your actual credentials - not committed)
│
├── sql_scripts/                # Database setup scripts
│   ├── 01_rcm_data_setup.sql
│   ├── 02_rcm_documents_setup.sql
│   ├── 03_rcm_data_generation.sql
│   ├── 04_rcm_semantic_views.sql
│   ├── 05_rcm_cortex_search.sql
│   └── 06_rcm_agent_setup.sql
│
└── unstructured_docs/          # Sample RCM documents
```

---

## 🎓 Technical Deep Dive

### Why This Architecture?

**Traditional Multi-Tool Approach:**
```
User → UI (Choose Tool) → Tool A or Tool B or Tool C
Problems:
- User needs to understand which tool to use
- No shared context between tools
- Inconsistent cost tracking
- Domain knowledge not shared
```

**Orchestrated Approach:**
```
User → Supervisor → [Tool A | Tool B | Tool C]
Benefits:
- Single interface for all queries
- Centralized routing logic
- Unified cost tracking
- Shared terminology enhancement
```

### Intent Classification Prompt Engineering

The router prompt is designed to:
1. Provide clear intent definitions with examples
2. Include RCM domain context
3. Enforce single-word output for reliability
4. Use minimal tokens for speed

**Prompt Structure:**
```
System Context: RCM domain definitions
Intent Categories: ANALYTICS, KNOWLEDGE_BASE, GENERAL
Examples: 3-5 per category
RCM Terms: Domain-specific guidance
User Query: {query}
Output Format: Single word only
```

### Cost Optimization Strategy

**Problem:** Quadax reports 30k+ tokens per query

**Solutions Implemented:**

1. **Lightweight Router** (llama3.2-3b)
   - Classification: ~200-300 tokens
   - Cost: ~$0.0001 per classification

2. **Limited Context Retrieval**
   - Max 5 documents (vs 10-20)
   - Chunk size limit: 500 chars per doc
   - Total context: ~2,500 chars (vs 10k+)

3. **Smart Model Selection**
   - General queries: llama3.2-3b (cheap)
   - Analytics: mistral-large (when needed)
   - RAG: mistral-large (quality over cost for accuracy)

4. **Token Monitoring**
   - Real-time tracking per query
   - Session-level aggregation
   - Warnings at 15k/25k thresholds

**Result:** Average query: 1,500-3,000 tokens (vs 30k+)

---

## 🔧 Troubleshooting

### Connection Issues

**Error:** "Unable to connect to Snowflake"

**Solution:**
1. Verify `secrets.toml` exists in `.streamlit/`
2. Check credentials are correct
3. Ensure warehouse `RCM_INTELLIGENCE_WH` exists
4. Verify role `SF_INTELLIGENCE_DEMO` has permissions

### High Token Usage

**Warning:** "This query used over 25k tokens"

**Solutions:**
1. Narrow your question scope
2. Avoid asking multiple questions at once
3. Specify time ranges or filters
4. Use analytics for data, not descriptions

### Classification Issues

**Problem:** Router sends query to wrong tool

**Debug Steps:**
1. Enable "Show Debug/Cost Info" in sidebar
2. Check intent classification reasoning
3. Add query-specific keywords (e.g., "calculate" for analytics)
4. Review `INTENT_CLASSIFICATION_PROMPT` in config

---

## 📚 Additional Resources

### Snowflake Documentation

- [Cortex Complete](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions)
- [Cortex Search](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/cortex-search-overview)
- [Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)

### Best Practices Reference

- [Building Cortex Agents](https://github.com/Snowflake-Labs/sfquickstarts/blob/master/site/sfguides/src/best-practices-to-building-cortex-agents/best-practices-to-building-cortex-agents.md)

---

## 🎤 Demo Talking Points

### For Quadax Executives

**Problem Statement:**
*"You mentioned struggling with Point Solution Fatigue - multiple AI prototypes but no unified orchestration. You're also concerned about 30k+ token consumption per query and models not understanding RCM terminology."*

**Solution Demo:**

1. **Show Unified Interface**
   - "Notice there's no tool selection - just one chat interface"
   - Ask: *"What is the denial rate?"* → Auto-routes to Analytics
   - Ask: *"How do I resolve Code 45?"* → Auto-routes to Knowledge Base

2. **Show Cost Visibility**
   - Enable debug panel in sidebar
   - Run a query and expand "AIOps & Cost Visibility"
   - Point out: Token counts, cost estimate, routing decision

3. **Show RCM Terminology Handling**
   - Ask: *"Show me remits for Anthem"*
   - Expand debug panel
   - Show: "Remit" was auto-enhanced to "Remittance Advice (ERA)"

4. **Show Session Statistics**
   - Point to sidebar: Total queries, tokens, cost
   - Compare to "30k+ per query" concern
   - Show: "Average query: 2,000 tokens, $0.004"

**Key Messages:**
- ✅ One interface replaces multiple tools
- ✅ Automatic routing = no user training needed
- ✅ Full cost transparency = budget control
- ✅ RCM domain intelligence built-in

---

## 🏆 Success Metrics

Track these KPIs to demonstrate value:

1. **User Experience**
   - Time to answer (vs multi-tool workflow)
   - Questions answered per session
   - User satisfaction (did they get the right answer?)

2. **Cost Efficiency**
   - Average tokens per query (target: <5,000)
   - Cost per query (target: <$0.01)
   - Cost per session (target: <$0.10)

3. **Accuracy**
   - Routing accuracy (correct tool selection %)
   - Answer quality (subjective rating)
   - Terminology detection rate

---

## 📧 Support & Feedback

This demo was created to address Quadax's specific concerns:
- Point Solution Fatigue → Unified orchestration
- Domain Specificity → RCM terminology enhancement
- Cost Control → Token tracking and optimization

For questions or improvements, refer to the inline code comments
which explain the "why" behind each architectural decision.

---

**Built with ❤️ for Healthcare Revenue Cycle Management**

