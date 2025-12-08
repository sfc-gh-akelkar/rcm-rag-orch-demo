"""
RCM Terminology Enhancement Module
Handles healthcare revenue cycle management domain-specific terminology

This addresses Quadax's concern about RCM "slang" - specific meanings
for denials, adjustments, remit codes that generic LLMs may not understand.
"""

from typing import List, Tuple
import re
from config import RCM_TERMINOLOGY


class RCMTerminologyEnhancer:
    """
    Enhances queries and contexts with RCM-specific terminology definitions.
    
    Solves the "Domain Specificity" problem where models struggle with
    RCM slang like "remits", "write-offs", specific denial codes, etc.
    """
    
    def __init__(self):
        """Initialize with RCM terminology mappings."""
        self.terminology = RCM_TERMINOLOGY
        
        # Common RCM abbreviations that need expansion
        self.abbreviations = {
            "ccr": "clean claim rate",
            "ncr": "net collection rate",
            "carc": "claim adjustment reason code",
            "rarc": "remittance advice remark code",
            "cpt": "current procedural terminology",
            "icd": "international classification of diseases",
            "hcpcs": "healthcare common procedure coding system",
            "npi": "national provider identifier",
            "tin": "tax identification number",
            "pos": "place of service",
            "drg": "diagnosis-related group",
            "ub": "uniform billing (UB-04 claim form)",
            "cms": "centers for medicare & medicaid services",
            "hhs": "health and human services",
            "oig": "office of inspector general"
        }
        
        # Denial code patterns that need context
        self.denial_code_patterns = {
            r'\bCO-?\s*45\b': "CO-45 (Contractual Obligation - charge exceeds fee schedule)",
            r'\bPR-?\s*1\b': "PR-1 (Patient Responsibility - deductible)",
            r'\bPR-?\s*2\b': "PR-2 (Patient Responsibility - coinsurance)",
            r'\bPR-?\s*3\b': "PR-3 (Patient Responsibility - copayment)",
            r'\bCO-?\s*16\b': "CO-16 (Claim/service lacks information)",
            r'\bCO-?\s*18\b': "CO-18 (Duplicate claim/service)",
            r'\bCO-?\s*22\b': "CO-22 (Coordination of Benefits)",
            r'\bCO-?\s*27\b': "CO-27 (Expenses incurred after coverage terminated)",
            r'\bCO-?\s*29\b': "CO-29 (Time limit for filing has expired)",
            r'\bCO-?\s*50\b': "CO-50 (Non-covered service)",
            r'\bCO-?\s*96\b': "CO-96 (Non-covered charge)",
            r'\bCO-?\s*97\b': "CO-97 (Benefit maximum reached)",
            r'\bCO-?\s*109\b': "CO-109 (Claim not covered by this payer)",
        }
    
    def detect_rcm_terms(self, text: str) -> List[Tuple[str, str]]:
        """
        Detect RCM terminology in text and return definitions.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of tuples: (detected_term, definition)
        """
        detected = []
        text_lower = text.lower()
        
        # Check for direct terminology matches
        for term, definition in self.terminology.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                detected.append((term, definition))
        
        # Check for abbreviations
        for abbr, expansion in self.abbreviations.items():
            pattern = r'\b' + re.escape(abbr) + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                detected.append((abbr.upper(), expansion))
        
        # Check for denial codes
        for pattern, description in self.denial_code_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                detected.append((pattern.replace(r'\b', '').replace('\\', ''), description))
        
        return detected
    
    def enhance_query(self, query: str) -> Tuple[str, str]:
        """
        Enhance a user query with RCM terminology context.
        
        This prepends relevant terminology definitions to help the model
        understand domain-specific terms.
        
        Args:
            query: Original user query
            
        Returns:
            Tuple of (enhanced_query, context_added)
        """
        detected_terms = self.detect_rcm_terms(query)
        
        if not detected_terms:
            return query, ""
        
        # Build context string with detected terminology
        context_parts = ["**RCM Terminology Context:**"]
        for term, definition in detected_terms:
            context_parts.append(f"- **{term}**: {definition}")
        
        context = "\n".join(context_parts)
        
        # Enhanced query includes context + original query
        enhanced = f"{context}\n\n**User Query:** {query}"
        
        return enhanced, context
    
    def enhance_rag_context(self, context: str, query: str) -> str:
        """
        Enhance RAG context with RCM terminology explanations.
        
        This adds terminology definitions to the retrieved context to ensure
        the model correctly interprets RCM-specific terms in documents.
        
        Args:
            context: Retrieved document context
            query: User's original query
            
        Returns:
            Enhanced context with terminology definitions
        """
        detected_in_query = self.detect_rcm_terms(query)
        detected_in_context = self.detect_rcm_terms(context)
        
        # Combine and deduplicate
        all_detected = {
            term: definition
            for term, definition in (detected_in_query + detected_in_context)
        }
        
        if not all_detected:
            return context
        
        # Add terminology header
        terminology_section = "**RCM TERMINOLOGY REFERENCE:**\n"
        for term, definition in all_detected.items():
            terminology_section += f"- {term}: {definition}\n"
        
        return f"{terminology_section}\n---\n\n{context}"
    
    def expand_abbreviations(self, text: str) -> str:
        """
        Expand common RCM abbreviations in text.
        
        Useful for normalizing queries before sending to models.
        
        Args:
            text: Input text with potential abbreviations
            
        Returns:
            Text with abbreviations expanded
        """
        result = text
        
        for abbr, expansion in self.abbreviations.items():
            # Replace abbreviation with expansion (case-insensitive, whole word)
            pattern = r'\b' + re.escape(abbr) + r'\b'
            result = re.sub(
                pattern,
                f"{abbr.upper()} ({expansion})",
                result,
                flags=re.IGNORECASE
            )
        
        return result
    
    def get_terminology_summary(self) -> str:
        """
        Get a formatted summary of available RCM terminology.
        
        Useful for displaying in UI help text or documentation.
        
        Returns:
            Formatted markdown string of terminology
        """
        sections = []
        
        # Core terminology
        sections.append("### Common RCM Terms")
        for term, definition in sorted(self.terminology.items())[:10]:
            sections.append(f"- **{term}**: {definition}")
        
        # Abbreviations
        sections.append("\n### Common Abbreviations")
        for abbr, expansion in sorted(self.abbreviations.items())[:10]:
            sections.append(f"- **{abbr.upper()}**: {expansion}")
        
        # Denial codes
        sections.append("\n### Common Denial Codes")
        sections.append("- **CO-45**: Charge exceeds fee schedule")
        sections.append("- **PR-1**: Patient deductible")
        sections.append("- **CO-16**: Missing information")
        sections.append("- **CO-29**: Timely filing deadline passed")
        sections.append("- **CO-50**: Non-covered service")
        
        return "\n".join(sections)
    
    def suggest_corrections(self, query: str) -> List[str]:
        """
        Suggest query improvements based on RCM best practices.
        
        Args:
            query: User's query
            
        Returns:
            List of suggestion strings
        """
        suggestions = []
        query_lower = query.lower()
        
        # Suggest using specific metrics
        vague_terms = {
            "performance": "Try: 'clean claim rate' or 'denial rate' or 'net collection rate'",
            "problems": "Try: 'denial reasons' or 'claim errors' or 'payer rejections'",
            "money": "Try: 'revenue', 'reimbursement', 'accounts receivable', or 'write-offs'",
            "issues": "Try: 'denial codes', 'claim rejections', or 'appeal outcomes'"
        }
        
        for vague, suggestion in vague_terms.items():
            if vague in query_lower and not any(
                specific in query_lower 
                for specific in ["rate", "code", "revenue", "amount"]
            ):
                suggestions.append(suggestion)
        
        # Suggest adding time frames
        if any(word in query_lower for word in ["trend", "change", "growth"]):
            if not any(time in query_lower for time in ["month", "quarter", "year", "ytd"]):
                suggestions.append("💡 Consider adding a time frame: 'last month', 'Q4', 'YTD'")
        
        # Suggest specificity for payers/providers
        if "payer" in query_lower and "which" not in query_lower:
            suggestions.append("💡 Be specific: 'which payer' or name a specific payer")
        
        return suggestions


# Singleton instance
_enhancer = None

def get_enhancer() -> RCMTerminologyEnhancer:
    """Get or create the global RCM terminology enhancer instance."""
    global _enhancer
    if _enhancer is None:
        _enhancer = RCMTerminologyEnhancer()
    return _enhancer

