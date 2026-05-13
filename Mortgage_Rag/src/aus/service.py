from __future__ import annotations

from .schemas import AUSFinding, AUSRequest, AUSResponse
from .rules import evaluate_rules


def _base_required_documents() -> list[str]:
    return [
        "Income documentation (W-2s / pay stubs / tax returns)",
        "Asset documentation (bank statements, reserves verification)",
        "Employment verification (VOE / employer letter)",
        "Credit report",
        "Property appraisal",
        "Government-issued ID",
        "Signed loan application (1003)",
    ]


def _additional_documents(data: AUSRequest) -> list[str]:
    docs: list[str] = []
    if data.occupancy_type == "Investment":
        docs.append("Lease agreements or projected rental income support")
    if data.loan_type in {"FHA", "VA"}:
        docs.append(f"{data.loan_type} program-specific eligibility documents")
    if data.reserves < 2:
        docs.append("Letter of explanation for limited reserves")
    return docs


def evaluate_aus(data: AUSRequest) -> AUSResponse:
    evaluations = evaluate_rules(data)

    failed_program = [rule for rule in evaluations if not rule.passed and rule.severity == "program"]
    failed_moderate = [rule for rule in evaluations if not rule.passed and rule.severity == "moderate"]

    strong_profile = data.credit_score >= 740 and data.dti <= 30 and data.ltv <= 80

    reasons: list[str] = []
    if strong_profile and not failed_program and not failed_moderate:
        finding = AUSFinding.APPROVE_ELIGIBLE
        reasons.append("Strong profile satisfies streamlined AUS approval criteria")
    elif failed_program:
        finding = AUSFinding.REFER_INELIGIBLE
        reasons.extend(rule.reason for rule in failed_program)
        if failed_moderate:
            reasons.extend(rule.reason for rule in failed_moderate)
    elif len(failed_moderate) <= 1:
        finding = AUSFinding.REFER_ELIGIBLE
        if failed_moderate:
            reasons.append("One moderate risk rule failed; file requires manual underwriter review")
            reasons.extend(rule.reason for rule in failed_moderate)
        else:
            reasons.append("Does not meet streamlined approval profile; refer for underwriter discretion")
    else:
        finding = AUSFinding.REFER_INELIGIBLE
        reasons.append("Multiple moderate risk rules failed beyond eligible refer tolerance")
        reasons.extend(rule.reason for rule in failed_moderate)

    required_documents = _base_required_documents() + _additional_documents(data)

    return AUSResponse(
        finding=finding,
        reasons=reasons,
        required_documents=required_documents,
        rule_evaluations=evaluations,
    )
