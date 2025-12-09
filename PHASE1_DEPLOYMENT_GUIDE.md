# Phase 1 Deployment Guide - RCM Intelligence Hub

**Goal:** Get a working Streamlit app running in Snowflake in ~30 minutes

---

## Prerequisites

✅ You've completed setup scripts 01-07 (Agent is created)  
✅ You have access to Snowsight  
✅ You have privileges to create Streamlit apps  

---

## Step 1: Verify Agent Exists (5 minutes)

Before deploying the Streamlit app, verify your Cortex Agent is ready.

### 1.1 Open Snowsight

Navigate to: **AI & ML** → **Agents**

### 1.2 Find Your Agent

Look for one of these agents:
- `RCM_Healthcare_Agent_Prod` (recommended - includes RCM terminology)
- `RCM_Healthcare_Agent` (basic version)

### 1.3 Test the Agent

Click on the agent and try a test question:
```
Which payers have the highest denial rates?
```

If you get a response, you're ready to proceed! ✅

**Troubleshooting:**
- If agent doesn't exist: Run `setup/06_rcm_agent_setup.sql` and `setup/07_rcm_native_agent_production.sql`
- If you get permission errors: Make sure you're using role `SF_INTELLIGENCE_DEMO` or have USAGE on the agent

---

## Step 2: Create Streamlit App (10 minutes)

### 2.1 Navigate to Streamlit

In Snowsight: **Projects** → **Streamlit**

### 2.2 Click "+ Streamlit App"

### 2.3 Configure App Settings

**App name:** `RCM_INTELLIGENCE_HUB`

**App location:**
- **Warehouse:** `RCM_INTELLIGENCE_WH` (or your warehouse)
- **Database:** `RCM_AI_DEMO`
- **Schema:** `RCM_SCHEMA`

Click **Create**

### 2.4 Delete Default Code

Snowflake will show you a default template. Delete all of it.

### 2.5 Paste Phase 1 Code

Copy the entire contents of `setup/09_streamlit_app_phase1.py` and paste into the editor.

### 2.6 Update Configuration (if needed)

At the top of the file, verify these settings match your environment:

```python
# Agent configuration - UPDATE THESE FOR YOUR ENVIRONMENT
AGENT_DATABASE = "SNOWFLAKE_INTELLIGENCE"
AGENT_SCHEMA = "AGENTS"
AGENT_NAME = "RCM_Healthcare_Agent_Prod"  # or "RCM_Healthcare_Agent"
```

**Common configurations:**

| Agent Location | Use These Settings |
|----------------|-------------------|
| Created with script 07 (Production) | `SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod` |
| Created with script 06 (Basic) | `SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent` |

---

## Step 3: Run the App (2 minutes)

### 3.1 Click "Run" (top right)

Wait 10-30 seconds for the app to initialize.

### 3.2 Verify App Loads

You should see:
- ✅ Header: "🏥 RCM Intelligence Hub"
- ✅ Sidebar with sample questions
- ✅ Welcome message in the main area
- ✅ Chat input at the bottom

### 3.3 Test Sample Questions

Click one of the sidebar buttons:
- **"What can you help me with?"** (Getting Started section)

Wait for the response (should take 2-5 seconds).

### 3.4 Verify Features Work

**Test checklist:**
- [ ] Sample question buttons populate the chat ✅
- [ ] Agent responds to questions ✅
- [ ] Response time shows at bottom of each response ✅
- [ ] Session stats update (Queries count, Avg Time) ✅
- [ ] Can type custom questions in chat input ✅
- [ ] "New Conversation" button clears chat ✅

---

## Step 4: Demo the App (10 minutes)

### 4.1 Sample Demo Flow

Try these questions in order to show different capabilities:

**1. Introduction**
```
What can you help me with?
```
→ Shows agent self-awareness

**2. Analytics Query**
```
Which payers have the highest denial rates?
```
→ Demonstrates Cortex Analyst (structured data)

**3. Knowledge Base Query**
```
How do I resolve a CO-45 denial?
```
→ Demonstrates Cortex Search (unstructured documents)

**4. RCM Terminology**
```
Show me remits for Anthem
```
→ Shows domain intelligence (understands "remits" = remittance advice)

**5. Multi-Tool Orchestration**
```
Which payers have the highest denial rates and what do our appeal procedures say?
```
→ Demonstrates agent using multiple tools in one query

**6. Follow-up (Context)**
```
How does that compare to last quarter?
```
→ Shows conversation memory (knows "that" refers to previous query)

### 4.2 Point Out Features

**While demoing, highlight:**

✅ **Speed:** "Notice the response time - 2-3 seconds for complex queries"

✅ **Session Stats:** "The sidebar tracks queries and average response time in real-time"

✅ **Thread Management:** "Each conversation has a unique thread ID - you can start fresh anytime"

✅ **Sample Questions:** "Pre-built questions organized by category make it easy to explore"

✅ **Real Data:** "All responses come from real Snowflake data - 50,000+ claims, 40+ documents"

---

## Step 5: Share with Others (5 minutes)

### 5.1 Get Shareable Link

In Snowsight, click **Share** (top right of Streamlit app)

### 5.2 Grant Access to Users

Run this SQL to grant access:

```sql
-- Grant access to the Streamlit app
GRANT USAGE ON STREAMLIT RCM_AI_DEMO.RCM_SCHEMA.RCM_INTELLIGENCE_HUB 
TO ROLE <TARGET_ROLE>;

-- Grant access to the agent
GRANT USAGE ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod 
TO ROLE <TARGET_ROLE>;

-- Grant warehouse usage
GRANT USAGE ON WAREHOUSE RCM_INTELLIGENCE_WH 
TO ROLE <TARGET_ROLE>;

-- Assign role to user
GRANT ROLE <TARGET_ROLE> TO USER <username>;
```

**Example:**
```sql
GRANT USAGE ON STREAMLIT RCM_AI_DEMO.RCM_SCHEMA.RCM_INTELLIGENCE_HUB 
TO ROLE BUSINESS_ANALYST;

GRANT USAGE ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod 
TO ROLE BUSINESS_ANALYST;

GRANT USAGE ON WAREHOUSE RCM_INTELLIGENCE_WH 
TO ROLE BUSINESS_ANALYST;

GRANT ROLE BUSINESS_ANALYST TO USER john.smith@company.com;
```

---

## Troubleshooting

### Issue: "Error calling agent"

**Possible causes:**
1. Agent name is wrong
2. You don't have USAGE privilege
3. Agent is in different database/schema

**Fix:**
- Verify agent exists: `SHOW AGENTS IN SNOWFLAKE_INTELLIGENCE.AGENTS;`
- Check your role has access: `SHOW GRANTS ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod;`
- Update `AGENT_NAME`, `AGENT_DATABASE`, `AGENT_SCHEMA` in the code

---

### Issue: "No response received from agent"

**Possible causes:**
1. Agent timed out
2. Query failed
3. Response format unexpected

**Fix:**
- Try a simpler question first: "Hello"
- Check agent logs in Snowsight (AI & ML → Agents → Monitoring)
- Increase timeout if needed

---

### Issue: App is slow

**Possible causes:**
1. Warehouse is too small
2. First query (cold start)
3. Complex query

**Fix:**
- Resize warehouse: `ALTER WAREHOUSE RCM_INTELLIGENCE_WH SET WAREHOUSE_SIZE = MEDIUM;`
- Wait for warehouse to warm up
- Subsequent queries will be faster

---

### Issue: Sample questions don't work

**Possible causes:**
1. Button click handler issue
2. Session state problem

**Fix:**
- Click "New Conversation" to reset
- Refresh the browser page
- Try typing the question manually instead

---

## What's Included in Phase 1

✅ **Chat Interface**
- Message history with timestamps
- User/assistant message bubbles
- Chat input with placeholder text

✅ **Agent Integration**
- Real Cortex Agent API calls
- Error handling
- Response parsing

✅ **Sample Questions**
- 15+ pre-built questions
- Organized by category (Getting Started, Analytics, Knowledge Base, etc.)
- One-click to ask

✅ **Session Statistics**
- Query count
- Average response time
- Thread ID display

✅ **Thread Management**
- Unique thread per conversation
- "New Conversation" button to reset
- Context maintained within thread

✅ **Response Time Tracking**
- Measured in Python (not from Snowflake metadata)
- Displayed with each response
- Aggregated in session stats

---

## What's NOT Included (Future Phases)

❌ Debug panel showing tool execution  
❌ Token usage tracking  
❌ Cost estimation  
❌ Export conversation  
❌ Generated SQL display  
❌ Enhanced query visualization  
❌ Suggested follow-up questions  

These will be added in Phase 2 and Phase 3.

---

## Success Criteria

✅ App loads without errors  
✅ Sample questions return valid responses  
✅ Response time is 2-5 seconds per query  
✅ Session stats update correctly  
✅ Can start new conversations  
✅ Multiple users can access the app  

---

## Next Steps

Once Phase 1 is stable:

1. **Gather Feedback:** Let users try it for a week
2. **Identify Pain Points:** What features do they need?
3. **Prioritize Phase 2:** Based on actual usage patterns
4. **Plan Enhancements:** Debug panel? Token tracking? Export?

---

## Support

**If you encounter issues:**

1. Check the agent works in Snowflake Intelligence (AI & ML → Agents)
2. Verify all setup scripts completed successfully
3. Review error messages in the app
4. Check Snowflake query history for errors: `SELECT * FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY()) WHERE QUERY_TEXT LIKE '%CORTEX.COMPLETE_AGENT%' ORDER BY START_TIME DESC LIMIT 10;`

---

**Ready to Deploy?** Follow Step 1 above to get started! 🚀


