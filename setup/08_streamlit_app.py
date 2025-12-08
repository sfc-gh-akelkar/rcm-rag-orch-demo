"""
RCM Intelligence Hub - Streamlit in Snowflake (SiS) Version
Step 8 of 8 in the RCM Intelligence Hub setup process

Production deployment with Native Cortex Agent orchestration following
official Snowflake standards: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents

Key features:
- Uses get_active_session() for native Snowflake integration
- Calls Cortex Agent via REST API (_snowflake module)
- Thread-based conversation context management
- RCM domain intelligence with 50+ healthcare terms
- Zero data movement (HIPAA compliant)
- Auto model selection (orchestration: "auto")
"""

import streamlit as st
import json
from datetime import datetime
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import functions as F

# ========================================================================
# PAGE CONFIGURATION
# ========================================================================

st.set_page_config(
    page_title="RCM Intelligence Hub",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========================================================================
# CONFIGURATION
# ========================================================================

# Agent configuration
AGENT_NAME = "RCM_Healthcare_Agent_Prod"
AGENT_SCHEMA = "SNOWFLAKE_INTELLIGENCE.AGENTS"
DATABASE = "RCM_AI_DEMO"
SCHEMA = "RCM_SCHEMA"

# UI configuration
MAX_CHAT_HISTORY = 50
WELCOME_MESSAGE = """
👋 **Welcome to the RCM Intelligence Hub!**

I'm your unified AI assistant for healthcare revenue cycle management, powered by **Snowflake Cortex Agents** following official Snowflake best practices.

**🎯 Production Architecture Features:**
- ✅ **Zero Data Movement**: Everything runs inside Snowflake
- ✅ **Native Agent Orchestration**: Auto model selection, planning, and reflection
- ✅ **REST API Integration**: Official Snowflake SiS pattern
- ✅ **Thread Management**: Maintains conversation context automatically
- ✅ **HIPAA Compliant**: Data never leaves Snowflake perimeter

I can help you with:

**📊 Analytics & Metrics** (Claims, Denials, Payer Performance)
- *"What is the clean claim rate by provider?"*
- *"Which payers have the highest denial rates?"*
- *"Show me revenue trends for the last quarter"*

**📚 Knowledge Base** (Policies, Procedures, ServiceNow)
- *"How do I resolve a Code 45 denial in ServiceNow?"*
- *"What are our appeal filing deadlines by payer?"*
- *"Find HIPAA compliance requirements for claims processing"*

**💡 General Questions**
- *"What RCM metrics should I focus on?"*
- *"Explain the difference between CO and PR adjustments"*

---
**🔄 Architecture**: 
- **Agent Model**: Auto (Snowflake selects best available)
- **Tools**: 2 Cortex Analyst + 5 Cortex Search + 3 Custom UDFs
- **Orchestration**: Planning → Tool Use → Reflection → Response
"""

# ========================================================================
# SESSION STATE INITIALIZATION
# ========================================================================

def init_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "thread_id" not in st.session_state:
        # Create new thread for conversation context
        st.session_state.thread_id = None
    
    if "show_debug" not in st.session_state:
        st.session_state.show_debug = False
    
    if "query_count" not in st.session_state:
        st.session_state.query_count = 0
    
    if "session" not in st.session_state:
        st.session_state.session = get_active_session()

# ========================================================================
# SNOWFLAKE AGENT INTERACTION
# ========================================================================

def create_thread():
    """Create a new conversation thread with the agent using REST API."""
    try:
        import _snowflake
        
        # Create thread using native REST API
        response = _snowflake.send_snow_api_request(
            method="POST",
            url=f"/api/v2/databases/{DATABASE}/schemas/{SCHEMA}/agents/{AGENT_NAME}/threads",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body=json.dumps({}),  # Empty body for new thread
            timeout=30
        )
        
        if response and 'data' in response:
            thread_id = response['data'].get('thread_id')
            return thread_id
        else:
            # Fallback to UUID if API doesn't return thread_id
            import uuid
            return str(uuid.uuid4())
            
    except ImportError:
        # Fallback for local development
        import uuid
        return str(uuid.uuid4())
    except Exception as e:
        st.error(f"Error creating thread: {e}")
        import uuid
        return str(uuid.uuid4())


def call_agent(user_query: str, thread_id: str = None):
    """
    Call the native Cortex Agent using the REST API pattern.
    
    This follows Snowflake's recommended approach for calling agents from
    Streamlit in Snowflake (SiS) applications.
    
    The agent handles:
    - Intent classification
    - RCM terminology enhancement (via UDF)
    - Routing to Cortex Analyst or Cortex Search
    - Response generation
    """
    session = st.session_state.session
    
    try:
        import _snowflake
        
        # Build request payload per Snowflake standards
        request_payload = {
            "query": user_query
        }
        
        # Add thread_id if maintaining conversation context
        if thread_id:
            request_payload["thread_id"] = thread_id
        
        # Call agent using native REST API from SiS
        # This is the recommended pattern per official docs
        response = _snowflake.send_snow_api_request(
            method="POST",
            url=f"/api/v2/databases/{DATABASE}/schemas/{SCHEMA}/agents/{AGENT_NAME}:run",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body=json.dumps(request_payload),
            timeout=60
        )
        
        # Parse the streaming response
        if response and 'data' in response:
            response_data = response['data']
            
            # Extract message content
            if 'message' in response_data:
                message = response_data['message']
                response_text = message.get('content', 'No response generated')
                
                # Get usage info for cost tracking
                usage = response_data.get('usage', {})
                
                return {
                    "success": True,
                    "response": response_text,
                    "model": response_data.get('model', 'auto'),
                    "usage": {
                        "input_tokens": usage.get('prompt_tokens', 0),
                        "output_tokens": usage.get('completion_tokens', 0),
                        "total_tokens": usage.get('total_tokens', 0)
                    },
                    "agent_name": AGENT_NAME,
                    "thread_id": response_data.get('thread_id')
                }
            else:
                return {
                    "success": False,
                    "error": "Unexpected response format",
                    "response": "I apologize, but I couldn't generate a response. Please try again."
                }
        else:
            return {
                "success": False,
                "error": "No response from agent",
                "response": "I apologize, but I couldn't generate a response. Please try again."
            }
            
    except ImportError:
        # Fallback to SQL-based approach if _snowflake module not available
        # This can happen in local development or older SiS versions
        return call_agent_sql_fallback(user_query, thread_id)
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response": f"I encountered an error: {str(e)}"
        }


def call_agent_sql_fallback(user_query: str, thread_id: str = None):
    """
    Fallback method using SQL when REST API is not available.
    Used for local development or older SiS versions.
    """
    session = st.session_state.session
    
    try:
        # SQL-based agent call (fallback)
        agent_query = f"""
        SELECT PARSE_JSON(
            SNOWFLAKE.CORTEX.COMPLETE(
                '{AGENT_NAME}',
                [
                    {{
                        'role': 'user',
                        'content': '{user_query.replace("'", "''")}'
                    }}
                ]
            )
        ) as response
        """
        
        result = session.sql(agent_query).collect()
        
        if result and len(result) > 0:
            response_data = result[0]['RESPONSE']
            
            if isinstance(response_data, str):
                response_data = json.loads(response_data)
            
            if 'choices' in response_data and len(response_data['choices']) > 0:
                message = response_data['choices'][0].get('message', {})
                response_text = message.get('content', 'No response generated')
                usage = response_data.get('usage', {})
                
                return {
                    "success": True,
                    "response": response_text,
                    "model": response_data.get('model', 'auto'),
                    "usage": {
                        "input_tokens": usage.get('prompt_tokens', 0),
                        "output_tokens": usage.get('completion_tokens', 0),
                        "total_tokens": usage.get('total_tokens', 0)
                    },
                    "agent_name": AGENT_NAME
                }
        
        return {
            "success": False,
            "error": "No response from agent",
            "response": "I apologize, but I couldn't generate a response. Please try again."
        }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response": f"I encountered an error: {str(e)}"
        }


def get_session_statistics():
    """Get session statistics from query history."""
    session = st.session_state.session
    
    try:
        # Query recent history for this session
        # This is a simplified version - in production, would track by session ID
        stats_query = """
        SELECT 
            COUNT(*) as query_count,
            SUM(TOTAL_ELAPSED_TIME) / 1000 as total_time_seconds,
            AVG(TOTAL_ELAPSED_TIME) / 1000 as avg_time_seconds
        FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
        WHERE QUERY_TYPE = 'SELECT'
        AND START_TIME > DATEADD(hour, -1, CURRENT_TIMESTAMP())
        LIMIT 100
        """
        
        result = session.sql(stats_query).collect()
        
        if result and len(result) > 0:
            row = result[0]
            return {
                "total_queries": row['QUERY_COUNT'],
                "total_time": row['TOTAL_TIME_SECONDS'],
                "avg_time": row['AVG_TIME_SECONDS']
            }
        else:
            return {
                "total_queries": 0,
                "total_time": 0,
                "avg_time": 0
            }
    except:
        return {
            "total_queries": st.session_state.query_count,
            "total_time": 0,
            "avg_time": 0
        }

# ========================================================================
# UI COMPONENTS
# ========================================================================

def render_header():
    """Render the application header."""
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        st.image("https://www.snowflake.com/wp-content/themes/snowflake/assets/img/brand-guidelines/logo-sno-blue-example.svg", width=150)
    
    with col2:
        st.title("🏥 RCM Intelligence Hub")
        st.caption("*Powered by Snowflake Native Cortex Agent • Streamlit in Snowflake*")
    
    with col3:
        if st.button("🔄 New Session", use_container_width=True):
            st.session_state.messages = []
            st.session_state.thread_id = None
            st.session_state.query_count = 0
            st.rerun()


def render_welcome_message():
    """Display welcome message on first load."""
    if len(st.session_state.messages) == 0:
        st.info(WELCOME_MESSAGE)


def render_sidebar():
    """Render sidebar with session controls and statistics."""
    with st.sidebar:
        st.header("⚙️ Session Controls")
        
        # Debug toggle
        st.session_state.show_debug = st.checkbox(
            "Show Debug/Agent Info",
            value=st.session_state.show_debug,
            help="Display agent reasoning and cost estimates"
        )
        
        st.divider()
        
        # Deployment info
        st.subheader("📡 Deployment Info")
        st.success("✅ Streamlit in Snowflake (SiS)")
        st.info(f"🤖 Agent: {AGENT_NAME}")
        st.caption(f"Database: {DATABASE}")
        st.caption(f"Schema: {SCHEMA}")
        
        st.divider()
        
        # Session statistics
        st.subheader("📊 Session Statistics")
        stats = get_session_statistics()
        
        st.metric("Queries Processed", st.session_state.query_count)
        if stats['total_queries'] > 0:
            st.metric("Avg Response Time", f"{stats['avg_time']:.2f}s")
        
        st.divider()
        
        # Architecture info
        with st.expander("ℹ️ About This App"):
            st.markdown("""
            **Architecture**: Streamlit in Snowflake + Cortex Agents (Official Pattern)
            
            **Snowflake Standards Compliance**:
            - ✅ REST API integration (_snowflake module)
            - ✅ Auto model selection (best available)
            - ✅ Thread-based context management
            - ✅ CORTEX_AGENT_USER role-based access
            - ✅ Multi-tool orchestration (10 tools total)
            
            **Agent Workflow** (per [official docs](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)):
            1. **Planning**: Agent analyzes your question and creates execution plan
            2. **Tool Use**: Routes to Analyst, Search, or Custom tools
            3. **Reflection**: Evaluates results and determines next steps
            4. **Response**: Generates comprehensive answer with context
            
            **Tools Available**:
            - 📊 **Cortex Analyst** (2): Claims & Denials semantic views
            - 📚 **Cortex Search** (5): Finance, Ops, Compliance, Strategy, Knowledge Base
            - 🔧 **Custom Tools** (3): RCM terminology, document URLs, alerts
            """)
        
        # RCM Terminology
        with st.expander("📖 RCM Terminology"):
            st.markdown("""
            **Common Terms**:
            - **Remit**: Electronic Remittance Advice (ERA)
            - **Write-off**: Contractual adjustment (CO-45, PR-1)
            - **Clean Claim**: First-pass acceptance
            - **A/R**: Accounts Receivable
            - **COB**: Coordination of Benefits
            
            **Denial Codes**:
            - **CO-45**: Charge exceeds fee schedule
            - **PR-1**: Patient deductible
            - **CO-16**: Missing information
            - **CO-29**: Timely filing deadline
            - **CO-50**: Non-covered service
            """)


def render_debug_panel(metadata: dict):
    """Render debug panel showing agent reasoning and cost info."""
    with st.expander("🔍 Agent Reasoning & Cost Info", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🤖 Agent Info")
            st.write(f"**Agent**: {metadata.get('agent_name', 'N/A')}")
            st.write(f"**Model**: {metadata.get('model', 'auto')}")
            
            if 'usage' in metadata:
                st.markdown("### 💰 Token Usage")
                usage = metadata['usage']
                st.metric("Input Tokens", f"{usage.get('input_tokens', 0):,}")
                st.metric("Output Tokens", f"{usage.get('output_tokens', 0):,}")
                st.metric("Total Tokens", f"{usage.get('total_tokens', 0):,}")
        
        with col2:
            st.markdown("### 📊 Performance")
            st.caption("Native agent handles all orchestration")
            st.write("✅ RCM terminology enhancement")
            st.write("✅ Intent classification")
            st.write("✅ Tool routing")
            st.write("✅ Response generation")
            
            # Cost warning if high usage
            if 'usage' in metadata:
                total_tokens = metadata['usage'].get('total_tokens', 0)
                if total_tokens > 25000:
                    st.warning("⚠️ High token usage (>25k)")
                elif total_tokens > 15000:
                    st.info("ℹ️ Moderate token usage")


def process_user_query(user_query: str):
    """Process user query through the native Cortex Agent."""
    
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_query,
        "timestamp": datetime.now().isoformat()
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # Process query through agent
    with st.chat_message("assistant"):
        with st.spinner("🤔 Native agent analyzing and routing your query..."):
            
            # Create thread if needed
            if st.session_state.thread_id is None:
                st.session_state.thread_id = create_thread()
            
            # Call agent
            result = call_agent(user_query, st.session_state.thread_id)
            
            # Update thread_id if agent returned one
            if result.get("thread_id"):
                st.session_state.thread_id = result["thread_id"]
            
            # Display response
            response_text = result.get("response", "I apologize, but I couldn't generate a response.")
            st.markdown(response_text)
            
            # Show debug panel if enabled
            if st.session_state.show_debug:
                render_debug_panel(result)
            
            # Add assistant message to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "metadata": result,
                "timestamp": datetime.now().isoformat()
            })
            
            # Update query count
            st.session_state.query_count += 1
            
            # Trim chat history if too long
            if len(st.session_state.messages) > MAX_CHAT_HISTORY:
                st.session_state.messages = st.session_state.messages[-MAX_CHAT_HISTORY:]


# ========================================================================
# MAIN APPLICATION
# ========================================================================

def main():
    """Main application entry point."""
    
    # Initialize session state
    init_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar()
    
    # Display welcome message
    render_welcome_message()
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show debug info if enabled and available
            if (st.session_state.show_debug and 
                message["role"] == "assistant" and 
                "metadata" in message):
                render_debug_panel(message["metadata"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about RCM analytics, policies, or procedures..."):
        process_user_query(prompt)
        st.rerun()
    
    # Sample questions (for first-time users)
    if len(st.session_state.messages) == 0:
        st.markdown("### 💡 Try These Sample Questions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📊 Analytics**")
            if st.button("Clean claim rate by provider?", use_container_width=True):
                process_user_query("What is the clean claim rate by provider?")
                st.rerun()
            if st.button("Which payers have high denials?", use_container_width=True):
                process_user_query("Which payers have the highest denial rates?")
                st.rerun()
        
        with col2:
            st.markdown("**📚 Knowledge Base**")
            if st.button("How to resolve Code 45?", use_container_width=True):
                process_user_query("How do I resolve a Code 45 denial in ServiceNow?")
                st.rerun()
            if st.button("HIPAA compliance requirements?", use_container_width=True):
                process_user_query("Find our HIPAA compliance requirements for claims processing")
                st.rerun()
        
        with col3:
            st.markdown("**💬 General**")
            if st.button("What can you help with?", use_container_width=True):
                process_user_query("What can you help me with?")
                st.rerun()
            if st.button("Explain RCM metrics", use_container_width=True):
                process_user_query("Explain the key RCM metrics I should focus on")
                st.rerun()


# ========================================================================
# APPLICATION ENTRY POINT
# ========================================================================

if __name__ == "__main__":
    main()

