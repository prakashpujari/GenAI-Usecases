from typing import List, Optional

from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class PipelineStep(BaseModel):
    node: str
    status: str   # "completed" | "error" | "skipped"
    output: str


class QueryResponse(BaseModel):
    question: str
    route: str
    retrieved_docs: List[str]
    sql_results: Optional[str]
    final_answer: str
    pipeline_steps: List[PipelineStep]


class HealthResponse(BaseModel):
    status: str
    vector_store: str
    database: str
    llm_model: str


# ---------------------------------------------------------------------------
# PDF ingestion schemas
# ---------------------------------------------------------------------------

class DocumentInfo(BaseModel):
    filename: str
    pages: int
    chunks: int
    skipped: bool = False
    message: str = ""


class IngestResponse(BaseModel):
    message: str
    documents: List[DocumentInfo]
    total_chunks: int
