import logging
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.graph.state import AgentState

logger = logging.getLogger(__name__)


def llm_node(state: AgentState, llm: ChatOpenAI) -> AgentState:
    """Merge all available context and produce the final answer."""
    question = state["question"]
    retrieved_docs = state.get("retrieved_docs") or []
    sql_results = state.get("sql_results") or ""

    parts: List[str] = []

    if retrieved_docs:
        docs_block = "\n".join(f"  • {doc}" for doc in retrieved_docs)
        parts.append(f"### Retrieved Documents:\n{docs_block}")

    if sql_results:
        parts.append(f"### Database Results:\n  {sql_results}")

    context = "\n\n".join(parts) if parts else "No additional context was retrieved."

    final_prompt = (
        f"{context}\n\n"
        f"### User Question:\n{question}\n\n"
        "Provide a clear, concise answer that draws on all context above."
    )

    response = llm.invoke([
        SystemMessage(content=(
            "You are a knowledgeable assistant. "
            "Combine document knowledge and database information to answer precisely."
        )),
        HumanMessage(content=final_prompt),
    ])

    answer = response.content.strip()
    logger.info("[llm] answer generated (%d chars)", len(answer))

    steps = list(state.get("pipeline_steps") or [])
    steps.append({
        "node": "llm",
        "status": "completed",
        "output": "Final answer synthesized from all available context.",
    })
    return {**state, "final_answer": answer, "pipeline_steps": steps}
