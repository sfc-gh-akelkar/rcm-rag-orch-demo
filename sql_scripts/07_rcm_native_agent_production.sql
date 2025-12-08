-- ========================================================================
-- RCM AI Demo - Production Native Cortex Agent Setup
-- Streamlit in Snowflake (SiS) + Native Orchestration
-- ========================================================================
-- This replaces the custom orchestrator.py with Snowflake's native
-- Cortex Agent for production deployment
-- ========================================================================

USE ROLE ACCOUNTADMIN;
USE DATABASE RCM_AI_DEMO;
USE SCHEMA RCM_SCHEMA;

-- ========================================================================
-- STEP 1: CREATE RCM TERMINOLOGY ENHANCEMENT UDFs
-- ========================================================================
-- These replace the Python rcm_terminology.py module
-- Runs inside Snowflake for zero data movement

-- Main terminology enhancement function
CREATE OR REPLACE FUNCTION ENHANCE_RCM_QUERY(query STRING)
RETURNS OBJECT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python')
HANDLER = 'enhance_query'
COMMENT = 'Enhances user queries with RCM domain terminology definitions'
AS $$
def enhance_query(query):
    """
    Detect RCM terminology in queries and add context.
    Replaces rcm_terminology.py for SiS deployment.
    """
    import re
    
    # RCM terminology mappings
    terminology = {
        "remit": "remittance advice (ERA - Electronic Remittance Advice)",
        "remits": "remittance advice documents",
        "write-off": "contractual adjustment or bad debt write-off (adjustment codes CO-45, PR-1)",
        "clean claim": "claim submitted without errors that is accepted on first submission",
        "dirty claim": "claim requiring correction or additional information before processing",
        "scrub": "automated claim validation and error checking before submission",
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
        "eob": "explanation of benefits",
        "era": "electronic remittance advice",
        "edi": "electronic data interchange"
    }
    
    # Denial code patterns
    denial_codes = {
        r'\bCO-?45\b': "CO-45 (Contractual Obligation - charge exceeds fee schedule)",
        r'\bPR-?1\b': "PR-1 (Patient Responsibility - deductible)",
        r'\bCO-?16\b': "CO-16 (Claim/service lacks information)",
        r'\bCO-?29\b': "CO-29 (Time limit for filing has expired)",
        r'\bCO-?50\b': "CO-50 (Non-covered service)"
    }
    
    detected_terms = []
    query_lower = query.lower()
    
    # Detect terminology
    for term, definition in terminology.items():
        pattern = r'\b' + re.escape(term) + r'\b'
        if re.search(pattern, query_lower, re.IGNORECASE):
            detected_terms.append({"term": term, "definition": definition})
    
    # Detect denial codes
    for pattern, description in denial_codes.items():
        if re.search(pattern, query, re.IGNORECASE):
            detected_terms.append({"term": pattern.replace(r'\b', ''), "definition": description})
    
    # Build enhanced query
    if detected_terms:
        context = "RCM Terminology Context:\n"
        for item in detected_terms:
            context += f"- {item['term']}: {item['definition']}\n"
        
        enhanced_query = f"{context}\n\nUser Query: {query}"
        
        return {
            "enhanced_query": enhanced_query,
            "original_query": query,
            "terms_detected": detected_terms,
            "has_enhancements": True
        }
    else:
        return {
            "enhanced_query": query,
            "original_query": query,
            "terms_detected": [],
            "has_enhancements": False
        }
$$;

-- Get just the enhanced query text (for agent use)
CREATE OR REPLACE FUNCTION GET_ENHANCED_QUERY(query STRING)
RETURNS STRING
LANGUAGE SQL
AS $$
    SELECT ENHANCE_RCM_QUERY(query):enhanced_query::STRING
$$;

-- Check if query has RCM terminology
CREATE OR REPLACE FUNCTION HAS_RCM_TERMS(query STRING)
RETURNS BOOLEAN
LANGUAGE SQL
AS $$
    SELECT ENHANCE_RCM_QUERY(query):has_enhancements::BOOLEAN
$$;

-- Get detected terms as array
CREATE OR REPLACE FUNCTION GET_RCM_TERMS(query STRING)
RETURNS ARRAY
LANGUAGE SQL
AS $$
    SELECT ENHANCE_RCM_QUERY(query):terms_detected
$$;

-- Test the UDF
SELECT ENHANCE_RCM_QUERY('What is the denial rate for CO-45 remits?') as enhancement_result;

-- ========================================================================
-- STEP 2: CREATE COST TRACKING FUNCTIONS
-- ========================================================================
-- Replaces cost_tracker.py with SQL functions

-- Estimate tokens from text
CREATE OR REPLACE FUNCTION ESTIMATE_TOKENS(text STRING)
RETURNS INTEGER
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
HANDLER = 'estimate_tokens'
COMMENT = 'Estimates token count from text (1 token ≈ 4 characters)'
AS $$
def estimate_tokens(text):
    if not text:
        return 0
    # Simple estimation: 1 token ≈ 4 characters
    # In production, could use tiktoken library
    return len(text) // 4
$$;

-- Calculate cost estimate
CREATE OR REPLACE FUNCTION ESTIMATE_COST(
    input_tokens INTEGER,
    output_tokens INTEGER,
    model STRING
)
RETURNS FLOAT
LANGUAGE JAVASCRIPT
COMMENT = 'Estimates cost based on token counts and model'
AS $$
    // Model pricing per million tokens (Dec 2024)
    const pricing = {
        'auto': {input: 2.00, output: 6.00},
        'mistral-large': {input: 2.00, output: 6.00},
        'llama3.1-70b': {input: 0.90, output: 0.90},
        'llama3-70b': {input: 0.90, output: 0.90},
        'llama3.2-3b': {input: 0.20, output: 0.20},
        'claude-sonnet-4': {input: 3.00, output: 15.00}
    };
    
    const modelPricing = pricing[MODEL] || pricing['auto'];
    const inputCost = (INPUT_TOKENS / 1000000) * modelPricing.input;
    const outputCost = (OUTPUT_TOKENS / 1000000) * modelPricing.output;
    
    return inputCost + outputCost;
$$;

-- ========================================================================
-- STEP 3: CREATE PRODUCTION CORTEX AGENT
-- ========================================================================
-- This replaces orchestrator.py with native Snowflake orchestration

-- Drop existing agent if it exists
DROP AGENT IF EXISTS SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod;

-- Create production agent with native orchestration
CREATE AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod
WITH PROFILE='{ 
    "display_name": "RCM Intelligence Hub (Production)",
    "description": "Production agent for Healthcare Revenue Cycle Management with native orchestration and SiS deployment"
}'
COMMENT = 'Production Cortex Agent replacing custom orchestrator.py. Handles automatic routing between Analytics (Cortex Analyst), Knowledge Base (Cortex Search), and general queries.'
FROM SPECIFICATION $$
{
  "models": {
    "orchestration": "auto"
  },
  "instructions": {
    "response": "You are a healthcare revenue cycle management (RCM) analyst with deep expertise in claims processing, denial management, payer relations, and healthcare financial operations. 

IMPORTANT: Before processing any user query, ALWAYS call the GET_ENHANCED_QUERY function to enhance the query with RCM terminology context. Use the enhanced query for all subsequent tool calls.

When answering questions:
1. Use GET_ENHANCED_QUERY to enhance the user's query first
2. Focus on RCM-specific KPIs like clean claim rates, denial rates, net collection rates, days in A/R, appeal success rates, and payer performance metrics
3. Provide visualizations when possible
4. Always relate insights back to revenue cycle optimization and healthcare financial performance
5. Use healthcare terminology throughout your responses

RCM Terminology You Should Understand:
- Clean Claim Rate = % of claims accepted on first submission
- Denial Rate = % of claims denied
- Net Collection Rate = (Paid Amount / Charge Amount) × 100
- Days in A/R = Average days from submission to payment
- Appeal Success Rate = % of appeals resulting in payment
- CO codes = Contractual Obligation (payer responsibility)
- PR codes = Patient Responsibility
- ERA = Electronic Remittance Advice
- EDI = Electronic Data Interchange",

    "orchestration": "You have access to three types of tools: Cortex Analyst (structured data analysis), Cortex Search (document/policy search), and custom UDFs (RCM terminology enhancement).

ROUTING LOGIC (Critical - Follow Exactly):

1. ALWAYS start by calling GET_ENHANCED_QUERY(user_query) to enhance the query with RCM terminology

2. For ANALYTICS queries (metrics, calculations, trends, comparisons):
   - Triggers: 'what is', 'show me', 'calculate', 'how many', 'rate', 'percentage', 'total', 'average', 'top', 'bottom', 'trend', 'compare'
   - Examples: 'What is the denial rate?', 'Show me top payers', 'Calculate net collection rate'
   - Route to: Cortex Analyst tools (Claims Processing or Denials Management)
   - Use the enhanced query from GET_ENHANCED_QUERY

3. For KNOWLEDGE BASE queries (policies, procedures, documentation, how-to):
   - Triggers: 'how do i', 'how to', 'policy', 'procedure', 'documentation', 'compliance', 'guideline', 'find', 'search'
   - Examples: 'How do I resolve Code 45?', 'What is our HIPAA policy?', 'Find appeal procedures'
   - Route to: Cortex Search tools (RCM Finance, Operations, Compliance, or Knowledge Base)
   - Use the enhanced query from GET_ENHANCED_QUERY

4. For GENERAL queries (greetings, help, explanations):
   - Triggers: 'hello', 'hi', 'help', 'what can you', 'explain', 'tell me about'
   - Examples: 'What can you help with?', 'Explain RCM metrics'
   - Respond directly without tools, but provide guidance on using analytics and knowledge base tools

EXECUTION FLOW:
Step 1: Call GET_ENHANCED_QUERY(user_query)
Step 2: Use enhanced query to determine intent
Step 3: Route to appropriate tool(s)
Step 4: Generate response with RCM context

Always prioritize accuracy and cite specific data sources or policies when available.",

    "sample_questions": [
      {
        "question": "What is the clean claim rate by provider?",
        "route": "Analytics - Claims Processing"
      },
      {
        "question": "Which payers have the highest denial rates?",
        "route": "Analytics - Denials Management"
      },
      {
        "question": "How do I resolve a CO-45 denial in ServiceNow?",
        "route": "Knowledge Base - Operations"
      },
      {
        "question": "What are our HIPAA compliance requirements for claims processing?",
        "route": "Knowledge Base - Compliance"
      },
      {
        "question": "Show me revenue trends for Q4",
        "route": "Analytics - Claims Processing"
      }
    ]
  },
  "tools": [
    {
      "tool_spec": {
        "type": "cortex_analyst_text_to_sql",
        "name": "Analyze Claims Processing Data",
        "description": "Query and analyze healthcare claims processing data including provider performance, payer behavior, procedure analysis, clean claim rates, denial rates, and financial metrics. Use this for questions about claims volume, processing times, reimbursement patterns, revenue trends, and operational efficiency metrics."
      }
    },
    {
      "tool_spec": {
        "type": "cortex_analyst_text_to_sql", 
        "name": "Analyze Denials and Appeals Data",
        "description": "Query and analyze denials management data including denial reasons, appeal outcomes, recovery rates, payer-specific denial patterns, and appeal success metrics. Use this for questions about denial trends, appeal effectiveness, denial management optimization, and recovery strategies."
      }
    },
    {
      "tool_spec": {
        "type": "cortex_search",
        "name": "Search RCM Financial Documents",
        "description": "Search financial policies, vendor contracts, expense procedures, and financial reports related to revenue cycle management. Use for questions about financial policies, contract terms, billing procedures, and financial compliance."
      }
    },
    {
      "tool_spec": {
        "type": "cortex_search",
        "name": "Search RCM Operations Documents", 
        "description": "Search operational procedures, employee handbooks, performance guidelines, and training materials for RCM operations. Use for questions about operational policies, staffing procedures, performance standards, ServiceNow workflows, and training requirements."
      }
    },
    {
      "tool_spec": {
        "type": "cortex_search",
        "name": "Search RCM Compliance Documents",
        "description": "Search compliance policies, audit procedures, regulatory requirements, and client success documentation. Use for questions about compliance requirements (HIPAA, etc.), audit preparation, regulatory updates, and client implementation best practices."
      }
    },
    {
      "tool_spec": {
        "type": "cortex_search",
        "name": "Search RCM Strategy Documents",
        "description": "Search strategic plans, market analysis, competitive intelligence, and growth strategies for healthcare revenue cycle management. Use for questions about strategic planning, market opportunities, competitive analysis, and business development."
      }
    },
    {
      "tool_spec": {
        "type": "cortex_search",
        "name": "Search Healthcare Knowledge Base",
        "description": "Search the comprehensive healthcare RCM knowledge base covering all document types. Use for broad questions that might span multiple areas or when you need to find information across all healthcare documentation."
      }
    },
    {
      "tool_spec": {
        "type": "generic",
        "name": "Enhance RCM Query",
        "description": "Enhances user queries with RCM domain terminology definitions. ALWAYS call this FIRST before routing to other tools. Input is the raw user query, output is enhanced query with terminology context.",
        "input_schema": {
          "type": "object",
          "properties": {
            "query": {
              "description": "The user's original query to enhance with RCM terminology",
              "type": "string"
            }
          },
          "required": ["query"]
        }
      }
    }
  ],
  "tool_resources": {
    "Analyze Claims Processing Data": {
      "semantic_view": "RCM_AI_DEMO.RCM_SCHEMA.CLAIMS_PROCESSING_VIEW"
    },
    "Analyze Denials and Appeals Data": {
      "semantic_view": "RCM_AI_DEMO.RCM_SCHEMA.DENIALS_MANAGEMENT_VIEW"
    },
    "Search RCM Financial Documents": {
      "id_column": "RELATIVE_PATH",
      "max_results": 5,
      "name": "RCM_AI_DEMO.RCM_SCHEMA.RCM_FINANCE_DOCS_SEARCH",
      "title_column": "TITLE"
    },
    "Search RCM Operations Documents": {
      "id_column": "RELATIVE_PATH",
      "max_results": 5,
      "name": "RCM_AI_DEMO.RCM_SCHEMA.RCM_OPERATIONS_DOCS_SEARCH",
      "title_column": "TITLE"
    },
    "Search RCM Compliance Documents": {
      "id_column": "RELATIVE_PATH",
      "max_results": 5,
      "name": "RCM_AI_DEMO.RCM_SCHEMA.RCM_COMPLIANCE_DOCS_SEARCH",
      "title_column": "TITLE"
    },
    "Search RCM Strategy Documents": {
      "id_column": "RELATIVE_PATH",
      "max_results": 5,
      "name": "RCM_AI_DEMO.RCM_SCHEMA.RCM_STRATEGY_DOCS_SEARCH",
      "title_column": "TITLE"
    },
    "Search Healthcare Knowledge Base": {
      "id_column": "RELATIVE_PATH",
      "max_results": 5,
      "name": "RCM_AI_DEMO.RCM_SCHEMA.RCM_KNOWLEDGE_BASE_SEARCH",
      "title_column": "TITLE"
    },
    "Enhance RCM Query": {
      "execution_environment": {
        "query_timeout": 30,
        "type": "warehouse",
        "warehouse": "RCM_INTELLIGENCE_WH"
      },
      "identifier": "RCM_AI_DEMO.RCM_SCHEMA.GET_ENHANCED_QUERY",
      "name": "GET_ENHANCED_QUERY(VARCHAR)",
      "type": "function"
    }
  }
}
$$;

-- Grant permissions for Streamlit app to use agent
GRANT USAGE ON DATABASE SNOWFLAKE_INTELLIGENCE TO ROLE SF_INTELLIGENCE_DEMO;
GRANT USAGE ON SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS TO ROLE SF_INTELLIGENCE_DEMO;
GRANT USAGE ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod TO ROLE SF_INTELLIGENCE_DEMO;

-- Grant usage on UDFs
GRANT USAGE ON FUNCTION RCM_AI_DEMO.RCM_SCHEMA.ENHANCE_RCM_QUERY(STRING) TO ROLE SF_INTELLIGENCE_DEMO;
GRANT USAGE ON FUNCTION RCM_AI_DEMO.RCM_SCHEMA.GET_ENHANCED_QUERY(STRING) TO ROLE SF_INTELLIGENCE_DEMO;
GRANT USAGE ON FUNCTION RCM_AI_DEMO.RCM_SCHEMA.HAS_RCM_TERMS(STRING) TO ROLE SF_INTELLIGENCE_DEMO;
GRANT USAGE ON FUNCTION RCM_AI_DEMO.RCM_SCHEMA.GET_RCM_TERMS(STRING) TO ROLE SF_INTELLIGENCE_DEMO;
GRANT USAGE ON FUNCTION RCM_AI_DEMO.RCM_SCHEMA.ESTIMATE_TOKENS(STRING) TO ROLE SF_INTELLIGENCE_DEMO;
GRANT USAGE ON FUNCTION RCM_AI_DEMO.RCM_SCHEMA.ESTIMATE_COST(INTEGER, INTEGER, STRING) TO ROLE SF_INTELLIGENCE_DEMO;

-- ========================================================================
-- STEP 4: ADD AGENT TO SNOWFLAKE INTELLIGENCE
-- ========================================================================
-- Make agent visible in Snowflake Intelligence UI

-- Create Snowflake Intelligence object if it doesn't exist
-- (Run this in Snowsight or adjust based on your setup)

-- Add agent to Snowflake Intelligence
-- ALTER SNOWFLAKE INTELLIGENCE SNOWFLAKE_INTELLIGENCE_OBJECT_DEFAULT 
--   ADD AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod;

-- ========================================================================
-- VERIFICATION
-- ========================================================================

-- Show created UDFs
SHOW FUNCTIONS LIKE 'ENHANCE%' IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;
SHOW FUNCTIONS LIKE 'GET%' IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;
SHOW FUNCTIONS LIKE 'ESTIMATE%' IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;

-- Show created agent
SHOW AGENTS IN SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS;

-- Test terminology enhancement
SELECT 
    'Test Query 1' as test_case,
    GET_ENHANCED_QUERY('What is the denial rate for CO-45 remits?') as enhanced_query
UNION ALL
SELECT 
    'Test Query 2' as test_case,
    GET_ENHANCED_QUERY('Show me clean claim rates by provider') as enhanced_query;

-- Success message
SELECT 
    '✅ Production Native Agent Setup Complete!' as status,
    'Agent: RCM_Healthcare_Agent_Prod' as agent_name,
    'UDFs created for RCM terminology enhancement' as terminology,
    'Ready for Streamlit in Snowflake deployment' as next_step;

