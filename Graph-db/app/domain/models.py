from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class BorrowerIn(BaseModel):
    borrowerId: str
    name: str
    ssnHash: str | None = None
    dob: date | None = None


class LoanIn(BaseModel):
    loanId: str
    amount: float
    status: str
    purpose: str
    originationDate: date | None = None
    ltv: float = Field(default=0.0, ge=0.0)
    dti: float = Field(default=0.0, ge=0.0)


class PropertyIn(BaseModel):
    propertyId: str
    address: str
    city: str
    state: str
    zip: str
    type: str


class IncomeSourceIn(BaseModel):
    incomeId: str
    type: str
    employerName: str
    annualIncome: float
    startDate: date | None = None


class DocumentIn(BaseModel):
    documentId: str
    type: str
    sourceSystem: str
    uploadedAt: datetime | None = None


class LoanIngestPayload(BaseModel):
    borrower: BorrowerIn
    loan: LoanIn
    property: PropertyIn
    income: IncomeSourceIn
    documents: list[DocumentIn] = Field(default_factory=list)


class RiskResponse(BaseModel):
    loanId: str
    ltv: float
    dti: float
    fraudCommunity: int | None = None
    riskCentrality: float | None = None
    sharedContacts: int = 0
    similarityFlags: int = 0
    riskScore: float
    networkRiskScore: float


class ExplainResponse(BaseModel):
    loanId: str
    rules: list[dict]
    regulations: list[dict]
    graphSignals: dict
