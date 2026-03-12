from __future__ import annotations

from fastapi import FastAPI

from .schemas import AUSRequest, AUSResponse
from .service import evaluate_aus


app = FastAPI(
    title="Mortgage AUS Service",
    description="Production-ready Automated Underwriting System (AUS) simulation API for mortgage lending.",
    version="1.0.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/aus/evaluate", response_model=AUSResponse)
def evaluate(request: AUSRequest) -> AUSResponse:
    return evaluate_aus(request)
