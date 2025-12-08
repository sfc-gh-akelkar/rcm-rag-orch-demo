"""
RCM Intelligence Hub - Unified Streamlit Interface
Orchestrated AI for Healthcare Revenue Cycle Management

This application implements a Supervisor Agent pattern that intelligently
routes user queries to the appropriate backend tool, solving Quadax's
"Point Solution Fatigue" problem.

Architecture:
- Single unified chat interface (no tool selection needed)
- Automatic intent classification and routing
- Cost tracking and visibility
- RCM domain-specific terminology handling
"""

import streamlit as st
import snowflake.connector
from datetime import datetime
import json

from orchestrator import RCMOrchestrator
from cost_tracker import CostTracker, get_cost_warning
from rcm_terminology import get_enhancer
from config import (
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
    WELCOME_MESSAGE,
    DEBUG_PANEL_TITLE,
    SHOW_DEBUG_BY_DEFAULT,
    SNOWFLAKE_WAREHOUSE,
    SNOWFLAKE_DATABASE,
    SNOWFLAKE_SCHEMA,
    SNOWFLAKE_ROLE,
    MAX_CHAT_HISTORY
)


# ========================================================================
# PAGE CONFIGURATION
# ========================================================================

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="collapsed"  # Unified interface - minimal sidebar
)


# ========================================================================
# SESSION STATE INITIALIZATION
# ========================================================================

def init_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = None
    
    if "snowflake_connected" not in st.session_state:
        st.session_state.snowflake_connected = False
    
    if "show_debug" not in st.session_state:
        st.session_state.show_debug = SHOW_DEBUG_BY_DEFAULT
    
    if "query_history" not in st.session_state:
        st.session_state.query_history = []


# ========================================================================
# SNOWFLAKE CONNECTION
# ========================================================================

@st.cache_resource
def get_snowflake_connection():
    """
    Create and cache Snowflake connection.
    
    Uses Streamlit secrets for credentials.
    Falls back to config values for development.
    """
    try:
        # Try to use Streamlit secrets first
        if "snowflake" in st.secrets:
            conn = snowflake.connector.connect(
                user=st.secrets["snowflake"]["user"],
                password=st.secrets["snowflake"]["password"],
                account=st.secrets["snowflake"]["account"],
                warehouse=st.secrets.get("snowflake", {}).get("warehouse", SNOWFLAKE_WAREHOUSE),
                database=st.secrets.get("snowflake", {}).get("database", SNOWFLAKE_DATABASE),
                schema=st.secrets.get("snowflake", {}).get("schema", SNOWFLAKE_SCHEMA),
                role=st.secrets.get("snowflake", {}).get("role", SNOWFLAKE_ROLE)
            )
        else:
            # Fallback to manual connection (for development)
            st.warning("⚠️ Snowflake secrets not configured. Please add credentials in Streamlit secrets.")
            return None
        
        return conn
    
    except Exception as e:
        st.error(f"❌ Failed to connect to Snowflake: {str(e)}")
        return None


def init_orchestrator():
    """Initialize the RCM Orchestrator with Snowflake connection."""
    if st.session_state.orchestrator is None:
        conn = get_snowflake_connection()
        if conn:
            st.session_state.orchestrator = RCMOrchestrator(conn)
            st.session_state.snowflake_connected = True
            return True
        else:
            st.session_state.snowflake_connected = False
            return False
    return st.session_state.snowflake_connected


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
        st.caption("*Unified AI Orchestration for Healthcare Revenue Cycle Management*")
    
    with col3:
        if st.button("🔄 New Session", use_container_width=True):
            st.session_state.messages = []
            st.session_state.query_history = []
            st.rerun()


def render_welcome_message():
    """Display welcome message on first load."""
    if len(st.session_state.messages) == 0:
        st.info(WELCOME_MESSAGE)


def render_sidebar():
    """
    Render sidebar with minimal controls and session statistics.
    
    Note: Sidebar is minimal because this is a unified interface.
    Users don't need to select tools - the orchestrator does that automatically.
    """
    with st.sidebar:
        st.header("⚙️ Session Controls")
        
        # Debug toggle
        st.session_state.show_debug = st.checkbox(
            "Show Debug/Cost Info",
            value=st.session_state.show_debug,
            help="Display routing decisions and cost estimates for each query"
        )
        
        st.divider()
        
        # Connection status
        st.subheader("📡 Connection Status")
        if st.session_state.snowflake_connected:
            st.success("✅ Connected to Snowflake")
        else:
            st.error("❌ Not connected to Snowflake")
            if st.button("🔌 Retry Connection"):
                st.cache_resource.clear()
                st.rerun()
        
        st.divider()
        
        # Session statistics
        if st.session_state.orchestrator:
            st.subheader("📊 Session Statistics")
            summary = st.session_state.orchestrator.get_session_summary()
            
            st.metric("Queries Processed", summary["total_queries"])
            st.metric("Total Tokens", f"{summary['total_tokens']:,}")
            st.metric("Total Cost", f"${summary['total_cost']:.4f}")
            
            if summary["total_queries"] > 0:
                st.metric(
                    "Avg Tokens/Query",
                    f"{summary['avg_tokens_per_query']:.0f}"
                )
                st.metric(
                    "Avg Cost/Query",
                    f"${summary['avg_cost_per_query']:.4f}"
                )
            
            # Route breakdown
            with st.expander("📈 Route Breakdown"):
                for route, data in summary["by_route"].items():
                    if data["count"] > 0:
                        st.write(f"**{route}**")
                        st.write(f"- Queries: {data['count']}")
                        st.write(f"- Tokens: {data['tokens']:,}")
                        st.write(f"- Cost: ${data['cost']:.4f}")
        
        st.divider()
        
        # Help section
        with st.expander("❓ About This App"):
            st.markdown("""
            **Architecture**: Supervisor Agent Pattern
            
            This app solves the "Point Solution Fatigue" problem by using
            a central orchestrator that automatically routes your queries:
            
            - 📊 **Analytics** → Cortex Analyst (structured data)
            - 📚 **Knowledge Base** → Cortex Search (RAG)
            - 💬 **General** → Conversational AI
            
            **Key Features**:
            - ✅ No tool selection needed - automatic routing
            - ✅ RCM domain terminology handling
            - ✅ Cost tracking and visibility (AIOps)
            - ✅ Optimized for token efficiency
            """)
        
        # RCM Terminology reference
        with st.expander("📖 RCM Terminology"):
            enhancer = get_enhancer()
            st.markdown(enhancer.get_terminology_summary())


def render_chat_message(message: dict):
    """
    Render a single chat message.
    
    Args:
        message: Message dictionary with role, content, and optional metadata
    """
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show debug/cost info if enabled and available
        if st.session_state.show_debug and "metadata" in message:
            render_debug_panel(message["metadata"])


def render_debug_panel(metadata: dict):
    """
    Render debug/cost visibility panel.
    
    This addresses Quadax's need for "AIOps" and cost monitoring.
    
    Args:
        metadata: Query execution metadata
    """
    with st.expander(DEBUG_PANEL_TITLE, expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Routing Decision")
            if "routing" in metadata:
                routing = metadata["routing"]
                st.write(f"**Intent**: {routing.get('intent', 'Unknown')}")
                st.write(f"**Reasoning**: {routing.get('reasoning', 'N/A')}")
                st.write(f"**Route**: {metadata.get('route', 'Unknown')}")
                st.write(f"**Model**: {metadata.get('model', 'Unknown')}")
        
        with col2:
            st.markdown("### 💰 Cost Analysis")
            if "cost_stats" in metadata:
                stats = metadata["cost_stats"]
                st.metric("Input Tokens", f"{stats.get('input_tokens', 0):,}")
                st.metric("Output Tokens", f"{stats.get('output_tokens', 0):,}")
                st.metric("Total Tokens", f"{stats.get('total_tokens', 0):,}")
                st.metric("Estimated Cost", f"${stats.get('estimated_cost', 0):.4f}")
                
                # Show warning if high token usage
                warning = get_cost_warning(stats.get('total_tokens', 0))
                if warning:
                    st.warning(warning)
        
        # Additional context for knowledge base queries
        if metadata.get("route") == "KNOWLEDGE_BASE":
            st.markdown("### 📚 Sources Retrieved")
            st.write(f"**Search Service**: {metadata.get('search_service', 'N/A')}")
            st.write(f"**Documents Retrieved**: {metadata.get('num_sources', 0)}")
            st.write(f"**Context Size**: {metadata.get('context_size', 0):,} chars")
            
            if "sources" in metadata and metadata["sources"]:
                with st.expander("View Sources"):
                    for idx, source in enumerate(metadata["sources"], 1):
                        st.write(f"**{idx}. {source.get('TITLE', 'Untitled')}**")
                        st.caption(source.get('RELATIVE_PATH', 'No path'))
        
        # SQL for analytics queries
        if metadata.get("route") == "ANALYTICS":
            st.markdown("### 🔍 SQL Generated")
            if metadata.get("sql_generated"):
                st.code(metadata["sql_generated"], language="sql")
            else:
                st.caption("*SQL generation in progress...*")


def process_user_query(user_query: str):
    """
    Process user query through the orchestrator.
    
    This is where the Supervisor Agent pattern executes.
    
    Args:
        user_query: User's natural language query
    """
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_query,
        "timestamp": datetime.now().isoformat()
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # Process query through orchestrator
    with st.chat_message("assistant"):
        with st.spinner("🤔 Analyzing query and routing to appropriate tool..."):
            # Execute orchestration
            result = st.session_state.orchestrator.process_query(user_query)
            
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
            
            # Add to query history
            st.session_state.query_history.append({
                "query": user_query,
                "intent": result.get("routing", {}).get("intent"),
                "timestamp": datetime.now().isoformat()
            })
            
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
    
    # Initialize orchestrator
    if not init_orchestrator():
        st.error("""
        ❌ **Unable to connect to Snowflake**
        
        Please configure your Snowflake credentials in `.streamlit/secrets.toml`:
        
        ```toml
        [snowflake]
        user = "your_user"
        password = "your_password"
        account = "your_account"
        warehouse = "RCM_INTELLIGENCE_WH"
        database = "RCM_AI_DEMO"
        schema = "RCM_SCHEMA"
        role = "SF_INTELLIGENCE_DEMO"
        ```
        """)
        return
    
    # Display welcome message
    render_welcome_message()
    
    # Display chat history
    for message in st.session_state.messages:
        render_chat_message(message)
    
    # Chat input (unified interface - no tool selection needed!)
    if prompt := st.chat_input("Ask me anything about RCM analytics, policies, or procedures..."):
        process_user_query(prompt)
        st.rerun()
    
    # Sample questions (for first-time users)
    if len(st.session_state.messages) == 0:
        st.markdown("### 💡 Try These Sample Questions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📊 Analytics**")
            if st.button("What is the clean claim rate by provider?", use_container_width=True):
                process_user_query("What is the clean claim rate by provider?")
                st.rerun()
            if st.button("Which payers have the highest denial rates?", use_container_width=True):
                process_user_query("Which payers have the highest denial rates?")
                st.rerun()
        
        with col2:
            st.markdown("**📚 Knowledge Base**")
            if st.button("How do I resolve a Code 45 denial?", use_container_width=True):
                process_user_query("How do I resolve a Code 45 denial in ServiceNow?")
                st.rerun()
            if st.button("What are our HIPAA compliance requirements?", use_container_width=True):
                process_user_query("Find our HIPAA compliance requirements for claims processing")
                st.rerun()
        
        with col3:
            st.markdown("**💬 General**")
            if st.button("What can you help me with?", use_container_width=True):
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

