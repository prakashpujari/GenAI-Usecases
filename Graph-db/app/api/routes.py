from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from neo4j.exceptions import AuthError, Neo4jError, ServiceUnavailable
import psycopg

from app.config.settings import Settings, get_settings
from app.db.neo4j_client import Neo4jClient
from app.db.postgres_client import PostgresClient
from app.domain.models import ExplainResponse, LoanIngestPayload, RiskResponse
from app.services.ingest_service import IngestService
from app.services.risk_service import RiskService

router = APIRouter()


def _db_unavailable(exc: Exception) -> HTTPException:
    return HTTPException(
        status_code=503,
        detail=f"Database unavailable: {exc}",
    )


def get_neo4j(settings: Settings = Depends(get_settings)) -> Neo4jClient:
    client = Neo4jClient(settings)
    try:
        client.verify_connectivity()
        return client
    except Exception:
        client.close()
        raise


@router.post("/loans/ingest")
def ingest_loan(payload: LoanIngestPayload, settings: Settings = Depends(get_settings)) -> dict:
    if settings.storage_backend == "postgres":
        pg = PostgresClient(settings)
        try:
            pg.ensure_schema()
            pg.upsert_ingest_event(
                loan_id=payload.loan.loanId,
                payload=payload.model_dump(mode="json"),
                violations=[],
            )
            return {"loanId": payload.loan.loanId, "violations": [], "status": "ingested"}
        except psycopg.Error as exc:
            raise HTTPException(status_code=503, detail=f"Postgres unavailable: {exc}") from exc

    neo4j = Neo4jClient(settings)
    try:
        neo4j.verify_connectivity()
        return IngestService(neo4j).ingest(payload)
    except (ServiceUnavailable, AuthError, Neo4jError, OSError) as exc:
        raise _db_unavailable(exc) from exc
    finally:
        neo4j.close()


@router.get("/loans/{loan_id}/risk", response_model=RiskResponse)
def loan_risk(loan_id: str, settings: Settings = Depends(get_settings)) -> RiskResponse:
    if settings.storage_backend == "postgres":
        raise HTTPException(status_code=501, detail="Risk endpoint is only available with storage_backend=neo4j")

    neo4j = Neo4jClient(settings)
    try:
        neo4j.verify_connectivity()
        try:
            return RiskService(neo4j).get_risk(loan_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except (ServiceUnavailable, AuthError, Neo4jError, OSError) as exc:
            raise _db_unavailable(exc) from exc
    finally:
        neo4j.close()


@router.get("/loans/{loan_id}/explain", response_model=ExplainResponse)
def loan_explain(loan_id: str, settings: Settings = Depends(get_settings)) -> ExplainResponse:
    if settings.storage_backend == "postgres":
        raise HTTPException(status_code=501, detail="Explain endpoint is only available with storage_backend=neo4j")

    neo4j = Neo4jClient(settings)
    try:
        neo4j.verify_connectivity()
        return RiskService(neo4j).explain(loan_id)
    except (ServiceUnavailable, AuthError, Neo4jError, OSError) as exc:
        raise _db_unavailable(exc) from exc
    finally:
        neo4j.close()
