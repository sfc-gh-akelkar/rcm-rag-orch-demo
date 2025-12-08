# 🚀 Deployment Guide: Streamlit in Snowflake (SiS)

## Overview

This guide walks through deploying the RCM Intelligence Hub to **Streamlit in Snowflake (SiS)** with **Native Cortex Agent** orchestration.

**Architecture**: Production-ready deployment with all compute and data inside Snowflake.

---

## 📋 Prerequisites

### 1. Snowflake Account Requirements
- ✅ Snowflake account with Cortex enabled
- ✅ ACCOUNTADMIN or equivalent privileges
- ✅ Database `RCM_AI_DEMO` created
- ✅ Warehouse `RCM_INTELLIGENCE_WH` running
- ✅ Role `SF_INTELLIGENCE_DEMO` with proper permissions

### 2. Local Development Environment
- ✅ Python 3.9+ installed
- ✅ Snowflake CLI installed
- ✅ Git installed (for version control)

### 3. Completed Setup Scripts (1-6)
All base RCM demo scripts must be executed first:
- ✅ `01_rcm_data_setup.sql`
- ✅ `02_rcm_documents_setup.sql`
- ✅ `03_rcm_data_generation.sql`
- ✅ `04_rcm_semantic_views.sql`
- ✅ `05_rcm_cortex_search.sql`
- ✅ `06_rcm_agent_setup.sql`

---

## 🔧 Step-by-Step Deployment

### Step 1: Install Snowflake CLI

```bash
# Install Snowflake CLI
pip install snowflake-cli-labs

# Verify installation
snow --version
```

**Expected output**: `snowflake-cli version X.X.X`

### Step 2: Configure Snowflake Connection

```bash
# Add connection configuration
snow connection add

# Follow prompts:
# Connection name: rcm_demo
# Account: your_account (format: orgname-accountname)
# User: your_user
# Password: [enter securely]
# Role: SF_INTELLIGENCE_DEMO (or ACCOUNTADMIN)
# Warehouse: RCM_INTELLIGENCE_WH
# Database: RCM_AI_DEMO
# Schema: RCM_SCHEMA
```

**Verify connection**:
```bash
snow connection test --connection rcm_demo
```

### Step 3: Execute Native Agent Setup SQL

```bash
# In Snowflake, execute the production agent setup
# This creates:
# - RCM terminology UDFs
# - Cost tracking functions
# - Native Cortex Agent with orchestration
```

**Run in Snowflake Worksheet**:
```sql
-- Execute the production agent setup
-- File: sql_scripts/07_rcm_native_agent_production.sql
```

**Verify agent created**:
```sql
SHOW AGENTS IN SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS;

-- Should see: RCM_Healthcare_Agent_Prod
```

### Step 4: Deploy Streamlit App to Snowflake

```bash
# Navigate to project directory
cd /path/to/RCM_RAG_ORCH_DEMO

# Deploy the app using Snowflake CLI
snow streamlit deploy \
  --connection rcm_demo \
  --replace \
  --open

# Flags explained:
# --replace: Replace existing app if it exists
# --open: Open app in browser after deployment
```

**What This Does**:
1. Uploads `streamlit_app.py` to Snowflake stage
2. Creates Streamlit object in Snowflake
3. Configures warehouse and permissions
4. Opens app in your browser

**Expected output**:
```
Uploading files to stage...
Creating Streamlit object...
✅ Streamlit app 'rcm_intelligence_hub' deployed successfully!
🌐 Opening app in browser...
```

### Step 5: Verify Deployment

**In Snowflake (Snowsight)**:
1. Navigate to: **Projects** → **Streamlit**
2. Find: `rcm_intelligence_hub`
3. Click to open the app

**In SQL**:
```sql
-- Show deployed Streamlit apps
SHOW STREAMLITS IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;

-- Verify agent is accessible
SELECT 
    'Agent Status' as check_type,
    COUNT(*) as count
FROM SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod;
```

### Step 6: Test the Application

**Test Queries**:

1. **Analytics Query**:
   ```
   What is the clean claim rate by provider?
   ```
   → Should route to Cortex Analyst

2. **Knowledge Base Query**:
   ```
   How do I resolve a Code 45 denial?
   ```
   → Should route to Cortex Search

3. **RCM Terminology**:
   ```
   Show me remits for Anthem
   ```
   → Should enhance with "remittance advice (ERA)" context

**Verify**:
- ✅ Responses are accurate
- ✅ Debug panel shows agent reasoning (if enabled)
- ✅ No errors in query history

---

## 🔐 Security & Permissions

### Grant App Access to Users

```sql
-- Grant usage to specific roles
GRANT USAGE ON STREAMLIT RCM_AI_DEMO.RCM_SCHEMA.rcm_intelligence_hub 
  TO ROLE BUSINESS_ANALYST;

-- Or grant to all authenticated users
GRANT USAGE ON STREAMLIT RCM_AI_DEMO.RCM_SCHEMA.rcm_intelligence_hub 
  TO ROLE PUBLIC;
```

### Verify RBAC

```sql
-- Check who can access the app
SHOW GRANTS ON STREAMLIT RCM_AI_DEMO.RCM_SCHEMA.rcm_intelligence_hub;

-- Check who can use the agent
SHOW GRANTS ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod;
```

---

## 📊 Monitoring & Maintenance

### Monitor App Usage

```sql
-- View Streamlit app query history
SELECT 
    query_text,
    user_name,
    start_time,
    execution_time,
    total_elapsed_time
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE query_text LIKE '%rcm_intelligence_hub%'
ORDER BY start_time DESC
LIMIT 100;
```

### Monitor Agent Performance

```sql
-- View agent interactions
-- (Adjust based on your logging setup)
SELECT 
    query_text,
    user_name,
    start_time,
    total_elapsed_time / 1000 as seconds
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE query_text LIKE '%RCM_Healthcare_Agent_Prod%'
ORDER BY start_time DESC
LIMIT 50;
```

### Update the App

When you make changes to `streamlit_app.py`:

```bash
# Redeploy with replace flag
snow streamlit deploy \
  --connection rcm_demo \
  --replace

# App will update automatically
```

---

## 🔄 Updating Components

### Update Agent Configuration

```sql
-- Modify agent instructions or tools
ALTER AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod
SET <new configuration>;
```

### Update RCM Terminology UDF

```sql
-- Modify the ENHANCE_RCM_QUERY function
-- in 07_rcm_native_agent_production.sql
-- Then re-execute the CREATE OR REPLACE statement
```

### Update Semantic Views

```sql
-- Modify semantic views in 04_rcm_semantic_views.sql
-- Then re-execute to update
```

---

## 🐛 Troubleshooting

### Issue: "Agent not found"

**Solution**:
```sql
-- Verify agent exists
SHOW AGENTS IN SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS;

-- Check permissions
SHOW GRANTS ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod;

-- Grant if needed
GRANT USAGE ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod 
  TO ROLE SF_INTELLIGENCE_DEMO;
```

### Issue: "Cannot access UDF"

**Solution**:
```sql
-- Verify UDFs exist
SHOW FUNCTIONS LIKE 'ENHANCE%' IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;

-- Grant permissions
GRANT USAGE ON FUNCTION RCM_AI_DEMO.RCM_SCHEMA.GET_ENHANCED_QUERY(STRING) 
  TO ROLE SF_INTELLIGENCE_DEMO;
```

### Issue: "Streamlit app won't start"

**Solution**:
```bash
# Check app status
snow streamlit describe rcm_intelligence_hub \
  --connection rcm_demo

# View app logs
snow streamlit logs rcm_intelligence_hub \
  --connection rcm_demo

# Redeploy
snow streamlit deploy --replace --connection rcm_demo
```

### Issue: "Warehouse suspended"

**Solution**:
```sql
-- Resume warehouse
ALTER WAREHOUSE RCM_INTELLIGENCE_WH RESUME;

-- Or set auto-resume
ALTER WAREHOUSE RCM_INTELLIGENCE_WH SET AUTO_RESUME = TRUE;
```

---

## 📈 Performance Optimization

### Optimize Warehouse Size

```sql
-- For light usage (demos, testing)
ALTER WAREHOUSE RCM_INTELLIGENCE_WH SET WAREHOUSE_SIZE = 'XSMALL';

-- For production (multiple concurrent users)
ALTER WAREHOUSE RCM_INTELLIGENCE_WH SET WAREHOUSE_SIZE = 'SMALL';

-- For high traffic
ALTER WAREHOUSE RCM_INTELLIGENCE_WH SET WAREHOUSE_SIZE = 'MEDIUM';
```

### Configure Auto-Suspend

```sql
-- Suspend after 1 minute of inactivity (cost optimization)
ALTER WAREHOUSE RCM_INTELLIGENCE_WH SET AUTO_SUSPEND = 60;

-- Suspend after 5 minutes (better UX, slightly higher cost)
ALTER WAREHOUSE RCM_INTELLIGENCE_WH SET AUTO_SUSPEND = 300;
```

### Monitor Costs

```sql
-- View warehouse credit usage
SELECT 
    warehouse_name,
    SUM(credits_used) as total_credits,
    SUM(credits_used_compute) as compute_credits,
    SUM(credits_used_cloud_services) as cloud_services_credits
FROM TABLE(INFORMATION_SCHEMA.WAREHOUSE_METERING_HISTORY(
    DATE_RANGE_START => DATEADD(day, -7, CURRENT_DATE()),
    DATE_RANGE_END => CURRENT_DATE()
))
WHERE warehouse_name = 'RCM_INTELLIGENCE_WH'
GROUP BY warehouse_name;
```

---

## 🚀 Production Checklist

Before going live with Quadax:

- [ ] All setup scripts (01-07) executed successfully
- [ ] Native Cortex Agent created and tested
- [ ] RCM terminology UDFs working correctly
- [ ] Streamlit app deployed to Snowflake
- [ ] RBAC configured for Quadax users
- [ ] Test queries validated (analytics, KB, terminology)
- [ ] Debug panel tested (if needed for demos)
- [ ] Warehouse auto-suspend configured
- [ ] Monitoring queries set up
- [ ] Backup/rollback plan documented
- [ ] User training materials prepared
- [ ] Support contact information shared

---

## 📞 Support & Resources

### Snowflake Documentation
- [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)
- [Snowflake CLI](https://docs.snowflake.com/en/developer-guide/snowflake-cli)

### Project Documentation
- `README_ORCHESTRATION.md` - Architecture overview
- `IMPLEMENTATION_EVALUATION.md` - Why we chose SiS
- `ARCHITECTURE.md` - Technical deep dive

### Quick Commands Reference

```bash
# Deploy app
snow streamlit deploy --replace --open --connection rcm_demo

# Get app URL
snow streamlit get-url rcm_intelligence_hub --connection rcm_demo

# View app logs
snow streamlit logs rcm_intelligence_hub --connection rcm_demo

# Delete app
snow streamlit drop rcm_intelligence_hub --connection rcm_demo
```

---

## 🎉 Success!

Your RCM Intelligence Hub is now running in **Streamlit in Snowflake** with:
- ✅ Native Cortex Agent orchestration
- ✅ RCM domain intelligence (UDFs)
- ✅ Zero data movement (HIPAA compliant)
- ✅ Auto-scaling compute
- ✅ 50% cost savings vs external hosting

**Next Steps**:
1. Share app URL with Quadax users
2. Monitor usage and performance
3. Collect feedback for improvements
4. Iterate on agent instructions as needed

**Questions?** Refer to troubleshooting section or Snowflake documentation.

