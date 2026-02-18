from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    paystub = "paystub"
    w2 = "w2"
    bank_statement = "bank_statement"
    credit_report = "credit_report"
    other = "other"


class UploadInitRequest(BaseModel):
    document_type: DocumentType
    loan_id: str
    file_name: str
    content_type: str


class UploadInitResponse(BaseModel):
    document_id: str
    upload_url: str
    expires_in: int


class UploadCompleteRequest(BaseModel):
    document_id: str
    loan_id: str
    document_type: DocumentType


class MortgageFields(BaseModel):
    employer: Optional[str] = None
    income: Optional[str] = None
    pay_frequency: Optional[str] = None
    account_balances: List[str] = Field(default_factory=list)
    loan_numbers: List[str] = Field(default_factory=list)


class ExtractedDocument(BaseModel):
    document_id: str
    loan_id: str
    document_type: DocumentType
    raw_text: str
    extracted_fields: MortgageFields


class PiiType(str, Enum):
    ssn = "ssn"
    dob = "dob"
    account_number = "account_number"
    address = "address"
    other = "other"


class PiiEntity(BaseModel):
    type: PiiType
    text: str
    start: int
    end: int
    confidence: float


class RedactionResult(BaseModel):
    redacted_text: str
    tokens: Dict[str, str]
    pii_entities: List[PiiEntity]


class EmbeddingRecord(BaseModel):
    document_id: str
    loan_id: str
    document_type: DocumentType
    chunk_id: str
    text: str
    embedding: List[float]
    metadata: Dict[str, Any]


class QueryRequest(BaseModel):
    loan_id: str
    question: str
    document_types: List[DocumentType] | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    model_provider: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LlmTaskType(str, Enum):
    extraction = "extraction"
    rag_answer = "rag_answer"
    summarization = "summarization"


class LlmRequest(BaseModel):
    task_type: LlmTaskType
    prompt: str
    max_tokens: int = 700
    temperature: float = 0.2


class LlmResponse(BaseModel):
    provider: str
    model: str
    content: str
