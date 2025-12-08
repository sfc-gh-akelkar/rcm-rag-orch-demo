# 🚀 Quick Start Guide - RCM Intelligence Hub

## 5-Minute Setup

### Step 1: Prerequisites ✅

Before starting, ensure you have:
- [ ] Snowflake account with Cortex enabled
- [ ] Python 3.9 or higher installed
- [ ] All 6 RCM setup scripts executed in Snowflake
- [ ] Terminal access

### Step 2: Install Dependencies 📦

```bash
# Navigate to the project directory
cd RCM_RAG_ORCH_DEMO

# Install required Python packages
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed streamlit-1.28.0 snowflake-connector-python-3.5.0 ...
```

### Step 3: Configure Snowflake Credentials 🔐

```bash
# Copy the example secrets file
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit with your credentials
nano .streamlit/secrets.toml
# OR
code .streamlit/secrets.toml
```

**Edit these values:**
```toml
[snowflake]
user = "YOUR_SNOWFLAKE_USER"           # Replace with your username
password = "YOUR_SNOWFLAKE_PASSWORD"   # Replace with your password
account = "YOUR_ORG-YOUR_ACCOUNT"      # Replace with your account identifier
warehouse = "RCM_INTELLIGENCE_WH"      # Leave as-is (or use your warehouse)
database = "RCM_AI_DEMO"               # Leave as-is
schema = "RCM_SCHEMA"                  # Leave as-is
role = "SF_INTELLIGENCE_DEMO"          # Leave as-is (or use your role)
```

💡 **Finding your account identifier:**
- Log in to Snowflake
- Look at the URL: `https://app.snowflake.com/{orgname}-{accountname}/...`
- Use format: `{orgname}-{accountname}`

### Step 4: Run the Application 🎉

```bash
streamlit run app.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

**The app will automatically open in your browser!**

---

## First Query - Test the System

### Try These Sample Questions

**Analytics (Cortex Analyst):**
```
What is the clean claim rate by provider?
```
→ Should return metrics and calculations

**Knowledge Base (Cortex Search):**
```
How do I resolve a Code 45 denial in ServiceNow?
```
→ Should search documents and provide procedures

**General (Conversation):**
```
What can you help me with?
```
→ Should provide overview of capabilities

---

## Verify Everything Works

### ✅ Checklist

After your first query, verify:

- [ ] **Connection Status**: Sidebar shows "✅ Connected to Snowflake"
- [ ] **Response Generated**: You received an answer to your question
- [ ] **Debug Panel**: (Enable in sidebar) Shows routing decision and cost
- [ ] **Session Stats**: Sidebar shows query count and token usage

### If Something Goes Wrong

**Problem: "Unable to connect to Snowflake"**

✅ **Solution:**
1. Double-check `.streamlit/secrets.toml` exists
2. Verify your credentials are correct
3. Ensure the warehouse exists: `SHOW WAREHOUSES;` in Snowflake
4. Check your role has permissions: `USE ROLE SF_INTELLIGENCE_DEMO;`

**Problem: "No response generated"**

✅ **Solution:**
1. Enable debug panel in sidebar
2. Check the error message in the debug section
3. Verify semantic views exist: `SHOW SEMANTIC VIEWS;` in Snowflake
4. Verify search services exist: `SHOW CORTEX SEARCH SERVICES;` in Snowflake

**Problem: "High token usage warning"**

✅ **Solution:**
- This is normal for complex queries
- Try narrowing your question
- Adjust `MAX_SEARCH_RESULTS` in `config.py` (default: 5)

---

## Understanding the Interface

### Main Chat Window

```
┌─────────────────────────────────────────┐
│  🏥 RCM Intelligence Hub                │
│  Unified AI Orchestration for RCM      │
├─────────────────────────────────────────┤
│                                         │
│  [Chat history appears here]            │
│                                         │
│  You: What is the denial rate?          │
│  Assistant: The denial rate is...       │
│                                         │
├─────────────────────────────────────────┤
│  Ask me anything about RCM...  [Send]   │
└─────────────────────────────────────────┘
```

### Sidebar Controls

- **Show Debug/Cost Info**: Toggle cost and routing visibility
- **Connection Status**: Snowflake connection state
- **Session Statistics**: Real-time token and cost tracking
- **About This App**: Architecture explanation
- **RCM Terminology**: Domain term reference

### Debug Panel (When Enabled)

Shows for each query:
- **🎯 Routing Decision**: Which tool was used and why
- **💰 Cost Analysis**: Token counts and estimated cost
- **📚 Sources**: Documents retrieved (for knowledge queries)
- **🔍 SQL**: Generated SQL (for analytics queries)

---

## Sample Demo Flow

### For Quadax Stakeholders

**1. Show Unified Interface** (1 minute)
```
"Notice there's just one chat window - no need to choose 
between tools. Let me demonstrate..."
```

**2. Analytics Query** (1 minute)
```
Query: "What is the clean claim rate by provider?"
Point out: "The system automatically routed this to Cortex Analyst"
Enable debug: Show tokens (~1,500) and cost (~$0.003)
```

**3. Knowledge Base Query** (1 minute)
```
Query: "How do I resolve a Code 45 denial?"
Point out: "Notice it understood 'Code 45' is a denial code"
Enable debug: Show sources retrieved and terminology enhancement
```

**4. Show Cost Tracking** (1 minute)
```
Point to sidebar:
- Total queries: 2
- Total tokens: ~3,000 (vs their concern of 30k+)
- Total cost: ~$0.006
```

**5. Explain Architecture** (1 minute)
```
"This solves your three concerns:
1. Point Solution Fatigue → One interface
2. Domain Specificity → RCM terminology built-in
3. Cost Control → Full transparency"
```

---

## Configuration Options

### Customize Models (config.py)

```python
# Use faster/cheaper models
ROUTER_MODEL = "llama3.2-3b"      # Classification
RAG_MODEL = "mixtral-8x7b"        # Knowledge base
ANALYST_MODEL = "mistral-large"   # Analytics

# Or use premium for everything
ROUTER_MODEL = "llama3.1-405b"
RAG_MODEL = "llama3.1-405b"
ANALYST_MODEL = "llama3.1-405b"
```

### Adjust Token Limits (config.py)

```python
# Reduce to save costs
MAX_SEARCH_RESULTS = 3  # Default: 5

# Increase for more comprehensive answers
MAX_SEARCH_RESULTS = 10
```

### Add Custom RCM Terms (config.py)

```python
RCM_TERMINOLOGY = {
    "your_custom_term": "definition",
    "client_specific_code": "what it means in your context"
}
```

---

## Next Steps

### For Development

1. **Customize the UI**: Edit `app.py` to match your branding
2. **Add Custom Metrics**: Extend `cost_tracker.py` for your KPIs
3. **Tune Prompts**: Adjust system prompts in `config.py`
4. **Add New Routes**: Extend `orchestrator.py` with new intent types

### For Production

1. **Set up secrets management**: Use Snowflake External Functions or AWS Secrets Manager
2. **Enable authentication**: Add Streamlit auth or SSO
3. **Set up monitoring**: Log queries and performance metrics
4. **Configure resource limits**: Set warehouse auto-suspend, token budgets

### For Demos

1. **Prepare sample data**: Ensure demo database has realistic data
2. **Create demo script**: Use `RCM_15_Minute_Demo_Story.md` as guide
3. **Test all routes**: Verify analytics, KB, and general all work
4. **Enable debug mode**: For transparency during demos

---

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Solution: Ensure all dependencies installed
pip install -r requirements.txt --upgrade
```

**Secrets Not Found**
```bash
# Solution: Verify file path and format
ls -la .streamlit/secrets.toml
cat .streamlit/secrets.toml
```

**Permission Denied**
```sql
-- In Snowflake, grant necessary permissions:
GRANT USAGE ON DATABASE RCM_AI_DEMO TO ROLE SF_INTELLIGENCE_DEMO;
GRANT USAGE ON SCHEMA RCM_AI_DEMO.RCM_SCHEMA TO ROLE SF_INTELLIGENCE_DEMO;
GRANT SELECT ON ALL TABLES IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA TO ROLE SF_INTELLIGENCE_DEMO;
GRANT USAGE ON ALL CORTEX SEARCH SERVICES IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA TO ROLE SF_INTELLIGENCE_DEMO;
```

**Warehouse Not Available**
```sql
-- Verify warehouse exists and is running:
SHOW WAREHOUSES LIKE 'RCM_INTELLIGENCE_WH';

-- Or create if needed:
CREATE WAREHOUSE RCM_INTELLIGENCE_WH WITH WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;
```

---

## Support

### Documentation

- **Architecture Deep Dive**: See `README_ORCHESTRATION.md`
- **Code Comments**: All modules have extensive inline documentation
- **Snowflake Docs**: https://docs.snowflake.com/en/user-guide/snowflake-cortex

### Debugging

Enable verbose logging:
```python
# In app.py, add at top:
import logging
logging.basicConfig(level=logging.DEBUG)
```

View Streamlit logs:
```bash
# Run with verbose output
streamlit run app.py --logger.level=debug
```

---

## Success! 🎉

You should now have a working RCM Intelligence Hub that:
- ✅ Accepts natural language queries
- ✅ Automatically routes to the right tool
- ✅ Handles RCM terminology
- ✅ Tracks costs and tokens
- ✅ Provides full visibility into operations

**Ready for your Quadax demo!**

