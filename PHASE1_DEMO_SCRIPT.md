# Phase 1 Demo Script - RCM Intelligence Hub

**Duration:** 10-15 minutes  
**Goal:** Show working Cortex Agent app with real Snowflake data

---

## Opening (1 minute)

> "Let me show you our RCM Intelligence Hub - a unified AI assistant built with Snowflake Cortex Agents. This is a working demo with real data, built in about 5 hours following Snowflake best practices."

**Open the Streamlit app**

> "What you're seeing is Streamlit in Snowflake - the entire app runs inside Snowflake, no external hosting needed. Let me walk you through the capabilities."

---

## Act 1: Basic Interaction (3 minutes)

### Demo: Self-Awareness

**Click sample question:** "What can you help me with?"

**While waiting for response, point out:**
- "Notice the sidebar has pre-built questions organized by category"
- "Session stats at the bottom track queries and response time"
- "Each conversation has a unique thread ID for context management"

**When response appears:**
> "See how the agent explains its own capabilities? It knows it has access to analytics, document search, and custom RCM tools. This isn't hardcoded - the agent genuinely understands what it can do."

**Point out:**
- Response time (typically 2-3 seconds)
- Timestamp on each message
- Clean, simple interface

---

## Act 2: Structured Data Analytics (4 minutes)

### Demo: Cortex Analyst in Action

**Click sample question:** "Which payers have the highest denial rates?"

**While waiting:**
> "This question requires querying our claims database - 50,000+ records across payers, providers, and procedures. The agent will automatically use Cortex Analyst to generate SQL and return results."

**When response appears:**
> "Here are the top payers by denial rate. Behind the scenes, the agent:
> 1. Understood this was an analytics question
> 2. Selected the right semantic model (Denials)
> 3. Generated SQL to calculate denial rates
> 4. Executed the query
> 5. Formatted the results
> 
> All automatically - no manual tool selection needed."

**Key talking points:**
- ✅ Real data from Snowflake tables
- ✅ Automatic Text-to-SQL conversion
- ✅ No pre-built report - generated on the fly
- ✅ Response in 2-3 seconds

### Demo: Follow-Up Question (Context)

**Type in chat:** "How does that compare to last quarter?"

**Point out:**
> "Notice I didn't have to repeat 'denial rates by payer' - the agent remembers the conversation context. This is thread-based conversation management."

---

## Act 3: Unstructured Data Search (3 minutes)

### Demo: Cortex Search / RAG

**Click sample question:** "How do I resolve a CO-45 denial?"

**While waiting:**
> "This is a completely different type of question - we're searching through policy documents, procedures, and compliance guidelines. The agent will automatically switch from analytics to document search."

**When response appears:**
> "The agent found relevant procedures in our knowledge base. It searched across 40+ documents covering policies, contracts, and procedures - and returned the most relevant information about CO-45 denial resolution.
>
> CO-45 is 'Charge exceeds fee schedule' - a common denial type. The agent understands RCM terminology and found the right procedures."

**Key talking points:**
- ✅ Searched unstructured documents (PDFs, policies)
- ✅ Hybrid search (semantic + keyword)
- ✅ Automatic tool selection (Search vs. Analytics)
- ✅ RCM domain knowledge (understands denial codes)

---

## Act 4: Multi-Tool Orchestration (3 minutes)

### Demo: The Power Move

**Click sample question:** "Which payers have the highest denial rates and what do our appeal procedures say?"

**While waiting:**
> "This question requires BOTH analytics AND document search. Let's see if the agent can handle it..."

**When response appears:**
> "Impressive! The agent:
> 1. Recognized this as a two-part question
> 2. Used Cortex Analyst to get denial rates (structured data)
> 3. Used Cortex Search to find appeal procedures (unstructured)
> 4. Combined both results into one coherent answer
>
> This is true orchestration - the agent decided which tools to use, executed them, and synthesized the results. You didn't have to say 'use analytics' or 'search documents' - it figured that out."

**Key talking points:**
- ✅ Multi-tool execution in one query
- ✅ Intelligent routing (agent decides which tools)
- ✅ Synthesis of disparate data sources
- ✅ This is what separates agents from chatbots

---

## Act 5: RCM Domain Intelligence (2 minutes)

### Demo: Healthcare Terminology

**Click sample question:** "Show me remits for Anthem"

**Point out:**
> "I just used RCM shorthand - 'remits' instead of 'remittance advice' or 'ERA'. The agent understands 50+ healthcare revenue cycle terms automatically."

**When response appears:**
> "The agent knew that 'remits' means remittance advice (ERA - Electronic Remittance Advice) and searched for the right data. This RCM terminology enhancement happens automatically through Snowflake UDFs - no external API calls, runs in-database."

**Other examples you could mention:**
- "A/R" → "Accounts Receivable aging"
- "CO-45" → "Contractual Obligation - charge exceeds fee schedule"
- "Clean claim" → "Claim submitted without errors accepted on first submission"

---

## Closing: The Snowflake Difference (2 minutes)

### Highlight Key Benefits

**Point to session stats:**
> "We've asked 5-6 questions in about 10 minutes. Look at the session stats:
> - Average response time: ~2-3 seconds
> - All queries executed successfully
> - Thread maintained context throughout"

**Recap:**
> "What you just saw demonstrates why Snowflake Cortex Agents are different:
>
> **1. Built-in Orchestration**
> - Agent automatically decides which tools to use
> - No custom routing code needed
> - Handles analytics, search, and custom tools seamlessly
>
> **2. Native Integration**
> - Everything runs inside Snowflake
> - Data never leaves your security perimeter
> - HIPAA compliant out of the box
>
> **3. Speed to Value**
> - This entire app: ~5 hours to build
> - No infrastructure setup
> - No multi-service integration
> - Just SQL and Python in Snowsight
>
> **4. Real Production Readiness**
> - Thread-based conversations
> - Session management
> - Error handling
> - All using Snowflake's managed services"

**New Conversation Demo:**
> "Let me show you one more thing - click 'New Conversation' in the sidebar."

**Click button, show chat clears:**
> "Fresh thread, clean slate. Each conversation is isolated, perfect for multi-user environments or new topics."

---

## Q&A Prompts

**If they ask about cost:**
> "This runs on a SMALL warehouse - about $2/hour when active. Cortex AI costs are token-based - roughly $0.006 per query for this complexity. Much cheaper than running separate AI infrastructure."

**If they ask about security:**
> "Everything stays in Snowflake. Your PHI, policies, contracts - none of it goes to external services. Covered by your Snowflake BAA, automatic encryption, full audit trail."

**If they ask about setup:**
> "We ran 7 SQL scripts in Snowsight - total setup time was about 30 minutes. No Docker, no Kubernetes, no cloud architecture. Just copy/paste SQL and click Run."

**If they ask about customization:**
> "Completely customizable - add more search services, connect to different data sources, add custom tools. It's all SQL and Python, no black box."

**If they ask what's next:**
> "This is Phase 1 - core functionality. Phase 2 adds debug panels showing which tools were used, token tracking, export capabilities. Phase 3 could include voice input, scheduled reports, advanced analytics. But we wanted to start with something real and working - validate the use case before building more."

---

## Fallback Questions (If Demo Fails)

**If agent doesn't respond:**
1. Try simpler question: "Hello"
2. Check agent in Snowflake Intelligence directly
3. Fall back to screenshots/video

**If response is slow (>10 seconds):**
> "First query can be slower due to warehouse cold start. Subsequent queries are much faster - see, this one is 2 seconds."

**If error occurs:**
> "This is why we have session stats and error handling - in production, we'd log this and investigate. But you can see the conversation context is preserved, so we can just try again."

---

## Key Metrics to Mention

✅ **Built in:** 5 hours  
✅ **Setup time:** 30 minutes  
✅ **Response time:** 2-3 seconds average  
✅ **Data scale:** 50,000+ claims, 40+ documents  
✅ **Tools available:** 10 (2 Analyst, 5 Search, 3 Custom)  
✅ **RCM terms:** 50+ automatically enhanced  
✅ **Cost:** ~$0.006 per query  
✅ **Security:** HIPAA compliant, data stays in Snowflake  

---

## Strong Closing Line

> "This is the power of Snowflake Cortex Agents - you get production-ready AI orchestration in hours, not months. No infrastructure, no DevOps, no multi-service complexity. Just intelligent, secure, fast access to your RCM data - both structured and unstructured - through natural language."

**Pause, then:**

> "Want to try asking a question yourself?"

---

**End of Demo** 🎯


