from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from .config import Settings
from .extract import extract_text_from_pdf, extract_fields
from .pii import redact_pii, detect_pii
from .embedding import chunk_text, EmbeddingItem, build_faiss_index
from .llm import LlmClient
from .logger import get_logger
from .underwriting_agents import run_underwriting_workflow

logger = get_logger(__name__)


@dataclass(frozen=True)
class ProcessedDocument:
    doc_id: str
    text: str
    redacted_text: str
    fields: dict[str, str]
    pii_found: list[dict[str, str]]


def _redact_structure(value: Any) -> Any:
    if isinstance(value, str):
        return redact_pii(value)
    if isinstance(value, list):
        return [_redact_structure(item) for item in value]
    if isinstance(value, dict):
        return {key: _redact_structure(item) for key, item in value.items()}
    return value


def process_document(path: Path) -> ProcessedDocument:
    logger.info(f"Processing document: {path.name}")
    doc_text = extract_text_from_pdf(path)
    fields = extract_fields(doc_text.text)
    pii_matches = detect_pii(doc_text.text)
    redacted_text = redact_pii(doc_text.text)
    redacted_fields = {key: redact_pii(value) for key, value in fields.items()}
    logger.info(f"Document processed: {path.stem}, fields={len(fields)}, pii_matches={len(pii_matches)}")
    return ProcessedDocument(
        doc_id=path.stem,
        text=doc_text.text,
        redacted_text=redacted_text,
        fields=redacted_fields,
        pii_found=[{"label": m.label, "value": redact_pii(m.value)} for m in pii_matches],
    )


def run_pipeline(settings: Settings) -> None:
    logger.info("Starting document processing pipeline")
    logger.info(f"Pipeline config: data_dir={settings.data_dir}, output_dir={settings.output_dir}")
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.faiss_dir.mkdir(parents=True, exist_ok=True)

    pdf_paths = list(settings.data_dir.glob("*.pdf"))
    if not pdf_paths:
        logger.error(f"No PDF files found in {settings.data_dir}")
        raise FileNotFoundError(f"No PDF files found in {settings.data_dir}")
    
    logger.info(f"Found {len(pdf_paths)} PDF files to process")

    llm = None
    if settings.openai_api_key:
        logger.info("Initializing LLM client")
        llm = LlmClient(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            embed_model=settings.openai_embed_model,
        )
    else:
        logger.warning("No OpenAI API key found, skipping embeddings")

    embeddings: list[EmbeddingItem] = []
    processed_documents: list[ProcessedDocument] = []
    policy_documents: list[Document] = []

    for idx, path in enumerate(pdf_paths, start=1):
        logger.info(f"Processing document {idx}/{len(pdf_paths)}: {path.name}")
        processed = process_document(path)
        processed_documents.append(processed)
        output_path = settings.output_dir / f"{processed.doc_id}.json"
        output_path.write_text(
            json.dumps(
                {
                    "doc_id": processed.doc_id,
                    "fields": processed.fields,
                    "pii_found": processed.pii_found,
                    "redacted_text": processed.redacted_text,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        logger.info(f"Saved processed document to {output_path}")

        chunks = chunk_text(
            processed.redacted_text,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        logger.info(f"Generated {len(chunks)} chunks for {path.name}")

        if llm:
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            vectors = llm.embed_texts(chunks)
            for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
                embeddings.append(
                    EmbeddingItem(
                        doc_id=processed.doc_id,
                        chunk_id=idx,
                        text=chunk,
                        vector=vector,
                    )
                )

        for chunk_idx, chunk in enumerate(chunks):
            policy_documents.append(
                Document(page_content=chunk, metadata={"source": path.name, "chunk": chunk_idx})
            )

    if embeddings:
        logger.info(f"Building FAISS index with {len(embeddings)} embeddings")
        build_faiss_index(embeddings, settings.faiss_dir)
        logger.info("FAISS index created successfully")
    else:
        logger.warning("No embeddings generated, skipping FAISS index creation")

    policy_vector_store = None
    if settings.openai_api_key and policy_documents:
        logger.info("Building policy vector store for underwriting citations")
        policy_embeddings = OpenAIEmbeddings(model=settings.openai_embed_model, api_key=settings.openai_api_key)
        policy_vector_store = FAISS.from_documents(documents=policy_documents, embedding=policy_embeddings)

    if processed_documents:
        logger.info("Generating compliance-first underwriting recommendation")
        underwriting_result = run_underwriting_workflow(
            query="Batch underwriting assessment",
            borrower_documents=[
                {"name": f"{item.doc_id}.pdf", "text": item.text}
                for item in processed_documents
            ],
            policy_vector_store=policy_vector_store,
            thresholds={
                "min_credit_score": settings.min_credit_score,
                "max_dti": settings.max_dti,
                "max_ltv": settings.max_ltv,
                "min_employment_months": settings.min_employment_months,
            },
        )

        summary_path = settings.output_dir / "summary.txt"
        summary_path.write_text(redact_pii(underwriting_result.summary_markdown), encoding="utf-8")
        logger.info(f"Summary saved to {summary_path}")

        recommendation_path = settings.output_dir / "underwriting_recommendation.json"
        recommendation_path.write_text(
            json.dumps(_redact_structure(underwriting_result.output), indent=2), encoding="utf-8"
        )
        logger.info(f"Underwriting recommendation saved to {recommendation_path}")
    
    logger.info("Pipeline completed successfully")
