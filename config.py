"""
Configuration settings for RCM Orchestration Demo
Centralized configuration for Snowflake connections, models, and RCM-specific settings
"""

# ========================================================================
# SNOWFLAKE CONNECTION SETTINGS
# ========================================================================
SNOWFLAKE_ACCOUNT = "your_account"  # Will be overridden by Streamlit secrets
SNOWFLAKE_USER = "your_user"        # Will be overridden by Streamlit secrets
SNOWFLAKE_PASSWORD = "your_password" # Will be overridden by Streamlit secrets
SNOWFLAKE_WAREHOUSE = "RCM_INTELLIGENCE_WH"
SNOWFLAKE_DATABASE = "RCM_AI_DEMO"
SNOWFLAKE_SCHEMA = "RCM_SCHEMA"
SNOWFLAKE_ROLE = "SF_INTELLIGENCE_DEMO"

# ========================================================================
# CORTEX MODEL CONFIGURATION
# ========================================================================

# Router/Orchestrator Model - Lightweight for fast intent classification
# Options: mistral-large, llama3-70b, llama3.1-70b, llama3.2-3b
ROUTER_MODEL = "llama3.2-3b"  # Fast and cost-effective for classification

# Analytics Model - Used for Cortex Analyst queries (structured data)
ANALYST_MODEL = "mistral-large"  # Best for SQL generation

# RAG/Knowledge Base Model - Used for document search responses
RAG_MODEL = "mistral-large"  # Good balance of quality and cost

# General Conversation Model
GENERAL_MODEL = "llama3.2-3b"  # Lightweight for simple interactions

# ========================================================================
# CORTEX SEARCH CONFIGURATION
# ========================================================================

# Search Services (fully qualified names)
CORTEX_SEARCH_SERVICES = {
    "finance": "RCM_AI_DEMO.RCM_SCHEMA.RCM_FINANCE_DOCS_SEARCH",
    "operations": "RCM_AI_DEMO.RCM_SCHEMA.RCM_OPERATIONS_DOCS_SEARCH",
    "compliance": "RCM_AI_DEMO.RCM_SCHEMA.RCM_COMPLIANCE_DOCS_SEARCH",
    "strategy": "RCM_AI_DEMO.RCM_SCHEMA.RCM_STRATEGY_DOCS_SEARCH",
    "knowledge_base": "RCM_AI_DEMO.RCM_SCHEMA.RCM_KNOWLEDGE_BASE_SEARCH"
}

# Default search service for general knowledge queries
DEFAULT_SEARCH_SERVICE = "RCM_AI_DEMO.RCM_SCHEMA.RCM_KNOWLEDGE_BASE_SEARCH"

# Maximum chunks to retrieve (reducing from default to control token usage)
MAX_SEARCH_RESULTS = 5  # Top 5 chunks instead of all matches

# ========================================================================
# CORTEX ANALYST CONFIGURATION
# ========================================================================

# Semantic Views (fully qualified names)
SEMANTIC_VIEWS = {
    "claims_processing": "RCM_AI_DEMO.RCM_SCHEMA.CLAIMS_PROCESSING_VIEW",
    "denials_management": "RCM_AI_DEMO.RCM_SCHEMA.DENIALS_MANAGEMENT_VIEW"
}

# Default semantic view for analytics queries
DEFAULT_SEMANTIC_VIEW = "RCM_AI_DEMO.RCM_SCHEMA.CLAIMS_PROCESSING_VIEW"

# ========================================================================
# COST TRACKING CONFIGURATION
# ========================================================================

# Approximate token costs per million tokens (as of Dec 2024)
# These are estimated costs - adjust based on your actual pricing
MODEL_COSTS_PER_MILLION = {
    "mistral-large": {"input": 2.00, "output": 6.00},
    "llama3.1-70b": {"input": 0.90, "output": 0.90},
    "llama3-70b": {"input": 0.90, "output": 0.90},
    "llama3.2-3b": {"input": 0.20, "output": 0.20},
    "snowflake-arctic-embed-l-v2.0": {"input": 0.10, "output": 0.00},  # Embedding model
}

# Token estimation multipliers (rough estimates)
CHARS_PER_TOKEN = 4  # Approximate: 1 token ≈ 4 characters

# ========================================================================
# INTENT CLASSIFICATION
# ========================================================================

# Intent types for routing
INTENT_ANALYTICS = "ANALYTICS"
INTENT_KNOWLEDGE_BASE = "KNOWLEDGE_BASE"
INTENT_GENERAL = "GENERAL"

# Keywords that suggest analytics intent
ANALYTICS_KEYWORDS = [
    "how many", "what is the", "show me", "calculate", "average", "total",
    "count", "sum", "trend", "compare", "rate", "percentage", "top",
    "bottom", "highest", "lowest", "growth", "decline", "revenue",
    "metrics", "kpi", "performance", "analytics", "report", "dashboard",
    "deny", "denial", "claim", "payer", "provider", "appeal"
]

# Keywords that suggest knowledge base/RAG intent
KNOWLEDGE_KEYWORDS = [
    "how do i", "how to", "what does", "explain", "define", "policy",
    "procedure", "guideline", "documentation", "code", "servicenow",
    "ticket", "resolve", "compliance", "regulation", "hipaa", "cms",
    "contract", "agreement", "training", "handbook", "standard"
]

# ========================================================================
# RCM TERMINOLOGY MAPPINGS
# ========================================================================

# Domain-specific terminology that models may misunderstand
# Maps colloquial RCM terms to their formal definitions
RCM_TERMINOLOGY = {
    "remit": "remittance advice (ERA - Electronic Remittance Advice)",
    "remits": "remittance advice documents",
    "write-off": "contractual adjustment or bad debt write-off (adjustment codes CO-45, PR-1)",
    "clean claim": "claim submitted without errors that is accepted on first submission",
    "dirty claim": "claim requiring correction or additional information before processing",
    "scrub": "automated claim validation and error checking before submission",
    "scrubbing": "claim validation process",
    "aging": "accounts receivable aging - time since claim submission",
    "a/r": "accounts receivable",
    "ar": "accounts receivable",
    "days in ar": "average days in accounts receivable (DSO - Days Sales Outstanding)",
    "dso": "days sales outstanding",
    "denial code": "claim adjustment reason code (CARC) or remittance advice remark code (RARC)",
    "co": "contractual obligation (payer responsibility adjustment)",
    "pr": "patient responsibility (patient owes amount)",
    "timely filing": "claim submission deadline per payer contract",
    "coordination of benefits": "COB - determining primary vs secondary payer responsibility",
    "cob": "coordination of benefits",
    "explanation of benefits": "EOB - payer statement to patient",
    "eob": "explanation of benefits",
    "era": "electronic remittance advice",
    "edi": "electronic data interchange",
    "837": "electronic claim submission format",
    "835": "electronic remittance advice format",
    "payer mix": "distribution of claims across different insurance payers",
    "case mix": "distribution of patient acuity and procedure complexity"
}

# ========================================================================
# UI CONFIGURATION
# ========================================================================

# Streamlit page config
PAGE_TITLE = "RCM Intelligence Hub"
PAGE_ICON = "🏥"
LAYOUT = "wide"

# Chat interface settings
MAX_CHAT_HISTORY = 50  # Maximum messages to retain in session
WELCOME_MESSAGE = """
👋 **Welcome to the RCM Intelligence Hub!**

I'm your unified AI assistant for healthcare revenue cycle management. I can help you with:

**📊 Analytics & Metrics** (Claims, Denials, Payer Performance)
- *"What is the clean claim rate by provider?"*
- *"Which payers have the highest denial rates?"*
- *"Show me revenue trends for the last quarter"*

**📚 Knowledge Base** (Policies, Procedures, ServiceNow)
- *"How do I resolve a Code 45 denial in ServiceNow?"*
- *"What are our appeal filing deadlines by payer?"*
- *"Find HIPAA compliance requirements for claims processing"*

**💡 General Questions**
- *"What RCM metrics should I focus on?"*
- *"Explain the difference between CO and PR adjustments"*

---
**🎯 Key Feature:** I automatically route your question to the right tool - you don't need to choose!
"""

# Debug panel configuration
SHOW_DEBUG_BY_DEFAULT = False  # Set to True for development
DEBUG_PANEL_TITLE = "🔍 AIOps & Cost Visibility"

# ========================================================================
# SYSTEM PROMPTS
# ========================================================================

# Intent classification prompt
INTENT_CLASSIFICATION_PROMPT = """You are an intent classifier for a Healthcare Revenue Cycle Management (RCM) system.

Analyze the user's query and classify it into ONE of these intents:

1. **ANALYTICS**: Questions about metrics, numbers, calculations, trends, comparisons, or data analysis
   - Examples: "What is the denial rate?", "Show me top payers", "Compare Q1 vs Q2 revenue"
   
2. **KNOWLEDGE_BASE**: Questions about procedures, policies, documentation, "how-to" guides, or definitions
   - Examples: "How do I appeal a denial?", "What is Code 45?", "Find our HIPAA policy"
   
3. **GENERAL**: Greetings, clarifications, general conversation, or off-topic questions
   - Examples: "Hello", "Thank you", "What can you do?", "Explain RCM"

RCM Domain Context:
- "Denials", "claims", "appeals", "payers", "providers" with metrics → ANALYTICS
- "How to resolve", "policy for", "procedure", "ServiceNow ticket" → KNOWLEDGE_BASE
- Remittance advice, write-offs, adjustments, aging are RCM financial concepts

**CRITICAL**: Respond with ONLY one word: ANALYTICS, KNOWLEDGE_BASE, or GENERAL

User Query: {query}

Intent:"""

# RAG enhancement prompt (prepended to context)
RAG_SYSTEM_PROMPT = """You are an expert Healthcare Revenue Cycle Management (RCM) analyst.

Use the following document excerpts to answer the user's question. Be specific and cite policies/procedures when available.

RCM Terminology Reference:
- Remit/Remittance = Electronic Remittance Advice (ERA) from payer
- Write-off = Contractual adjustment or bad debt (CO-45, PR-1 codes)
- Clean Claim = First-pass acceptance without errors
- A/R Aging = Days since claim submission
- Timely Filing = Payer-specific claim submission deadline
- COB = Coordination of Benefits (primary vs secondary payer)

Retrieved Context:
{context}

User Question: {query}

Provide a clear, actionable answer focused on RCM operations:"""

# Analytics enhancement prompt
ANALYTICS_SYSTEM_PROMPT = """You are an expert Healthcare Revenue Cycle Management (RCM) data analyst.

When generating SQL and interpreting results, use RCM-specific terminology:
- Clean Claim Rate = % of claims accepted on first submission
- Denial Rate = % of claims denied
- Net Collection Rate = (Paid Amount / Charge Amount) × 100
- Days in A/R = Average days from submission to payment
- Appeal Success Rate = % of appeals resulting in payment

Focus on actionable insights for RCM operations. Highlight trends, outliers, and opportunities for improvement.

User Query: {query}"""

# General conversation prompt
GENERAL_SYSTEM_PROMPT = """You are a helpful assistant for a Healthcare Revenue Cycle Management (RCM) system.

You can help users with:
1. Analytics queries about claims, denials, and payer performance
2. Knowledge base searches for policies, procedures, and documentation
3. General RCM questions and guidance

Be friendly, concise, and guide users on how to ask questions effectively.

User Query: {query}"""

