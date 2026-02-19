from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from .config import Settings
from .extract import extract_text_from_pdf, extract_fields
from .pii import redact_pii, detect_pii
from .embedding import chunk_text, EmbeddingItem, build_faiss_index
from .llm import LlmClient
from .logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class ProcessedDocument:
    doc_id: str
    text: str
    redacted_text: str
    fields: dict[str, str]
    pii_found: list[dict[str, str]]


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

    for idx, path in enumerate(pdf_paths, start=1):
        logger.info(f"Processing document {idx}/{len(pdf_paths)}: {path.name}")
        processed = process_document(path)
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

    if embeddings:
        logger.info(f"Building FAISS index with {len(embeddings)} embeddings")
        build_faiss_index(embeddings, settings.faiss_dir)
        logger.info("FAISS index created successfully")
    else:
        logger.warning("No embeddings generated, skipping FAISS index creation")

    if llm:
        logger.info("Generating pipeline summary using LLM")
        safe_summary = llm.safe_chat(
            system_prompt=(
                "You are an underwriting assistant. Summarize the sanitized document "
                "content into key underwriting-relevant facts."
            ),
            user_prompt=(
                "Summarize the following sanitized text:\n" + embeddings[0].text
                if embeddings
                else "No content"
            ),
        )
        summary_path = settings.output_dir / "summary.txt"
        summary_path.write_text(safe_summary, encoding="utf-8")
        logger.info(f"Summary saved to {summary_path}")
    
    logger.info("Pipeline completed successfully")
