"""
Orchestrator Module - Supervisor Agent Pattern
Implements intelligent routing and orchestration of user queries

This is the core solution to Quadax's "Point Solution Fatigue" problem.
Instead of users choosing between tools, a central supervisor agent routes
queries to the appropriate backend (Cortex Analyst, Cortex Search, or General).
"""

import snowflake.connector
from snowflake.cortex import Complete
from typing import Dict, Tuple, Optional
import json
import re

from config import (
    ROUTER_MODEL,
    ANALYST_MODEL,
    RAG_MODEL,
    GENERAL_MODEL,
    INTENT_ANALYTICS,
    INTENT_KNOWLEDGE_BASE,
    INTENT_GENERAL,
    INTENT_CLASSIFICATION_PROMPT,
    RAG_SYSTEM_PROMPT,
    ANALYTICS_SYSTEM_PROMPT,
    GENERAL_SYSTEM_PROMPT,
    CORTEX_SEARCH_SERVICES,
    DEFAULT_SEARCH_SERVICE,
    SEMANTIC_VIEWS,
    DEFAULT_SEMANTIC_VIEW,
    MAX_SEARCH_RESULTS
)
from rcm_terminology import get_enhancer
from cost_tracker import CostTracker


class RCMOrchestrator:
    """
    Supervisor Agent that orchestrates query routing and execution.
    
    Architecture Pattern:
    ┌─────────────────────┐
    │   User Query        │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │  Intent Classifier  │  ← Lightweight LLM (llama3.2-3b)
    │  (Supervisor)       │
    └──────────┬──────────┘
               │
         ┌─────┴─────┬──────────────┐
         │           │              │
         ▼           ▼              ▼
    ┌────────┐  ┌─────────┐  ┌──────────┐
    │Analytics│  │Knowledge│  │ General  │
    │(Analyst)│  │  (RAG)  │  │   Chat   │
    └────────┘  └─────────┘  └──────────┘
    """
    
    def __init__(self, snowflake_connection: snowflake.connector.SnowflakeConnection):
        """
        Initialize the orchestrator with Snowflake connection.
        
        Args:
            snowflake_connection: Active Snowflake connection
        """
        self.conn = snowflake_connection
        self.cursor = self.conn.cursor()
        self.enhancer = get_enhancer()
        self.cost_tracker = CostTracker()
    
    def determine_intent(self, user_query: str) -> Tuple[str, str]:
        """
        Classify user intent using lightweight LLM.
        
        This is the "Supervisor" that decides which tool to use.
        Uses a small, fast model (llama3.2-3b) to minimize latency and cost.
        
        Args:
            user_query: The user's natural language query
            
        Returns:
            Tuple of (intent, reasoning)
            intent: One of ANALYTICS, KNOWLEDGE_BASE, or GENERAL
            reasoning: Brief explanation of classification
        """
        # Enhance query with RCM terminology context
        enhanced_query, terminology_context = self.enhancer.enhance_query(user_query)
        
        # Build classification prompt
        prompt = INTENT_CLASSIFICATION_PROMPT.format(query=enhanced_query)
        
        try:
            # Use lightweight model for fast classification
            response = Complete(
                model=ROUTER_MODEL,
                prompt=prompt,
                session=self.conn
            )
            
            # Parse response (should be single word: ANALYTICS, KNOWLEDGE_BASE, or GENERAL)
            intent_raw = response.strip().upper()
            
            # Extract intent (handle cases where model adds explanation)
            if INTENT_ANALYTICS in intent_raw:
                intent = INTENT_ANALYTICS
                reasoning = "Query requires data analysis, metrics, or calculations"
            elif INTENT_KNOWLEDGE_BASE in intent_raw:
                intent = INTENT_KNOWLEDGE_BASE
                reasoning = "Query asks about policies, procedures, or documentation"
            elif INTENT_GENERAL in intent_raw:
                intent = INTENT_GENERAL
                reasoning = "General conversation or clarification"
            else:
                # Default to general if unclear
                intent = INTENT_GENERAL
                reasoning = f"Unable to classify clearly (raw: {intent_raw})"
            
            # Track cost of classification
            self.cost_tracker.track_query(
                route="ROUTER",
                input_text=prompt,
                output_text=response,
                model_name=ROUTER_MODEL,
                context_text=""
            )
            
            return intent, reasoning
            
        except Exception as e:
            # Fallback to keyword-based classification
            return self._fallback_intent_classification(user_query)
    
    def _fallback_intent_classification(self, query: str) -> Tuple[str, str]:
        """
        Fallback intent classification using keywords.
        
        Used when LLM classification fails.
        
        Args:
            query: User query
            
        Returns:
            Tuple of (intent, reasoning)
        """
        query_lower = query.lower()
        
        # Check for analytics keywords
        analytics_keywords = [
            "how many", "what is the", "show me", "calculate", "average",
            "total", "count", "rate", "percentage", "top", "trend",
            "compare", "revenue", "claim", "denial", "payer", "provider"
        ]
        
        knowledge_keywords = [
            "how do i", "how to", "what does", "explain", "policy",
            "procedure", "documentation", "servicenow", "resolve",
            "compliance", "guideline"
        ]
        
        analytics_score = sum(1 for kw in analytics_keywords if kw in query_lower)
        knowledge_score = sum(1 for kw in knowledge_keywords if kw in query_lower)
        
        if analytics_score > knowledge_score:
            return INTENT_ANALYTICS, "Keyword-based: analytics terms detected"
        elif knowledge_score > 0:
            return INTENT_KNOWLEDGE_BASE, "Keyword-based: knowledge/policy terms detected"
        else:
            return INTENT_GENERAL, "Keyword-based: no specific intent detected"
    
    def execute_analytics_query(self, user_query: str) -> Dict:
        """
        Execute analytics query using Cortex Analyst.
        
        Routes to structured data analysis via semantic views.
        
        Args:
            user_query: User's query
            
        Returns:
            Dictionary with response, SQL, data, and metadata
        """
        try:
            # Enhance query with RCM context
            enhanced_query, _ = self.enhancer.enhance_query(user_query)
            
            # Build analyst prompt
            prompt = ANALYTICS_SYSTEM_PROMPT.format(query=enhanced_query)
            
            # Call Cortex Analyst (simplified - in production, use proper Analyst API)
            # For now, we'll use Complete with analytics-focused prompt
            response = Complete(
                model=ANALYST_MODEL,
                prompt=prompt,
                session=self.conn
            )
            
            # Track cost
            stats = self.cost_tracker.track_query(
                route=INTENT_ANALYTICS,
                input_text=prompt,
                output_text=response,
                model_name=ANALYST_MODEL,
                context_text=""
            )
            
            return {
                "success": True,
                "response": response,
                "route": INTENT_ANALYTICS,
                "model": ANALYST_MODEL,
                "semantic_view": DEFAULT_SEMANTIC_VIEW,
                "sql_generated": None,  # In production, extract from Analyst response
                "data": None,           # In production, execute SQL and return results
                "cost_stats": stats
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "route": INTENT_ANALYTICS,
                "response": f"I encountered an error processing your analytics query: {str(e)}"
            }
    
    def execute_knowledge_base_query(self, user_query: str) -> Dict:
        """
        Execute knowledge base query using Cortex Search (RAG).
        
        Routes to document search and retrieval.
        
        Args:
            user_query: User's query
            
        Returns:
            Dictionary with response, sources, and metadata
        """
        try:
            # Step 1: Retrieve relevant documents using Cortex Search
            search_results = self._cortex_search(user_query)
            
            # Step 2: Build context from search results
            context = self._build_rag_context(search_results)
            
            # Step 3: Enhance context with RCM terminology
            enhanced_context = self.enhancer.enhance_rag_context(context, user_query)
            
            # Step 4: Generate response using RAG model
            prompt = RAG_SYSTEM_PROMPT.format(
                context=enhanced_context,
                query=user_query
            )
            
            response = Complete(
                model=RAG_MODEL,
                prompt=prompt,
                session=self.conn
            )
            
            # Track cost
            stats = self.cost_tracker.track_query(
                route=INTENT_KNOWLEDGE_BASE,
                input_text=prompt,
                output_text=response,
                model_name=RAG_MODEL,
                context_text=context
            )
            
            return {
                "success": True,
                "response": response,
                "route": INTENT_KNOWLEDGE_BASE,
                "model": RAG_MODEL,
                "search_service": DEFAULT_SEARCH_SERVICE,
                "sources": search_results,
                "num_sources": len(search_results),
                "context_size": len(context),
                "cost_stats": stats
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "route": INTENT_KNOWLEDGE_BASE,
                "response": f"I encountered an error searching the knowledge base: {str(e)}"
            }
    
    def execute_general_query(self, user_query: str) -> Dict:
        """
        Execute general conversation query.
        
        Routes to lightweight conversational model.
        
        Args:
            user_query: User's query
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            prompt = GENERAL_SYSTEM_PROMPT.format(query=user_query)
            
            response = Complete(
                model=GENERAL_MODEL,
                prompt=prompt,
                session=self.conn
            )
            
            # Track cost
            stats = self.cost_tracker.track_query(
                route=INTENT_GENERAL,
                input_text=prompt,
                output_text=response,
                model_name=GENERAL_MODEL,
                context_text=""
            )
            
            return {
                "success": True,
                "response": response,
                "route": INTENT_GENERAL,
                "model": GENERAL_MODEL,
                "cost_stats": stats
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "route": INTENT_GENERAL,
                "response": f"I encountered an error: {str(e)}"
            }
    
    def _cortex_search(self, query: str, service_name: str = None) -> list:
        """
        Execute Cortex Search query.
        
        Args:
            query: Search query
            service_name: Specific search service (defaults to knowledge base)
            
        Returns:
            List of search results
        """
        if service_name is None:
            service_name = DEFAULT_SEARCH_SERVICE
        
        try:
            # Build search query using modern SNOWFLAKE.CORTEX.SEARCH_PREVIEW syntax
            search_sql = f"""
            SELECT 
                SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
                    '{service_name}',
                    '{{
                        "query": "{self._escape_json_string(query)}",
                        "columns": ["RELATIVE_PATH", "TITLE", "FILE_URL"],
                        "limit": {MAX_SEARCH_RESULTS}
                    }}'
                ) as results
            """
            
            self.cursor.execute(search_sql)
            results = self.cursor.fetchone()
            
            if results and results[0]:
                # Parse JSON results
                search_data = json.loads(results[0]) if isinstance(results[0], str) else results[0]
                
                # Extract results from response
                if isinstance(search_data, dict) and 'results' in search_data:
                    return search_data['results'][:MAX_SEARCH_RESULTS]
                elif isinstance(search_data, list):
                    return search_data[:MAX_SEARCH_RESULTS]
            
            return []
            
        except Exception as e:
            print(f"Cortex Search error: {e}")
            return []
    
    def _build_rag_context(self, search_results: list) -> str:
        """
        Build context string from search results.
        
        Args:
            search_results: List of search result dictionaries
            
        Returns:
            Formatted context string
        """
        if not search_results:
            return "No relevant documents found."
        
        context_parts = []
        for idx, result in enumerate(search_results[:MAX_SEARCH_RESULTS], 1):
            # Extract fields (handle different result formats)
            title = result.get('TITLE', result.get('title', 'Untitled'))
            content = result.get('chunk', result.get('CONTENT', result.get('content', '')))
            path = result.get('RELATIVE_PATH', result.get('relative_path', ''))
            
            context_parts.append(f"""
**Document {idx}: {title}**
Source: {path}
Content: {content[:500]}...
""")
        
        return "\n---\n".join(context_parts)
    
    def _escape_json_string(self, text: str) -> str:
        """Escape special characters for JSON string."""
        return text.replace('"', '\\"').replace('\n', ' ').replace('\r', '')
    
    def process_query(self, user_query: str) -> Dict:
        """
        Main orchestration method - routes and executes query.
        
        This is the entry point for the Supervisor Agent pattern.
        
        Args:
            user_query: User's natural language query
            
        Returns:
            Dictionary with response and full execution metadata
        """
        # Step 1: Determine intent (routing decision)
        intent, reasoning = self.determine_intent(user_query)
        
        # Step 2: Route to appropriate handler
        if intent == INTENT_ANALYTICS:
            result = self.execute_analytics_query(user_query)
        elif intent == INTENT_KNOWLEDGE_BASE:
            result = self.execute_knowledge_base_query(user_query)
        else:
            result = self.execute_general_query(user_query)
        
        # Step 3: Add routing metadata
        result["routing"] = {
            "intent": intent,
            "reasoning": reasoning,
            "query": user_query
        }
        
        # Step 4: Add session statistics
        result["session_stats"] = self.cost_tracker.get_session_summary()
        
        return result
    
    def get_session_summary(self) -> Dict:
        """Get current session statistics."""
        return self.cost_tracker.get_session_summary()

