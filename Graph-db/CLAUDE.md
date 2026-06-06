# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Mortgage Graph Platform** is a production-grade Neo4j mortgage knowledge graph implementation with ontology translation, ETL, GDS analytics, and FastAPI risk/compliance endpoints.

Stack: Python 3.11+, FastAPI, Neo4j 5.x, Streamlit, pandas, RDFlib

## Development Setup

### Local Environment (without Docker)

**Windows (native Neo4j)**
```powershell
# 1. Set Java 17 environment
$env:JAVA_HOME='C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot'
$env:Path="$env:JAVA_HOME\bin;$env:Path"

# 2. Initialize Neo4j password (first run only)
.\.local-tools\neo4j-community-5.26.0\bin\neo4j-admin.bat dbms set-initial-password "changeme123"

# 3. Start Neo4j
.\.local-tools\neo4j-community-5.26.0\bin\neo4j.bat console

# 4. In separate terminal, start API
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 5. Optional: start Streamlit UI
.\.venv\Scripts\python.exe -m streamlit run app/ui/streamlit_app.py --server.address 127.0.0.1 --server.port 8501
```

**Docker**
```bash
docker compose up -d --build
docker compose exec api python -m app.etl.migrate_schema
docker compose exec api python -m app.etl.run_full_load
docker compose exec api python -m app.gds.run_gds_jobs
```

### Environment Configuration

Copy `.env.example` to `.env` and configure:
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `NEO4J_DATABASE` — Neo4j connection
- `STORAGE_BACKEND` — "neo4j" (default, enables risk/explain) or "postgres" (ingest-only mode)
- `DATA_PATH`, `EXPORT_PATH` — file system paths

**Important**: Machine-level environment variables override `.env` values. Check with `Get-ChildItem Env:NEO4J*` on Windows.

## Architecture

### Layers

- **`app/config`** — Environment-driven settings (pydantic-settings) and structured logging
- **`app/db`** — Resilient database clients (Neo4j with exponential backoff retry, optional Postgres)
- **`app/domain`** — Pydantic schemas and scoring logic (Borrower, Loan, Property, etc.)
- **`app/etl`** — Batch ingestion pipelines and idempotent schema setup
- **`app/services`** — Business logic (IngestService, RiskService, RuleEngine, GraphRepository)
- **`app/api`** — FastAPI routes (dependency injection for DB clients, error handling)
- **`app/gds`** — Graph Data Science job orchestration
- **`app/ontology`** — OWL/RDF to Labeled Property Graph translation
- **`app/ui`** — Streamlit dashboard for visualization and graph exploration
- **`cypher/`** — Reusable Cypher query scripts
- **`scripts/`** — Export and utility jobs (e.g., export_metrics.py)
- **`tests/`** — Unit and API tests with pytest

### Key Components

**Neo4jClient** (`app/db/neo4j_client.py`)
- Exponential backoff retry (4 attempts, 1–8s waits) on all queries
- Single session per request; closed in route finally blocks
- Both read and write operations wrapped in tenacity retry logic

**API Routes** (`app/api/routes.py`)
- Health check at `GET /health`
- Ingest: `POST /loans/ingest` — supports both Neo4j and Postgres backends
- Risk: `GET /loans/{loanId}/risk` — Neo4j only (returns traditional + graph metrics)
- Explain: `GET /loans/{loanId}/explain` — Neo4j only (rules, regulations, graph contributions)
- Errors: 503 on DB unavailable, 501 on unsupported backend, 404 on missing loan

**IngestService** → GraphRepository (upsert loan bundles) + RuleEngine (evaluate underwriting rules)

**RiskService** → computes fraud/risk signals, graph metrics, and violations

### Data Model

Core entities: `Borrower`, `Loan`, `Property`, `IncomeSource`, `Document`, `UnderwritingRule`, `Regulation`

Ingestion is idempotent—upserting by primary key (e.g., `loanId`).

## Common Commands

### API & Services

```bash
# Start FastAPI (local native)
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Health check
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/docs  # Swagger UI
```

### ETL & Schema

```bash
# Apply schema migrations
python -m app.etl.migrate_schema

# Run full ETL load
python -m app.etl.run_full_load
```

### Graph Analytics (GDS)

```bash
# Run GDS projection & algorithm jobs
python -m app.gds.run_gds_jobs
```

### Ontology Translation

```bash
# Translate OWL/RDF to LPG mapping
python -m app.ontology.run_translate --input ./ontology --output ./exports/mapping.yaml --overrides ./ontology/overrides.yaml
```

### Exports

```bash
# Export metrics to CSV/Parquet
python scripts/export_metrics.py
# Output: exports/loan_metrics.csv, exports/loan_metrics.parquet
```

### Testing

```bash
# Run all tests
pytest -q

# Run single test file
pytest tests/test_api.py -v

# Run a specific test
pytest tests/test_api.py::test_function_name -v
```

### Streamlit UI

```bash
# Local
.venv\Scripts\python.exe -m streamlit run app/ui/streamlit_app.py --server.address 127.0.0.1 --server.port 8501

# Docker
docker compose exec api streamlit run app/ui/streamlit_app.py --server.port 8501
```

## Key Design Patterns

**Dependency Injection**: `get_settings()` and database clients passed as FastAPI dependencies → ensures clean teardown (finally blocks).

**Idempotent Upserts**: ETL uses MERGE and ON MATCH/CREATE patterns → safe retries.

**Retry with Exponential Backoff**: Neo4j client wraps all queries with tenacity → handles transient failures.

**Dual Storage Backend**: `storage_backend` setting routes requests to Neo4j or Postgres; risk/explain 501 on Postgres (Neo4j-only features).

**Error Handling**: 503 for database unavailable (ServiceUnavailable, AuthError, Neo4jError), 404 for missing loans, 501 for unsupported operations.

## Testing

Test files:
- `tests/test_api.py` — FastAPI endpoint tests
- `tests/test_migrations.py` — Schema setup validation
- `tests/test_risk_scoring.py` — Risk calculation logic
- `tests/test_transforms.py` — ETL transformation functions

Run with `pytest -q` (quiet) or `-v` (verbose). pytestconfig in `pyproject.toml`: `pythonpath=["."]`, `testpaths=["tests"]`.

## Troubleshooting

**Database unavailable on localhost:7687**
- Check: `Test-NetConnection -ComputerName localhost -Port 7687` (Windows)
- Ensure Neo4j process is running and Bolt listener enabled

**Neo4j auth failure**
- Verify `.env` password matches Neo4j initial password
- Check for machine-level `NEO4J_PASSWORD` override: `Get-ChildItem Env:NEO4J*`

**Java version mismatch**
- Neo4j 5.x requires Java 17+
- Set `JAVA_HOME` before starting Neo4j

**Docker unavailable**
- Fall back to native Neo4j + local FastAPI/Streamlit (documented in README)

## References

- **Neo4j Driver**: retryable operations with exponential backoff in `Neo4jClient`
- **FastAPI**: dependency injection pattern in `routes.py` for DB client lifecycle
- **Pydantic**: domain models validate ingest payloads; Settings loads from `.env`
- **RDFlib**: OWL/RDF parsing in ontology translator
- **Streamlit**: interactive UI with graph explorer in `app/ui/streamlit_app.py`
