import logging

from langchain_core.retrievers import BaseRetriever

from app.graph.state import AgentState

logger = logging.getLogger(__name__)


def retrieve_node(state: AgentState, retriever: BaseRetriever) -> AgentState:
    """Query the FAISS index and return the top-k most relevant chunks."""
    docs = retriever.invoke(state["question"])
    texts = [doc.page_content for doc in docs]

    logger.info("[retrieve] returned %d documents", len(texts))
    for i, t in enumerate(texts, 1):
        logger.debug("  [%d] %s", i, t)

    steps = list(state.get("pipeline_steps") or [])
    steps.append({
        "node": "retrieve",
        "status": "completed",
        "output": f"Retrieved {len(texts)} chunks from FAISS:\n"
                  + "\n".join(f"  • {t}" for t in texts),
    })
    return {**state, "retrieved_docs": texts, "pipeline_steps": steps}
