from __future__ import annotations

from app.db.neo4j_client import Neo4jClient
from app.domain.models import LoanIngestPayload


class GraphRepository:
    def __init__(self, neo4j: Neo4jClient) -> None:
        self.neo4j = neo4j

    def upsert_loan_bundle(self, payload: LoanIngestPayload) -> None:
        query = """
        MERGE (b:Borrower {borrowerId: $borrower.borrowerId})
        SET b.name = $borrower.name,
            b.ssnHash = $borrower.ssnHash,
            b.dob = $borrower.dob,
            b.updatedAt = datetime(),
            b.createdAt = coalesce(b.createdAt, datetime())

        MERGE (l:Loan {loanId: $loan.loanId})
        SET l.amount = $loan.amount,
            l.status = $loan.status,
            l.purpose = $loan.purpose,
            l.originationDate = $loan.originationDate,
            l.ltv = $loan.ltv,
            l.dti = $loan.dti

        MERGE (p:Property {propertyId: $property.propertyId})
        SET p.address = $property.address,
            p.city = $property.city,
            p.state = $property.state,
            p.zip = $property.zip,
            p.type = $property.type

        MERGE (i:IncomeSource {incomeId: $income.incomeId})
        SET i.type = $income.type,
            i.employerName = $income.employerName,
            i.annualIncome = $income.annualIncome,
            i.startDate = $income.startDate

        MERGE (b)-[:APPLIES_FOR]->(l)
        MERGE (l)-[:SECURED_BY]->(p)
        MERGE (b)-[:HAS_INCOME_FROM]->(i)

        WITH l, $documents AS docs
        UNWIND docs AS doc
        MERGE (d:Document {documentId: doc.documentId})
        SET d.type = doc.type,
            d.sourceSystem = doc.sourceSystem,
            d.uploadedAt = doc.uploadedAt
        MERGE (l)-[:HAS_DOCUMENT]->(d)
        """
        self.neo4j.run_write(query, payload.model_dump(mode="json"))

    def get_loan_risk_inputs(self, loan_id: str) -> dict | None:
        query = """
        MATCH (:Borrower)-[:APPLIES_FOR]->(l:Loan {loanId: $loanId})
        OPTIONAL MATCH (b:Borrower)-[:APPLIES_FOR]->(l)
        OPTIONAL MATCH (b)-[:SHARES_CONTACT_INFO_WITH]-(:Borrower)
        OPTIONAL MATCH (b)-[s:SIMILAR_TO]-(:Borrower)
        RETURN l.loanId AS loanId,
               coalesce(l.ltv, 0.0) AS ltv,
               coalesce(l.dti, 0.0) AS dti,
               l.fraudCommunity AS fraudCommunity,
               l.riskCentrality AS riskCentrality,
               count(DISTINCT s) AS similarityFlags,
               count(DISTINCT b) - 1 AS sharedContacts
        LIMIT 1
        """
        rows = self.neo4j.run_read(query, {"loanId": loan_id})
        return rows[0] if rows else None

    def get_loan_explain(self, loan_id: str) -> dict:
        rules_query = """
        MATCH (l:Loan {loanId: $loanId})-[:EVALUATED_BY]->(r:UnderwritingRule)
        OPTIONAL MATCH (l)-[v:VIOLATES_RULE]->(r)
        RETURN r.ruleId AS ruleId, r.name AS name, r.ruleType AS ruleType,
               r.severity AS severity, v.reason AS violationReason
        """
        regs_query = """
        MATCH (l:Loan {loanId: $loanId})-[:EVALUATED_BY]->(:UnderwritingRule)-[:DERIVED_FROM]->(g:Regulation)
        RETURN DISTINCT g.regId AS regId, g.name AS name, g.jurisdiction AS jurisdiction
        """
        signals_query = """
        MATCH (l:Loan {loanId: $loanId})
        RETURN l.fraudCommunity AS fraudCommunity,
               l.riskCentrality AS riskCentrality,
               l.networkRiskScore AS networkRiskScore,
               l.riskScore AS riskScore
        """
        return {
            "rules": self.neo4j.run_read(rules_query, {"loanId": loan_id}),
            "regulations": self.neo4j.run_read(regs_query, {"loanId": loan_id}),
            "graphSignals": (self.neo4j.run_read(signals_query, {"loanId": loan_id}) or [{}])[0],
        }
