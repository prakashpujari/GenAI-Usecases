from __future__ import annotations

import logging
from typing import Dict, List

from fastapi import FastAPI
from pydantic import BaseModel

from shared.config import settings
from shared.cache import EmbeddingCache
from shared.llm import LlmProvider, call_service
from shared.logging import configure_logging
from shared.models import QueryRequest, QueryResponse
from shared.utils import chunk_text, stable_hash
from shared.vector_store import index_embedding, search_embeddings


logger = logging.getLogger("rag")
provider = LlmProvider()
embedding_cache = EmbeddingCache()


class IndexRequest(BaseModel):
    document_id: str
    loan_id: str
    document_type: str
    redacted_text: str


app = FastAPI(title="Mortgage Assistant RAG", version="1.0.0")


@app.on_event("startup")
async def startup() -> None:
    configure_logging("rag")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/v1/index")
async def index_document(request: IndexRequest) -> dict:
    chunks = chunk_text(request.redacted_text, settings.max_chunk_tokens, settings.chunk_overlap_tokens)

    for idx, chunk in enumerate(chunks):
        cache_key = stable_hash(chunk)
        embedding = embedding_cache.get(cache_key)
        if embedding is None:
            embedding = provider.embed_bedrock(chunk)
            embedding_cache.set(cache_key, embedding)
        record = {
            "document_id": request.document_id,
            "loan_id": request.loan_id,
            "document_type": request.document_type,
            "chunk_id": f"{request.document_id}-{idx}",
            "text": chunk,
            "embedding": embedding,
            "metadata": {
                "loan_id": request.loan_id,
                "document_type": request.document_type,
                "chunk_index": idx,
            },
        }
        index_embedding(record)

    return {"status": "indexed", "chunks": len(chunks)}


@app.post("/v1/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest) -> QueryResponse:
    query_key = stable_hash(request.question)
    query_embedding = embedding_cache.get(query_key)
    if query_embedding is None:
        query_embedding = provider.embed_bedrock(request.question)
        embedding_cache.set(query_key, query_embedding)
    hits = search_embeddings(
        query_vector=query_embedding,
        loan_id=request.loan_id,
        document_types=[doc.value for doc in request.document_types] if request.document_types else None,
        k=5,
    )

    context = "\n\n".join([hit["text"] for hit in hits])
    prompt = (
        "You are a mortgage assistant. Answer the question using ONLY the provided context. "
        "If the answer is not in context, say you do not have enough information.\n\n"
        f"Context:\n{context}\n\nQuestion: {request.question}\nAnswer:"
    )

    llm_response = await call_service(
        f"{settings.llm_router_url}/v1/route",
        {
            "task_type": "rag_answer",
            "prompt": prompt,
            "max_tokens": 500,
            "temperature": 0.2,
            "reasoning_required": True,
            "pii_safe": True,
            "allow_openai": True,
        },
    )

    sources = [
        {
            "document_id": hit.get("document_id"),
            "chunk_id": hit.get("chunk_id"),
            "document_type": hit.get("document_type"),
        }
        for hit in hits
    ]

    return QueryResponse(answer=llm_response["content"], sources=sources, model_provider=llm_response["provider"])
