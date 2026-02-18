from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class GuardrailResult:
    """Result of a guardrail check"""
    passed: bool
    reason: Optional[str] = None
    suggested_action: Optional[str] = None


class InputGuardrails:
    """Guardrails for user input validation"""
    
    MAX_QUERY_LENGTH = 500
    MIN_QUERY_LENGTH = 3
    
    # Patterns that might indicate prompt injection attempts
    PROMPT_INJECTION_PATTERNS = [
        r"ignore\s+.{0,30}(instructions?|prompts?|rules?|commands?)",
        r"disregard\s+.{0,30}(instructions?|prompts?|rules?|commands?)",
        r"forget\s+.{0,30}(instructions?|prompts?|rules?|commands?)",
        r"you\s+are\s+(now|a)\s+(?!mortgage|loan|financial)",  # Try to change role
        r"(system\s+prompt|system\s+message)",
        r"(admin|developer|debug)\s+mode",
        r"jailbreak",
        r"pretend\s+(you|to)\s+(are|be)",
        r"act\s+as\s+(if|a|an)\s+(?!mortgage|loan|financial)",
    ]
    
    # Inappropriate content patterns
    INAPPROPRIATE_PATTERNS = [
        r"\b(hack|exploit|bypass|malicious|illegal)\b",
        r"\b(password|credential|token|secret)\b.*\b(steal|extract|get)\b",
    ]
    
    # Allowed topics - mortgage and finance related
    ALLOWED_TOPICS_KEYWORDS = [
        "mortgage", "loan", "income", "salary", "employment", "w-2", "paystub",
        "tax", "payment", "down payment", "interest", "rate", "credit",
        "property", "home", "house", "address", "employer", "year", "amount",
        "document", "refinance", "qualification", "bank", "account", "finance",
    ]
    
    @classmethod
    def validate_query(cls, query: str) -> GuardrailResult:
        """Validate a search query against all guardrails"""
        
        # Check for empty or whitespace-only queries
        if not query or not query.strip():
            return GuardrailResult(
                passed=False,
                reason="Query is empty",
                suggested_action="Please enter a search query"
            )
        
        # Check length constraints
        if len(query) < cls.MIN_QUERY_LENGTH:
            return GuardrailResult(
                passed=False,
                reason=f"Query too short (minimum {cls.MIN_QUERY_LENGTH} characters)",
                suggested_action="Please enter a more detailed query"
            )
        
        if len(query) > cls.MAX_QUERY_LENGTH:
            return GuardrailResult(
                passed=False,
                reason=f"Query too long (maximum {cls.MAX_QUERY_LENGTH} characters)",
                suggested_action=f"Please shorten your query to under {cls.MAX_QUERY_LENGTH} characters"
            )
        
        # Check for prompt injection attempts
        for pattern in cls.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return GuardrailResult(
                    passed=False,
                    reason="Potential prompt injection detected",
                    suggested_action="Please rephrase your query without system instructions"
                )
        
        # Check for inappropriate content
        for pattern in cls.INAPPROPRIATE_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return GuardrailResult(
                    passed=False,
                    reason="Query contains inappropriate or suspicious content",
                    suggested_action="Please use appropriate language related to mortgage document search"
                )
        
        # Check topic relevance (warn but don't block)
        query_lower = query.lower()
        has_relevant_keyword = any(keyword in query_lower for keyword in cls.ALLOWED_TOPICS_KEYWORDS)
        
        if not has_relevant_keyword:
            # This is a soft warning, still passes but with a message
            return GuardrailResult(
                passed=True,
                reason="Query may not be relevant to mortgage documents",
                suggested_action="For best results, search for mortgage-related information (income, loans, employment, etc.)"
            )
        
        return GuardrailResult(passed=True)


class OutputGuardrails:
    """Guardrails for output validation"""
    
    @staticmethod
    def validate_search_results(results: list[str]) -> GuardrailResult:
        """Validate search results don't contain unreacted PII"""
        from src.pii import contains_pii
        
        for idx, result in enumerate(results):
            if contains_pii(result):
                return GuardrailResult(
                    passed=False,
                    reason=f"PII detected in search result {idx + 1}",
                    suggested_action="Results have been filtered for safety"
                )
        
        return GuardrailResult(passed=True)
    
    @staticmethod
    def sanitize_result(text: str) -> str:
        """Apply additional sanitization to results"""
        from src.pii import redact_pii
        
        # Double-check PII redaction
        sanitized = redact_pii(text)
        
        # Remove any potential code injection
        sanitized = sanitized.replace("<script>", "").replace("</script>", "")
        sanitized = sanitized.replace("javascript:", "")
        
        return sanitized


def apply_input_guardrails(query: str) -> GuardrailResult:
    """Apply all input guardrails to a query"""
    return InputGuardrails.validate_query(query)


def apply_output_guardrails(results: list[str]) -> tuple[list[str], GuardrailResult]:
    """Apply output guardrails and return sanitized results"""
    # Validate results
    validation = OutputGuardrails.validate_search_results(results)
    
    # Sanitize all results
    sanitized_results = [OutputGuardrails.sanitize_result(result) for result in results]
    
    return sanitized_results, validation
