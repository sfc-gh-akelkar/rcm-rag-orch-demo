"""
Cost Tracking and Token Estimation Module
Provides utilities for tracking LLM token usage and estimating costs
"""

import tiktoken
from typing import Dict, Tuple
from config import MODEL_COSTS_PER_MILLION, CHARS_PER_TOKEN


class CostTracker:
    """
    Tracks token usage and estimates costs for Cortex LLM calls.
    
    Addresses Quadax's concern about 30k+ token consumption per query
    by providing visibility into token usage and cost estimates.
    """
    
    def __init__(self):
        """Initialize the cost tracker with session totals."""
        self.session_stats = {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost": 0.0,
            "queries_processed": 0,
            "by_route": {
                "ANALYTICS": {"count": 0, "tokens": 0, "cost": 0.0},
                "KNOWLEDGE_BASE": {"count": 0, "tokens": 0, "cost": 0.0},
                "GENERAL": {"count": 0, "tokens": 0, "cost": 0.0}
            }
        }
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimate token count from text.
        
        Uses tiktoken for accurate counting when possible, falls back to
        character-based estimation (1 token ≈ 4 chars).
        
        Args:
            text: Input text to count tokens for
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
            
        try:
            # Use tiktoken for accurate counting (OpenAI's tokenizer)
            # This is a good approximation for most LLMs
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except Exception:
            # Fallback to character-based estimation
            return len(text) // CHARS_PER_TOKEN
    
    @staticmethod
    def estimate_cost(
        input_tokens: int,
        output_tokens: int,
        model_name: str
    ) -> float:
        """
        Estimate cost for a model invocation.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model_name: Name of the Cortex model used
            
        Returns:
            Estimated cost in USD
        """
        # Get model pricing (default to mistral-large if unknown)
        pricing = MODEL_COSTS_PER_MILLION.get(
            model_name,
            MODEL_COSTS_PER_MILLION["mistral-large"]
        )
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
    
    def track_query(
        self,
        route: str,
        input_text: str,
        output_text: str,
        model_name: str,
        context_text: str = ""
    ) -> Dict:
        """
        Track a single query and update session statistics.
        
        Args:
            route: Intent route (ANALYTICS, KNOWLEDGE_BASE, or GENERAL)
            input_text: User query
            output_text: Model response
            model_name: Model used for generation
            context_text: Additional context (e.g., RAG chunks)
            
        Returns:
            Dictionary with query-level statistics
        """
        # Calculate tokens
        input_tokens = self.estimate_tokens(input_text + context_text)
        output_tokens = self.estimate_tokens(output_text)
        total_tokens = input_tokens + output_tokens
        
        # Calculate cost
        cost = self.estimate_cost(input_tokens, output_tokens, model_name)
        
        # Update session totals
        self.session_stats["total_input_tokens"] += input_tokens
        self.session_stats["total_output_tokens"] += output_tokens
        self.session_stats["total_cost"] += cost
        self.session_stats["queries_processed"] += 1
        
        # Update route-specific stats
        if route in self.session_stats["by_route"]:
            self.session_stats["by_route"][route]["count"] += 1
            self.session_stats["by_route"][route]["tokens"] += total_tokens
            self.session_stats["by_route"][route]["cost"] += cost
        
        # Return query-level stats
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost": cost,
            "model": model_name,
            "route": route
        }
    
    def get_session_summary(self) -> Dict:
        """
        Get summary statistics for the current session.
        
        Returns:
            Dictionary with session-level statistics
        """
        total_tokens = (
            self.session_stats["total_input_tokens"] + 
            self.session_stats["total_output_tokens"]
        )
        
        avg_tokens_per_query = (
            total_tokens / self.session_stats["queries_processed"]
            if self.session_stats["queries_processed"] > 0
            else 0
        )
        
        return {
            "total_queries": self.session_stats["queries_processed"],
            "total_input_tokens": self.session_stats["total_input_tokens"],
            "total_output_tokens": self.session_stats["total_output_tokens"],
            "total_tokens": total_tokens,
            "avg_tokens_per_query": avg_tokens_per_query,
            "total_cost": self.session_stats["total_cost"],
            "avg_cost_per_query": (
                self.session_stats["total_cost"] / 
                self.session_stats["queries_processed"]
                if self.session_stats["queries_processed"] > 0
                else 0
            ),
            "by_route": self.session_stats["by_route"]
        }
    
    def format_query_stats(self, stats: Dict) -> str:
        """
        Format query statistics for display.
        
        Args:
            stats: Query statistics dictionary from track_query()
            
        Returns:
            Formatted string for display
        """
        return f"""
**Query Statistics:**
- **Route**: {stats['route']}
- **Model**: {stats['model']}
- **Input Tokens**: {stats['input_tokens']:,}
- **Output Tokens**: {stats['output_tokens']:,}
- **Total Tokens**: {stats['total_tokens']:,}
- **Estimated Cost**: ${stats['estimated_cost']:.4f}
"""
    
    def format_session_stats(self) -> str:
        """
        Format session statistics for display.
        
        Returns:
            Formatted string for display
        """
        summary = self.get_session_summary()
        
        route_breakdown = "\n".join([
            f"  - **{route}**: {data['count']} queries, "
            f"{data['tokens']:,} tokens, ${data['cost']:.4f}"
            for route, data in summary['by_route'].items()
            if data['count'] > 0
        ])
        
        return f"""
**Session Summary:**
- **Total Queries**: {summary['total_queries']}
- **Total Tokens**: {summary['total_tokens']:,}
  - Input: {summary['total_input_tokens']:,}
  - Output: {summary['total_output_tokens']:,}
- **Average Tokens/Query**: {summary['avg_tokens_per_query']:.0f}
- **Total Cost**: ${summary['total_cost']:.4f}
- **Average Cost/Query**: ${summary['avg_cost_per_query']:.4f}

**By Route:**
{route_breakdown if route_breakdown else "  - No queries processed yet"}
"""


def get_cost_warning(tokens: int) -> str:
    """
    Generate a warning message if token usage is high.
    
    Quadax's concern: 30k+ tokens per query
    This function alerts users when approaching that threshold.
    
    Args:
        tokens: Total token count for a query
        
    Returns:
        Warning message if tokens exceed threshold, empty string otherwise
    """
    if tokens > 25000:
        return "⚠️ **High Token Usage**: This query used over 25k tokens. Consider simplifying or narrowing your question."
    elif tokens > 15000:
        return "ℹ️ **Moderate Token Usage**: This query used significant tokens. Results are comprehensive but costly."
    else:
        return ""

