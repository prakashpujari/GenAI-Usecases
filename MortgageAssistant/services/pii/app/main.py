from __future__ import annotations

import logging
from typing import Dict

from fastapi import FastAPI
from pydantic import BaseModel

from shared.audit import audit_log
from shared.logging import configure_logging
from shared.models import PiiEntity, RedactionResult
from shared.vault import SecureVault
from .redaction import apply_redaction, detect_pii


logger = logging.getLogger("pii")


class RedactRequest(BaseModel):
    document_id: str
    text: str
    role: str = "external"


app = FastAPI(title="Mortgage Assistant PII", version="1.0.0")


@app.on_event("startup")
async def startup() -> None:
    configure_logging("pii")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/v1/redact", response_model=RedactionResult)
async def redact(request: RedactRequest) -> RedactionResult:
    entities = detect_pii(request.text)
    vault = SecureVault()

    pii_values: Dict[str, str] = {entity.text: entity.type.value for entity in entities}
    token_map = vault.store_pii(request.document_id, pii_values)

    redacted_text = apply_redaction(request.text, entities, token_map, request.role)

    audit_log(
        "pii_redacted",
        {"document_id": request.document_id, "pii_count": len(entities)},
    )

    return RedactionResult(redacted_text=redacted_text, tokens=token_map, pii_entities=entities)
