"""
Enhanced FastAPI routes for React UI support.
This file contains refactored routes split into logical groups.
Will replace the current routes.py in production.
"""

from __future__ import annotations

from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
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


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@router.get("/health")
def health(settings: Settings = Depends(get_settings)) -> dict:
    """Check API and database health status."""
    try:
        neo4j = Neo4jClient(settings)
        neo4j.verify_connectivity()
        neo4j.close()
        return {"status": "ok", "database": "neo4j"}
    except Exception:
        try:
            if settings.storage_backend == "postgres":
                pg = PostgresClient(settings)
                _ = pg._get_connection()
                return {"status": "ok", "database": "postgres"}
        except Exception:
            pass
        return {"status": "unavailable", "database": "unknown"}


@router.get("/metrics")
def metrics(settings: Settings = Depends(get_settings)) -> dict:
    """Get dashboard metrics (cached for 5 minutes in production)."""
    if settings.storage_backend == "postgres":
        return {
            "totalLoans": 0,
            "totalBorrowers": 0,
            "avgRiskScore": None,
            "networkDensity": None,
            "lastGdsJobTime": None,
            "lastGdsJobStatus": None,
        }

    neo4j = Neo4jClient(settings)
    try:
        # Query total loans and borrowers
        loan_count = neo4j.run_read(
            "MATCH (l:Loan) RETURN count(l) as count"
        )
        borrower_count = neo4j.run_read(
            "MATCH (b:Borrower) RETURN count(b) as count"
        )

        # Query average risk score (placeholder)
        risk_avg = neo4j.run_read(
            "MATCH (l:Loan) WHERE l.riskScore IS NOT NULL "
            "RETURN avg(l.riskScore) as avg_risk"
        )

        total_loans = loan_count[0].get("count", 0) if loan_count else 0
        total_borrowers = borrower_count[0].get("count", 0) if borrower_count else 0
        avg_risk_score = risk_avg[0].get("avg_risk") if risk_avg and risk_avg[0] else None

        return {
            "totalLoans": total_loans,
            "totalBorrowers": total_borrowers,
            "avgRiskScore": avg_risk_score,
            "networkDensity": None,  # Requires GDS metrics
            "lastGdsJobTime": None,  # Would come from job tracking
            "lastGdsJobStatus": None,
        }
    except (ServiceUnavailable, AuthError, Neo4jError, OSError) as exc:
        raise _db_unavailable(exc) from exc
    finally:
        neo4j.close()


# ============================================================================
# LOAN ENDPOINTS
# ============================================================================

@router.post("/loans/ingest")
def ingest_loan(payload: LoanIngestPayload, settings: Settings = Depends(get_settings)) -> dict:
    """Ingest a new loan bundle."""
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


@router.get("/loans")
def list_loans(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    settings: Settings = Depends(get_settings),
) -> dict:
    """Get paginated list of loans with summary data."""
    if settings.storage_backend == "postgres":
        return {"items": [], "total": 0}

    neo4j = Neo4jClient(settings)
    try:
        # Query loans with pagination
        query = """
        MATCH (b:Borrower)-[:OWNS]->(l:Loan)
        RETURN l.loanId as loanId, b.name as borrowerName, l.amount as amount,
               l.status as status, l.riskScore as riskScore, l.createdAt as createdAt
        ORDER BY l.createdAt DESC
        SKIP $offset
        LIMIT $limit
        """

        items = neo4j.run_read(query, {"offset": offset, "limit": limit})

        # Query total count
        count_result = neo4j.run_read("MATCH (l:Loan) RETURN count(l) as total")
        total = count_result[0]["total"] if count_result else 0

        return {"items": items, "total": total}
    except (ServiceUnavailable, AuthError, Neo4jError, OSError) as exc:
        raise _db_unavailable(exc) from exc
    finally:
        neo4j.close()


@router.get("/loans/{loan_id}")
def get_loan_detail(loan_id: str, settings: Settings = Depends(get_settings)) -> dict:
    """Get detailed loan information with all relationships."""
    if settings.storage_backend == "postgres":
        raise HTTPException(status_code=501, detail="Loan detail endpoint is only available with storage_backend=neo4j")

    neo4j = Neo4jClient(settings)
    try:
        # Query loan with all relationships
        query = """
        MATCH (l:Loan {loanId: $loanId})
        OPTIONAL MATCH (b:Borrower)-[:OWNS]->(l)
        OPTIONAL MATCH (l)-[:ON]->(p:Property)
        OPTIONAL MATCH (b)-[:HAS_INCOME]->(i:IncomeSource)
        OPTIONAL MATCH (l)-[:HAS_DOCUMENT]->(d:Document)
        RETURN {
            loan: l, borrower: b, property: p, income: i,
            documents: collect(d), riskScore: l.riskScore,
            networkRiskScore: l.networkRiskScore
        } as result
        """

        result = neo4j.run_read(query, {"loanId": loan_id})
        if not result:
            raise HTTPException(status_code=404, detail=f"Loan {loan_id} not found")

        return result[0].get("result", {})
    except (ServiceUnavailable, AuthError, Neo4jError, OSError) as exc:
        raise _db_unavailable(exc) from exc
    finally:
        neo4j.close()


# ============================================================================
# RISK ENDPOINTS (existing)
# ============================================================================

@router.get("/loans/{loan_id}/risk", response_model=RiskResponse)
def loan_risk(loan_id: str, settings: Settings = Depends(get_settings)) -> RiskResponse:
    """Get risk metrics for a loan."""
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
    """Get explainability details for a loan."""
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


# ============================================================================
# GRAPH EXPLORATION ENDPOINTS
# ============================================================================

@router.post("/graph/query")
def graph_query(
    request: dict,
    settings: Settings = Depends(get_settings),
) -> dict:
    """Execute a Cypher query against Neo4j (with validation)."""
    if settings.storage_backend == "postgres":
        raise HTTPException(status_code=501, detail="Graph query endpoint is only available with storage_backend=neo4j")

    cypher = request.get("cypher", "")
    params = request.get("params", {})

    # Simple Cypher validation (blocklist dangerous patterns)
    dangerous_patterns = ["LOAD CSV", "CALL apoc", "ALTER DATABASE", "ALTER SYSTEM"]
    if any(pattern in cypher.upper() for pattern in dangerous_patterns):
        raise HTTPException(status_code=400, detail="Dangerous Cypher pattern detected")

    neo4j = Neo4jClient(settings)
    try:
        # Add LIMIT to prevent runaway queries
        if "LIMIT" not in cypher.upper():
            cypher += " LIMIT 1000"

        result = neo4j.run_read(cypher, params)

        # Transform result to match GraphQueryResponse format
        columns = list(result[0].keys()) if result else []
        rows = result if result else []

        return {"columns": columns, "rows": rows}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Cypher error: {str(exc)}") from exc
    finally:
        neo4j.close()


@router.get("/graph/nodes/{node_id}")
def get_node_details(node_id: str, settings: Settings = Depends(get_settings)) -> dict:
    """Get details about a specific node."""
    if settings.storage_backend == "postgres":
        raise HTTPException(status_code=501, detail="Graph node endpoint is only available with storage_backend=neo4j")

    neo4j = Neo4jClient(settings)
    try:
        query = """
        MATCH (n) WHERE id(n) = $node_id
        RETURN {
            id: id(n), labels: labels(n), properties: properties(n)
        } as node
        """

        result = neo4j.run_read(query, {"node_id": int(node_id)})
        if not result:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found")

        return result[0].get("node", {})
    except (ServiceUnavailable, AuthError, Neo4jError, OSError) as exc:
        raise _db_unavailable(exc) from exc
    finally:
        neo4j.close()


# ============================================================================
# JOBS ENDPOINTS (PLACEHOLDER)
# ============================================================================

@router.get("/jobs")
def list_jobs(settings: Settings = Depends(get_settings)) -> dict:
    """Get list of recent GDS/ETL jobs (placeholder)."""
    # In production, integrate with job queue (Celery, APScheduler, etc.)
    return {
        "jobs": [
            {
                "jobId": "job-001",
                "type": "gds",
                "status": "completed",
                "startTime": "2026-01-15T10:00:00Z",
                "endTime": "2026-01-15T10:05:00Z",
                "progress": 100,
            }
        ]
    }


@router.post("/jobs/gds/{job_type}")
def run_gds_job(
    job_type: str,
    settings: Settings = Depends(get_settings),
) -> dict:
    """Trigger a GDS job (placeholder)."""
    valid_types = ["project-fraud", "project-risk", "community-detection", "centrality", "similarity", "run-all"]
    if job_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid job type: {job_type}")

    # In production, queue the job asynchronously
    return {"jobId": f"job-{job_type}-{int(__import__('time').time())}", "status": "pending"}


@router.get("/jobs/{job_id}")
def get_job_status(job_id: str, settings: Settings = Depends(get_settings)) -> dict:
    """Get status of a specific job (placeholder)."""
    # In production, fetch from job queue
    return {
        "jobId": job_id,
        "type": "gds",
        "status": "completed",
        "startTime": "2026-01-15T10:00:00Z",
        "endTime": "2026-01-15T10:05:00Z",
        "progress": 100,
    }
