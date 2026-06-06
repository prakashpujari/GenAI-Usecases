import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from langchain_openai import ChatOpenAI
from nlq_sql.main_nlq_sql import nlq_pipeline
from nlq_sql.langgraph_orchestrator import NLQGraph
import os

# --- Production-Grade UI ---
st.set_page_config(
    page_title="Mortgage Insights NLQ",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
# 🏦 Mortgage Insights NLQ
Natural Language to SQL for Mortgage Data
""", unsafe_allow_html=True)

st.sidebar.header("Configuration")
db_url = st.sidebar.text_input(
    "Database URL", value="postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
)
llm_model = st.sidebar.selectbox(
    "LLM Model", ["gpt-4"], index=0
)

if 'engine' not in st.session_state or st.session_state['engine_url'] != db_url:
    st.session_state.engine = create_engine(db_url)
    st.session_state.engine_url = db_url
    st.session_state.db_fallback = False

if 'llm' not in st.session_state or st.session_state['llm_model'] != llm_model:
    st.session_state.llm = ChatOpenAI(model=llm_model, temperature=0)
    st.session_state.llm_model = llm_model
    st.session_state.llm_fallback = False

st.markdown("""
Enter your question about mortgage applications below. Example: 
- How many mortgage applications are pending?
- Show all approved applications in the last 30 days.
""")

nlq = st.text_input("Ask a question:", key="nlq_input")

if nlq:
    with st.spinner("Processing your question..."):
        output = None
        db_fallback = False
        llm_fallback = False

        try:
            output = nlq_pipeline(nlq, st.session_state.engine, st.session_state.llm)
            st.success("Query executed successfully!")
        except SQLAlchemyError as db_err:
            st.warning(f"Primary DB error: {db_err}\nFalling back to SQLite.")
            db_fallback = True
            fallback_engine = create_engine("sqlite:///mortgage_fallback.db")
            try:
                output = nlq_pipeline(nlq, fallback_engine, st.session_state.llm)
                st.success("Query executed successfully with fallback DB!")
            except Exception as e:
                st.error(f"DB Fallback also failed: {e}")
        except Exception as llm_err:
            st.warning(f"Primary LLM error: {llm_err}\nFalling back to gpt-3.5-turbo.")
            llm_fallback = True
            fallback_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
            try:
                output = nlq_pipeline(nlq, st.session_state.engine, fallback_llm)
                st.success("Query executed successfully with fallback LLM!")
            except Exception as e:
                st.error("Sorry, your request could not be processed by either the main or fallback LLM. Only SELECT (retrieve) operations are supported, and the LLM did not generate a valid SELECT statement. Please rephrase your question or contact support.")
                output = None

        if output:
            if db_fallback:
                st.info("[Fallback] Using local SQLite database.")
            if llm_fallback:
                st.info("[Fallback] Using gpt-3.5-turbo LLM.")
            st.markdown("### Generated SQL")
            st.code(output["sql"], language="sql")
            st.markdown("### Results (table)")
            if isinstance(output["results"], list) and output["results"]:
                df = pd.DataFrame(output["results"])
                st.dataframe(df, use_container_width=True)
            elif isinstance(output["results"], list) and not output["results"]:
                st.info("No results found.")
            else:
                st.warning(str(output["results"]))
            # Show results as plain text
            st.markdown("### Results (plain text)")
            if isinstance(output["results"], list) and output["results"]:
                for row in output["results"]:
                    st.text(str(row))
            elif isinstance(output["results"], list) and not output["results"]:
                st.text("No results found.")
            else:
                st.text(str(output["results"]))

# --- LangGraph Orchestration & FAISS RAG ---
st.sidebar.markdown('---')
st.sidebar.header('RAG & Orchestration')
use_rag = st.sidebar.checkbox('Enable FAISS RAG + LangGraph', value=False)
faiss_path = st.sidebar.text_input('FAISS Index Path', value=os.path.join(os.getcwd(), 'faiss_index'))

if use_rag:
    st.markdown("---")
    st.markdown("## 🔗 LangGraph Orchestration")

    # --- Dedicated FAISS / Mortgage Rates Search ---
    st.markdown("### 🔍 Search Mortgage Rates (FAISS RAG)")
    faiss_query = st.text_input(
        "Search mortgage rates, terms, or policies:",
        placeholder="e.g. What is the rate for a 30-year FHA loan?",
        key="faiss_search_input",
    )
    col1, col2 = st.columns(2)
    with col1:
        num_results = st.slider("Max results", min_value=1, max_value=10, value=5, key="faiss_k")
    with col2:
        score_threshold = st.slider(
            "Min relevance score (0=all, 1=exact)",
            min_value=0.0, max_value=1.0, value=0.35, step=0.05, key="faiss_threshold"
        )

    if faiss_query:
        with st.spinner("Searching FAISS index..."):
            try:
                from nlq_sql.faiss_vector import FaissVectorDB
                fdb = FaissVectorDB.load(faiss_path)
                docs = fdb.similarity_search_with_threshold(
                    faiss_query, k=num_results, score_threshold=score_threshold
                )
                # Fallback if nothing passes threshold
                if not docs:
                    st.caption("No results above threshold — showing best matches anyway.")
                    docs = fdb.similarity_search(faiss_query, k=num_results)
                if docs:
                    st.caption(f"{len(docs)} result(s) found.")
                    for i, doc in enumerate(docs, 1):
                        source = doc.metadata.get("source", "unknown")
                        chunk = doc.metadata.get("chunk", "")
                        score = doc.metadata.get("relevance_score", "")
                        badge = f" | score: {score}" if score else ""
                        label = f"Result {i} — {source}, chunk {chunk}{badge}"
                        with st.expander(label, expanded=(i == 1)):
                            st.write(doc.page_content)
                else:
                    st.info("No matching documents found.")
            except Exception as fe:
                st.error(f"FAISS search error: {fe}")

    st.markdown("---")

    # --- Graph flow diagram ---
    with st.expander("📊 LangGraph Routing Flow", expanded=False):
        st.markdown("""
```
          START
            │
            ▼
    ┌───────────────┐
    │  Router Node  │  ← Classifies query as: sql | rag | both
    └──────┬────────┘
           │
   ┌───────┼──────────┐
   ▼       ▼          ▼
 sql      rag        both
   │       │          │
   ▼       │     ┌────┴─────┐
┌──────┐   │     │  LLM Node│
│ LLM  │   │     └────┬─────┘
└──┬───┘   │          ▼
   ▼       │     ┌─────────┐
┌──────┐   │     │ PG Node │
│ PG   │   │     └────┬────┘
└──┬───┘   │          │
   │       ▼          ▼
   │   ┌───────┐  ┌───────┐
   │   │  RAG  │  │  RAG  │
   │   └───┬───┘  └───┬───┘
   │       │          │
   └───────┴────┬─────┘
                ▼
        ┌───────────────┐
        │  Synthesizer  │  ← Concise natural-language answer
        └───────┬───────┘
                ▼
               END
```
        """)

    if nlq:
        with st.spinner("Routing and processing your question..."):
            try:
                graph = NLQGraph(db_url, faiss_path=faiss_path, llm_model=llm_model)
                result = graph.run(nlq)

                route = result.get("route", "sql")
                route_labels = {
                    "sql": ("🗄️ Database Query", "blue"),
                    "rag": ("📚 Knowledge Base (RAG)", "green"),
                    "both": ("🔀 Database + Knowledge Base", "orange"),
                }
                route_label, route_color = route_labels.get(route, ("unknown", "gray"))

                # Route badge
                st.markdown(
                    f"**Route taken:** &nbsp; "
                    f'<span style="background:{route_color};color:white;'
                    f'padding:3px 10px;border-radius:12px;font-size:0.85em">'
                    f'{route_label}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown("")

                # --- Concise Answer (primary output) ---
                answer = result.get("answer", "")
                if answer:
                    st.markdown("### 💬 Answer")
                    st.info(answer)
                else:
                    st.warning("No answer was synthesized.")

                # --- Supporting details ---
                sql_out = result.get("sql", "")
                results_out = result.get("results", [])
                rag_docs = result.get("rag_docs", [])

                if sql_out or results_out:
                    with st.expander("🧠 Generated SQL & Query Results", expanded=False):
                        if sql_out:
                            st.code(sql_out, language="sql")
                        if isinstance(results_out, list) and results_out:
                            df = pd.DataFrame(results_out)
                            st.dataframe(df, use_container_width=True)
                            st.caption(f"{len(results_out)} row(s) returned.")
                        elif isinstance(results_out, list) and not results_out:
                            st.info("Query returned no rows.")
                        elif results_out:
                            st.warning(str(results_out))

                if rag_docs:
                    with st.expander(f"📚 Knowledge Base Sources ({len(rag_docs)} doc(s))", expanded=False):
                        for i, doc in enumerate(rag_docs, 1):
                            source = doc.metadata.get("source", "unknown") if hasattr(doc, "metadata") else ""
                            page = doc.metadata.get("page", "") if hasattr(doc, "metadata") else ""
                            label = f"Source {i} — {source}" + (f", page {page}" if page != "" else "")
                            with st.expander(label, expanded=(i == 1)):
                                content = doc.page_content if hasattr(doc, "page_content") else str(doc)
                                st.write(content)

                with st.expander("🔍 Full LangGraph State (debug)", expanded=False):
                    st.json({k: str(v) for k, v in result.items()})

            except Exception as lg_err:
                st.error(f"LangGraph pipeline error: {lg_err}")
    else:
        st.info("Enter a question above to run the LangGraph pipeline.")
