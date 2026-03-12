from __future__ import annotations

from app.db.neo4j_client import Neo4jClient
from app.domain.models import ExplainResponse, RiskResponse
from app.domain.risk import compute_scores
from app.services.repository import GraphRepository


class RiskService:
    def __init__(self, neo4j: Neo4jClient) -> None:
        self.neo4j = neo4j
        self.repo = GraphRepository(neo4j)

    def get_risk(self, loan_id: str) -> RiskResponse:
        row = self.repo.get_loan_risk_inputs(loan_id)
        if not row:
            raise ValueError(f"Loan not found: {loan_id}")

        risk_score, network_risk_score = compute_scores(
            ltv=float(row["ltv"]),
            dti=float(row["dti"]),
            risk_centrality=float(row["riskCentrality"] or 0.0),
            shared_contacts=int(max(0, row["sharedContacts"] or 0)),
            similarity_flags=int(row["similarityFlags"] or 0),
        )

        self.neo4j.run_write(
            """
            MATCH (l:Loan {loanId: $loanId})
            SET l.riskScore = $riskScore,
                l.networkRiskScore = $networkRiskScore
            """,
            {
                "loanId": loan_id,
                "riskScore": risk_score,
                "networkRiskScore": network_risk_score,
            },
        )

        return RiskResponse(
            loanId=loan_id,
            ltv=float(row["ltv"]),
            dti=float(row["dti"]),
            fraudCommunity=row.get("fraudCommunity"),
            riskCentrality=float(row.get("riskCentrality") or 0.0),
            sharedContacts=int(max(0, row.get("sharedContacts") or 0)),
            similarityFlags=int(row.get("similarityFlags") or 0),
            riskScore=risk_score,
            networkRiskScore=network_risk_score,
        )

    def explain(self, loan_id: str) -> ExplainResponse:
        data = self.repo.get_loan_explain(loan_id)
        return ExplainResponse(
            loanId=loan_id,
            rules=data["rules"],
            regulations=data["regulations"],
            graphSignals=data["graphSignals"],
        )
