"""
rag_ingest.py
---
Ingests .txt, .md, and .pdf documents into a FAISS vector DB using
Semantic Chunking (SemanticChunker from langchain_experimental).

Semantic chunking splits text at natural topic boundaries by measuring
cosine similarity between consecutive sentences — producing richer,
more coherent chunks than fixed-size splitting.

Usage: python -m nlq_sql.rag_ingest <docs_folder> <faiss_index_path>
"""

import os
import re
import unicodedata
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from nlq_sql.faiss_vector import FaissVectorDB


def _clean_text(text: str) -> str:
    """Remove control characters and normalise whitespace for clean RAG chunks."""
    # Replace non-printable control chars (except newline/tab) with a space
    text = "".join(
        ch if (unicodedata.category(ch)[0] != "C" or ch in "\n\t") else " "
        for ch in text
    )
    # Collapse multiple blank lines to at most two
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip trailing whitespace per line
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip()


def ingest_folder(docs_folder, faiss_path):
    embeddings = OpenAIEmbeddings()
    # SemanticChunker: splits on semantic dissimilarity between sentences.
    # breakpoint_threshold_type options: "percentile", "standard_deviation", "interquartile"
    chunker = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=85,  # split when similarity drops to 85th‑percentile dissimilarity
    )

    texts = []
    metadatas = []

    for fname in sorted(os.listdir(docs_folder)):
        fpath = os.path.join(docs_folder, fname)
        if not os.path.isfile(fpath):
            continue

        ext = fname.lower().rsplit(".", 1)[-1]

        if ext in ("txt", "md"):
            with open(fpath, "r", encoding="utf-8") as f:
                raw = _clean_text(f.read())
            chunks = chunker.split_text(raw)
            for i, chunk in enumerate(chunks):
                texts.append(chunk)
                metadatas.append({"source": fname, "chunk": i})
            print(f"  [txt/md] {fname}: {len(chunks)} semantic chunk(s)")

        elif ext == "pdf":
            loader = PyPDFLoader(fpath)
            pages = loader.load()
            # Merge all pages, clean, then chunk semantically for cross-page coherence
            full_text = _clean_text("\n\n".join(p.page_content for p in pages))
            chunks = chunker.split_text(full_text)
            for i, chunk in enumerate(chunks):
                texts.append(chunk)
                metadatas.append({"source": fname, "chunk": i})
            print(f"  [pdf]    {fname}: {len(pages)} page(s) -> {len(chunks)} semantic chunk(s)")

    if not texts:
        print("No supported documents found (txt, md, pdf).")
        return

    vector_db = FaissVectorDB(embedding_model=embeddings)
    vector_db.add_texts(texts, metadatas)
    vector_db.save(faiss_path)
    print(f"\nIngested {len(texts)} semantic chunk(s) into FAISS index at: {faiss_path}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python -m nlq_sql.rag_ingest <docs_folder> <faiss_index_path>")
        sys.exit(1)
    ingest_folder(sys.argv[1], sys.argv[2])
