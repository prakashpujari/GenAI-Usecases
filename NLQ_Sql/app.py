import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from langchain_openai import ChatOpenAI
from nlq_sql.main_nlq_sql import nlq_pipeline

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
