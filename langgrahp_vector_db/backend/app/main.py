import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI

from app.api.routes import health as health_routes
from app.api.routes import ingest as ingest_routes
from app.api.routes import query as query_routes
from app.config import get_settings
from app.graph.builder import build_graph
from app.logging_config import configure_logging
from app.tools.sql_tool import build_sql_tool, setup_postgres
from app.tools.vector_store import build_or_load_store, build_retriever

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan – initialise all heavy resources once on startup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("Starting RAG Agent API …")

    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=0,
        api_key=settings.openai_api_key,
    )
    faiss_store, _ = build_or_load_store(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
    )
    retriever = build_retriever(faiss_store)

    # PostgreSQL is optional – if unavailable the server still starts
    # but SQL-routed queries will return an error in the sql_node.
    sql_tool = None
    db_status = "unavailable"
    try:
        setup_postgres(settings.postgres_dsn)
        _, sql_tool = build_sql_tool(settings.postgres_dsn)
        db_status = "ready"
    except Exception as exc:
        logger.warning("PostgreSQL unavailable – SQL tool disabled: %s", exc)

    # Compile the graph once; store on app.state for route handlers
    app.state.graph       = build_graph(llm=llm, retriever=retriever, sql_tool=sql_tool)
    app.state.settings    = settings
    app.state.db_status   = db_status
    app.state.faiss_store = faiss_store   # exposed to /api/ingest

    logger.info("RAG Agent API ready (db=%s).", db_status)
    yield
    logger.info("RAG Agent API shutting down.")


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="RAG Agent API",
    description="LangGraph + OpenAI + FAISS + PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],   # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query_routes.router,  prefix="/api", tags=["query"])
app.include_router(health_routes.router, prefix="/api", tags=["health"])
app.include_router(ingest_routes.router, prefix="/api", tags=["ingest"])
