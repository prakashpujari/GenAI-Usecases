from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import json
import numpy as np
import faiss


@dataclass(frozen=True)
class EmbeddingItem:
    doc_id: str
    chunk_id: int
    text: str
    vector: np.ndarray


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    if chunk_size <= 0:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = max(end - chunk_overlap, end)
    return chunks


def build_faiss_index(embeddings: Iterable[EmbeddingItem], output_dir: Path) -> Path:
    vectors = [item.vector for item in embeddings]
    if not vectors:
        raise ValueError("No embeddings provided")
    matrix = np.vstack(vectors).astype("float32")
    index = faiss.IndexFlatL2(matrix.shape[1])
    index.add(matrix)

    output_dir.mkdir(parents=True, exist_ok=True)
    index_path = output_dir / "index.faiss"
    meta_path = output_dir / "metadata.json"

    faiss.write_index(index, str(index_path))
    metadata = [
        {"doc_id": item.doc_id, "chunk_id": item.chunk_id, "text": item.text}
        for item in embeddings
    ]
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return index_path
