from fastapi import APIRouter, Request

from app.api.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    """Liveness + readiness probe for the agent API."""
    settings  = request.app.state.settings
    db_status = getattr(request.app.state, "db_status", "unknown")
    return HealthResponse(
        status="ok",
        vector_store="ready",
        database=db_status,
        llm_model=settings.openai_model,
    )
