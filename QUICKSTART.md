# RCM Intelligence Hub - Quick Start Guide

**Get running in 30 minutes using only Snowsight (no CLI required)**

---

## Prerequisites

✅ Snowflake account with Cortex AI access (Agents, Search, Analyst)  
✅ Role with privileges to create databases, schemas, warehouses, agents  
✅ Web browser access to Snowsight

**No local setup required!** Everything runs in Snowsight.

---

## Step-by-Step Setup

### Step 1: Execute SQL Scripts (20 minutes)

Open **Snowsight** → **Projects** → **Worksheets**

For each script below:
1. Create a new SQL worksheet
2. Copy/paste the script contents
3. Execute all statements (Ctrl+Enter or click ▶ Run All)
4. Verify success with the verification queries at the end

**Execute in this exact order:**

#### 1️⃣ Database & Infrastructure
File: `sql_scripts/01_rcm_data_setup.sql`
- Creates database, schema, warehouse
- Sets up roles and permissions
- Creates dimension tables

**Verify:** Should see "RCM Infrastructure Setup Complete"

#### 2️⃣ Document Loading  
File: `sql_scripts/02_rcm_documents_setup.sql`
- Parses RCM documents with Cortex Document AI
- Creates parsed content table
- Loads ~40 documents

**Verify:** `SELECT COUNT(*) FROM rcm_parsed_content;` → Should return ~40

#### 3️⃣ Data Generation
File: `sql_scripts/03_rcm_data_generation.sql`
- Generates 50,000 claims
- Generates 7,500 denials
- Creates payment records

**Verify:** `SELECT COUNT(*) FROM claims_fact;` → Should return 50,000

#### 4️⃣ Semantic Views
File: `sql_scripts/04_rcm_semantic_views.sql`
- Creates Claims Processing semantic view
- Creates Denials Management semantic view

**Verify:** `SHOW SEMANTIC VIEWS;` → Should show 2 views

#### 5️⃣ Cortex Search Services
File: `sql_scripts/05_rcm_cortex_search.sql`
- Creates 5 search services for RCM documents

**Verify:** Search services listed in `INFORMATION_SCHEMA.CORTEX_SEARCH_SERVICES`

#### 6️⃣ Agent Setup
File: `sql_scripts/06_rcm_agent_setup.sql`
- Creates helper UDFs and procedures
- Creates RCM_Healthcare_Agent with 10 tools

**Verify:** `SHOW AGENTS;` → Should list RCM_Healthcare_Agent

#### 7️⃣ Production Agent (Recommended)
File: `sql_scripts/07_rcm_native_agent_production.sql`
- Creates production agent with RCM terminology
- Adds 50+ healthcare term enhancements

**Verify:** Agent shows in `SNOWFLAKE_INTELLIGENCE.AGENTS` schema

---

### Step 2: Create Streamlit App (5 minutes)

In **Snowsight**:

1. Navigate to **Projects** → **Streamlit**

2. Click **+ Streamlit App**

3. Configure:
   - **Name**: `RCM_INTELLIGENCE_HUB`
   - **Location**:
     - Warehouse: `RCM_INTELLIGENCE_WH`
     - Database: `RCM_AI_DEMO`
     - Schema: `RCM_SCHEMA`

4. **Delete** the default template code

5. Open `08_streamlit_app.py` in your repository

6. **Copy** entire contents → **Paste** into Streamlit editor

7. Click **Run** (top right corner)

**Expected Result:** App launches in preview pane with chat interface

---

### Step 3: Test the App (5 minutes)

Try these sample questions:

#### Analytics (Cortex Analyst)
```
What is the clean claim rate by provider?
```
**Expected:** Table/chart with provider performance metrics

#### Knowledge Base (Cortex Search)
```
How do I resolve a Code 45 denial?
```
**Expected:** Document excerpts with denial resolution procedures

#### RCM Terminology (Agent Intelligence)
```
Show me remits for Anthem
```
**Expected:** Query auto-enhanced ("remit" → "remittance advice ERA")

#### Multi-Tool (Agent Orchestration)
```
Which payers have the highest denial rates and what do our appeal procedures say?
```
**Expected:** Combined answer from both analytics and documents

---

## Troubleshooting

### Agent not found
**Error:** "Agent SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent does not exist"

**Fix:** Make sure you executed `06_rcm_agent_setup.sql` completely

### Search service not ready
**Error:** "Cortex Search service not found"

**Fix:** 
1. Check `SHOW CORTEX SEARCH SERVICES;`
2. Ensure `05_rcm_cortex_search.sql` completed successfully
3. Wait 1-2 minutes for services to initialize

### Streamlit app errors
**Error:** Module import errors

**Fix:**
1. Ensure warehouse is running: `ALTER WAREHOUSE RCM_INTELLIGENCE_WH RESUME;`
2. Check you're using the correct database/schema in app configuration

### Permission errors
**Error:** "Insufficient privileges"

**Fix:**
1. Ensure you're using `ACCOUNTADMIN` role for setup scripts
2. Grant usage on agent:
```sql
GRANT USAGE ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent 
  TO ROLE YOUR_ROLE;
```

---

## Next Steps

### Share with Team
```sql
-- Grant app access to users
GRANT USAGE ON STREAMLIT RCM_AI_DEMO.RCM_SCHEMA.RCM_INTELLIGENCE_HUB 
  TO ROLE BUSINESS_ANALYST;

GRANT USAGE ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent 
  TO ROLE BUSINESS_ANALYST;

GRANT ROLE BUSINESS_ANALYST TO USER john.doe@company.com;
```

### Try Snowflake Intelligence
1. Go to **AI & ML** → **Snowflake Intelligence**
2. Select `RCM_Healthcare_Agent`
3. Ask questions directly (no Streamlit app needed)

### Customize the Agent
- Edit orchestration instructions in Snowsight (AI & ML → Agents → Edit)
- Add more RCM terminology in `07_rcm_native_agent_production.sql`
- Adjust search service `max_results` for cost optimization

---

## Success Criteria

✅ All 7 SQL scripts executed without errors  
✅ Streamlit app running and accessible  
✅ Analytics questions return data  
✅ Knowledge questions return documents  
✅ RCM terminology enhanced automatically  
✅ Debug panel shows agent reasoning (if enabled)

---

## Getting Help

- **Documentation**: See `ARCHITECTURE.md` for technical details
- **Demo Script**: See `DEMO_HIGHLIGHTS.md` for presentation guide
- **Standards**: See `SNOWFLAKE_STANDARDS_UPDATE.md` for compliance info

- **Snowflake Resources**:
  - [Cortex Agents Docs](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)
  - [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
  - [Getting Started with Cortex Agents (Snowflake Labs)](https://github.com/Snowflake-Labs/sfquickstarts/blob/master/site/sfguides/src/getting-started-with-cortex-agents/getting-started-with-cortex-agents.md)

---

**Total Time:** ~30 minutes  
**Difficulty:** Beginner (copy/paste in Snowsight)  
**Result:** Production-ready RCM Intelligence Hub 🎉
