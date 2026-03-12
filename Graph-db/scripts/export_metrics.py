from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.config.settings import get_settings
from app.db.neo4j_client import Neo4jClient


QUERY = """
MATCH (l:Loan)
OPTIONAL MATCH (:Borrower)-[:APPLIES_FOR]->(l)
RETURN l.loanId AS loanId,
       l.riskScore AS riskScore,
       l.networkRiskScore AS networkRiskScore,
       l.fraudCommunity AS fraudCommunity,
       l.riskCentrality AS riskCentrality,
       l.status AS status
"""


def main() -> None:
    settings = get_settings()
    out_dir = Path(settings.export_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    client = Neo4jClient(settings)
    try:
        rows = client.run_read(QUERY)
    finally:
        client.close()

    df = pd.DataFrame(rows)
    csv_path = out_dir / "loan_metrics.csv"
    parquet_path = out_dir / "loan_metrics.parquet"
    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)


if __name__ == "__main__":
    main()
