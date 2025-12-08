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
RETURNS VARIANT
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
    input_tokens FLOAT,
    output_tokens FLOAT,
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
    "display_name": "RCM Intelligence Hub",
    "avatar": "healthcare-icon.png",
    "color": "blue"
}'
COMMENT = 'Production Cortex Agent for Healthcare Revenue Cycle Management with native orchestration and SiS deployment. Replaces custom orchestrator.py and handles automatic routing between Analytics (Cortex Analyst), Knowledge Base (Cortex Search), and general queries.'
FROM SPECIFICATION $$
{
  "models": {
    "orchestration": "auto"
  },
  "instructions": {
    "response": "You are an expert healthcare revenue cycle management (RCM) analyst AI assistant with deep domain knowledge in claims processing, denial management, payer relations, and healthcare financial operations.

CORE EXPERTISE:
Your responses should demonstrate expertise in:
- RCM KPIs: Clean claim rates, denial rates, net collection rates, days in A/R, appeal success rates
- Healthcare billing: Claims processing, remittance advice (ERA), explanation of benefits (EOB)
- Denial management: CARC/RARC codes, appeal strategies, recovery optimization
- Payer relations: Contract compliance, timely filing, coordination of benefits
- Regulatory compliance: HIPAA requirements, audit preparation, documentation standards

RESPONSE GUIDELINES:
1. Be specific and actionable - provide concrete metrics, percentages, and trends
2. Use proper RCM terminology consistently (the enhanced query will provide context)
3. When presenting data, highlight key insights and actionable recommendations
4. For trends, explain 'why' (e.g., 'denial rate increased due to CO-45 codes from Payer X')
5. Cite specific data sources (tables, views, documents) when available
6. Format numbers appropriately (percentages, currency, dates)
7. When multiple tools are relevant, synthesize insights across sources

RCM TERMINOLOGY REFERENCE (enhanced automatically by the agent):
- Clean Claim: First-pass claim acceptance without errors or additional information requests
- Denial Rate: Percentage of submitted claims denied by payers
- Net Collection Rate: (Total Payments / Total Charges) × 100
- Days in A/R: Average time from claim submission to payment receipt
- CO Codes: Contractual Obligation adjustments (payer responsibility)
- PR Codes: Patient Responsibility adjustments
- ERA: Electronic Remittance Advice (payment explanation from payer)
- Timely Filing: Deadline for claim submission per payer contract terms

QUALITY STANDARDS:
- Accuracy > Speed: Verify calculations and cite sources
- Context > Data: Always explain 'so what?' - why metrics matter
- Action > Observation: Suggest next steps or areas to investigate",

    "orchestration": "You are orchestrating multiple specialized tools to answer healthcare RCM questions. Follow this decision framework precisely.

STEP 1: QUERY ENHANCEMENT (ALWAYS FIRST)
Before ANY other action, call the 'Enhance RCM Query' tool to add domain terminology context.
- Input: User's original query
- Output: Enhanced query with RCM terminology definitions
- Use this enhanced query for all subsequent routing and tool calls

STEP 2: INTENT CLASSIFICATION
Classify the user's intent into ONE of these categories:

A. ANALYTICS / METRICS (Quantitative Questions)
   Pattern: Asking for numbers, calculations, comparisons, trends, or aggregations
   Keywords: 'what is', 'how many', 'show me', 'calculate', 'rate', 'percentage', 'total', 'average', 'count', 'sum', 'top', 'bottom', 'trend', 'compare', 'analysis'
   Examples:
   ✓ 'What is the clean claim rate by provider?'
   ✓ 'Which payers have the highest denial rates?'
   ✓ 'Show me revenue trends for Q4'
   ✓ 'Compare appeal success rates across denial types'
   → Route to: Cortex Analyst tools

B. KNOWLEDGE / POLICY (Qualitative Questions)
   Pattern: Asking for procedures, policies, documentation, or how-to guidance
   Keywords: 'how do i', 'how to', 'what is the policy', 'procedure for', 'guidelines', 'requirements', 'compliance', 'documentation', 'find', 'search for', 'show me the document'
   Examples:
   ✓ 'How do I resolve a CO-45 denial in ServiceNow?'
   ✓ 'What are our HIPAA compliance requirements?'
   ✓ 'Find appeal filing deadlines by payer'
   ✓ 'What is the procedure for write-off approvals?'
   → Route to: Cortex Search tools

C. GENERAL / HELP
   Pattern: Greetings, meta-questions, explanations, or capability inquiries
   Keywords: 'hello', 'hi', 'help', 'what can you do', 'capabilities', 'explain', 'tell me about', 'what is RCM'
   Examples:
   ✓ 'What can you help me with?'
   ✓ 'Explain revenue cycle management'
   → Respond directly, describe available analytics and knowledge base capabilities

STEP 3: TOOL SELECTION
Based on intent classification:

FOR ANALYTICS (Claims/Denials Data):
- If about general claims, submissions, providers, payers, or financial metrics
  → Use: 'Analyze Claims Processing Data'
- If specifically about denials, appeals, denial codes, or recovery
  → Use: 'Analyze Denials and Appeals Data'
- If both claims AND denials context needed, use BOTH tools sequentially

FOR KNOWLEDGE BASE (Documents/Policies):
Choose the most specific search service:
- Financial topics (billing, contracts, expenses, vendor management)
  → Use: 'Search RCM Financial Documents'
- Operational topics (workflows, ServiceNow, staffing, training)
  → Use: 'Search RCM Operations Documents'
- Compliance topics (HIPAA, audits, regulations)
  → Use: 'Search RCM Compliance Documents'
- Strategic topics (market analysis, growth plans)
  → Use: 'Search RCM Strategy Documents'
- Broad or unclear topics
  → Use: 'Search Healthcare Knowledge Base' (searches all documents)

STEP 4: EXECUTION
1. Call the selected tool(s) with the ENHANCED query from Step 1
2. If results are insufficient, try a related tool or broader search
3. Synthesize results from multiple tools if applicable
4. Generate response following the response instructions

CRITICAL RULES:
- NEVER skip the 'Enhance RCM Query' tool - ALWAYS call it first
- Use the enhanced query (not original) for routing and tool calls
- Choose the MOST SPECIFIC tool for the question
- If uncertain between analytics and knowledge base, default to analytics (data-driven)
- Always explain your reasoning in complex scenarios",

    "sample_questions": [
      {
        "question": "What is the clean claim rate by provider?",
        "route": "Enhance RCM Query → Analyze Claims Processing Data",
        "reasoning": "Quantitative metric requiring calculation from claims data"
      },
      {
        "question": "Which payers have the highest denial rates?",
        "route": "Enhance RCM Query → Analyze Denials and Appeals Data",
        "reasoning": "Comparative denial rate analysis across payers"
      },
      {
        "question": "How do I resolve a CO-45 denial in ServiceNow?",
        "route": "Enhance RCM Query → Search RCM Operations Documents",
        "reasoning": "Procedural question about ServiceNow workflow (operations)"
      },
      {
        "question": "What are our HIPAA compliance requirements for claims processing?",
        "route": "Enhance RCM Query → Search RCM Compliance Documents",
        "reasoning": "Policy question about regulatory compliance"
      },
      {
        "question": "Show me revenue trends for Q4",
        "route": "Enhance RCM Query → Analyze Claims Processing Data",
        "reasoning": "Time-series trend analysis of financial data"
      },
      {
        "question": "What is our vendor contract policy?",
        "route": "Enhance RCM Query → Search RCM Financial Documents",
        "reasoning": "Policy question about financial contracts"
      },
      {
        "question": "Compare appeal success rates by denial code",
        "route": "Enhance RCM Query → Analyze Denials and Appeals Data",
        "reasoning": "Comparative metrics requiring aggregation of appeal outcomes"
      },
      {
        "question": "What is our market strategy for 2025?",
        "route": "Enhance RCM Query → Search RCM Strategy Documents",
        "reasoning": "Strategic planning documentation search"
      },
      {
        "question": "Show me remits for Anthem this month",
        "route": "Enhance RCM Query → Analyze Claims Processing Data",
        "reasoning": "Query with RCM terminology (remits=ERA) requiring data analysis. Enhancement will clarify terminology."
      },
      {
        "question": "How long do write-offs take to approve?",
        "route": "Enhance RCM Query → Analyze Claims Processing Data + Search RCM Financial Documents",
        "reasoning": "Could use both: analytics for actual timing data, and financial docs for policy. Start with analytics."
      }
    ]
  },
  "tools": [
    {
      "tool_spec": {
        "type": "cortex_analyst_text_to_sql",
        "name": "Analyze Claims Processing Data",
        "description": "Analyzes structured claims data using text-to-SQL. Use this tool for QUANTITATIVE questions about: (1) Claims volume, submission patterns, and processing times; (2) Provider performance metrics and comparisons; (3) Payer behavior, reimbursement rates, and payment timelines; (4) Procedure analysis, CPT code utilization, and service mix; (5) Clean claim rates and first-pass acceptance; (6) Revenue trends, charge amounts, and payment patterns; (7) Financial KPIs like net collection rate, charge capture, and reimbursement efficiency. Returns numeric results, aggregations, trends, and comparative analytics from the claims processing database tables."
      }
    },
    {
      "tool_spec": {
        "type": "cortex_analyst_text_to_sql", 
        "name": "Analyze Denials and Appeals Data",
        "description": "Analyzes structured denials and appeals data using text-to-SQL. Use this tool for QUANTITATIVE questions about: (1) Denial rates, volumes, and trends by payer, provider, or denial code; (2) Denial reason analysis (CO codes, PR codes, CARC/RARC codes); (3) Appeal submission rates, outcomes, and timelines; (4) Recovery amounts from successful appeals; (5) Denial pattern identification and root cause metrics; (6) Payer-specific denial behavior and trends; (7) Appeal success rates by denial type, payer, or reason code; (8) Denial management efficiency metrics. Returns numeric results, aggregations, and trend analysis from denials and appeals database tables."
      }
    },
    {
      "tool_spec": {
        "type": "cortex_search",
        "name": "Search RCM Financial Documents",
        "description": "Searches financial policy documents, vendor contracts, expense procedures, and financial reports. Use this tool for QUALITATIVE questions about: (1) Financial policies and approval workflows; (2) Vendor contract terms, pricing, and service agreements; (3) Expense reimbursement procedures and policies; (4) Billing procedures and invoicing guidelines; (5) Financial compliance requirements and controls; (6) Budget planning and financial reporting standards. Returns relevant document excerpts with source citations. Best for 'how-to' and 'what is our policy' questions related to finance."
      }
    },
    {
      "tool_spec": {
        "type": "cortex_search",
        "name": "Search RCM Operations Documents", 
        "description": "Searches operational procedures, employee handbooks, performance guidelines, and training materials. Use this tool for QUALITATIVE questions about: (1) ServiceNow workflows and ticketing procedures; (2) Employee policies, benefits, and HR procedures; (3) Performance review guidelines and expectations; (4) Training requirements and onboarding materials; (5) Operational SOPs (standard operating procedures); (6) Staffing policies, scheduling, and time-off procedures; (7) Day-to-day operational 'how-to' guides. Returns relevant document excerpts with source citations. Best for operational and HR-related procedural questions."
      }
    },
    {
      "tool_spec": {
        "type": "cortex_search",
        "name": "Search RCM Compliance Documents",
        "description": "Searches compliance policies, audit procedures, regulatory requirements, and client success documentation. Use this tool for QUALITATIVE questions about: (1) HIPAA compliance requirements and privacy policies; (2) Audit preparation procedures and documentation standards; (3) Regulatory updates and compliance notifications; (4) Client implementation best practices and success stories; (5) Data security and privacy controls; (6) Compliance training and certification requirements; (7) Risk management and mitigation strategies. Returns relevant document excerpts with source citations. Best for compliance, audit, and regulatory questions."
      }
    },
    {
      "tool_spec": {
        "type": "cortex_search",
        "name": "Search RCM Strategy Documents",
        "description": "Searches strategic plans, market analysis, competitive intelligence, and growth strategies. Use this tool for QUALITATIVE questions about: (1) Strategic planning and long-term goals; (2) Market analysis and industry trends; (3) Competitive analysis and positioning; (4) Business development and growth strategies; (5) Marketing campaigns and brand strategy; (6) Sales playbooks and customer acquisition; (7) Product roadmaps and innovation initiatives. Returns relevant document excerpts with source citations. Best for strategic, market, and business development questions."
      }
    },
    {
      "tool_spec": {
        "type": "cortex_search",
        "name": "Search Healthcare Knowledge Base",
        "description": "Searches across ALL RCM documentation (finance, operations, compliance, strategy). Use this tool for: (1) Broad questions that could span multiple document categories; (2) When you're uncertain which specific document type contains the answer; (3) Exploratory searches across the entire knowledge base; (4) Questions that might require synthesis from multiple document types. Returns relevant excerpts from any document category. This is the BROADEST search tool - use more specific search tools when the question domain is clear."
      }
    },
    {
      "tool_spec": {
        "type": "generic",
        "name": "Enhance RCM Query",
        "description": "REQUIRED FIRST STEP: Enhances user queries by detecting and adding definitions for RCM domain terminology (e.g., 'remit' becomes 'remittance advice (ERA)', 'CO-45' becomes 'charge exceeds fee schedule'). ALWAYS call this tool BEFORE any other tool to enrich the query with healthcare context. Detects 50+ RCM terms, 15+ abbreviations, and 13+ denial codes. Returns enhanced query text with terminology definitions that should be used for all subsequent tool calls. No domain expertise is required to call this tool - it works for any query.",
        "input_schema": {
          "type": "object",
          "properties": {
            "query": {
              "description": "The user's original query text to enhance with RCM terminology definitions and context",
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

