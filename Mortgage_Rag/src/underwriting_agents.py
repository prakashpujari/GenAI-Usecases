from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, TypedDict
import re

from langgraph.graph import END, StateGraph

from .extract import extract_fields
from .guardrails import apply_output_guardrails
from .logger import get_logger

logger = get_logger(__name__)


REQUIRED_DOCUMENT_TYPES = {
    "pay_stub": "Pay stubs",
    "bank_statement": "Bank statements",
    "tax_return": "Tax returns (W-2/1099/1040)",
    "employment_letter": "Employment letters",
    "id_document": "ID documents (KYC)",
}


DEFAULT_THRESHOLDS = {
    "min_credit_score": 620.0,
    "max_dti": 43.0,
    "max_ltv": 80.0,
    "min_employment_months": 24.0,
}


class UnderwritingState(TypedDict, total=False):
    query: str
    borrower_documents: list[dict[str, Any]]
    policy_vector_store: Any
    thresholds: dict[str, float]
    extracted_documents: list[dict[str, Any]]
    missing_items: list[str]
    document_quality_flags: list[str]
    profile: dict[str, Any]
    inconsistencies: list[str]
    hard_rule_results: list[dict[str, str]]
    soft_rule_results: list[dict[str, str]]
    policy_citations: list[dict[str, str]]
    policy_uncertainty: str | None
    recommendation: str
    recommendation_reasons: list[str]
    output: dict[str, Any]


@dataclass(frozen=True)
class UnderwritingResult:
    recommendation: str
    summary_markdown: str
    output: dict[str, Any]


def _parse_money(value: Any) -> float | None:
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    cleaned = re.sub(r"[^0-9.\-]", "", raw)
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_number(value: Any) -> float | None:
    return _parse_money(value)


def _infer_document_type(name: str, text: str) -> str:
    content = f"{name} {text[:1000]}".lower()
    if any(token in content for token in ["paystub", "pay stub", "gross pay", "net pay"]):
        return "pay_stub"
    if any(token in content for token in ["bank statement", "statement period", "available balance"]):
        return "bank_statement"
    if any(token in content for token in ["w-2", "1099", "1040", "tax return", "wages, tips"]):
        return "tax_return"
    if any(token in content for token in ["employment letter", "verification of employment", "employer"]):
        return "employment_letter"
    if any(token in content for token in ["driver", "passport", "id", "identification", "kyc"]):
        return "id_document"
    return "unknown"


def _augment_fields(text: str, fields: dict[str, str]) -> dict[str, str]:
    augmented = dict(fields)
    patterns: dict[str, re.Pattern[str]] = {
        "borrower_name": re.compile(r"\b(?:Borrower|Name)\s*[:\-]\s*([A-Za-z ,.'-]+)", re.IGNORECASE),
        "dob": re.compile(r"\b(?:DOB|Date of Birth)\s*[:\-]\s*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})", re.IGNORECASE),
        "address": re.compile(r"\b(?:Address|Property Address)\s*[:\-]\s*(.+)", re.IGNORECASE),
        "credit_score": re.compile(r"\bCredit\s*Score\s*[:\-]\s*([0-9]{3})", re.IGNORECASE),
        "loan_amount": re.compile(r"\bLoan\s*Amount\s*[:\-]\s*\$?([0-9,]+\.?[0-9]{0,2})", re.IGNORECASE),
        "property_value": re.compile(r"\b(?:Property\s*Value|Appraised\s*Value)\s*[:\-]\s*\$?([0-9,]+\.?[0-9]{0,2})", re.IGNORECASE),
        "monthly_debt": re.compile(r"\b(?:Monthly\s*Debt|Total\s*Monthly\s*Obligations)\s*[:\-]\s*\$?([0-9,]+\.?[0-9]{0,2})", re.IGNORECASE),
        "monthly_income": re.compile(r"\b(?:Monthly\s*Income|Gross\s*Monthly\s*Income)\s*[:\-]\s*\$?([0-9,]+\.?[0-9]{0,2})", re.IGNORECASE),
        "employment_months": re.compile(r"\b(?:Employment\s*Tenure|Tenure)\s*[:\-]\s*([0-9]{1,3})\s*(?:months?|mos?)", re.IGNORECASE),
    }
    for key, pattern in patterns.items():
        if key not in augmented:
            match = pattern.search(text)
            if match:
                augmented[key] = match.group(1).strip()
    return augmented


def _document_analysis_agent(state: UnderwritingState) -> dict[str, Any]:
    logger.info("Document Analysis Agent started")
    borrower_documents = state.get("borrower_documents", [])
    extracted_documents: list[dict[str, Any]] = []
    quality_flags: list[str] = []
    seen_types: Counter[str] = Counter()

    for item in borrower_documents:
        name = str(item.get("name", "unknown.pdf"))
        text = str(item.get("text", ""))
        doc_type = _infer_document_type(name, text)
        seen_types[doc_type] += 1

        if len(text.strip()) < 150:
            quality_flags.append(f"Low-quality or unreadable content: {name}")
        if "page 1" in text.lower() and "page 2" not in text.lower() and len(text) > 1200:
            quality_flags.append(f"Potential missing pages in: {name}")

        extracted = _augment_fields(text, extract_fields(text))
        extracted_documents.append(
            {
                "name": name,
                "document_type": doc_type,
                "fields": extracted,
            }
        )

    missing_items = [
        description
        for doc_type, description in REQUIRED_DOCUMENT_TYPES.items()
        if seen_types.get(doc_type, 0) == 0
    ]

    logger.info(
        "Document Analysis Agent completed: docs=%s, missing_docs=%s, quality_flags=%s",
        len(extracted_documents),
        len(missing_items),
        len(quality_flags),
    )
    return {
        "extracted_documents": extracted_documents,
        "missing_items": missing_items,
        "document_quality_flags": quality_flags,
    }


def _income_risk_analysis_agent(state: UnderwritingState) -> dict[str, Any]:
    logger.info("Income & Risk Analysis Agent started")
    extracted_documents = state.get("extracted_documents", [])

    borrower_name = "MISSING"
    dob = "MISSING"
    address = "MISSING"
    credit_score: float | str = "MISSING"
    loan_amount: float | str = "MISSING"
    property_value: float | str = "MISSING"
    monthly_income: float | str = "MISSING"
    monthly_debt: float | str = "MISSING"
    employment_months: float | str = "MISSING"
    income_samples: list[float] = []

    for doc in extracted_documents:
        fields = doc.get("fields", {})
        if borrower_name == "MISSING" and fields.get("borrower_name"):
            borrower_name = fields["borrower_name"]
        if dob == "MISSING" and fields.get("dob"):
            dob = fields["dob"]
        if address == "MISSING" and fields.get("address"):
            address = fields["address"]

        parsed_credit = _parse_number(fields.get("credit_score"))
        if parsed_credit is not None:
            credit_score = parsed_credit

        parsed_loan = _parse_money(fields.get("loan_amount"))
        if parsed_loan is not None:
            loan_amount = parsed_loan

        parsed_property_value = _parse_money(fields.get("property_value"))
        if parsed_property_value is not None:
            property_value = parsed_property_value

        parsed_monthly_income = _parse_money(fields.get("monthly_income"))
        if parsed_monthly_income is not None:
            monthly_income = parsed_monthly_income
            income_samples.append(parsed_monthly_income)

        parsed_gross_pay = _parse_money(fields.get("gross_pay"))
        if parsed_gross_pay is not None:
            income_samples.append(parsed_gross_pay * 2)
            if monthly_income == "MISSING":
                monthly_income = parsed_gross_pay * 2

        parsed_w2 = _parse_money(fields.get("w2_box1_wages"))
        if parsed_w2 is not None:
            annualized = parsed_w2 / 12.0
            income_samples.append(annualized)
            if monthly_income == "MISSING":
                monthly_income = annualized

        parsed_monthly_debt = _parse_money(fields.get("monthly_debt"))
        if parsed_monthly_debt is not None:
            monthly_debt = parsed_monthly_debt

        parsed_employment_months = _parse_number(fields.get("employment_months"))
        if parsed_employment_months is not None:
            employment_months = parsed_employment_months

    dti_ratio: float | str = "MISSING"
    ltv_ratio: float | str = "MISSING"
    inconsistencies: list[str] = []

    if isinstance(monthly_income, float) and isinstance(monthly_debt, float) and monthly_income > 0:
        dti_ratio = (monthly_debt / monthly_income) * 100.0

    if isinstance(loan_amount, float) and isinstance(property_value, float) and property_value > 0:
        ltv_ratio = (loan_amount / property_value) * 100.0

    if len(income_samples) >= 2:
        low = min(income_samples)
        high = max(income_samples)
        if low > 0 and ((high - low) / low) > 0.15:
            inconsistencies.append("Income inconsistency across documents (>15% variance)")

    profile = {
        "borrower_name": borrower_name,
        "dob": dob,
        "address": address,
        "credit_score": credit_score,
        "monthly_income": monthly_income,
        "monthly_debt": monthly_debt,
        "dti_ratio": dti_ratio,
        "loan_amount": loan_amount,
        "property_value": property_value,
        "ltv_ratio": ltv_ratio,
        "employment_months": employment_months,
    }

    logger.info("Income & Risk Analysis Agent completed")
    return {
        "profile": profile,
        "inconsistencies": inconsistencies,
    }


def _policy_retrieval_agent(state: UnderwritingState) -> dict[str, Any]:
    logger.info("Policy Retrieval Agent started")
    query = state.get("query", "")
    vector_store = state.get("policy_vector_store")
    citations: list[dict[str, str]] = []
    uncertainty: str | None = None

    if vector_store is None:
        uncertainty = "Policy retrieval unavailable; refer for manual policy verification"
        logger.warning("No policy vector store provided")
        return {"policy_citations": citations, "policy_uncertainty": uncertainty}

    try:
        retrieved = vector_store.similarity_search_with_score(query or "mortgage underwriting policy", k=5)
        docs = [doc for doc, _ in retrieved]
        texts = [doc.page_content for doc in docs]
        sanitized_texts, validation = apply_output_guardrails(texts)

        if not validation.passed:
            uncertainty = "Policy retrieval validation failed; manual review required"
            logger.warning("Policy retrieval output guardrail failed: %s", validation.reason)

        for (doc, score), sanitized_text in zip(retrieved, sanitized_texts):
            source = str(doc.metadata.get("source", "Unknown policy source"))
            section = str(doc.metadata.get("section", doc.metadata.get("chunk", "N/A")))
            snippet = sanitized_text[:280].replace("\n", " ").strip()
            citations.append(
                {
                    "source": source,
                    "section": section,
                    "score": f"{score:.4f}",
                    "snippet": snippet,
                }
            )

        if not citations:
            uncertainty = "No policy citations retrieved; refer for human underwriter review"
    except Exception as exc:
        logger.error("Policy retrieval failed: %s", exc, exc_info=True)
        uncertainty = "Policy retrieval error; refer for manual policy verification"

    logger.info("Policy Retrieval Agent completed: citations=%s", len(citations))
    return {
        "policy_citations": citations,
        "policy_uncertainty": uncertainty,
    }


def _rules_engine_agent(state: UnderwritingState) -> dict[str, Any]:
    logger.info("Rules Engine Agent started")
    profile = state.get("profile", {})
    thresholds = {**DEFAULT_THRESHOLDS, **state.get("thresholds", {})}

    hard_rules: list[dict[str, str]] = []
    soft_rules: list[dict[str, str]] = []

    def evaluate_hard(rule_name: str, value: Any, comparator: str, threshold: float) -> None:
        if value == "MISSING":
            hard_rules.append(
                {
                    "rule": rule_name,
                    "status": "FAIL",
                    "reason": "MISSING",
                    "type": "HARD",
                }
            )
            return

        passed = False
        numeric_value = float(value)
        if comparator == ">=":
            passed = numeric_value >= threshold
        elif comparator == "<=":
            passed = numeric_value <= threshold

        hard_rules.append(
            {
                "rule": rule_name,
                "status": "PASS" if passed else "FAIL",
                "reason": f"value={numeric_value:.2f}, threshold {comparator} {threshold:.2f}",
                "type": "HARD",
            }
        )

    evaluate_hard("Minimum credit score", profile.get("credit_score", "MISSING"), ">=", thresholds["min_credit_score"])
    evaluate_hard("Maximum DTI", profile.get("dti_ratio", "MISSING"), "<=", thresholds["max_dti"])
    evaluate_hard("Maximum LTV", profile.get("ltv_ratio", "MISSING"), "<=", thresholds["max_ltv"])

    employment_months = profile.get("employment_months", "MISSING")
    if employment_months == "MISSING":
        soft_rules.append(
            {
                "rule": "Employment stability",
                "status": "REVIEW",
                "reason": "MISSING tenure evidence",
                "type": "SOFT",
            }
        )
    else:
        soft_rules.append(
            {
                "rule": "Employment stability",
                "status": "PASS" if float(employment_months) >= thresholds["min_employment_months"] else "REVIEW",
                "reason": f"tenure_months={float(employment_months):.0f}, guideline >= {thresholds['min_employment_months']:.0f}",
                "type": "SOFT",
            }
        )

    if state.get("missing_items"):
        soft_rules.append(
            {
                "rule": "Documentation completeness",
                "status": "REVIEW",
                "reason": "; ".join(state["missing_items"]),
                "type": "SOFT",
            }
        )

    logger.info("Rules Engine Agent completed: hard=%s, soft=%s", len(hard_rules), len(soft_rules))
    return {
        "hard_rule_results": hard_rules,
        "soft_rule_results": soft_rules,
    }


def _recommendation_agent(state: UnderwritingState) -> dict[str, Any]:
    logger.info("Recommendation Agent started")
    hard_rules = state.get("hard_rule_results", [])
    soft_rules = state.get("soft_rule_results", [])
    policy_uncertainty = state.get("policy_uncertainty")
    missing_items = state.get("missing_items", [])
    quality_flags = state.get("document_quality_flags", [])
    inconsistencies = state.get("inconsistencies", [])
    profile = state.get("profile", {})
    citations = state.get("policy_citations", [])

    hard_failures = [r for r in hard_rules if r.get("status") == "FAIL"]
    review_soft = [r for r in soft_rules if r.get("status") == "REVIEW"]

    reasons: list[str] = []
    if hard_failures:
        reasons.extend([f"Hard rule failed: {item['rule']} ({item['reason']})" for item in hard_failures])
    if missing_items:
        reasons.append("Required documentation missing")
    if quality_flags:
        reasons.append("Document quality issues detected")
    if inconsistencies:
        reasons.extend(inconsistencies)
    if policy_uncertainty:
        reasons.append(policy_uncertainty)

    if hard_failures and not missing_items and not policy_uncertainty:
        recommendation = "Decline"
    elif reasons or review_soft:
        recommendation = "Refer"
    else:
        recommendation = "Approve"

    if recommendation == "Approve" and not citations:
        recommendation = "Refer"
        reasons.append("No policy citations available for traceability")

    if not reasons:
        reasons.append("All evaluated hard rules passed and no material risk flags identified")

    output = {
        "decision": f"{recommendation} (recommendation only; requires human underwriter approval)",
        "profile": profile,
        "hard_rules": hard_rules,
        "soft_guidelines": soft_rules,
        "risk_factors": reasons,
        "policy_citations": citations,
        "missing": [
            key for key, value in profile.items() if value == "MISSING"
        ] + missing_items,
    }

    logger.info("Recommendation Agent completed: recommendation=%s", recommendation)
    return {
        "recommendation": recommendation,
        "recommendation_reasons": reasons,
        "output": output,
    }


def _build_graph():
    workflow = StateGraph(UnderwritingState)
    workflow.add_node("document_analysis", _document_analysis_agent)
    workflow.add_node("income_risk_analysis", _income_risk_analysis_agent)
    workflow.add_node("policy_retrieval", _policy_retrieval_agent)
    workflow.add_node("rules_engine", _rules_engine_agent)
    workflow.add_node("recommendation", _recommendation_agent)

    workflow.set_entry_point("document_analysis")
    workflow.add_edge("document_analysis", "income_risk_analysis")
    workflow.add_edge("income_risk_analysis", "policy_retrieval")
    workflow.add_edge("policy_retrieval", "rules_engine")
    workflow.add_edge("rules_engine", "recommendation")
    workflow.add_edge("recommendation", END)
    return workflow.compile()


def run_underwriting_workflow(
    query: str,
    borrower_documents: list[dict[str, Any]],
    policy_vector_store: Any,
    thresholds: dict[str, float] | None = None,
) -> UnderwritingResult:
    logger.info("Running underwriting workflow")
    graph = _build_graph()
    state: UnderwritingState = {
        "query": query,
        "borrower_documents": borrower_documents,
        "policy_vector_store": policy_vector_store,
        "thresholds": thresholds or DEFAULT_THRESHOLDS,
    }
    result_state = graph.invoke(state)
    output = result_state["output"]

    summary_markdown = format_underwriting_summary(output)
    return UnderwritingResult(
        recommendation=result_state["recommendation"],
        summary_markdown=summary_markdown,
        output=output,
    )


def format_underwriting_summary(output: dict[str, Any]) -> str:
    decision = output.get("decision", "Refer (recommendation only; requires human underwriter approval)")
    profile = output.get("profile", {})
    hard_rules = output.get("hard_rules", [])
    soft_rules = output.get("soft_guidelines", [])
    risks = output.get("risk_factors", [])
    citations = output.get("policy_citations", [])
    missing_items = output.get("missing", [])

    dti_value = profile.get("dti_ratio", "MISSING")
    ltv_value = profile.get("ltv_ratio", "MISSING")
    dti_text = "MISSING" if dti_value == "MISSING" else f"{float(dti_value):.2f}%"
    ltv_text = "MISSING" if ltv_value == "MISSING" else f"{float(ltv_value):.2f}%"

    lines = [
        "**Underwriting Decision Summary (Recommendation Only)**",
        f"- **Recommendation:** {decision}",
        "- **Borrower Snapshot:**",
        f"  - Credit Score: {profile.get('credit_score', 'MISSING')}",
        f"  - DTI: {dti_text}",
        f"  - LTV: {ltv_text}",
        "- **Hard Rules (Must Pass):**",
    ]

    for item in hard_rules:
        lines.append(f"  - {item.get('rule')}: {item.get('status')} ({item.get('reason')})")

    lines.append("- **Soft Guidelines (Underwriter Judgment):**")
    for item in soft_rules:
        lines.append(f"  - {item.get('rule')}: {item.get('status')} ({item.get('reason')})")

    lines.append("- **Key Risks / Reasons:**")
    for risk in risks:
        lines.append(f"  - {risk}")

    lines.append("- **Policy Citations:**")
    if citations:
        for citation in citations:
            lines.append(
                f"  - Source: {citation.get('source')} | Section: {citation.get('section')} | Evidence: {citation.get('snippet')}"
            )
    else:
        lines.append("  - MISSING")

    if missing_items:
        lines.append("- **Missing Data / Docs:**")
        for item in missing_items:
            lines.append(f"  - {item}")

    lines.append("- **Control Note:** This system provides decision support only and never makes final credit decisions.")
    return "\n".join(lines)
