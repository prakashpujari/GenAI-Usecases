from __future__ import annotations

import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from shared.config import settings
from shared.llm import LlmProvider
from shared.logging import configure_logging
from shared.models import LlmRequest, LlmResponse, LlmTaskType


logger = logging.getLogger("llm_router")
provider = LlmProvider()


class RouteRequest(LlmRequest):
    reasoning_required: bool = False
    pii_safe: bool = True
    allow_openai: bool = True
    load_factor: Optional[float] = None


app = FastAPI(title="Mortgage Assistant LLM Router", version="1.0.0")


@app.on_event("startup")
async def startup() -> None:
    configure_logging("llm_router")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


def _select_provider(request: RouteRequest) -> str:
    if not request.pii_safe:
        return "bedrock"

    if request.task_type == LlmTaskType.extraction:
        return "bedrock"

    if request.reasoning_required:
        return "openai" if request.allow_openai else "bedrock"

    if request.load_factor and request.load_factor > 0.8:
        return "bedrock"

    return "bedrock" if request.task_type == LlmTaskType.summarization else "openai"


@app.post("/v1/route", response_model=LlmResponse)
async def route(request: RouteRequest) -> LlmResponse:
    provider_choice = _select_provider(request)

    try:
        if provider_choice == "openai":
            content = provider.chat_openai(request.prompt, request.max_tokens, request.temperature)
            return LlmResponse(provider="openai", model=settings.openai_chat_model, content=content)

        content = provider.chat_bedrock(request.prompt, request.max_tokens, request.temperature)
        return LlmResponse(provider="bedrock", model=settings.bedrock_chat_model, content=content)
    except Exception as exc:
        logger.exception("primary_llm_failed", extra={"provider": provider_choice})
        fallback = "bedrock" if provider_choice == "openai" else "openai"
        if fallback == "openai" and not request.allow_openai:
            raise HTTPException(status_code=503, detail="No available LLM provider") from exc

        try:
            if fallback == "openai":
                content = provider.chat_openai(request.prompt, request.max_tokens, request.temperature)
                return LlmResponse(provider="openai", model=settings.openai_chat_model, content=content)

            content = provider.chat_bedrock(request.prompt, request.max_tokens, request.temperature)
            return LlmResponse(provider="bedrock", model=settings.bedrock_chat_model, content=content)
        except Exception as fallback_exc:
            logger.exception("fallback_llm_failed", extra={"provider": fallback})
            raise HTTPException(status_code=503, detail="LLM providers unavailable") from fallback_exc
