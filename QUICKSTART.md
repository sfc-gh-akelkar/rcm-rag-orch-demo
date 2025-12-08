# 🚀 Quick Start Guide - RCM Intelligence Hub

**Get your Snowflake-native RCM AI running in 30 minutes**

---

## Prerequisites ✅

- [ ] Snowflake account with Cortex enabled
- [ ] Python 3.9+ installed  
- [ ] Terminal/command line access

---

## Step 1: Install Snowflake CLI

```bash
# Install Snowflake CLI
pip install snowflake-cli-labs

# Verify installation
snow --version
```

**Expected**: `snowflake-cli version X.X.X`

---

## Step 2: Configure Snowflake Connection

```bash
# Add connection
snow connection add

# Follow prompts:
# - Connection name: rcm_demo (or your choice)
# - Account: your_account (orgname-accountname)
# - User: your_user
# - Password: [enter securely]
# - Role: SF_INTELLIGENCE_DEMO (or ACCOUNTADMIN)
# - Warehouse: RCM_INTELLIGENCE_WH
# - Database: RCM_AI_DEMO
# - Schema: RCM_SCHEMA

# Test connection
snow connection test --connection rcm_demo
```

**Expected**: `✅ Connection test successful!`

---

## Step 3: Execute SQL Setup

Run these scripts in Snowflake (in order):

```sql
-- 1. Infrastructure
sql_scripts/01_rcm_data_setup.sql

-- 2. Load documents
sql_scripts/02_rcm_documents_setup.sql

-- 3. Generate RCM data
sql_scripts/03_rcm_data_generation.sql

-- 4. Create semantic views
sql_scripts/04_rcm_semantic_views.sql

-- 5. Create search services
sql_scripts/05_rcm_cortex_search.sql

-- 6. Basic agent (optional)
sql_scripts/06_rcm_agent_setup.sql

-- 7. Production agent + RCM UDFs ← IMPORTANT
sql_scripts/07_rcm_native_agent_production.sql
```

**Verify**:
```sql
-- Check agent created
SHOW AGENTS IN SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS;
-- Should see: RCM_Healthcare_Agent_Prod

-- Check UDFs created
SHOW FUNCTIONS LIKE 'ENHANCE%' IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;
```

---

## Step 4: Deploy to Snowflake

### Option A: Automated (Recommended)

```bash
# Make script executable
chmod +x deploy_to_snowflake.sh

# Run deployment
./deploy_to_snowflake.sh
```

### Option B: Manual

```bash
# Deploy using Snowflake CLI
snow streamlit deploy \
  --connection rcm_demo \
  --replace \
  --open
```

**Expected**:
```
✅ Streamlit app 'rcm_intelligence_hub' deployed successfully!
🌐 Opening app in browser...
```

---

## Step 5: Test the App

**Access the app**:
- Snowsight → **Projects** → **Streamlit** → `rcm_intelligence_hub`
- Or use the URL that opened in your browser

**Test queries**:

1. **Analytics**: `What is the clean claim rate by provider?`
   → Should show metrics from Cortex Analyst

2. **Knowledge Base**: `How do I resolve a Code 45 denial?`
   → Should search documents and cite sources

3. **RCM Terminology**: `Show me remits for Anthem`
   → Should enhance "remits" to "remittance advice (ERA)"

---

## ✅ Verification Checklist

After deployment:

- [ ] App opens in Snowflake
- [ ] Test analytics query works
- [ ] Test knowledge base query works
- [ ] RCM terminology enhancement working
- [ ] Debug panel shows agent reasoning (enable in sidebar)
- [ ] No errors in Snowflake query history

---

## 🎉 Success!

Your RCM Intelligence Hub is now running in Snowflake with:
- ✅ Native Cortex Agent orchestration
- ✅ RCM domain intelligence (50+ terms)
- ✅ Zero data movement (HIPAA compliant)
- ✅ Auto-scaling compute

---

## Next Steps

### Enable Debug Mode
Sidebar → Check "Show Debug/Agent Info"
- See agent reasoning
- View token counts
- Track costs

### Grant User Access
```sql
GRANT USAGE ON STREAMLIT RCM_AI_DEMO.RCM_SCHEMA.rcm_intelligence_hub 
  TO ROLE BUSINESS_ANALYST;
```

### Customize RCM Terms
Edit `07_rcm_native_agent_production.sql` and redeploy UDFs

---

## 🐛 Troubleshooting

**CLI not found**:
```bash
pip install snowflake-cli-labs --upgrade
```

**Connection failed**:
```bash
snow connection test --connection rcm_demo
# If fails, remove and recreate:
snow connection remove --connection rcm_demo
snow connection add
```

**Agent not found**:
```sql
-- Re-run production agent setup
-- File: 07_rcm_native_agent_production.sql
```

**App won't start**:
```bash
# View logs
snow streamlit logs rcm_intelligence_hub --connection rcm_demo

# Redeploy
snow streamlit deploy --replace --connection rcm_demo
```

---

## 📚 Need More Help?

- **Full Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Technical Details**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Demo Script**: [RCM_15_Minute_Demo_Story.md](RCM_15_Minute_Demo_Story.md)

---

**You're all set! Start querying your RCM data with natural language.** 🎉
