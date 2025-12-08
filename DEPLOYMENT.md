# RCM Intelligence Hub - Deployment Guide

**Complete deployment instructions using Snowsight (Web UI)**

---

## Overview

This guide covers deploying the RCM Intelligence Hub entirely within **Snowsight**, Snowflake's web interface. 

**Deployment Method**: 100% Snowsight (no CLI or local tools required)  
**Deployment Time**: ~30 minutes  
**Result**: Production-ready, HIPAA-compliant RCM AI in Snowflake

---

## Prerequisites

### Snowflake Account

✅ **Required**:
- Cortex enabled in your Snowflake account
- Access to Snowsight (web UI)
- Role with sufficient privileges:
  - CREATE DATABASE
  - CREATE SCHEMA
  - CREATE WAREHOUSE
  - CREATE AGENT
  - CREATE STREAMLIT
  - Or `ACCOUNTADMIN` role

### No Local Setup Required

❌ **NOT needed**:
- Python installation
- Snowflake CLI
- Git client
- Local development environment

**Everything is done in your browser via Snowsight!**

---

## Step-by-Step Deployment

### Step 1: Access Snowsight

1. Open your browser
2. Navigate to your Snowflake account URL:
   ```
   https://<orgname>-<accountname>.snowflakecomputing.com
   ```
3. Log in with your credentials
4. Select appropriate role (e.g., `ACCOUNTADMIN` or `SF_INTELLIGENCE_DEMO`)

---

### Step 2: Execute SQL Setup Scripts

#### Create SQL Worksheet

1. In Snowsight, navigate to **Projects** → **Worksheets**
2. Click **+ Worksheet** (top right, blue button)
3. Name it: `RCM Setup - 01 Infrastructure`

#### Execute Scripts in Order

**Script 01: Infrastructure Setup**

1. Open file: `sql_scripts/01_rcm_data_setup.sql`
2. Copy entire contents
3. Paste into your worksheet
4. Click **Run All** (or press `Cmd/Ctrl + Enter`)
5. Verify: Database `RCM_AI_DEMO` created

**Script 02: Documents Setup**

1. Create new worksheet: `RCM Setup - 02 Documents`
2. Copy/paste: `sql_scripts/02_rcm_documents_setup.sql`
3. Click **Run All**
4. Verify: Documents table created

**Script 03: Data Generation**

1. Create new worksheet: `RCM Setup - 03 Data`
2. Copy/paste: `sql_scripts/03_rcm_data_generation.sql`
3. Click **Run All** (may take 2-3 minutes)
4. Verify: 50,000+ records created

**Script 04: Semantic Views**

1. Create new worksheet: `RCM Setup - 04 Semantic Views`
2. Copy/paste: `sql_scripts/04_rcm_semantic_views.sql`
3. Click **Run All**
4. Verify: 2 semantic views created

**Script 05: Cortex Search Services**

1. Create new worksheet: `RCM Setup - 05 Search`
2. Copy/paste: `sql_scripts/05_rcm_cortex_search.sql`
3. Click **Run All** (may take 3-5 minutes)
4. Verify: 5 search services created

**Script 06: Basic Agent** (Optional)

1. Create new worksheet: `RCM Setup - 06 Agent`
2. Copy/paste: `sql_scripts/06_rcm_agent_setup.sql`
3. Click **Run All**
4. Verify: Agent created (reference implementation)

**Script 07: Production Agent + UDFs** ← **CRITICAL**

1. Create new worksheet: `RCM Setup - 07 Production`
2. Copy/paste: `sql_scripts/07_rcm_native_agent_production.sql`
3. Click **Run All**
4. Verify: Production agent and UDFs created

#### Verification Queries

Run in a new worksheet:

```sql
-- Check database & schema
SHOW DATABASES LIKE 'RCM_AI_DEMO';
SHOW SCHEMAS IN DATABASE RCM_AI_DEMO;

-- Check tables (should see 14)
SHOW TABLES IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;

-- Check semantic views (should see 2)
SHOW SEMANTIC VIEWS IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;

-- Check search services (should see 5)
SHOW CORTEX SEARCH SERVICES IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;

-- Check production agent (should see RCM_Healthcare_Agent_Prod)
SHOW AGENTS IN SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS;

-- Check UDFs (should see ENHANCE_RCM_QUERY, etc.)
SHOW FUNCTIONS LIKE 'ENHANCE%' IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;

-- Check warehouse
SHOW WAREHOUSES LIKE 'RCM_INTELLIGENCE_WH';
```

**✅ All objects should be created successfully!**

---

### Step 3: Create Streamlit App

#### Navigate to Streamlit

1. In Snowsight, go to **Projects** → **Streamlit** (left navigation)
2. Click **+ Streamlit App** (top right, blue button)

#### Configure App Settings

**In the "Create Streamlit App" dialog**:

- **App name**: `RCM_INTELLIGENCE_HUB`
- **App location**:
  - Database: `RCM_AI_DEMO`
  - Schema: `RCM_SCHEMA`
- **Warehouse**: `RCM_INTELLIGENCE_WH`

Click **Create**

#### Add Application Code

1. The Snowsight Streamlit editor will open
2. **Delete** all the default template code
3. **Copy** the entire contents of `streamlit_app.py` from this repo
4. **Paste** into the editor
5. Click **Run** (top right)

The app will start building and running (may take 30-60 seconds on first run).

#### Verify App is Running

**You should see**:
- App title: "🏥 RCM Intelligence Hub"
- Chat interface with input box
- Sidebar with session stats
- Sample question buttons

**If successful**: App is ready to use! 🎉

---

### Step 4: Test the Application

#### Test Analytics Query

Type in chat:
```
What is the clean claim rate by provider?
```

**Expected**:
- Agent routes to Cortex Analyst
- Returns metrics with provider breakdown
- Shows clean claim percentages

#### Test Knowledge Base Query

Type in chat:
```
How do I resolve a Code 45 denial in ServiceNow?
```

**Expected**:
- Agent routes to Cortex Search
- Returns relevant documents
- Cites sources (document names)
- Explains Code 45 = "charge exceeds fee schedule"

#### Test RCM Terminology Enhancement

Type in chat:
```
Show me remits for Anthem
```

**Expected**:
- "remits" enhanced to "remittance advice (ERA)"
- Query searches for Anthem payer
- Returns relevant remittance data

#### Enable Debug Panel

1. Click **>** in sidebar to expand
2. Check ✅ **"Show Debug/Agent Info"**
3. Re-run a query

**You should see**:
- Agent name: RCM_Healthcare_Agent_Prod
- Token counts (input/output/total)
- Estimated cost
- Performance metrics

---

## Post-Deployment Configuration

### Configure User Access

#### Grant App Access to Roles

```sql
-- Grant Streamlit app access
GRANT USAGE ON STREAMLIT RCM_AI_DEMO.RCM_SCHEMA.RCM_INTELLIGENCE_HUB 
  TO ROLE BUSINESS_ANALYST;

-- Grant agent access
GRANT USAGE ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod 
  TO ROLE BUSINESS_ANALYST;

-- Grant database access
GRANT USAGE ON DATABASE RCM_AI_DEMO TO ROLE BUSINESS_ANALYST;
GRANT USAGE ON SCHEMA RCM_AI_DEMO.RCM_SCHEMA TO ROLE BUSINESS_ANALYST;

-- Grant warehouse access
GRANT USAGE ON WAREHOUSE RCM_INTELLIGENCE_WH TO ROLE BUSINESS_ANALYST;
```

#### Assign Role to Users

```sql
-- Grant role to specific users
GRANT ROLE BUSINESS_ANALYST TO USER john.doe@quadax.com;
GRANT ROLE BUSINESS_ANALYST TO USER jane.smith@quadax.com;
```

#### Share App Link

1. In Snowsight, open your Streamlit app
2. Click **Share** button (top right)
3. Copy the URL
4. Send to users (they must have appropriate grants)

---

### Optimize Warehouse

#### For Development/Demos

```sql
ALTER WAREHOUSE RCM_INTELLIGENCE_WH 
SET WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60     -- 1 minute idle
    AUTO_RESUME = TRUE;
```

**Cost**: ~$25-50/month

#### For Production (5-20 concurrent users)

```sql
ALTER WAREHOUSE RCM_INTELLIGENCE_WH 
SET WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND = 300    -- 5 minutes idle
    AUTO_RESUME = TRUE;
```

**Cost**: ~$50-100/month

#### For High Traffic (50+ concurrent users)

```sql
ALTER WAREHOUSE RCM_INTELLIGENCE_WH 
SET WAREHOUSE_SIZE = 'MEDIUM'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 3
    SCALING_POLICY = 'STANDARD';
```

**Cost**: ~$100-300/month

---

### Monitor Usage

#### Query History

```sql
SELECT 
    query_text,
    user_name,
    start_time,
    execution_status,
    total_elapsed_time / 1000 as seconds,
    bytes_scanned
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE query_text ILIKE '%RCM_Healthcare_Agent%'
ORDER BY start_time DESC
LIMIT 100;
```

#### Warehouse Costs

```sql
SELECT 
    warehouse_name,
    SUM(credits_used) as total_credits,
    SUM(credits_used_compute) as compute_credits,
    SUM(credits_used_cloud_services) as cloud_services_credits
FROM TABLE(INFORMATION_SCHEMA.WAREHOUSE_METERING_HISTORY(
    DATE_RANGE_START => DATEADD(day, -30, CURRENT_DATE())
))
WHERE warehouse_name = 'RCM_INTELLIGENCE_WH'
GROUP BY warehouse_name;
```

#### User Activity

```sql
SELECT 
    user_name,
    COUNT(*) as query_count,
    AVG(total_elapsed_time) / 1000 as avg_seconds,
    MAX(start_time) as last_access
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE query_text ILIKE '%RCM_INTELLIGENCE_HUB%'
  AND start_time >= DATEADD(day, -7, CURRENT_DATE())
GROUP BY user_name
ORDER BY query_count DESC;
```

---

## Updating the Deployment

### Update Streamlit App Code

**In Snowsight**:

1. Navigate to **Projects** → **Streamlit**
2. Click on `RCM_INTELLIGENCE_HUB`
3. Edit the code in the editor
4. Click **Run** to apply changes

**Changes are live immediately!**

### Update Agent Configuration

```sql
-- Method 1: Alter existing agent
ALTER AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod
SET /* new configuration */;

-- Method 2: Drop and recreate
DROP AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod;
-- Then copy/paste and re-run 07_rcm_native_agent_production.sql
```

### Update RCM UDFs

1. Open `sql_scripts/07_rcm_native_agent_production.sql`
2. Edit the UDF code (e.g., add new terminology)
3. Copy the `CREATE OR REPLACE FUNCTION` statement
4. Paste into a SQL worksheet in Snowsight
5. Run the statement

**UDF updates are immediate!**

---

## Troubleshooting

### SQL Setup Issues

#### Agent not found

**Symptom**: App shows error "Agent not found"

**Solution**:
```sql
-- Verify agent exists
SHOW AGENTS IN SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS;

-- If missing, re-run:
-- Copy/paste sql_scripts/07_rcm_native_agent_production.sql
-- Run All in Snowsight
```

#### UDF not found

**Symptom**: App shows error about missing function

**Solution**:
```sql
-- Verify UDFs exist
SHOW FUNCTIONS LIKE 'ENHANCE%' IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;

-- If missing, re-run:
-- Copy/paste sql_scripts/07_rcm_native_agent_production.sql
-- Run All in Snowsight
```

#### Warehouse suspended

**Symptom**: App shows "Warehouse is suspended"

**Solution**:
```sql
-- Resume warehouse
ALTER WAREHOUSE RCM_INTELLIGENCE_WH RESUME;

-- Enable auto-resume (should already be set)
ALTER WAREHOUSE RCM_INTELLIGENCE_WH SET AUTO_RESUME = TRUE;
```

---

### Streamlit App Issues

#### App won't start

**Symptom**: Clicking "Run" does nothing or shows errors

**Solutions**:

1. **Check warehouse**:
   ```sql
   SHOW WAREHOUSES LIKE 'RCM_INTELLIGENCE_WH';
   -- Verify STATE = 'STARTED' or 'SUSPENDED' (will auto-resume)
   ```

2. **Verify app location**:
   - Database: `RCM_AI_DEMO`
   - Schema: `RCM_SCHEMA`
   - Warehouse: `RCM_INTELLIGENCE_WH`

3. **Check for syntax errors** in code editor (red underlines)

4. **Restart app**: Click **Stop** → **Run** in Snowsight

#### Import errors

**Symptom**: `ModuleNotFoundError` or `ImportError`

**Solutions**:

Most packages are pre-installed. If needed:

1. Click **Packages** in left sidebar
2. Add missing package name
3. Click **Run** again

**Common packages** (usually pre-installed):
- `snowflake-snowpark-python`
- `streamlit`
- `pandas`

#### Permission errors

**Symptom**: "Insufficient privileges" or "Access denied"

**Solution**:
```sql
-- Grant app access to your role
GRANT USAGE ON STREAMLIT RCM_AI_DEMO.RCM_SCHEMA.RCM_INTELLIGENCE_HUB 
  TO ROLE YOUR_ROLE;

-- Grant agent access
GRANT USAGE ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod 
  TO ROLE YOUR_ROLE;

-- Grant database/schema access
GRANT USAGE ON DATABASE RCM_AI_DEMO TO ROLE YOUR_ROLE;
GRANT USAGE ON SCHEMA RCM_AI_DEMO.RCM_SCHEMA TO ROLE YOUR_ROLE;

-- Assign role to yourself
USE ROLE YOUR_ROLE;
```

#### Agent not responding

**Symptom**: App hangs or shows "Agent error"

**Solutions**:

1. **Verify agent exists**:
   ```sql
   SHOW AGENTS IN SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS;
   ```

2. **Check agent name** in `streamlit_app.py`:
   - Should be: `RCM_Healthcare_Agent_Prod`
   - In schema: `SNOWFLAKE_INTELLIGENCE.AGENTS`

3. **Verify agent grants**:
   ```sql
   SHOW GRANTS ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod;
   ```

4. **Test agent directly**:
   ```sql
   SELECT SNOWFLAKE.CORTEX.COMPLETE(
       'RCM_Healthcare_Agent_Prod',
       [{'role': 'user', 'content': 'Hello'}]
   ) as response;
   ```

---

## Production Checklist

Before going live:

- [ ] All SQL scripts (01-07) executed successfully
- [ ] Production agent created and verified
- [ ] RCM UDFs tested and working
- [ ] Streamlit app deployed in Snowsight
- [ ] App accessible and responding
- [ ] RBAC configured for all user roles
- [ ] Test queries validated:
  - [ ] Analytics query (clean claim rate)
  - [ ] Knowledge base query (Code 45 denial)
  - [ ] RCM terminology enhancement (remits)
- [ ] Debug panel tested
- [ ] Warehouse auto-suspend configured
- [ ] Monitoring queries documented
- [ ] User access grants completed
- [ ] App link shared with users
- [ ] User training completed
- [ ] Support process defined

---

## Snowsight Tips & Tricks

### Organize Your Worksheets

**Create folders**:
1. Right-click in Worksheets sidebar
2. Select "New Folder"
3. Name: `RCM Setup Scripts`
4. Drag worksheets into folder

### Save Verification Queries

Create a worksheet: `RCM Verification`

```sql
-- Quick health check
SHOW AGENTS IN SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS;
SHOW STREAMLITS IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;
SHOW WAREHOUSES LIKE 'RCM_INTELLIGENCE_WH';

-- Usage summary
SELECT 
    COUNT(*) as query_count,
    COUNT(DISTINCT user_name) as unique_users
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE query_text ILIKE '%RCM_Healthcare_Agent%'
  AND start_time >= CURRENT_DATE();
```

### Keyboard Shortcuts

- **Run All**: `Cmd/Ctrl + Enter`
- **Run Selection**: `Cmd/Ctrl + Shift + Enter`
- **Format SQL**: `Cmd/Ctrl + Shift + F`
- **Comment Line**: `Cmd/Ctrl + /`

---

## Cost Estimates

**Monthly Cost** (100 users, 10 queries/day):

```
Snowflake Compute (SMALL warehouse):  $80
Cortex AI (30,000 queries × $0.006):  $180
Storage (minimal):                    $10
─────────────────────────────────────────
TOTAL:                                $270/month
```

**Per-query cost**: ~$0.006  
**Per-user cost**: ~$2.70/month

**Compare to external hosting**: ~$500/month  
**Savings**: 46% ($230/month = $2,760/year)

---

## Support Resources

### Snowflake Documentation

- [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)
- [Cortex Search](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/cortex-search-overview)
- [Snowsight Overview](https://docs.snowflake.com/en/user-guide/ui-snowsight)

### Project Documentation

- [QUICKSTART.md](QUICKSTART.md) - 30-minute rapid setup
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical deep dive
- [RCM_15_Minute_Demo_Story.md](RCM_15_Minute_Demo_Story.md) - Demo script

---

## Success!

Your RCM Intelligence Hub is now production-ready in Snowflake with:

✅ **Native Cortex Agent orchestration**  
✅ **RCM domain intelligence** (50+ terms)  
✅ **Zero data movement** (HIPAA compliant)  
✅ **Snowsight-managed** (no CLI needed)  
✅ **Auto-scaling compute**  
✅ **46% cost savings** vs external hosting

**Start querying with natural language - all in Snowsight!** 🎉

---

**Last Updated**: December 2024  
**Deployment Method**: 100% Snowsight (Web UI)
