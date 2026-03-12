from __future__ import annotations

from app.db.neo4j_client import Neo4jClient
from app.domain.models import LoanIngestPayload
from app.services.repository import GraphRepository
from app.services.rule_engine import RuleEngine


class IngestService:
    def __init__(self, neo4j: Neo4jClient) -> None:
        self.repo = GraphRepository(neo4j)
        self.rules = RuleEngine(neo4j)

    def ingest(self, payload: LoanIngestPayload) -> dict:
        self.repo.upsert_loan_bundle(payload)
        violations = self.rules.evaluate_loan(payload.loan.loanId)
        return {"loanId": payload.loan.loanId, "violations": violations, "status": "ingested"}
