import logging
from typing import Optional

from langchain_core.messages import HumanMessage
from langchain_community.tools import QuerySQLDatabaseTool
from langchain_openai import ChatOpenAI

from app.graph.state import AgentState

logger = logging.getLogger(__name__)


def sql_node(
    state: AgentState,
    llm: ChatOpenAI,
    sql_tool: Optional[QuerySQLDatabaseTool],
) -> AgentState:
    """Ask the LLM to generate a SQL query, execute it, and store results."""

    # Graceful degradation when PostgreSQL is unavailable
    if sql_tool is None:
        logger.warning("[sql] SQL tool unavailable (PostgreSQL not connected).")
        steps = list(state.get("pipeline_steps") or [])
        steps.append({
            "node": "sql",
            "status": "error",
            "output": "SQL tool unavailable – PostgreSQL is not configured or unreachable.",
        })
        return {**state, "sql_results": "Database unavailable.", "pipeline_steps": steps}

    question = state["question"]

    sql_prompt = (
        "You are a SQL expert. The database has one table:\n"
        "  employees(id INTEGER, name VARCHAR, role VARCHAR)\n\n"
        f"Write a SQL SELECT query that answers: {question}\n\n"
        "Return ONLY the SQL statement, nothing else."
    )

    sql_response = llm.invoke([HumanMessage(content=sql_prompt)])
    sql_query = (
        sql_response.content.strip()
        .removeprefix("```sql")
        .removesuffix("```")
        .strip()
    )
    logger.info("[sql] generated query: %s", sql_query)

    try:
        sql_results = sql_tool.invoke(sql_query)
        step_status = "completed"
        step_output = f"Query:\n  {sql_query}\n\nResults:\n  {sql_results}"
        logger.info("[sql] results: %s", sql_results)
    except Exception as exc:
        sql_results = f"SQL error: {exc}"
        step_status = "error"
        step_output = f"Query:\n  {sql_query}\n\nError:\n  {exc}"
        logger.error("[sql] error executing query: %s", exc)

    steps = list(state.get("pipeline_steps") or [])
    steps.append({"node": "sql", "status": step_status, "output": step_output})
    return {**state, "sql_results": sql_results, "pipeline_steps": steps}
