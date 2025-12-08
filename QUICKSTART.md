# 🚀 Quick Start Guide - RCM Intelligence Hub

**Get your Snowflake-native RCM AI running in 30 minutes**

---

## Prerequisites ✅

- [ ] Snowflake account with Cortex enabled
- [ ] Access to Snowsight (web UI)
- [ ] Role with privileges to create databases, agents, and Streamlit apps

**No Python or CLI installation required!** Everything is done in Snowsight.

---

## Step 1: Execute SQL Setup

Log into **Snowsight** and run these scripts in order:

### Open a SQL Worksheet

1. Go to **Snowsight** → **Projects** → **Worksheets**
2. Click **+ Worksheet** (create new)
3. Run each script below in sequence

### Execute Scripts

```sql
-- 1. Infrastructure (database, schema, warehouse, role)
-- Copy/paste: sql_scripts/01_rcm_data_setup.sql
-- Run the entire script

-- 2. Load RCM documents into database
-- Copy/paste: sql_scripts/02_rcm_documents_setup.sql
-- Run the entire script

-- 3. Generate synthetic RCM data (50k+ records)
-- Copy/paste: sql_scripts/03_rcm_data_generation.sql
-- Run the entire script

-- 4. Create semantic views for Cortex Analyst
-- Copy/paste: sql_scripts/04_rcm_semantic_views.sql
-- Run the entire script

-- 5. Create Cortex Search services
-- Copy/paste: sql_scripts/05_rcm_cortex_search.sql
-- Run the entire script

-- 6. Basic agent (optional reference)
-- Copy/paste: sql_scripts/06_rcm_agent_setup.sql
-- Run the entire script

-- 7. Production agent + RCM UDFs ← CRITICAL
-- Copy/paste: sql_scripts/07_rcm_native_agent_production.sql
-- Run the entire script
```

### Verify Setup

Run in a SQL worksheet:

```sql
-- Check database & schema
SHOW DATABASES LIKE 'RCM_AI_DEMO';
SHOW SCHEMAS IN DATABASE RCM_AI_DEMO;

-- Check tables
SHOW TABLES IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;
-- Should see: 14 tables

-- Check semantic views
SHOW SEMANTIC VIEWS IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;
-- Should see: 2 views (CLAIMS_PROCESSING_VIEW, DENIALS_MANAGEMENT_VIEW)

-- Check search services
SHOW CORTEX SEARCH SERVICES IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;
-- Should see: 5 services

-- Check production agent
SHOW AGENTS IN SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS;
-- Should see: RCM_Healthcare_Agent_Prod

-- Check UDFs
SHOW FUNCTIONS LIKE 'ENHANCE%' IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;
-- Should see: ENHANCE_RCM_QUERY, GET_ENHANCED_QUERY, etc.
```

**✅ If all checks pass, you're ready for Step 2!**

---

## Step 2: Create Streamlit App in Snowsight

### Navigate to Streamlit

1. In **Snowsight**, go to **Projects** → **Streamlit**
2. Click **+ Streamlit App** (top right)

### Configure the App

**App Settings**:
- **App title**: `RCM Intelligence Hub`
- **App location**:
  - Database: `RCM_AI_DEMO`
  - Schema: `RCM_SCHEMA`
  - Warehouse: `RCM_INTELLIGENCE_WH`

### Add App Code

1. The Snowsight editor will open
2. **Delete** the default template code
3. **Copy/paste** the entire contents of `streamlit_app.py` from this repo
4. Click **Run** (top right)

### Add Dependencies (Optional)

If the app needs additional packages:

1. Click **Packages** (left sidebar in Streamlit editor)
2. Add these packages:
   ```
   snowflake-snowpark-python
   ```

Most dependencies are already included in Snowflake's Streamlit environment.

---

## Step 3: Test the App

**Access the app**:
- The app should now be running in Snowsight
- Click **Run** if not already started

**Test queries**:

1. **Analytics**: 
   ```
   What is the clean claim rate by provider?
   ```
   → Should show metrics from Cortex Analyst

2. **Knowledge Base**: 
   ```
   How do I resolve a Code 45 denial?
   ```
   → Should search documents and cite sources

3. **RCM Terminology**: 
   ```
   Show me remits for Anthem
   ```
   → Should enhance "remits" to "remittance advice (ERA)"

---

## ✅ Verification Checklist

After deployment:

- [ ] App runs in Snowsight
- [ ] Test analytics query works (returns metrics)
- [ ] Test knowledge base query works (returns documents)
- [ ] RCM terminology enhancement working (terms detected)
- [ ] Debug panel shows agent reasoning (enable in sidebar)
- [ ] No errors in chat responses

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

### Share with Users

**Grant Access**:

```sql
-- Grant app access to users
GRANT USAGE ON STREAMLIT RCM_AI_DEMO.RCM_SCHEMA.RCM_INTELLIGENCE_HUB 
  TO ROLE BUSINESS_ANALYST;

-- Grant agent access
GRANT USAGE ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod 
  TO ROLE BUSINESS_ANALYST;

-- Grant to specific user
GRANT ROLE BUSINESS_ANALYST TO USER john.doe@quadax.com;
```

**Share Link**:
1. In Snowsight, open your Streamlit app
2. Click **Share** (top right)
3. Copy the link and send to users

### Customize RCM Terms

Edit and re-run `sql_scripts/07_rcm_native_agent_production.sql`:

```sql
CREATE OR REPLACE FUNCTION ENHANCE_RCM_QUERY(query STRING)
AS $$
def enhance_query(query):
    terminology = {
        # Add your custom terms
        "your_term": "definition",
        "quadax_specific": "your context",
        
        # Existing 50+ terms
        "remit": "remittance advice (ERA)",
        # ...
    }
$$;
```

Then refresh your Streamlit app to use updated UDF.

---

## 🐛 Troubleshooting

### SQL Setup Issues

**Agent not found**:
```sql
-- Verify agent exists
SHOW AGENTS IN SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS;

-- If missing, re-run:
-- sql_scripts/07_rcm_native_agent_production.sql
```

**UDF not found**:
```sql
-- Verify UDFs exist
SHOW FUNCTIONS LIKE 'ENHANCE%' IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;

-- If missing, re-run:
-- sql_scripts/07_rcm_native_agent_production.sql
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
1. Check warehouse is running: `SHOW WAREHOUSES LIKE 'RCM_INTELLIGENCE_WH';`
2. Verify app location (Database: `RCM_AI_DEMO`, Schema: `RCM_SCHEMA`)
3. Click **Run** again in Snowsight

**Import errors**:
- Most packages are pre-installed in Snowflake's Streamlit
- If needed, add to **Packages** in left sidebar

**Permission errors**:
```sql
-- Grant app access to your role
GRANT USAGE ON STREAMLIT RCM_AI_DEMO.RCM_SCHEMA.RCM_INTELLIGENCE_HUB 
  TO ROLE YOUR_ROLE;

-- Grant agent access
GRANT USAGE ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod 
  TO ROLE YOUR_ROLE;
```

**Agent not responding**:
1. Verify agent exists (see above)
2. Check agent name in `streamlit_app.py` matches: `RCM_Healthcare_Agent_Prod`
3. Verify you have USAGE grant on agent

---

## 📚 Need More Help?

- **Full Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Technical Details**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Demo Script**: [RCM_15_Minute_Demo_Story.md](RCM_15_Minute_Demo_Story.md)

---

## 📹 Video Walkthrough

**Step-by-Step Deployment** (If recorded):
1. SQL setup (10 min)
2. Streamlit app creation (5 min)
3. Testing and validation (5 min)
4. User access configuration (5 min)

---

## ⏱️ Time Breakdown

| Step | Time | Status |
|------|------|--------|
| SQL Scripts (01-07) | 15 min | ✅ |
| Streamlit App Setup | 5 min | ✅ |
| Testing | 5 min | ✅ |
| User Access Config | 5 min | ⚙️ Optional |
| **Total** | **25-30 min** | **🎉** |

---

**You're all set! Start querying your RCM data with natural language.** 🎉

**Everything runs in Snowsight - no local setup required!**
