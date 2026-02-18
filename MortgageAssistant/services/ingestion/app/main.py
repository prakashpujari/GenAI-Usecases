from __future__ import annotations

import logging
import re
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from shared.audit import audit_log
from shared.aws_clients import dynamodb_resource, s3_client, textract_client
from shared.config import settings
from shared.logging import configure_logging
from shared.models import DocumentType, ExtractedDocument, MortgageFields
from shared.llm import call_service


logger = logging.getLogger("ingestion")


class IngestRequest(BaseModel):
    document_id: str
    loan_id: str
    document_type: DocumentType


app = FastAPI(title="Mortgage Assistant Ingestion", version="1.0.0")


@app.on_event("startup")
async def startup() -> None:
    configure_logging("ingestion")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


def _extract_text_from_s3(s3_key: str) -> str:
    response = textract_client().detect_document_text(
        Document={"S3Object": {"Bucket": settings.s3_bucket, "Name": s3_key}}
    )
    lines = [block["Text"] for block in response.get("Blocks", []) if block.get("BlockType") == "LINE"]
    return "\n".join(lines)


def _extract_mortgage_fields(text: str) -> MortgageFields:
    employer_match = re.search(r"Employer\s*:?\s*(.+)", text, re.IGNORECASE)
    income_match = re.search(r"(Gross\s*Pay|Income)\s*:?\s*\$?([0-9,\.]+)", text, re.IGNORECASE)
    pay_frequency_match = re.search(r"(Pay\s*Frequency|Pay\s*Period)\s*:?\s*(Weekly|Bi-Weekly|Monthly|Semi-Monthly)", text, re.IGNORECASE)
    account_balance_matches = re.findall(r"Balance\s*:?\s*\$?([0-9,\.]+)", text, re.IGNORECASE)
    loan_number_matches = re.findall(r"Loan\s*(Number|#)\s*:?\s*([A-Z0-9-]+)", text, re.IGNORECASE)

    return MortgageFields(
        employer=employer_match.group(1).strip() if employer_match else None,
        income=income_match.group(2) if income_match else None,
        pay_frequency=pay_frequency_match.group(2) if pay_frequency_match else None,
        account_balances=[value for value in account_balance_matches],
        loan_numbers=[value for _, value in loan_number_matches],
    )


async def _redact_pii(document: ExtractedDocument) -> dict:
    payload = {
        "document_id": document.document_id,
        "text": document.raw_text,
        "role": "internal",
    }
    return await call_service(f"{settings.pii_service_url}/v1/redact", payload)


async def _index_redacted(document: ExtractedDocument, redacted_text: str) -> None:
    payload = {
        "document_id": document.document_id,
        "loan_id": document.loan_id,
        "document_type": document.document_type.value,
        "redacted_text": redacted_text,
    }
    await call_service(f"{settings.rag_service_url}/v1/index", payload)


@app.post("/v1/ingest")
async def ingest(request: IngestRequest) -> dict:
    metadata_table = dynamodb_resource().Table(settings.dynamodb_metadata_table)
    item = metadata_table.get_item(Key={"document_id": request.document_id}).get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="Document not found")

    s3_key = item.get("s3_key")
    if not s3_key:
        raise HTTPException(status_code=400, detail="Missing S3 key")

    raw_text = _extract_text_from_s3(s3_key)
    fields = _extract_mortgage_fields(raw_text)

    extracted = ExtractedDocument(
        document_id=request.document_id,
        loan_id=request.loan_id,
        document_type=request.document_type,
        raw_text=raw_text,
        extracted_fields=fields,
    )

    redaction_result = await _redact_pii(extracted)
    await _index_redacted(extracted, redaction_result["redacted_text"])

    metadata_table.update_item(
        Key={"document_id": request.document_id},
        UpdateExpression="SET #status=:s, extracted_fields=:f",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={":s": "INDEXED", ":f": fields.model_dump()},
    )

    audit_log(
        "document_ingested",
        {"document_id": request.document_id, "loan_id": request.loan_id},
    )

    return {"status": "indexed", "document_id": request.document_id}
