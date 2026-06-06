import logging

from fastapi import APIRouter, HTTPException, Request

from app.api.schemas import PipelineStep, QueryRequest, QueryResponse
from app.graph.state import AgentState

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/query", response_model=QueryResponse)
async def run_query(request: Request, body: QueryRequest) -> QueryResponse:
    """Run the LangGraph agent and return the full pipeline trace."""
    graph = request.app.state.graph

    initial_state: AgentState = {
        "question": body.question,
        "route": None,
        "retrieved_docs": None,
        "sql_results": None,
        "final_answer": None,
        "pipeline_steps": [],
    }

    try:
        result = graph.invoke(initial_state)
    except Exception as exc:
        logger.exception("Graph execution failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))

    return QueryResponse(
        question=result["question"],
        route=result.get("route") or "unknown",
        retrieved_docs=result.get("retrieved_docs") or [],
        sql_results=result.get("sql_results"),
        final_answer=result.get("final_answer") or "",
        pipeline_steps=[
            PipelineStep(**s) for s in (result.get("pipeline_steps") or [])
        ],
    )
