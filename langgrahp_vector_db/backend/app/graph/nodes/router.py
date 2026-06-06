import logging

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from app.graph.state import AgentState

logger = logging.getLogger(__name__)


def router_node(state: AgentState, llm: ChatOpenAI) -> AgentState:
    """Classify the question as 'rag', 'sql', or 'both'."""
    question = state["question"]

    prompt = (
        "You are a routing assistant. Given the user question, choose the best strategy.\n\n"
        f"Question: {question}\n\n"
        "Respond with EXACTLY one word:\n"
        '- "rag"  → the answer lives in documents (concepts, descriptions)\n'
        '- "sql"  → the answer lives in a database (names, roles, records)\n'
        '- "both" → the answer needs documents AND database\n'
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    route = response.content.strip().lower()

    if route not in ("rag", "sql", "both"):
        route = "both"  # safe default

    logger.info("[router] → %s", route)

    steps = list(state.get("pipeline_steps") or [])
    steps.append({
        "node": "router",
        "status": "completed",
        "output": f"Routed to strategy: {route}",
    })
    return {**state, "route": route, "pipeline_steps": steps}
