import logging
from functools import partial
from typing import Optional

from langchain_core.retrievers import BaseRetriever
from langchain_community.tools import QuerySQLDatabaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from app.graph.nodes.llm_node import llm_node
from app.graph.nodes.retrieve import retrieve_node
from app.graph.nodes.router import router_node
from app.graph.nodes.sql_node import sql_node
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Conditional edge functions
# ---------------------------------------------------------------------------

def _route_after_router(state: AgentState) -> str:
    """sql-only questions skip retrieval; everything else retrieves first."""
    return "sql" if state.get("route") == "sql" else "retrieve"


def _route_after_retrieve(state: AgentState) -> str:
    """After retrieval, also run SQL when route is 'both'."""
    return "sql" if state.get("route") == "both" else "llm"


# ---------------------------------------------------------------------------
# Graph factory
# ---------------------------------------------------------------------------

def build_graph(
    llm: ChatOpenAI,
    retriever: BaseRetriever,
    sql_tool: Optional[QuerySQLDatabaseTool],
):
    """Compile and return the runnable LangGraph agent.

    Dependency injection keeps each node pure and independently testable:
      - router_node   ← llm
      - retrieve_node ← retriever
      - sql_node      ← llm, sql_tool
      - llm_node      ← llm
    """
    g = StateGraph(AgentState)

    g.add_node("router",   partial(router_node,   llm=llm))
    g.add_node("retrieve", partial(retrieve_node, retriever=retriever))
    g.add_node("sql",      partial(sql_node,      llm=llm, sql_tool=sql_tool))
    g.add_node("llm",      partial(llm_node,      llm=llm))

    g.add_edge(START, "router")

    g.add_conditional_edges(
        "router",
        _route_after_router,
        {"retrieve": "retrieve", "sql": "sql"},
    )
    g.add_conditional_edges(
        "retrieve",
        _route_after_retrieve,
        {"sql": "sql", "llm": "llm"},
    )
    g.add_edge("sql", "llm")
    g.add_edge("llm", END)

    compiled = g.compile()
    logger.info("LangGraph compiled successfully.")
    return compiled
