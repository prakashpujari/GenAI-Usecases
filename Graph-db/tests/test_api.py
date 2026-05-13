from fastapi.testclient import TestClient

from app.main import app


class FakeNeo4jClient:
    def __init__(self, settings):
        self.calls = []

    def verify_connectivity(self):
        return None

    def run_write(self, query, parameters=None):
        self.calls.append((query, parameters))
        if "RETURN count(CASE WHEN violated" in query:
            return [{"violations": 1}]
        return []

    def run_read(self, query, parameters=None):
        if "MATCH (:Borrower)-[:APPLIES_FOR]->(l:Loan" in query:
            return [
                {
                    "loanId": "L001",
                    "ltv": 78.0,
                    "dti": 40.0,
                    "fraudCommunity": 4,
                    "riskCentrality": 0.67,
                    "similarityFlags": 1,
                    "sharedContacts": 2,
                }
            ]
        if "MATCH (l:Loan {loanId: $loanId})-[:EVALUATED_BY]->(r:UnderwritingRule)" in query:
            return [{"ruleId": "R001", "name": "LTV Threshold", "ruleType": "LTV_MAX", "severity": "HIGH", "violationReason": "Threshold exceeded"}]
        if "MATCH (l:Loan {loanId: $loanId})-[:EVALUATED_BY]->(:UnderwritingRule)-[:DERIVED_FROM]->(g:Regulation)" in query:
            return [{"regId": "REG001", "name": "Ability To Repay", "jurisdiction": "US Federal"}]
        if "RETURN l.fraudCommunity" in query:
            return [{"fraudCommunity": 4, "riskCentrality": 0.67, "networkRiskScore": 58.0, "riskScore": 62.0}]
        return []

    def close(self):
        return None


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ingest_and_risk_endpoints(monkeypatch) -> None:
    monkeypatch.setattr("app.api.routes.Neo4jClient", FakeNeo4jClient)

    client = TestClient(app)

    ingest_payload = {
        "borrower": {"borrowerId": "B001", "name": "Jane Doe", "ssnHash": "hash-001", "dob": "1988-06-01"},
        "loan": {"loanId": "L001", "amount": 350000, "status": "submitted", "purpose": "purchase", "originationDate": "2026-01-10", "ltv": 78, "dti": 40},
        "property": {"propertyId": "P001", "address": "10 River Rd", "city": "Austin", "state": "TX", "zip": "73301", "type": "single_family"},
        "income": {"incomeId": "I001", "type": "w2", "employerName": "Fabrikam", "annualIncome": 125000, "startDate": "2019-04-01"},
        "documents": [{"documentId": "D001", "type": "paystub", "sourceSystem": "doc-mgmt", "uploadedAt": "2026-01-11T09:00:00"}],
    }

    ingest = client.post("/loans/ingest", json=ingest_payload)
    assert ingest.status_code == 200
    assert ingest.json()["status"] == "ingested"

    risk = client.get("/loans/L001/risk")
    assert risk.status_code == 200
    body = risk.json()
    assert body["loanId"] == "L001"
    assert body["riskScore"] >= 0
    assert body["networkRiskScore"] >= 0
