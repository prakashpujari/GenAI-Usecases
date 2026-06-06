"""
langgraph_orchestrator.py
---
LangGraph orchestration with query routing:
  - "sql"  -> LLM generates SQL -> PostgreSQL
  - "rag"  -> FAISS similarity search
  - "both" -> SQL + FAISS, then synthesize
A Synthesizer node produces a concise natural-language answer from all results.
"""

import re
from langgraph.graph import StateGraph, END
from langgraph.constants import START
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import create_engine, text
from nlq_sql.faiss_vector import FaissVectorDB


# ---------------------------------------------------------------------------
# Tool wrappers
# ---------------------------------------------------------------------------

class PostgresTool:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)

    def query(self, sql):
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            return [dict(row) for row in result.mappings()]


class RagTool:
    def __init__(self, vector_db: FaissVectorDB):
        self.vector_db = vector_db

    def retrieve(self, query, k=6, score_threshold=0.35):
        """Use score-filtered retrieval; fall back to top-k if nothing passes threshold."""
        results = self.vector_db.similarity_search_with_threshold(
            query, k=k, score_threshold=score_threshold
        )
        if not results:
            # Fallback: return top-k without score filtering
            results = self.vector_db.similarity_search(query, k=k)
        return results


# ---------------------------------------------------------------------------
# LangGraph orchestration
# ---------------------------------------------------------------------------

class NLQGraph:
    def __init__(self, db_url, faiss_path=None, llm_model="gpt-4"):
        self.llm = ChatOpenAI(model=llm_model, temperature=0)
        self.pg_tool = PostgresTool(db_url)
        self.faiss_tool = RagTool(FaissVectorDB.load(faiss_path)) if faiss_path else None
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(dict)

        # ----------------------------------------------------------------
        # Node 1: Router  – classifies query as "sql", "rag", or "both"
        # ----------------------------------------------------------------
        def router_node(state):
            has_faiss = self.faiss_tool is not None
            prompt = ChatPromptTemplate.from_template(
                "You are a query router for a Mortgage platform.\n"
                "Classify the user question into exactly one of these categories:\n"
                "  sql  - requires querying the mortgage applications database "
                "(counts, lists, approvals, applicants, dates, amounts)\n"
                "  rag  - requires looking up mortgage knowledge/policies/rates/terms "
                "(interest rates, APR, FHA, VA, PMI, eligibility, glossary)\n"
                "  both - requires BOTH database data AND knowledge lookup\n"
                "FAISS available: {has_faiss}\n"
                "If FAISS is not available, always respond with: sql\n"
                "Respond with only one word: sql, rag, or both.\n"
                "Question: {question}"
            )
            runnable = prompt | self.llm
            raw = runnable.invoke({"question": state["question"], "has_faiss": str(has_faiss)})
            content = raw.content.strip().lower() if hasattr(raw, "content") else str(raw).strip().lower()
            # Extract first word that matches a valid route
            route = "sql"
            for word in re.findall(r"\b(sql|rag|both)\b", content):
                route = word
                break
            if not has_faiss and route in ("rag", "both"):
                route = "sql"
            return {**state, "route": route}

        graph.add_node("router", router_node)

        # ----------------------------------------------------------------
        # Node 2: LLM  – generates SQL for sql / both routes
        # ----------------------------------------------------------------
        def llm_node(state):
            prompt = ChatPromptTemplate.from_template(
                "You are an expert SQL generator for a Mortgage Application Data Platform (PostgreSQL).\n"
                "Generate ONLY a safe SQL SELECT query with no explanation.\n"
                "User question: {question}\n"
                "SQL:"
            )
            runnable = prompt | self.llm
            sql_raw = runnable.invoke({"question": state["question"]})

            sql_text = sql_raw.content if hasattr(sql_raw, "content") else str(sql_raw)

            match = re.search(r"```(?:sql)?\s*([\s\S]+?)```", sql_text, re.IGNORECASE)
            if match:
                sql = match.group(1).strip()
            else:
                sel = re.search(r"(SELECT\b[\s\S]+?)(?:;|$)", sql_text, re.IGNORECASE)
                sql = sel.group(1).strip() if sel else sql_text.strip()

            return {**state, "sql": sql}

        graph.add_node("llm", llm_node)

        # ----------------------------------------------------------------
        # Node 3: Postgres  – executes SQL
        # ----------------------------------------------------------------
        def pg_node(state):
            try:
                results = self.pg_tool.query(state.get("sql", ""))
            except Exception as e:
                results = [{"error": str(e)}]
            return {**state, "results": results}

        graph.add_node("pg", pg_node)

        # ----------------------------------------------------------------
        # Node 4: RAG  – FAISS similarity search
        # ----------------------------------------------------------------
        def rag_node(state):
            docs = self.faiss_tool.retrieve(state["question"]) if self.faiss_tool else []
            return {**state, "rag_docs": docs}

        graph.add_node("rag", rag_node)

        # ----------------------------------------------------------------
        # Node 5: Synthesizer  – concise natural-language answer
        # ----------------------------------------------------------------
        def synthesizer_node(state):
            route = state.get("route", "sql")
            sql_results = state.get("results", [])
            rag_docs = state.get("rag_docs", [])
            sql = state.get("sql", "")

            rag_text = "\n\n".join(
                d.page_content if hasattr(d, "page_content") else str(d)
                for d in rag_docs
            ) if rag_docs else "N/A"

            results_text = (
                "\n".join(str(r) for r in sql_results[:10])
                if sql_results else "No rows returned."
            )

            prompt = ChatPromptTemplate.from_template(
                "You are a helpful mortgage assistant. Answer the user question concisely "
                "and accurately using ONLY the data provided below.\n\n"
                "IMPORTANT RULES:\n"
                "- If the context contains a table with exact numbers (e.g. rates, percentages), "
                "quote them directly in your answer.\n"
                "- Be specific: include exact percentages, loan types, and terms where available.\n"
                "- If the answer is not in the data, say so clearly.\n"
                "- Keep the answer to 2-4 sentences.\n\n"
                "User question: {question}\n\n"
                "Route taken: {route}\n"
                "SQL query used: {sql}\n"
                "Database results:\n{results}\n\n"
                "Knowledge base context:\n{rag_context}\n\n"
                "Answer:"
            )
            runnable = prompt | self.llm
            answer_raw = runnable.invoke({
                "question": state["question"],
                "route": route,
                "sql": sql or "N/A",
                "results": results_text,
                "rag_context": rag_text,
            })
            answer = answer_raw.content if hasattr(answer_raw, "content") else str(answer_raw)
            return {**state, "answer": answer.strip()}

        graph.add_node("synthesizer", synthesizer_node)

        # ----------------------------------------------------------------
        # Routing logic
        # ----------------------------------------------------------------
        def route_decision(state):
            return state.get("route", "sql")

        # From router: branch by route
        graph.add_conditional_edges(
            "router",
            route_decision,
            {
                "sql": "llm",
                "rag": "rag",
                "both": "llm",
            },
        )

        # SQL path: llm -> pg
        graph.add_edge("llm", "pg")

        # After pg: if "both" continue to rag, else go to synthesizer
        def after_pg_decision(state):
            return "rag" if state.get("route") == "both" else "synthesizer"

        graph.add_conditional_edges(
            "pg",
            after_pg_decision,
            {
                "rag": "rag",
                "synthesizer": "synthesizer",
            },
        )

        # RAG always goes to synthesizer
        graph.add_edge("rag", "synthesizer")

        # Synthesizer -> END
        graph.add_edge("synthesizer", END)

        # Entry
        graph.add_edge(START, "router")

        return graph.compile()

    def run(self, question):
        return self.graph.invoke({"question": question})
