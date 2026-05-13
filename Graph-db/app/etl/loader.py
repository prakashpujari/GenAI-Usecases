from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.db.neo4j_client import Neo4jClient
from app.etl.migrate_schema import MigrationRunner
from app.etl.transforms import prepare_borrowers, prepare_loans


class ETLLoader:
    def __init__(self, neo4j: Neo4jClient, data_path: str) -> None:
        self.neo4j = neo4j
        self.data_path = Path(data_path)

    def apply_schema(self) -> None:
        MigrationRunner(self.neo4j).apply_pending()

    def _read(self, name: str) -> pd.DataFrame:
        path = self.data_path / name
        if path.suffix == ".parquet":
            return pd.read_parquet(path)
        return pd.read_csv(path)

    def load_borrowers(self) -> int:
        df = prepare_borrowers(self._read("borrowers.csv"))
        records = df.to_dict(orient="records")
        query = """
        UNWIND $rows AS row
        MERGE (b:Borrower {borrowerId: row.borrowerId})
        SET b.name = row.name,
            b.ssnHash = row.ssnHash,
            b.dob = row.dob,
            b.updatedAt = datetime(),
            b.createdAt = coalesce(b.createdAt, datetime())
        """
        self.neo4j.run_write(query, {"rows": records})
        return len(records)

    def load_properties(self) -> int:
        df = self._read("properties.csv")
        df["propertyId"] = df["propertyId"].astype(str).str.upper().str.strip()
        records = df.to_dict(orient="records")
        query = """
        UNWIND $rows AS row
        MERGE (p:Property {propertyId: row.propertyId})
        SET p.address = row.address,
            p.city = row.city,
            p.state = row.state,
            p.zip = row.zip,
            p.type = row.type
        """
        self.neo4j.run_write(query, {"rows": records})
        return len(records)

    def load_loans(self) -> int:
        df = prepare_loans(self._read("loans.csv"))
        records = df.to_dict(orient="records")
        query = """
        UNWIND $rows AS row
        MERGE (l:Loan {loanId: row.loanId})
        SET l.amount = toFloat(row.amount),
            l.status = row.status,
            l.purpose = row.purpose,
            l.originationDate = row.originationDate,
            l.ltv = toFloat(row.ltv),
            l.dti = toFloat(row.dti)
        WITH row, l
        MATCH (b:Borrower {borrowerId: row.borrowerId})
        MATCH (p:Property {propertyId: row.propertyId})
        MERGE (b)-[:APPLIES_FOR]->(l)
        MERGE (l)-[:SECURED_BY]->(p)
        """
        self.neo4j.run_write(query, {"rows": records})
        return len(records)

    def load_incomes(self) -> int:
        df = self._read("incomes.csv")
        df["incomeId"] = df["incomeId"].astype(str).str.upper().str.strip()
        df["borrowerId"] = df["borrowerId"].astype(str).str.upper().str.strip()
        records = df.to_dict(orient="records")
        query = """
        UNWIND $rows AS row
        MERGE (i:IncomeSource {incomeId: row.incomeId})
        SET i.type = row.type,
            i.employerName = row.employerName,
            i.annualIncome = toFloat(row.annualIncome),
            i.startDate = row.startDate
        WITH row, i
        MATCH (b:Borrower {borrowerId: row.borrowerId})
        MERGE (b)-[:HAS_INCOME_FROM]->(i)
        """
        self.neo4j.run_write(query, {"rows": records})
        return len(records)

    def load_documents(self) -> int:
        df = self._read("documents.csv")
        df["documentId"] = df["documentId"].astype(str).str.upper().str.strip()
        df["loanId"] = df["loanId"].astype(str).str.upper().str.strip()
        records = df.to_dict(orient="records")
        query = """
        UNWIND $rows AS row
        MERGE (d:Document {documentId: row.documentId})
        SET d.type = row.type,
            d.sourceSystem = row.sourceSystem,
            d.uploadedAt = row.uploadedAt
        WITH row, d
        MATCH (l:Loan {loanId: row.loanId})
        MERGE (l)-[:HAS_DOCUMENT]->(d)
        """
        self.neo4j.run_write(query, {"rows": records})
        return len(records)

    def load_rules_and_regulations(self) -> tuple[int, int]:
        rules = self._read("rules.csv")
        regs = self._read("regulations.csv")
        rule_records = rules.to_dict(orient="records")
        reg_records = regs.to_dict(orient="records")

        self.neo4j.run_write(
            """
            UNWIND $rows AS row
            MERGE (r:UnderwritingRule {ruleId: row.ruleId})
            SET r.name = row.name,
                r.description = row.description,
                r.ruleType = row.ruleType,
                r.severity = row.severity,
                r.regId = row.regId
            """,
            {"rows": rule_records},
        )

        self.neo4j.run_write(
            """
            UNWIND $rows AS row
            MERGE (g:Regulation {regId: row.regId})
            SET g.name = row.name,
                g.jurisdiction = row.jurisdiction,
                g.description = row.description
            """,
            {"rows": reg_records},
        )

        self.neo4j.run_write(
            """
            MATCH (r:UnderwritingRule), (g:Regulation {regId: r.regId})
            MERGE (r)-[:DERIVED_FROM]->(g)
            """
        )

        self.neo4j.run_write(
            """
            MATCH (l:Loan)
            MATCH (r:UnderwritingRule)
            WHERE (r.ruleType = 'LTV_MAX' AND l.purpose IN ['purchase', 'refinance'])
               OR (r.ruleType = 'DTI_MAX')
            MERGE (l)-[:EVALUATED_BY]->(r)
            WITH l, r
            MATCH (g:Regulation)<-[:DERIVED_FROM]-(r)
            MERGE (l)-[:SUBJECT_TO]->(g)
            """
        )

        return len(rule_records), len(reg_records)

    def run_full_load(self) -> dict[str, int]:
        self.apply_schema()
        borrowers = self.load_borrowers()
        properties = self.load_properties()
        loans = self.load_loans()
        incomes = self.load_incomes()
        documents = self.load_documents()
        rules, regulations = self.load_rules_and_regulations()
        return {
            "borrowers": borrowers,
            "properties": properties,
            "loans": loans,
            "incomes": incomes,
            "documents": documents,
            "rules": rules,
            "regulations": regulations,
        }
