from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .schemas import AUSRequest, RuleEvaluation


@dataclass(frozen=True)
class RuleDefinition:
    name: str
    severity: str
    evaluator: Callable[[AUSRequest], tuple[bool, str]]


def _evaluate_credit_program_rule(data: AUSRequest) -> tuple[bool, str]:
    if data.loan_type == "Conventional" and data.credit_score < 620:
        return False, "Conventional loans require minimum credit score 620"
    return True, "Program credit rule satisfied"


def _evaluate_max_dti_rule(data: AUSRequest) -> tuple[bool, str]:
    if data.dti > 43:
        return False, f"DTI {data.dti:.2f}% exceeds maximum 43.00%"
    return True, "DTI rule satisfied"


def _evaluate_streamlined_ltv_rule(data: AUSRequest) -> tuple[bool, str]:
    if data.ltv > 80:
        return False, f"LTV {data.ltv:.2f}% exceeds streamlined threshold 80.00%"
    return True, "LTV streamlined rule satisfied"


def _evaluate_strong_risk_profile_rule(data: AUSRequest) -> tuple[bool, str]:
    passed = data.credit_score >= 740 and data.dti <= 30 and data.ltv <= 80
    if passed:
        return True, "Strong risk profile met (credit≥740, dti≤30, ltv≤80)"
    return False, "Strong risk profile not fully met"


def get_rule_set() -> list[RuleDefinition]:
    return [
        RuleDefinition(
            name="Program minimum credit (Conventional)",
            severity="program",
            evaluator=_evaluate_credit_program_rule,
        ),
        RuleDefinition(
            name="Maximum DTI",
            severity="moderate",
            evaluator=_evaluate_max_dti_rule,
        ),
        RuleDefinition(
            name="Maximum LTV for streamlined",
            severity="moderate",
            evaluator=_evaluate_streamlined_ltv_rule,
        ),
        RuleDefinition(
            name="Strong risk profile",
            severity="advisory",
            evaluator=_evaluate_strong_risk_profile_rule,
        ),
    ]


def evaluate_rules(data: AUSRequest) -> list[RuleEvaluation]:
    evaluations: list[RuleEvaluation] = []
    for rule in get_rule_set():
        passed, reason = rule.evaluator(data)
        evaluations.append(
            RuleEvaluation(
                rule=rule.name,
                passed=passed,
                severity=rule.severity,
                reason=reason,
            )
        )
    return evaluations
