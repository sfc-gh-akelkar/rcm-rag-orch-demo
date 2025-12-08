# RCM Intelligence Hub - Deployment Guide

**Complete deployment instructions for both External and SiS approaches**

---

## Quick Navigation

- [Prerequisites](#prerequisites)
- [Option 1: External Streamlit (Demo/POC)](#option-1-external-streamlit-demopoc)
- [Option 2: Streamlit in Snowflake (Production)](#option-2-streamlit-in-snowflake-production-) 🎯
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### For Both Approaches

✅ **Snowflake Account**:
- Cortex enabled
- ACCOUNTADMIN or equivalent privileges
- Database `RCM_AI_DEMO` created
- Warehouse `RCM_INTELLIGENCE_WH` running

✅ **Base Setup Complete**:
Execute these SQL scripts first (in order):
```sql
-- 1. Infrastructure
sql_scripts/01_rcm_data_setup.sql

-- 2. Documents
sql_scripts/02_rcm_documents_setup.sql

-- 3. Sample data
sql_scripts/03_rcm_data_generation.sql

-- 4. Semantic views
sql_scripts/04_rcm_semantic_views.sql

-- 5. Search services
sql_scripts/05_rcm_cortex_search.sql

-- 6. Basic agent (optional)
sql_scripts/06_rcm_agent_setup.sql
```

✅ **Local Environment**:
- Python 3.9+
- Git installed

---

## Option 1: External Streamlit (Demo/POC)

**Use For**: Technical demos, development, showcasing custom orchestration

**Deployment Time**: ~5 minutes

### Step 1: Install Dependencies

```bash
cd RCM_RAG_ORCH_DEMO

# Install Python packages
pip install -r requirements.txt
```

**Expected packages**:
- streamlit
- snowflake-connector-python  
- snowflake-snowpark-python
- tiktoken

### Step 2: Configure Credentials

```bash
# Copy example secrets file
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit with your credentials
nano .streamlit/secrets.toml
```

**Edit** `.streamlit/secrets.toml`:
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

### Step 3: Run the Application

```bash
# Start Streamlit
streamlit run app.py
```

**Expected output**:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

App will auto-open in your browser!

### Step 4: Test the Demo

**Test Queries**:

1. **Analytics**: `What is the clean claim rate by provider?`
   → Should show metrics and calculations

2. **Knowledge Base**: `How do I resolve a Code 45 denial?`
   → Should search documents and cite sources

3. **RCM Terminology**: `Show me remits for Anthem`
   → Should enhance "remits" to "remittance advice (ERA)"

### External Deployment - Features

- ✅ Custom orchestrator with full transparency
- ✅ Debug panel showing routing decisions
- ✅ Token/cost tracking per query
- ✅ RCM terminology enhancement
- ✅ Easy local development and debugging

### External Deployment - Limitations

- ❌ Data crosses Snowflake boundary (security concern)
- ❌ Requires external hosting for production
- ❌ Manual credential management
- ❌ $150/mo hosting costs (plus Snowflake)

---

## Option 2: Streamlit in Snowflake (Production) 🎯

**Use For**: Quadax production, enterprise deployment, HIPAA compliance

**Deployment Time**: ~30 minutes

### Step 1: Install Snowflake CLI

```bash
# Install Snowflake CLI
pip install snowflake-cli-labs

# Verify installation
snow --version
```

### Step 2: Configure Snowflake Connection

```bash
# Add connection
snow connection add

# Follow prompts:
# - Connection name: rcm_demo (or your choice)
# - Account: your_account (orgname-accountname format)
# - User: your_user
# - Password: [enter securely]
# - Role: SF_INTELLIGENCE_DEMO (or ACCOUNTADMIN)
# - Warehouse: RCM_INTELLIGENCE_WH
# - Database: RCM_AI_DEMO
# - Schema: RCM_SCHEMA

# Test connection
snow connection test --connection rcm_demo
```

**Expected**: `Connection test successful!`

### Step 3: Create Production Agent & UDFs

**In Snowflake (Snowsight or worksheet)**:

```sql
-- Execute production agent setup
-- This creates:
-- - RCM terminology UDFs (ENHANCE_RCM_QUERY, etc.)
-- - Cost tracking functions (ESTIMATE_TOKENS, etc.)
-- - Native Cortex Agent (RCM_Healthcare_Agent_Prod)

-- File: sql_scripts/07_rcm_native_agent_production.sql
-- (Copy and execute the entire file)
```

**Verify agent created**:
```sql
-- Check agent exists
SHOW AGENTS IN SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS;

-- Should see: RCM_Healthcare_Agent_Prod

-- Check UDFs created
SHOW FUNCTIONS LIKE 'ENHANCE%' IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;
```

### Step 4: Deploy to Snowflake

#### Option A: Automated Script (Recommended)

```bash
# Make script executable (if not already)
chmod +x deploy_to_snowflake.sh

# Run deployment
./deploy_to_snowflake.sh
```

**The script will**:
1. Check prerequisites
2. Verify Snowflake connection
3. Confirm SQL setup complete
4. Deploy Streamlit app to Snowflake
5. Open app in browser

#### Option B: Manual Deployment

```bash
# Deploy using Snowflake CLI
snow streamlit deploy \
  --connection rcm_demo \
  --replace \
  --open
```

**Flags**:
- `--connection`: Connection name from Step 2
- `--replace`: Replace existing app if it exists
- `--open`: Auto-open in browser after deployment

### Step 5: Verify Deployment

**In Snowsight**:
1. Navigate to: **Projects** → **Streamlit**
2. Find: `rcm_intelligence_hub`
3. Click to open

**In SQL**:
```sql
-- Show deployed apps
SHOW STREAMLITS IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;

-- Should see: rcm_intelligence_hub
```

### Step 6: Test Production Deployment

**Test Queries** (same as external):

1. **Analytics**: `What is the clean claim rate by provider?`
2. **Knowledge Base**: `How do I resolve a Code 45 denial?`
3. **Terminology**: `Show me remits for Anthem`

**Enable Debug Panel**:
- Sidebar → Check "Show Debug/Agent Info"
- Shows: Agent reasoning, token usage, cost estimates

### SiS Deployment - Features

- ✅ Zero data movement (HIPAA compliant)
- ✅ Native Cortex Agent orchestration
- ✅ 50% cost reduction vs external
- ✅ Auto-scaling compute
- ✅ Snowflake RBAC (no credential management)
- ✅ Native audit trail
- ✅ Production-ready

### SiS Deployment - Limitations

- ⚠️ Requires Snowflake CLI knowledge
- ⚠️ Debugging more difficult than local
- ⚠️ Must execute SQL setup first

---

## Post-Deployment

### Configure User Access

**Grant access to roles**:
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
```

### Optimize Warehouse

**For development/demos**:
```sql
ALTER WAREHOUSE RCM_INTELLIGENCE_WH 
SET WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60     -- 1 minute
    AUTO_RESUME = TRUE;
```

**For production (concurrent users)**:
```sql
ALTER WAREHOUSE RCM_INTELLIGENCE_WH 
SET WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND = 300    -- 5 minutes
    AUTO_RESUME = TRUE;
```

### Monitor Usage

**Query history** (both approaches):
```sql
SELECT 
    query_text,
    user_name,
    start_time,
    total_elapsed_time / 1000 as seconds,
    bytes_scanned
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE query_text LIKE '%RCM%'
ORDER BY start_time DESC
LIMIT 100;
```

**Warehouse costs**:
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

## Troubleshooting

### Common Issues - External Deployment

#### Issue: "Cannot connect to Snowflake"

**Check**:
```bash
# Verify secrets file exists
ls .streamlit/secrets.toml

# Check credentials
cat .streamlit/secrets.toml
```

**Fix**:
- Ensure account format is `orgname-accountname`
- Test credentials in Snowsight first
- Check role has permissions on database

#### Issue: "Module not found"

**Fix**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

#### Issue: "Agent/Search service not found"

**Fix**:
```sql
-- Verify setup scripts executed
SHOW CORTEX SEARCH SERVICES IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;
SHOW SEMANTIC VIEWS IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;

-- Re-run if needed:
-- 04_rcm_semantic_views.sql
-- 05_rcm_cortex_search.sql
```

---

### Common Issues - SiS Deployment

#### Issue: "Snowflake CLI not found"

**Fix**:
```bash
pip install snowflake-cli-labs

# If still fails, try:
python -m pip install snowflake-cli-labs
```

#### Issue: "Connection test failed"

**Fix**:
```bash
# List connections
snow connection list

# Test specific connection
snow connection test --connection rcm_demo

# If fails, delete and recreate:
snow connection remove --connection rcm_demo
snow connection add
```

#### Issue: "Agent not found during deployment"

**Fix**:
```sql
-- Verify agent exists
SHOW AGENTS IN SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS;

-- If missing, re-run:
-- sql_scripts/07_rcm_native_agent_production.sql

-- Check permissions
GRANT USAGE ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod 
  TO ROLE SF_INTELLIGENCE_DEMO;
```

#### Issue: "Streamlit app won't start"

**Fix**:
```bash
# Check app status
snow streamlit describe rcm_intelligence_hub \
  --connection rcm_demo

# View logs
snow streamlit logs rcm_intelligence_hub \
  --connection rcm_demo \
  --tail

# Redeploy
snow streamlit deploy --replace --connection rcm_demo
```

#### Issue: "Warehouse suspended"

**Fix**:
```sql
-- Resume warehouse
ALTER WAREHOUSE RCM_INTELLIGENCE_WH RESUME;

-- Enable auto-resume
ALTER WAREHOUSE RCM_INTELLIGENCE_WH SET AUTO_RESUME = TRUE;
```

---

## Updating Deployments

### Update External Deployment

```bash
# 1. Make code changes
# Edit app.py, orchestrator.py, etc.

# 2. Test locally
streamlit run app.py

# 3. Commit changes
git add .
git commit -m "Update external app"

# 4. App automatically reloads (local dev)
# For production: Redeploy to hosting provider
```

### Update SiS Deployment

**Update Streamlit app**:
```bash
# 1. Edit streamlit_app.py

# 2. Redeploy
snow streamlit deploy --replace --connection rcm_demo

# App updates immediately
```

**Update agent configuration**:
```sql
-- Modify agent instructions or tools
ALTER AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod
SET <new configuration>;

-- Or drop and recreate:
DROP AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod;
-- Then re-run 07_rcm_native_agent_production.sql
```

**Update RCM UDFs**:
```sql
-- Edit and re-execute the CREATE OR REPLACE FUNCTION statements
-- in 07_rcm_native_agent_production.sql
```

---

## Production Checklist

### Before Going Live with Quadax

- [ ] All 7 SQL setup scripts executed successfully
- [ ] Native Cortex Agent created and tested
- [ ] RCM terminology UDFs working correctly
- [ ] Streamlit app deployed and accessible
- [ ] RBAC configured for Quadax users
- [ ] Test queries validated (analytics, KB, terminology)
- [ ] Debug panel tested (if needed for demos)
- [ ] Warehouse auto-suspend configured
- [ ] Monitoring queries documented
- [ ] User training materials prepared
- [ ] Support process defined
- [ ] Backup/rollback plan documented

---

## Quick Reference

### External Deployment Commands

```bash
# Install
pip install -r requirements.txt

# Configure
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Run
streamlit run app.py
```

### SiS Deployment Commands

```bash
# Install CLI
pip install snowflake-cli-labs

# Configure connection
snow connection add

# Deploy (automated)
./deploy_to_snowflake.sh

# Or deploy manually
snow streamlit deploy --replace --open --connection rcm_demo

# Get app URL
snow streamlit get-url rcm_intelligence_hub --connection rcm_demo

# View logs
snow streamlit logs rcm_intelligence_hub --connection rcm_demo

# Delete app
snow streamlit drop rcm_intelligence_hub --connection rcm_demo
```

---

## Cost Estimates

### External Deployment

```
Monthly cost (100 users, 10 queries/day):
- Snowflake compute:     $200
- External hosting (AWS): $150
- Data transfer:         $50
─────────────────────────────
TOTAL:                   $400/month
```

### SiS Deployment

```
Monthly cost (100 users, 10 queries/day):
- Snowflake compute:     $200
- Hosting:               $0 (included)
- Data transfer:         $0 (internal)
─────────────────────────────
TOTAL:                   $200/month

SAVINGS:                 $200/month (50%)
Annual savings:          $2,400/year
```

---

## Support Resources

### Snowflake Documentation
- [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)
- [Snowflake CLI](https://docs.snowflake.com/en/developer-guide/snowflake-cli)

### Project Documentation
- `README.md` - Project overview
- `ARCHITECTURE.md` - Technical details
- `QUICKSTART.md` - 5-minute quick start

### Demo Materials
- `RCM_15_Minute_Demo_Story.md` - Demo script and talking points

---

## Summary

### Choose External Deployment If:
- ✅ Building POC or demo
- ✅ Need full control over orchestration
- ✅ Want to showcase custom code
- ✅ Deploying outside Snowflake ecosystem

### Choose SiS Deployment If: 🎯
- ✅ **Deploying to Quadax production**
- ✅ Healthcare/RCM (HIPAA requirements)
- ✅ Want 50% cost savings
- ✅ Need enterprise security
- ✅ Prefer zero infrastructure management

**Both approaches are fully functional and documented. Choose based on your use case!**

---

**Last Updated**: December 2024

