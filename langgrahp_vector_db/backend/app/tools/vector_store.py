import logging
from pathlib import Path
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

FAISS_INDEX_DIR = Path("data/faiss_index")

# ---------------------------------------------------------------------------
# Sample seed corpus
# ---------------------------------------------------------------------------

SAMPLE_DOCUMENTS: List[str] = [
    "Software engineering involves designing, building, and maintaining software systems.",
    "Machine learning engineers build models that learn patterns from large datasets.",
    "DevOps engineers bridge development and operations to enable continuous delivery.",
    "Data engineers design pipelines that collect, store, and process large volumes of data.",
    "Cloud engineers architect and manage infrastructure on platforms like AWS, Azure, and GCP.",
    "AI engineers integrate large language models and AI tools into production applications.",
]


# ---------------------------------------------------------------------------
# Store lifecycle
# ---------------------------------------------------------------------------

def build_or_load_store(
    api_key: str,
    model: str = "text-embedding-3-small",
) -> Tuple[FAISS, OpenAIEmbeddings]:
    """Load a persisted FAISS index from disk or build one from the seed corpus.

    Returns (store, embeddings) so callers can reuse the embeddings object
    for subsequent add_documents calls without re-initialising.
    """
    embeddings = OpenAIEmbeddings(api_key=api_key, model=model)
    index_file = FAISS_INDEX_DIR / "index.faiss"

    if index_file.exists():
        logger.info("Loading FAISS index from disk (%s) …", FAISS_INDEX_DIR)
        store = FAISS.load_local(
            str(FAISS_INDEX_DIR),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        logger.info("FAISS index loaded.")
    else:
        logger.info("Building FAISS vector store from %d seed documents …", len(SAMPLE_DOCUMENTS))
        docs = [
            Document(
                page_content=text,
                metadata={"source": f"seed-doc-{i + 1}", "page": 0, "chunk_index": i},
            )
            for i, text in enumerate(SAMPLE_DOCUMENTS)
        ]
        store = FAISS.from_documents(docs, embeddings)
        _persist(store)
        logger.info("FAISS vector store built and saved.")

    return store, embeddings


def add_documents(
    store: FAISS,
    docs: List[Document],
) -> None:
    """Add pre-chunked documents to an existing store and persist to disk."""
    store.add_documents(docs)
    _persist(store)
    logger.info("Added %d chunks to FAISS index.", len(docs))


def _persist(store: FAISS) -> None:
    FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    store.save_local(str(FAISS_INDEX_DIR))


# ---------------------------------------------------------------------------
# Retriever factory
# ---------------------------------------------------------------------------

def build_retriever(store: FAISS, k: int = 3) -> BaseRetriever:
    """Return a retriever backed by *store*.

    The retriever holds a live reference to the store object, so documents
    added via add_documents() are immediately searchable without rebuilding.
    """
    return store.as_retriever(search_kwargs={"k": k})
