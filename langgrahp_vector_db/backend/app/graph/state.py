from typing import List, Optional, TypedDict


class PipelineStep(TypedDict):
    node: str
    status: str    # "completed" | "error" | "skipped"
    output: str


class AgentState(TypedDict):
    question: str
    route: Optional[str]            # "rag" | "sql" | "both"
    retrieved_docs: Optional[List[str]]
    sql_results: Optional[str]
    final_answer: Optional[str]
    pipeline_steps: List[PipelineStep]
