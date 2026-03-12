from __future__ import annotations

from app.db.neo4j_client import Neo4jClient


class GDSJobs:
    def __init__(self, neo4j: Neo4jClient) -> None:
        self.neo4j = neo4j

    def drop_graph_if_exists(self, name: str) -> None:
        self.neo4j.run_write(
            """
            CALL gds.graph.exists($name) YIELD exists
            WITH exists
            CALL apoc.do.when(
              exists,
              'CALL gds.graph.drop($name, false) YIELD graphName RETURN graphName',
              'RETURN "none" AS graphName',
              {name: $name}
            ) YIELD value
            RETURN value
            """,
            {"name": name},
        )

    def project_fraud_graph(self) -> None:
        self.drop_graph_if_exists("fraudGraph")
        self.neo4j.run_write(
            """
            CALL gds.graph.project(
              'fraudGraph',
              ['Borrower', 'Loan', 'Property', 'Document'],
              {
                APPLIES_FOR: {orientation: 'UNDIRECTED'},
                SECURED_BY: {orientation: 'UNDIRECTED'},
                HAS_DOCUMENT: {orientation: 'UNDIRECTED'},
                SHARES_CONTACT_INFO_WITH: {orientation: 'UNDIRECTED'}
              }
            )
            """
        )

    def project_risk_graph(self) -> None:
        self.drop_graph_if_exists("riskGraph")
        self.neo4j.run_write(
            """
            CALL gds.graph.project(
              'riskGraph',
              ['Borrower', 'Loan', 'IncomeSource', 'UnderwritingRule'],
              ['APPLIES_FOR', 'HAS_INCOME_FROM', 'EVALUATED_BY']
            )
            """
        )

    def run_community_detection(self) -> None:
        self.neo4j.run_write(
            """
            CALL gds.louvain.write('fraudGraph', {
              writeProperty: 'fraudCommunity'
            })
            """
        )

    def run_centrality(self) -> None:
        self.neo4j.run_write(
            """
            CALL gds.pageRank.write('riskGraph', {
              writeProperty: 'riskCentrality'
            })
            """
        )

    def run_similarity(self) -> None:
        self.neo4j.run_write(
            """
            CALL gds.nodeSimilarity.write('fraudGraph', {
              writeRelationshipType: 'SIMILAR_TO',
              writeProperty: 'similarityScore'
            })
            """
        )

    def run_all(self) -> None:
        self.project_fraud_graph()
        self.project_risk_graph()
        self.run_community_detection()
        self.run_centrality()
        self.run_similarity()
