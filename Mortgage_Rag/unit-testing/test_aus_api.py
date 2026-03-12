from __future__ import annotations

from fastapi.testclient import TestClient

from src.aus.api import app


client = TestClient(app)


def _payload(**overrides):
    base = {
        "credit_score": 742,
        "dti": 29.5,
        "ltv": 75.0,
        "income": 120000,
        "loan_amount": 420000,
        "property_value": 560000,
        "loan_type": "Conventional",
        "reserves": 6,
        "occupancy_type": "Primary",
    }
    base.update(overrides)
    return base


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_aus_approve_eligible() -> None:
    response = client.post("/aus/evaluate", json=_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["finding"] == "Approve/Eligible"
    assert "required_documents" in body
    assert "rule_evaluations" in body


def test_aus_refer_eligible() -> None:
    response = client.post("/aus/evaluate", json=_payload(dti=44.0))

    assert response.status_code == 200
    assert response.json()["finding"] == "Refer/Eligible"


def test_aus_refer_ineligible_program_violation() -> None:
    response = client.post("/aus/evaluate", json=_payload(credit_score=600, loan_type="Conventional"))

    assert response.status_code == 200
    body = response.json()
    assert body["finding"] == "Refer/Ineligible"


def test_aus_validation_error_for_inconsistent_ltv() -> None:
    response = client.post("/aus/evaluate", json=_payload(ltv=60.0))

    assert response.status_code == 422
