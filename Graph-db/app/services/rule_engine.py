from __future__ import annotations

from app.db.neo4j_client import Neo4jClient


class RuleEngine:
    def __init__(self, neo4j: Neo4jClient) -> None:
        self.neo4j = neo4j

    def evaluate_loan(self, loan_id: str) -> int:
        """Apply simple threshold-based rule evaluation and persist violations."""
        query = """
        MATCH (l:Loan {loanId: $loanId})-[:EVALUATED_BY]->(r:UnderwritingRule)
        WITH l, r,
             CASE
               WHEN r.ruleType = 'LTV_MAX' AND l.ltv > 80 THEN true
               WHEN r.ruleType = 'DTI_MAX' AND l.dti > 43 THEN true
               ELSE false
             END AS violated
        FOREACH (_ IN CASE WHEN violated THEN [1] ELSE [] END |
          MERGE (l)-[v:VIOLATES_RULE]->(r)
          SET v.reason = 'Threshold exceeded',
              v.evaluatedAt = datetime()
        )
        RETURN count(CASE WHEN violated THEN 1 END) AS violations
        """
        rows = self.neo4j.run_write(query, {"loanId": loan_id})
        return int(rows[0]["violations"]) if rows else 0
