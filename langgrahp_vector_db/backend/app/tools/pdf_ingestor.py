"""PDF ingestion pipeline.

Strategy
--------
1. Load each PDF page via PyPDFLoader (preserves page-level metadata).
2. Split with RecursiveCharacterTextSplitter:
     chunk_size=800   – fits comfortably inside gpt-4o's context alongside other chunks
     chunk_overlap=150 – ~19 % overlap keeps sentence/paragraph context across boundaries
     separators ranked paragraph → line → sentence → word → char
3. Enrich every chunk with: source, page, chunk_index, total_chunks.
4. Deduplicate: if a source with the same filename is already present in the
   store's docstore, skip re-ingestion (set replace=True to force overwrite).
5. Add to the live FAISS store and persist to disk immediately.
"""

import logging
import os
import tempfile
from dataclasses import dataclass
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.tools.vector_store import add_documents

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Splitter – created once at module level (stateless, thread-safe)
# ---------------------------------------------------------------------------

_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", ". ", "! ", "? ", ", ", " ", ""],
    length_function=len,
    is_separator_regex=False,
)


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class IngestResult:
    filename: str
    pages: int
    chunks: int
    skipped: bool = False
    message: str = ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ingest_pdf(
    file_bytes: bytes,
    filename: str,
    store: FAISS,
    *,
    replace: bool = False,
) -> IngestResult:
    """Ingest a single PDF into *store*.

    Parameters
    ----------
    file_bytes : raw PDF bytes
    filename   : original file name (used as the ``source`` metadata field)
    store      : live FAISS store to add chunks to
    replace    : if False (default), skip files that are already indexed
    """
    # ------------------------------------------------------------------
    # Deduplication check
    # ------------------------------------------------------------------
    if not replace and _already_indexed(store, filename):
        logger.info("[ingest] '%s' already indexed – skipping.", filename)
        return IngestResult(
            filename=filename,
            pages=0,
            chunks=0,
            skipped=True,
            message="Already indexed. Pass replace=true to re-ingest.",
        )

    # ------------------------------------------------------------------
    # Write bytes to a temp file (PyPDFLoader requires a path)
    # ------------------------------------------------------------------
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
    try:
        os.write(tmp_fd, file_bytes)
        os.close(tmp_fd)

        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    if not pages:
        return IngestResult(
            filename=filename,
            pages=0,
            chunks=0,
            message="PDF appears to be empty or could not be parsed.",
        )

    # ------------------------------------------------------------------
    # Chunk
    # ------------------------------------------------------------------
    raw_chunks = _SPLITTER.split_documents(pages)
    total = len(raw_chunks)

    for i, chunk in enumerate(raw_chunks):
        chunk.metadata.update(
            {
                "source": filename,
                # PyPDFLoader sets metadata["page"] as 0-based int; make 1-based
                "page": chunk.metadata.get("page", 0) + 1,
                "chunk_index": i,
                "total_chunks": total,
            }
        )

    # ------------------------------------------------------------------
    # Add to store (also persists to disk inside add_documents)
    # ------------------------------------------------------------------
    add_documents(store, raw_chunks)

    logger.info(
        "[ingest] '%s' → %d page(s), %d chunk(s) added.",
        filename,
        len(pages),
        total,
    )
    return IngestResult(filename=filename, pages=len(pages), chunks=total)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _already_indexed(store: FAISS, filename: str) -> bool:
    """Return True if any document in the store has source == filename."""
    try:
        docstore = store.docstore
        # FAISS docstore is an InMemoryDocstore; its _dict holds {id: Document}
        docs = getattr(docstore, "_dict", {}).values()
        return any(
            doc.metadata.get("source") == filename for doc in docs
        )
    except Exception:
        return False
