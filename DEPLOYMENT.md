# RCM Intelligence Hub - Deployment Guide

**Complete deployment instructions for Streamlit in Snowflake**

---

## Overview

This guide covers deploying the RCM Intelligence Hub as a **Streamlit in Snowflake (SiS)** application with **Native Cortex Agent** orchestration.

**Deployment Time**: ~30 minutes  
**Result**: Production-ready, HIPAA-compliant RCM AI in Snowflake

---

## Prerequisites

### Snowflake Account

✅ **Required**:
- Cortex enabled
- ACCOUNTADMIN or equivalent privileges
- Access to create databases, warehouses, and agents

### Local Environment

✅ **Required**:
- Python 3.9+
- Snowflake CLI installed
- Git (for cloning repo)

---

## Step-by-Step Deployment

### Step 1: Install Snowflake CLI

```bash
# Install
pip install snowflake-cli-labs

# Verify
snow --version
```

### Step 2: Configure Connection

```bash
# Add connection
snow connection add

# Prompts:
# - Connection name: rcm_demo
# - Account: your_account (orgname-accountname format)
# - User: your_user
# - Password: [secure entry]
# - Role: SF_INTELLIGENCE_DEMO (or ACCOUNTADMIN)
# - Warehouse: RCM_INTELLIGENCE_WH
# - Database: RCM_AI_DEMO
# - Schema: RCM_SCHEMA

# Test
snow connection test --connection rcm_demo
```

###Step 3: Execute SQL Setup Scripts

Run in Snowflake (Snowsight or worksheet) in order:

```sql
-- 1. Infrastructure (database, schema, warehouse, role)
sql_scripts/01_rcm_data_setup.sql

-- 2. Load RCM documents into database
sql_scripts/02_rcm_documents_setup.sql

-- 3. Generate synthetic RCM data (50k+ records)
sql_scripts/03_rcm_data_generation.sql

-- 4. Create semantic views for Cortex Analyst
sql_scripts/04_rcm_semantic_views.sql

-- 5. Create Cortex Search services
sql_scripts/05_rcm_cortex_search.sql

-- 6. Basic agent (optional reference)
sql_scripts/06_rcm_agent_setup.sql

-- 7. Production agent + RCM UDFs ← CRITICAL
sql_scripts/07_rcm_native_agent_production.sql
```

**Verify Setup**:
```sql
-- Check database & schema
SHOW DATABASES LIKE 'RCM_AI_DEMO';
SHOW SCHEMAS IN DATABASE RCM_AI_DEMO;

-- Check tables
SHOW TABLES IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;

-- Check semantic views
SHOW SEMANTIC VIEWS IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;

-- Check search services
SHOW CORTEX SEARCH SERVICES IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;

-- Check production agent
SHOW AGENTS IN SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS;

-- Should see: RCM_Healthcare_Agent_Prod
```

### Step 4: Deploy Streamlit App

#### Option A: Automated Script

```bash
# Navigate to project directory
cd RCM_RAG_ORCH_DEMO

# Make executable
chmod +x deploy_to_snowflake.sh

# Deploy
./deploy_to_snowflake.sh
```

The script will:
1. Check prerequisites
2. Verify Snowflake connection
3. Confirm SQL setup complete
4. Deploy Streamlit app
5. Open in browser

#### Option B: Manual Deployment

```bash
snow streamlit deploy \
  --connection rcm_demo \
  --replace \
  --open
```

**Expected Output**:
```
Uploading files to stage...
Creating Streamlit object...
✅ Streamlit app 'rcm_intelligence_hub' deployed successfully!
🌐 Opening app in browser...
```

### Step 5: Verify Deployment

**In Snowsight**:
- Navigate: **Projects** → **Streamlit**
- Find: `rcm_intelligence_hub`
- Click to open

**In SQL**:
```sql
-- Show deployed apps
SHOW STREAMLITS IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;

-- Get app URL
SELECT SYSTEM$GET_STREAMLIT_URL('RCM_AI_DEMO.RCM_SCHEMA.RCM_INTELLIGENCE_HUB');
```

### Step 6: Test the Application

**Test Analytics Query**:
```
What is the clean claim rate by provider?
```
→ Should route to Cortex Analyst, show metrics

**Test Knowledge Base Query**:
```
How do I resolve a Code 45 denial in ServiceNow?
```
→ Should route to Cortex Search, cite documents

**Test RCM Terminology**:
```
Show me remits for Anthem
```
→ Should enhance "remits" to "remittance advice (ERA)"

**Enable Debug Panel**:
- Sidebar → Check "Show Debug/Agent Info"
- Shows: Agent reasoning, token counts, cost estimates

---

## Post-Deployment Configuration

### Configure User Access

```sql
-- Grant to specific role
GRANT USAGE ON STREAMLIT RCM_AI_DEMO.RCM_SCHEMA.rcm_intelligence_hub 
  TO ROLE BUSINESS_ANALYST;

-- Grant to all authenticated users
GRANT USAGE ON STREAMLIT RCM_AI_DEMO.RCM_SCHEMA.rcm_intelligence_hub 
  TO ROLE PUBLIC;

-- Grant agent access
GRANT USAGE ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod 
  TO ROLE BUSINESS_ANALYST;

-- Grant UDF access
GRANT USAGE ON FUNCTION RCM_AI_DEMO.RCM_SCHEMA.ENHANCE_RCM_QUERY(STRING) 
  TO ROLE BUSINESS_ANALYST;
```

### Optimize Warehouse

**For Development/Demos**:
```sql
ALTER WAREHOUSE RCM_INTELLIGENCE_WH 
SET WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60     -- 1 minute
    AUTO_RESUME = TRUE;
```

**For Production (Concurrent Users)**:
```sql
ALTER WAREHOUSE RCM_INTELLIGENCE_WH 
SET WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND = 300    -- 5 minutes
    AUTO_RESUME = TRUE;
```

### Monitor Usage

**Query History**:
```sql
SELECT 
    query_text,
    user_name,
    start_time,
    total_elapsed_time / 1000 as seconds,
    bytes_scanned
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE query_text LIKE '%RCM_Healthcare_Agent%'
ORDER BY start_time DESC
LIMIT 100;
```

**Warehouse Costs**:
```sql
SELECT 
    warehouse_name,
    SUM(credits_used) as total_credits,
    SUM(credits_used_compute) as compute_credits
FROM TABLE(INFORMATION_SCHEMA.WAREHOUSE_METERING_HISTORY(
    DATE_RANGE_START => DATEADD(day, -7, CURRENT_DATE())
))
WHERE warehouse_name = 'RCM_INTELLIGENCE_WH'
GROUP BY warehouse_name;
```

---

## Updating the Deployment

### Update Streamlit App

```bash
# Edit streamlit_app.py
# Then redeploy
snow streamlit deploy --replace --connection rcm_demo
```

### Update Agent Configuration

```sql
-- Method 1: Alter agent
ALTER AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod
SET /* new configuration */;

-- Method 2: Drop and recreate
DROP AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod;
-- Then re-run 07_rcm_native_agent_production.sql
```

### Update RCM UDFs

```sql
-- Edit and re-execute CREATE OR REPLACE FUNCTION statements
-- in 07_rcm_native_agent_production.sql

-- Example: Update ENHANCE_RCM_QUERY
CREATE OR REPLACE FUNCTION ENHANCE_RCM_QUERY(...)
AS $$
    # Updated logic here
$$;
```

---

## Troubleshooting

### CLI Issues

**CLI not found**:
```bash
pip install snowflake-cli-labs --upgrade
python -m pip install snowflake-cli-labs  # If above fails
```

**Connection test failed**:
```bash
# List connections
snow connection list

# Remove and recreate
snow connection remove --connection rcm_demo
snow connection add
```

### SQL Setup Issues

**Agent not found**:
```sql
-- Verify agent exists
SHOW AGENTS IN SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS;

-- If missing, re-run
-- sql_scripts/07_rcm_native_agent_production.sql

-- Check permissions
GRANT USAGE ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod 
  TO ROLE SF_INTELLIGENCE_DEMO;
```

**UDF not found**:
```sql
-- Verify UDFs exist
SHOW FUNCTIONS LIKE 'ENHANCE%' IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;

-- Grant permissions
GRANT USAGE ON FUNCTION RCM_AI_DEMO.RCM_SCHEMA.GET_ENHANCED_QUERY(STRING) 
  TO ROLE SF_INTELLIGENCE_DEMO;
```

**Warehouse suspended**:
```sql
-- Resume warehouse
ALTER WAREHOUSE RCM_INTELLIGENCE_WH RESUME;

-- Enable auto-resume
ALTER WAREHOUSE RCM_INTELLIGENCE_WH SET AUTO_RESUME = TRUE;
```

### Streamlit App Issues

**App won't start**:
```bash
# Check app status
snow streamlit describe rcm_intelligence_hub --connection rcm_demo

# View logs
snow streamlit logs rcm_intelligence_hub --connection rcm_demo --tail

# Redeploy
snow streamlit deploy --replace --connection rcm_demo
```

**App shows errors**:
```bash
# View detailed logs
snow streamlit logs rcm_intelligence_hub --connection rcm_demo

# Check Snowflake query history for errors
```

**Can't access app**:
```sql
-- Verify app exists
SHOW STREAMLITS IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;

-- Check permissions
SHOW GRANTS ON STREAMLIT RCM_AI_DEMO.RCM_SCHEMA.rcm_intelligence_hub;

-- Grant access
GRANT USAGE ON STREAMLIT RCM_AI_DEMO.RCM_SCHEMA.rcm_intelligence_hub 
  TO ROLE YOUR_ROLE;
```

---

## Production Checklist

Before going live:

- [ ] All SQL scripts (01-07) executed successfully
- [ ] Production agent created and tested
- [ ] RCM UDFs working correctly
- [ ] Streamlit app deployed and accessible
- [ ] RBAC configured for all users
- [ ] Test queries validated (analytics, KB, terminology)
- [ ] Debug panel tested
- [ ] Warehouse auto-suspend configured
- [ ] Monitoring queries documented
- [ ] User training completed
- [ ] Support process defined

---

## Quick Command Reference

```bash
# Deploy app
snow streamlit deploy --replace --open --connection rcm_demo

# Get app URL
snow streamlit get-url rcm_intelligence_hub --connection rcm_demo

# View logs
snow streamlit logs rcm_intelligence_hub --connection rcm_demo

# Describe app
snow streamlit describe rcm_intelligence_hub --connection rcm_demo

# Delete app
snow streamlit drop rcm_intelligence_hub --connection rcm_demo
```

---

## Cost Estimates

**Monthly Cost** (100 users, 10 queries/day):
```
Snowflake compute:     $200
Hosting:               $0 (included)
Data transfer:         $0 (internal)
─────────────────────────────
TOTAL:                 $200/month
```

**Compare to External Hosting**: ~$400/month  
**Savings**: 50% ($200/month = $2,400/year)

---

## Support Resources

### Snowflake Documentation
- [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)
- [Snowflake CLI](https://docs.snowflake.com/en/developer-guide/snowflake-cli)

### Project Documentation
- [QUICKSTART.md](QUICKSTART.md) - 30-minute setup
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
- [RCM_15_Minute_Demo_Story.md](RCM_15_Minute_Demo_Story.md) - Demo script

---

## Success!

Your RCM Intelligence Hub is now production-ready in Snowflake with:
- ✅ Native Cortex Agent orchestration
- ✅ RCM domain intelligence
- ✅ Zero data movement (HIPAA compliant)
- ✅ Auto-scaling compute
- ✅ 50% cost savings

**Start querying with natural language!** 🎉

---

**Last Updated**: December 2024
