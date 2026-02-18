from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    output_dir: Path
    faiss_dir: Path
    openai_api_key: str | None
    openai_model: str
    openai_embed_model: str
    chunk_size: int
    chunk_overlap: int


def load_settings() -> Settings:
    base_dir = Path(os.getenv("MORTGAGE_RAG_BASE", Path.cwd()))
    data_dir = Path(os.getenv("MORTGAGE_RAG_DATA", base_dir / "data"))
    output_dir = Path(os.getenv("MORTGAGE_RAG_OUTPUT", base_dir / "output"))
    faiss_dir = Path(os.getenv("MORTGAGE_RAG_FAISS", base_dir / "faiss"))

    return Settings(
        data_dir=data_dir,
        output_dir=output_dir,
        faiss_dir=faiss_dir,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_embed_model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small"),
        chunk_size=int(os.getenv("MORTGAGE_RAG_CHUNK", "800")),
        chunk_overlap=int(os.getenv("MORTGAGE_RAG_CHUNK_OVERLAP", "120")),
    )
