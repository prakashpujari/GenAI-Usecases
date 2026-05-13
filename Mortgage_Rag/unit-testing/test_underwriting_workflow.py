from __future__ import annotations

from dataclasses import dataclass

from src.underwriting_agents import run_underwriting_workflow


@dataclass
class MockDoc:
    page_content: str
    metadata: dict


class MockVectorStore:
    def similarity_search_with_score(self, query: str, k: int = 5):
        return [
            (
                MockDoc(
                    page_content="Policy section: Minimum credit score is 620 and maximum DTI is 43%.",
                    metadata={"source": "UnderwritingPolicy.pdf", "section": "3.1"},
                ),
                0.12,
            ),
            (
                MockDoc(
                    page_content="Policy section: Maximum LTV for standard product is 80%.",
                    metadata={"source": "ProductMatrix.pdf", "section": "2.4"},
                ),
                0.21,
            ),
        ]


def test_recommendation_is_refer_when_docs_missing() -> None:
    result = run_underwriting_workflow(
        query="Assess this borrower",
        borrower_documents=[
            {
                "name": "paystub_jan.pdf",
                "text": "Borrower: Jane Doe\nGross Pay: $4000\nNet Pay: $3000\nCredit Score: 700",
            }
        ],
        policy_vector_store=MockVectorStore(),
    )

    assert result.recommendation == "Refer"
    assert "recommendation only" in result.output["decision"].lower()
    assert len(result.output["missing"]) > 0


def test_hard_rule_fail_can_decline_recommendation() -> None:
    result = run_underwriting_workflow(
        query="Assess this borrower",
        borrower_documents=[
            {
                "name": "full_package.pdf",
                "text": (
                    "Borrower: Sam Applicant\n"
                    "Credit Score: 580\n"
                    "Monthly Income: $5000\n"
                    "Monthly Debt: $1500\n"
                    "Loan Amount: $450000\n"
                    "Property Value: $500000\n"
                    "Employment Tenure: 36 months\n"
                    "W-2 wages, tips, other compensation $90000\n"
                    "Bank Statement available balance"
                ),
            },
            {"name": "w2_2024.pdf", "text": "W-2 wages, tips, other compensation $90000"},
            {"name": "bank_statement.pdf", "text": "Bank statement period Jan-Feb"},
            {"name": "employment_letter.pdf", "text": "Employment letter Employer: Contoso"},
            {"name": "id_passport.pdf", "text": "Passport ID document"},
        ],
        policy_vector_store=MockVectorStore(),
    )

    assert result.recommendation in {"Decline", "Refer"}
    hard_rules = result.output["hard_rules"]
    assert any(rule["type"] == "HARD" for rule in hard_rules)
    assert len(result.output["policy_citations"]) >= 1
