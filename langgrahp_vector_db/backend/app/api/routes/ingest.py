import logging
from typing import List

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile

from app.api.schemas import DocumentInfo, IngestResponse
from app.tools.pdf_ingestor import ingest_pdf

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


@router.post("/ingest", response_model=IngestResponse, summary="Ingest PDF(s) into the vector store")
async def ingest(
    request: Request,
    files: List[UploadFile] = File(..., description="One or more PDF files"),
    replace: bool = Query(False, description="Re-ingest even if already indexed"),
) -> IngestResponse:
    """Upload one or more PDF files.  Each file is:
    - Parsed page-by-page with PyPDFLoader
    - Split into overlapping chunks (800 chars, 150 overlap)
    - Embedded and added to the live FAISS store
    - Persisted to disk immediately

    Already-indexed files are skipped unless `replace=true`.
    """
    store = getattr(request.app.state, "faiss_store", None)
    if store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialised.")

    results: List[DocumentInfo] = []

    for upload in files:
        filename = upload.filename or "unknown.pdf"

        # Validate content type
        if upload.content_type not in ("application/pdf", "application/octet-stream"):
            if not filename.lower().endswith(".pdf"):
                raise HTTPException(
                    status_code=415,
                    detail=f"'{filename}' is not a PDF file.",
                )

        content = await upload.read()

        if len(content) == 0:
            raise HTTPException(status_code=400, detail=f"'{filename}' is empty.")
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"'{filename}' exceeds the {MAX_FILE_SIZE_MB} MB limit.",
            )

        try:
            result = ingest_pdf(content, filename, store, replace=replace)
        except Exception as exc:
            logger.exception("[ingest] failed to process '%s': %s", filename, exc)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process '{filename}': {exc}",
            ) from exc

        results.append(
            DocumentInfo(
                filename=result.filename,
                pages=result.pages,
                chunks=result.chunks,
                skipped=result.skipped,
                message=result.message,
            )
        )

    total_chunks = sum(r.chunks for r in results)
    ingested = sum(1 for r in results if not r.skipped)

    return IngestResponse(
        message=f"Processed {len(files)} file(s): {ingested} ingested, "
                f"{len(files) - ingested} skipped. {total_chunks} chunk(s) added.",
        documents=results,
        total_chunks=total_chunks,
    )
