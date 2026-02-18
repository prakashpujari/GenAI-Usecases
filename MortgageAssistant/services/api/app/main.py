from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from shared.aws_clients import dynamodb_resource, s3_client
from shared.config import settings
from shared.logging import configure_logging
from shared.middleware import RequestIdMiddleware
from shared.models import (
    QueryRequest,
    QueryResponse,
    UploadCompleteRequest,
    UploadInitRequest,
    UploadInitResponse,
)
from shared.rate_limit import InMemoryRateLimiter
from shared.llm import call_service


logger = logging.getLogger("api")
rate_limiter = InMemoryRateLimiter(settings.rate_limit_rps)

app = FastAPI(title="Mortgage Assistant API", version="1.0.0")
app.add_middleware(RequestIdMiddleware)


@app.on_event("startup")
async def startup() -> None:
    configure_logging("api")


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/v1/documents/initiate-upload", response_model=UploadInitResponse)
async def initiate_upload(request: UploadInitRequest) -> UploadInitResponse:
    if not rate_limiter.allow(request.loan_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    document_id = str(uuid4())
    object_key = f"{request.loan_id}/{document_id}/{request.file_name}"

    presigned_url = s3_client().generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": settings.s3_bucket,
            "Key": object_key,
            "ContentType": request.content_type,
        },
        ExpiresIn=900,
    )

    metadata_table = dynamodb_resource().Table(settings.dynamodb_metadata_table)
    metadata_table.put_item(
        Item={
            "document_id": document_id,
            "loan_id": request.loan_id,
            "document_type": request.document_type.value,
            "s3_key": object_key,
            "status": "UPLOADED",
        }
    )

    return UploadInitResponse(document_id=document_id, upload_url=presigned_url, expires_in=900)


@app.post("/v1/documents/complete")
async def complete_upload(request: UploadCompleteRequest) -> dict:
    payload = request.model_dump()
    await call_service(f"{settings.ingestion_service_url}/v1/ingest", payload)
    return {"status": "queued", "document_id": request.document_id}


@app.post("/v1/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    payload = request.model_dump()
    response = await call_service(f"{settings.rag_service_url}/v1/query", payload)
    return QueryResponse(**response)
