# RCM Intelligence Hub - File Structure

## Complete Project Tree

```
RCM_RAG_ORCH_DEMO/
│
├── 🚀 MAIN APPLICATION FILES
│   ├── app.py                          # Streamlit UI - Main entry point (450 lines)
│   ├── orchestrator.py                 # Supervisor Agent routing logic (350 lines)
│   ├── cost_tracker.py                 # Token & cost tracking (200 lines)
│   ├── rcm_terminology.py              # RCM domain intelligence (250 lines)
│   └── config.py                       # Configuration & prompts (300 lines)
│
├── 📚 DOCUMENTATION
│   ├── README.md                       # Updated main README with orchestration info
│   ├── README_ORCHESTRATION.md         # Complete architecture guide (17 pages)
│   ├── QUICKSTART.md                   # 5-minute setup walkthrough
│   ├── ARCHITECTURE.md                 # Technical deep dive (20 pages)
│   ├── PROJECT_SUMMARY.md              # Executive summary & deliverables
│   ├── FILE_STRUCTURE.md               # This file - project organization
│   └── RCM_15_Minute_Demo_Story.md     # Original demo script (unchanged)
│
├── ⚙️ CONFIGURATION
│   ├── requirements.txt                # Python dependencies
│   ├── verify_setup.py                 # Setup verification script
│   ├── .gitignore                      # Git ignore (protects secrets)
│   └── .streamlit/
│       ├── config.toml                 # Streamlit UI configuration
│       └── secrets.toml.example        # Credentials template
│
├── 🗄️ DATABASE SETUP (Pre-existing)
│   └── sql_scripts/
│       ├── 01_rcm_data_setup.sql       # Infrastructure & roles
│       ├── 02_rcm_documents_setup.sql  # Document loading
│       ├── 03_rcm_data_generation.sql  # Synthetic data generation
│       ├── 04_rcm_semantic_views.sql   # Cortex Analyst views
│       ├── 05_rcm_cortex_search.sql    # Cortex Search services
│       └── 06_rcm_agent_setup.sql      # Native Snowflake agent (optional)
│
└── 📄 SAMPLE DOCUMENTS (Pre-existing)
    └── unstructured_docs/
        ├── finance/                    # Financial policies, contracts
        ├── hr/                         # HR handbooks, guidelines
        ├── marketing/                  # Marketing strategies
        └── sales/                      # Sales playbooks, case studies
```

---

## File Purposes & Relationships

### Core Application Flow

```
┌─────────────┐
│   app.py    │ ← User interacts here
└──────┬──────┘
       │ imports
       ▼
┌─────────────────┐
│ orchestrator.py │ ← Routes queries
└──────┬──────────┘
       │ uses
       ├─────────────────┬────────────────┬
       │                 │                │
       ▼                 ▼                ▼
┌──────────────┐  ┌─────────────┐  ┌──────────┐
│cost_tracker  │  │rcm_terminology│  │ config.py│
│   .py        │  │     .py       │  │          │
│              │  │               │  │          │
│• Token count │  │• Term detect  │  │• Models  │
│• Cost calc   │  │• Enhancement  │  │• Prompts │
│• Session stats│  │• Definitions │  │• Settings│
└──────────────┘  └─────────────┘  └──────────┘
```

### Configuration Dependencies

```
config.py
├── Model Selection
│   ├── ROUTER_MODEL = "llama3.2-3b"
│   ├── ANALYST_MODEL = "mistral-large"
│   ├── RAG_MODEL = "mistral-large"
│   └── GENERAL_MODEL = "llama3.2-3b"
│
├── Snowflake Resources
│   ├── CORTEX_SEARCH_SERVICES {...}
│   ├── SEMANTIC_VIEWS {...}
│   └── Connection settings
│
├── System Prompts
│   ├── INTENT_CLASSIFICATION_PROMPT
│   ├── RAG_SYSTEM_PROMPT
│   ├── ANALYTICS_SYSTEM_PROMPT
│   └── GENERAL_SYSTEM_PROMPT
│
└── RCM Terminology
    └── RCM_TERMINOLOGY {...}
```

---

## Key Components Explained

### 1. `app.py` - User Interface

**Purpose**: Streamlit chat application

**Key Functions**:
- `main()` - Application entry point
- `render_header()` - UI header with branding
- `render_sidebar()` - Session stats & controls
- `render_chat_message()` - Display messages
- `render_debug_panel()` - Cost visibility
- `process_user_query()` - Main query handler

**Dependencies**:
- `orchestrator.py` - Query routing
- `cost_tracker.py` - Cost display
- `rcm_terminology.py` - Terminology help text
- `config.py` - UI settings

### 2. `orchestrator.py` - Supervisor Agent

**Purpose**: Central routing and orchestration

**Key Functions**:
- `process_query()` - Main entry point
- `determine_intent()` - Classify user intent
- `execute_analytics_query()` - Route to Cortex Analyst
- `execute_knowledge_base_query()` - Route to Cortex Search (RAG)
- `execute_general_query()` - Route to conversation
- `_cortex_search()` - Execute search
- `_build_rag_context()` - Build context from search results

**Dependencies**:
- `cost_tracker.py` - Track tokens/cost
- `rcm_terminology.py` - Enhance queries
- `config.py` - Models, prompts, settings

### 3. `cost_tracker.py` - Cost Management

**Purpose**: Token counting and cost estimation

**Key Functions**:
- `estimate_tokens()` - Count tokens in text
- `estimate_cost()` - Calculate cost for model call
- `track_query()` - Track single query
- `get_session_summary()` - Aggregate stats
- `format_query_stats()` - Format for display
- `get_cost_warning()` - Alert on high usage

**Dependencies**:
- `tiktoken` - Accurate token counting
- `config.py` - Model pricing

### 4. `rcm_terminology.py` - Domain Intelligence

**Purpose**: Healthcare terminology enhancement

**Key Functions**:
- `detect_rcm_terms()` - Find RCM terms in text
- `enhance_query()` - Add terminology context to query
- `enhance_rag_context()` - Add terminology to RAG context
- `expand_abbreviations()` - Expand RCM abbreviations
- `suggest_corrections()` - Improve query suggestions

**Dependencies**:
- `config.py` - Terminology mappings

### 5. `config.py` - Configuration

**Purpose**: Centralized settings

**Sections**:
- Snowflake connection settings
- Model selection (router, analyst, RAG, general)
- Cortex Search service names
- Cortex Analyst semantic view names
- Cost tracking (model pricing)
- Intent classification keywords
- RCM terminology mappings (50+ terms)
- System prompts (intent, RAG, analytics, general)
- UI configuration

**No Dependencies**: This is the root config

### 6. `verify_setup.py` - Setup Verification

**Purpose**: Pre-flight checks before running app

**Checks**:
- Python version (3.9+)
- Dependencies installed
- Required files exist
- Snowflake credentials configured
- Provides Snowflake setup guidance

**Usage**:
```bash
python verify_setup.py
```

---

## Documentation Structure

### For Different Audiences

**Executives** → `PROJECT_SUMMARY.md`
- Business problem & solution
- ROI calculation
- Success metrics

**Developers** → `ARCHITECTURE.md`
- Technical deep dive
- Component diagrams
- Extension guide

**End Users** → `QUICKSTART.md`
- 5-minute setup
- Sample queries
- Troubleshooting

**Architects** → `README_ORCHESTRATION.md`
- Supervisor Agent pattern
- Design rationale
- Scalability considerations

**All Users** → `README.md`
- Overview
- Quick links to other docs
- Getting started

---

## Data Flow Through Files

### Example: User asks "What is the denial rate?"

```
1. app.py
   └─> User types in chat input
   └─> process_user_query() called

2. orchestrator.py
   └─> process_query() receives query
   └─> determine_intent() called

3. rcm_terminology.py
   └─> enhance_query() adds "denial rate" definition
   └─> Returns enhanced query

4. orchestrator.py
   └─> Intent classified as ANALYTICS
   └─> execute_analytics_query() called
   └─> Calls Cortex Analyst with semantic view

5. cost_tracker.py
   └─> estimate_tokens() counts input/output
   └─> estimate_cost() calculates cost
   └─> track_query() updates session stats

6. orchestrator.py
   └─> Returns result with response + metadata

7. app.py
   └─> Displays response in chat
   └─> render_debug_panel() shows cost/routing
   └─> Updates session stats in sidebar
```

---

## Configuration Files Location

### `.streamlit/` Directory

```
.streamlit/
├── config.toml              ← Streamlit UI settings (theme, server)
├── secrets.toml.example     ← Template for credentials
└── secrets.toml             ← Your actual credentials (gitignored)
```

**Important**: Copy `secrets.toml.example` to `secrets.toml` and fill in your Snowflake credentials!

---

## SQL Scripts Execution Order

These should have been run already (pre-requisite):

```
1. 01_rcm_data_setup.sql
   └─> Creates database, schema, warehouse, role

2. 02_rcm_documents_setup.sql
   └─> Loads documents into RCM_DOCUMENT_CONTENT table

3. 03_rcm_data_generation.sql
   └─> Generates synthetic claims, denials, payers, providers

4. 04_rcm_semantic_views.sql
   └─> Creates CLAIMS_PROCESSING_VIEW, DENIALS_MANAGEMENT_VIEW

5. 05_rcm_cortex_search.sql
   └─> Creates 5 Cortex Search services

6. 06_rcm_agent_setup.sql
   └─> Creates native Snowflake agent (optional - not used by this app)
```

---

## Adding New Files (Guidelines)

### If Adding a New Route Type

1. Create `new_route.py` with handler logic
2. Import in `orchestrator.py`
3. Add new intent constant in `config.py`
4. Update `INTENT_CLASSIFICATION_PROMPT` in `config.py`
5. Add handler in `orchestrator.process_query()`
6. Update documentation

### If Adding New Terminology

1. Edit `RCM_TERMINOLOGY` dict in `config.py`
2. No code changes needed - auto-detected

### If Adding New Model

1. Edit `*_MODEL` setting in `config.py`
2. Add pricing in `MODEL_COSTS_PER_MILLION`
3. Test and update documentation

---

## File Size Summary

| Component | Lines of Code | Purpose |
|-----------|---------------|---------|
| `app.py` | ~450 | UI & interaction |
| `orchestrator.py` | ~350 | Routing logic |
| `cost_tracker.py` | ~200 | Cost tracking |
| `rcm_terminology.py` | ~250 | Domain intelligence |
| `config.py` | ~300 | Configuration |
| `verify_setup.py` | ~150 | Setup checks |
| **Total** | **~1,700** | **Production code** |

| Documentation | Pages | Purpose |
|--------------|-------|---------|
| `README_ORCHESTRATION.md` | 17 | Architecture guide |
| `ARCHITECTURE.md` | 20 | Technical deep dive |
| `QUICKSTART.md` | 8 | Setup walkthrough |
| `PROJECT_SUMMARY.md` | 12 | Executive summary |
| **Total** | **~57** | **Comprehensive docs** |

---

## Maintenance & Updates

### Version Control

**What to Commit**:
- ✅ All `.py` files
- ✅ All `.md` documentation
- ✅ `requirements.txt`
- ✅ `.streamlit/config.toml`
- ✅ `.streamlit/secrets.toml.example`
- ✅ `.gitignore`

**What NOT to Commit**:
- ❌ `.streamlit/secrets.toml` (contains credentials)
- ❌ `__pycache__/` directories
- ❌ `.DS_Store` (Mac)
- ❌ Any `.log` files

### Regular Updates

**Weekly**:
- Review session statistics
- Adjust `MAX_SEARCH_RESULTS` if needed
- Update terminology for new terms

**Monthly**:
- Check for new Cortex model releases
- Review and update model pricing
- Optimize based on usage patterns

**Quarterly**:
- Comprehensive cost analysis
- User satisfaction survey
- Architecture review for scaling

---

## Quick Reference

### Run the App
```bash
streamlit run app.py
```

### Verify Setup
```bash
python verify_setup.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Update Configuration
```
Edit: config.py
Then: Restart app (changes take effect)
```

### Enable Debug Mode
```
In app: Sidebar → Check "Show Debug/Cost Info"
```

### View Session Stats
```
In app: Sidebar → "Session Statistics" section
```

---

**File Structure Last Updated**: December 2024

