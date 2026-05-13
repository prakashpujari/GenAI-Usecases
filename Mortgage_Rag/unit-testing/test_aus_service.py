from __future__ import annotations

from pydantic import ValidationError

from src.aus.schemas import AUSRequest, AUSFinding
from src.aus.service import evaluate_aus


def _base_request() -> AUSRequest:
    return AUSRequest(
        credit_score=742,
        dti=29.5,
        ltv=75.0,
        income=120000,
        loan_amount=420000,
        property_value=560000,
        loan_type="Conventional",
        reserves=6,
        occupancy_type="Primary",
    )


def test_approve_eligible_when_strong_profile() -> None:
    result = evaluate_aus(_base_request())

    assert result.finding == AUSFinding.APPROVE_ELIGIBLE
    assert any("Strong profile" in reason for reason in result.reasons)
    assert len(result.required_documents) >= 7


def test_refer_eligible_when_one_moderate_rule_fails() -> None:
    req = _base_request().model_copy(update={"dti": 44.0})
    result = evaluate_aus(req)

    assert result.finding == AUSFinding.REFER_ELIGIBLE
    assert any("One moderate risk rule failed" in reason for reason in result.reasons)


def test_refer_ineligible_when_program_rule_fails() -> None:
    req = _base_request().model_copy(update={"credit_score": 600, "loan_type": "Conventional"})
    result = evaluate_aus(req)

    assert result.finding == AUSFinding.REFER_INELIGIBLE
    assert any("minimum credit score 620" in reason for reason in result.reasons)


def test_refer_ineligible_when_multiple_moderate_rules_fail() -> None:
    req = _base_request().model_copy(update={"dti": 46.0, "ltv": 85.0, "loan_amount": 476000, "property_value": 560000})
    result = evaluate_aus(req)

    assert result.finding == AUSFinding.REFER_INELIGIBLE
    assert any("Multiple moderate risk rules failed" in reason for reason in result.reasons)


def test_additional_documents_for_investment_and_low_reserves() -> None:
    req = _base_request().model_copy(update={"loan_type": "FHA", "occupancy_type": "Investment", "reserves": 1})
    result = evaluate_aus(req)

    assert any("FHA program-specific" in doc for doc in result.required_documents)
    assert any("Lease agreements" in doc for doc in result.required_documents)
    assert any("limited reserves" in doc for doc in result.required_documents)


def test_ltv_consistency_validation() -> None:
    try:
        AUSRequest(
            credit_score=742,
            dti=29.5,
            ltv=65.0,
            income=120000,
            loan_amount=420000,
            property_value=560000,
            loan_type="Conventional",
            reserves=6,
            occupancy_type="Primary",
        )
    except ValidationError:
        return

    raise AssertionError("Expected ValidationError for inconsistent LTV")
