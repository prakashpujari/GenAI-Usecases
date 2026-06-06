# =============================================================================
# rag_agent.py
#
# A complete RAG + Tool-Calling agent using:
#   - LangGraph  → workflow orchestration
#   - OpenAI     → LLM reasoning + embeddings
#   - FAISS      → semantic document retrieval
#   - PostgreSQL → structured data lookup
#
# Install dependencies:
#   pip install langgraph langchain langchain-community langchain-openai \
#               openai faiss-cpu psycopg2-binary
# =============================================================================

import os
from typing import TypedDict, Optional, List

# ---------- LangGraph ----------
from langgraph.graph import StateGraph, START, END

# ---------- LangChain – OpenAI ----------
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# ---------- LangChain – FAISS ----------
from langchain_community.vectorstores import FAISS

# ---------- LangChain – SQL ----------
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

# ---------- LangChain – Schema ----------
from langchain.schema import Document, HumanMessage, SystemMessage

# ---------- PostgreSQL (raw driver for table setup) ----------
import psycopg2


# =============================================================================
# STEP 1 – Configuration
# =============================================================================

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Set the OPENAI_API_KEY environment variable before running.")

# PostgreSQL connection string – update credentials to match your local setup
PG_DSN = "postgresql://postgres:password@localhost:5432/testdb"


# =============================================================================
# STEP 2 – LLM + Embeddings
# =============================================================================

llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=OPENAI_API_KEY)
embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)


# =============================================================================
# STEP 3 – Build FAISS Vector Index from Sample Documents
# =============================================================================

raw_docs = [
    "Software engineering involves designing, building, and maintaining software systems.",
    "Machine learning engineers build models that learn patterns from large datasets.",
    "DevOps engineers bridge development and operations to enable continuous delivery.",
    "Data engineers design pipelines that collect, store, and process large volumes of data.",
    "Cloud engineers architect and manage infrastructure on platforms like AWS, Azure, and GCP.",
    "AI engineers integrate large language models and AI tools into production applications.",
]

documents = [
    Document(page_content=text, metadata={"source": f"doc{i+1}"})
    for i, text in enumerate(raw_docs)
]

print("Building FAISS index from documents ...")
vector_store = FAISS.from_documents(documents, embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 3})
print("FAISS index ready.\n")


# =============================================================================
# STEP 4 – PostgreSQL: Create Table and Insert Sample Rows
# =============================================================================

def setup_postgres(dsn: str) -> None:
    """Create the employees table and populate it with sample data."""
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id   SERIAL PRIMARY KEY,
            name VARCHAR(100),
            role VARCHAR(100)
        );
    """)

    # Truncate so repeated runs stay idempotent
    cur.execute("TRUNCATE TABLE employees RESTART IDENTITY;")

    sample_employees = [
        ("Alice", "Software Engineer"),
        ("Bob",   "Data Engineer"),
        ("Carol", "AI Engineer"),
    ]
    cur.executemany(
        "INSERT INTO employees (name, role) VALUES (%s, %s);",
        sample_employees,
    )

    conn.commit()
    cur.close()
    conn.close()
    print("PostgreSQL 'employees' table created and populated.\n")


setup_postgres(PG_DSN)

# LangChain wrappers for SQL execution
db = SQLDatabase.from_uri(PG_DSN)
sql_tool = QuerySQLDataBaseTool(db=db)


# =============================================================================
# STEP 5 – Agent State Schema
# =============================================================================

class AgentState(TypedDict):
    question:       str                    # Original user question
    route:          Optional[str]          # "rag" | "sql" | "both"
    retrieved_docs: Optional[List[str]]    # Chunks from FAISS
    sql_results:    Optional[str]          # Raw SQL output
    final_answer:   Optional[str]          # LLM-generated answer


# =============================================================================
# STEP 6 – Node: router
#   Decides whether the question requires RAG, SQL, or both.
# =============================================================================

def router_node(state: AgentState) -> AgentState:
    question = state["question"]

    prompt = (
        "You are a routing assistant. Given the user question, choose the best strategy.\n\n"
        f"Question: {question}\n\n"
        "Respond with EXACTLY one word:\n"
        '- "rag"  → the answer lives in documents (concepts, descriptions, general knowledge)\n'
        '- "sql"  → the answer lives in a database (names, roles, structured records)\n'
        '- "both" → the answer needs both documents AND database\n'
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    route = response.content.strip().lower()

    if route not in ("rag", "sql", "both"):
        route = "both"  # safe default

    print(f"[router] → {route}")
    return {**state, "route": route}


# =============================================================================
# STEP 7 – Node: retrieve
#   Queries the FAISS index for the top-3 most relevant document chunks.
# =============================================================================

def retrieve_node(state: AgentState) -> AgentState:
    docs = retriever.invoke(state["question"])
    retrieved_texts = [doc.page_content for doc in docs]

    print(f"[retrieve] {len(retrieved_texts)} documents returned")
    for i, t in enumerate(retrieved_texts, 1):
        print(f"  [{i}] {t}")

    return {**state, "retrieved_docs": retrieved_texts}


# =============================================================================
# STEP 8 – Node: sql
#   Asks the LLM to write a SQL query, then executes it via QuerySQLDataBaseTool.
# =============================================================================

def sql_node(state: AgentState) -> AgentState:
    question = state["question"]

    # Ask the LLM to generate an appropriate SQL query
    sql_prompt = (
        "You are a SQL expert. The database contains one table:\n"
        "  employees(id INTEGER, name VARCHAR, role VARCHAR)\n\n"
        f"Write a SQL SELECT query that answers: {question}\n\n"
        "Return ONLY the SQL statement, nothing else."
    )
    sql_response = llm.invoke([HumanMessage(content=sql_prompt)])
    sql_query = sql_response.content.strip().strip("```sql").strip("```").strip()

    print(f"[sql] Generated query: {sql_query}")

    try:
        sql_results = sql_tool.invoke(sql_query)
    except Exception as exc:
        sql_results = f"SQL error: {exc}"

    print(f"[sql] Results: {sql_results}")
    return {**state, "sql_results": sql_results}


# =============================================================================
# STEP 9 – Node: llm
#   Merges retrieved documents + SQL results with the question and produces
#   a coherent final answer.
# =============================================================================

def llm_node(state: AgentState) -> AgentState:
    question       = state["question"]
    retrieved_docs = state.get("retrieved_docs") or []
    sql_results    = state.get("sql_results") or ""

    context_parts: List[str] = []

    if retrieved_docs:
        docs_block = "\n".join(f"  • {doc}" for doc in retrieved_docs)
        context_parts.append(f"### Retrieved Documents:\n{docs_block}")

    if sql_results:
        context_parts.append(f"### Database Query Results:\n  {sql_results}")

    context = (
        "\n\n".join(context_parts)
        if context_parts
        else "No additional context was retrieved."
    )

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

    final_answer = response.content.strip()
    print(f"\n[llm] Final answer:\n{final_answer}")
    return {**state, "final_answer": final_answer}


# =============================================================================
# STEP 10 – Conditional Routing Functions
# =============================================================================

def route_after_router(state: AgentState) -> str:
    """After the router node, decide the first retrieval step."""
    route = state.get("route", "both")
    if route == "sql":
        return "sql"
    # "rag" or "both" → start with document retrieval
    return "retrieve"


def route_after_retrieve(state: AgentState) -> str:
    """After retrieval, check whether SQL is also needed."""
    if state.get("route") == "both":
        return "sql"
    return "llm"


# =============================================================================
# STEP 11 – Build and Compile the LangGraph
# =============================================================================

graph_builder = StateGraph(AgentState)

# -- Register nodes --
graph_builder.add_node("router",   router_node)
graph_builder.add_node("retrieve", retrieve_node)
graph_builder.add_node("sql",      sql_node)
graph_builder.add_node("llm",      llm_node)

# -- Entry point --
graph_builder.add_edge(START, "router")

# -- router → retrieve | sql  (conditional) --
graph_builder.add_conditional_edges(
    "router",
    route_after_router,
    {"retrieve": "retrieve", "sql": "sql"},
)

# -- retrieve → sql | llm  (conditional) --
graph_builder.add_conditional_edges(
    "retrieve",
    route_after_retrieve,
    {"sql": "sql", "llm": "llm"},
)

# -- sql → llm (always) --
graph_builder.add_edge("sql", "llm")

# -- llm → END --
graph_builder.add_edge("llm", END)

# Compile into a runnable graph
graph = graph_builder.compile()
print("LangGraph compiled successfully.\n")


# =============================================================================
# STEP 12 – Run the Agent with Three Example Queries
# =============================================================================

def run_query(label: str, question: str) -> None:
    print("=" * 60)
    print(f"QUERY: {label}")
    print(f"  {question}")
    print("=" * 60)

    initial_state: AgentState = {
        "question":       question,
        "route":          None,
        "retrieved_docs": None,
        "sql_results":    None,
        "final_answer":   None,
    }

    result = graph.invoke(initial_state)
    print(f"\n>>> Answer:\n{result['final_answer']}\n")


if __name__ == "__main__":

    # 1. Both RAG + SQL: question spans documents and the employee database
    run_query(
        label    = "Combined (RAG + SQL)",
        question = "Who is the engineer and what documents mention engineering?",
    )

    # 2. RAG only: conceptual question answered by documents
    run_query(
        label    = "RAG only",
        question = "What do cloud engineers do?",
    )

    # 3. SQL only: structured data question answered by the database
    run_query(
        label    = "SQL only",
        question = "List all employees and their roles.",
    )


# =============================================================================
# EXAMPLE OUTPUT
# =============================================================================
#
# Building FAISS index from documents ...
# FAISS index ready.
#
# PostgreSQL 'employees' table created and populated.
#
# LangGraph compiled successfully.
#
# ============================================================
# QUERY: Combined (RAG + SQL)
#   Who is the engineer and what documents mention engineering?
# ============================================================
# [router] → both
# [retrieve] 3 documents returned
#   [1] Software engineering involves designing, building, and maintaining software systems.
#   [2] Machine learning engineers build models that learn patterns from large datasets.
#   [3] AI engineers integrate large language models and AI tools into production applications.
# [sql] Generated query: SELECT name, role FROM employees;
# [sql] Results: [('Alice', 'Software Engineer'), ('Bob', 'Data Engineer'), ('Carol', 'AI Engineer')]
#
# [llm] Final answer:
# The engineers in the database are:
#   • Alice – Software Engineer
#   • Bob   – Data Engineer
#   • Carol – AI Engineer
#
# Documents that mention engineering cover: software engineering, machine learning
# engineers, DevOps engineers, data engineers, cloud engineers, and AI engineers.
#
# ============================================================
# QUERY: RAG only
#   What do cloud engineers do?
# ============================================================
# [router] → rag
# [retrieve] 3 documents returned
#   [1] Cloud engineers architect and manage infrastructure on platforms like AWS, Azure, and GCP.
#   ...
# [llm] Final answer:
# Cloud engineers design and manage cloud infrastructure on platforms such as
# AWS, Azure, and Google Cloud Platform (GCP).
#
# ============================================================
# QUERY: SQL only
#   List all employees and their roles.
# ============================================================
# [router] → sql
# [sql] Generated query: SELECT name, role FROM employees;
# [sql] Results: [('Alice', 'Software Engineer'), ('Bob', 'Data Engineer'), ('Carol', 'AI Engineer')]
# [llm] Final answer:
# Here are all the employees and their roles:
#   1. Alice – Software Engineer
#   2. Bob   – Data Engineer
#   3. Carol – AI Engineer
