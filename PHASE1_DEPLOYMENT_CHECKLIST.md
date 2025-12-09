# Phase 1 Deployment Checklist

**Print this out or keep it on a second screen during deployment**

---

## Pre-Deployment (5 minutes)

### Verify Prerequisites

- [ ] Snowflake account with Cortex AI enabled
- [ ] Setup scripts 01-07 completed successfully
- [ ] Can access Snowsight (https://app.snowflake.com)
- [ ] Have privileges to create Streamlit apps

### Verify Agent Exists

**Open Snowsight → AI & ML → Agents**

- [ ] See agent named `RCM_Healthcare_Agent_Prod` OR `RCM_Healthcare_Agent`
- [ ] Can click on agent and see details
- [ ] Test agent with: "Hello" (should respond)

**If agent missing:** Run `setup/06_rcm_agent_setup.sql` and `setup/07_rcm_native_agent_production.sql`

---

## Deployment (10 minutes)

### Create Streamlit App

**Snowsight → Projects → Streamlit → + Streamlit App**

- [ ] App name: `RCM_INTELLIGENCE_HUB`
- [ ] Warehouse: `RCM_INTELLIGENCE_WH` (or your warehouse name)
- [ ] Database: `RCM_AI_DEMO`
- [ ] Schema: `RCM_SCHEMA`
- [ ] Click **Create**

### Paste Code

- [ ] Delete all default template code
- [ ] Copy entire contents of `setup/09_streamlit_app_phase1.py`
- [ ] Paste into Snowsight editor
- [ ] Verify code pasted completely (scroll to bottom)

### Configure Agent Name

**Find this section near the top:**

```python
# Agent configuration - UPDATE THESE FOR YOUR ENVIRONMENT
AGENT_DATABASE = "SNOWFLAKE_INTELLIGENCE"
AGENT_SCHEMA = "AGENTS"
AGENT_NAME = "RCM_Healthcare_Agent_Prod"
```

- [ ] Update `AGENT_NAME` if yours is different
- [ ] Leave database/schema as-is (usually correct)

### Run App

- [ ] Click **Run** button (top right)
- [ ] Wait 10-30 seconds for app to start
- [ ] App loads without error messages

---

## Testing (10 minutes)

### Visual Verification

- [ ] See header: "🏥 RCM Intelligence Hub"
- [ ] Sidebar shows sample questions
- [ ] Welcome message in main area
- [ ] Chat input at bottom
- [ ] Session stats show "Queries: 0"

### Functional Testing

**Test 1: Sample Question Button**
- [ ] Click "What can you help me with?" (Getting Started section)
- [ ] Response appears in 2-10 seconds
- [ ] Response makes sense (agent describes capabilities)
- [ ] Session stats update to "Queries: 1"
- [ ] Response time shown (e.g., "⚡ Response time: 2.3s")

**Test 2: Analytics Query**
- [ ] Click "Which payers have the highest denial rates?"
- [ ] Response includes payer names and rates
- [ ] Session stats update to "Queries: 2"
- [ ] Average time shows in stats

**Test 3: Knowledge Base Query**
- [ ] Click "How do I resolve a CO-45 denial?"
- [ ] Response discusses denial resolution procedures
- [ ] May reference policy documents
- [ ] Session stats update to "Queries: 3"

**Test 4: Chat Input**
- [ ] Type in chat input: "What is a clean claim?"
- [ ] Press Enter or click Send
- [ ] Response appears
- [ ] Session stats update to "Queries: 4"

**Test 5: New Conversation**
- [ ] Click "🔄 New Conversation" in sidebar
- [ ] Chat clears
- [ ] Welcome message appears again
- [ ] Session stats reset to "Queries: 0"
- [ ] Thread ID changes (first 8 chars different)

### Performance Check

- [ ] Most responses in 2-5 seconds
- [ ] No timeouts or errors
- [ ] UI remains responsive

---

## Sharing (5 minutes)

### Grant Access to Users

**Open SQL worksheet, run:**

```sql
-- Grant Streamlit app access
GRANT USAGE ON STREAMLIT RCM_AI_DEMO.RCM_SCHEMA.RCM_INTELLIGENCE_HUB 
TO ROLE <ROLE_NAME>;

-- Grant agent access
GRANT USAGE ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod 
TO ROLE <ROLE_NAME>;

-- Grant warehouse access
GRANT USAGE ON WAREHOUSE RCM_INTELLIGENCE_WH 
TO ROLE <ROLE_NAME>;

-- Assign role to specific user
GRANT ROLE <ROLE_NAME> TO USER <username@domain.com>;
```

- [ ] Replace `<ROLE_NAME>` with actual role (e.g., `BUSINESS_ANALYST`)
- [ ] Replace `<username@domain.com>` with actual usernames
- [ ] Run SQL statements
- [ ] Verify: "Statement executed successfully"

### Get Shareable Link

- [ ] In Streamlit app, click **Share** (top right)
- [ ] Copy the app URL
- [ ] Send to users with access

### Verify User Access

- [ ] Ask a user to open the URL
- [ ] They should see the app (not permission error)
- [ ] They can ask questions and get responses

---

## Demo Preparation (Optional)

### Practice Demo Flow

- [ ] Click "New Conversation" to start fresh
- [ ] Click "What can you help me with?"
- [ ] Click "Which payers have the highest denial rates?"
- [ ] Click "How do I resolve a CO-45 denial?"
- [ ] Click multi-tool question
- [ ] Type follow-up: "How does that compare to last quarter?"

- [ ] Total time: ~5 minutes
- [ ] All responses valid
- [ ] Can explain each step

### Review Demo Script

- [ ] Read [PHASE1_DEMO_SCRIPT.md](PHASE1_DEMO_SCRIPT.md)
- [ ] Note key talking points
- [ ] Practice timing (10-15 minutes total)

---

## Troubleshooting (If Needed)

### Issue: "Error calling agent"

**Check:**
- [ ] Agent name spelled correctly in code
- [ ] Agent exists: `SHOW AGENTS IN SNOWFLAKE_INTELLIGENCE.AGENTS;`
- [ ] Have USAGE privilege: `SHOW GRANTS ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod;`

**Fix:**
- [ ] Update `AGENT_NAME` in code
- [ ] Grant missing privilege
- [ ] Click **Run** again

### Issue: App won't load / Python error

**Check:**
- [ ] Code pasted completely (scroll to bottom, should end with `main()`)
- [ ] No syntax errors in editor
- [ ] Warehouse is running

**Fix:**
- [ ] Re-paste code from `09_streamlit_app_phase1.py`
- [ ] Check error message in Snowsight
- [ ] Restart warehouse if needed

### Issue: Slow responses (>10 seconds)

**Normal if:**
- [ ] First query (warehouse cold start)
- [ ] Complex multi-tool question

**Check if persists:**
- [ ] Warehouse size (consider MEDIUM instead of SMALL)
- [ ] Agent logs: AI & ML → Agents → Monitoring

### Issue: Sample buttons don't work

**Try:**
- [ ] Click "New Conversation"
- [ ] Refresh browser page
- [ ] Type question manually instead

---

## Success Criteria

### Deployment Success

- [x] App loads without errors
- [x] All 5 test queries work
- [x] Response time 2-10 seconds
- [x] Session stats update correctly
- [x] New conversation resets properly
- [x] Users can access the app

### Ready for Demo

- [x] Practiced demo flow
- [x] Can explain each feature
- [x] Know key talking points
- [x] Have demo script handy

### Ready for Production

- [x] Multiple users have access
- [x] Users can successfully ask questions
- [x] No consistent errors
- [x] Performance acceptable
- [x] Feedback mechanism in place

---

## Post-Deployment Tasks

### Week 1: Monitor Usage

- [ ] Check Streamlit app access logs
- [ ] Review query history for errors
- [ ] Gather initial user feedback
- [ ] Document common questions/issues

### Week 2: Gather Feedback

- [ ] Survey users: What works? What doesn't?
- [ ] Identify most-requested features
- [ ] Note performance issues
- [ ] Track adoption rate

### Week 3: Prioritize Phase 2

- [ ] Review feedback
- [ ] Decide which Phase 2 features to build
- [ ] Estimate effort for each
- [ ] Create implementation plan

---

## Quick Reference

### Key Files

- `setup/09_streamlit_app_phase1.py` - App code
- `PHASE1_DEPLOYMENT_GUIDE.md` - Detailed guide
- `PHASE1_DEMO_SCRIPT.md` - Demo talking points
- `PHASE1_README.md` - Overview

### Key SQL Commands

**Show agents:**
```sql
SHOW AGENTS IN SNOWFLAKE_INTELLIGENCE.AGENTS;
```

**Check privileges:**
```sql
SHOW GRANTS ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.RCM_Healthcare_Agent_Prod;
```

**Check query errors:**
```sql
SELECT * 
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE QUERY_TEXT LIKE '%CORTEX.COMPLETE_AGENT%'
ORDER BY START_TIME DESC 
LIMIT 10;
```

### Support

**If stuck:**
1. Check [PHASE1_DEPLOYMENT_GUIDE.md](PHASE1_DEPLOYMENT_GUIDE.md) troubleshooting
2. Review agent in Snowflake Intelligence UI
3. Check Snowflake query history for errors
4. Verify all privileges granted

---

**Estimated Total Time:** 30 minutes

**Status:** 
- [ ] Pre-deployment verified
- [ ] App deployed
- [ ] Testing complete
- [ ] Users granted access
- [ ] Demo prepared (optional)

---

✅ **ALL DONE?** You're ready to show off your RCM Intelligence Hub!


