from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field, model_validator


class LoanType(str, Enum):
    CONVENTIONAL = "Conventional"
    FHA = "FHA"
    VA = "VA"


class OccupancyType(str, Enum):
    PRIMARY = "Primary"
    SECOND_HOME = "Second Home"
    INVESTMENT = "Investment"


class AUSFinding(str, Enum):
    APPROVE_ELIGIBLE = "Approve/Eligible"
    REFER_ELIGIBLE = "Refer/Eligible"
    REFER_INELIGIBLE = "Refer/Ineligible"


class AUSRequest(BaseModel):
    credit_score: int = Field(..., ge=300, le=850)
    dti: float = Field(..., ge=0, le=100, description="Debt-to-income ratio (%)")
    ltv: float = Field(..., gt=0, le=200, description="Loan-to-value ratio (%)")
    income: float = Field(..., gt=0)
    loan_amount: float = Field(..., gt=0)
    property_value: float = Field(..., gt=0)
    loan_type: LoanType
    reserves: int = Field(..., ge=0, description="Reserves in months")
    occupancy_type: OccupancyType

    @model_validator(mode="after")
    def validate_ltv_consistency(self) -> "AUSRequest":
        computed_ltv = (self.loan_amount / self.property_value) * 100
        if abs(computed_ltv - self.ltv) > 2.0:
            raise ValueError(
                f"Provided ltv={self.ltv:.2f}% is inconsistent with loan_amount/property_value={computed_ltv:.2f}%"
            )
        return self


class RuleEvaluation(BaseModel):
    rule: str
    passed: bool
    severity: str
    reason: str


class AUSResponse(BaseModel):
    finding: AUSFinding
    reasons: list[str]
    required_documents: list[str]
    rule_evaluations: list[RuleEvaluation]
