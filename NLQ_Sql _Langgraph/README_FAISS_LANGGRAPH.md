# Enhanced README for FAISS RAG & LangGraph

## Vector DB (FAISS) & RAG
- Add your knowledge base `.txt` or `.md` files to a folder (e.g., `docs/`).
- Ingest them into FAISS vector DB:
  ```sh
  python -m nlq_sql.rag_ingest docs/ faiss_index
  ```
- This creates a FAISS index at `faiss_index` for retrieval-augmented generation (RAG).

## LangGraph Orchestration
- Enable the "FAISS RAG" option in the Streamlit sidebar to use LangGraph orchestration.
- The orchestrator will:
  - Use LLM to generate SQL
  - Optionally retrieve relevant docs from FAISS (RAG)
  - Query Postgres and/or return RAG results

## Production Notes
- FAISS index path is configurable in the UI.
- All LLM and DB calls are orchestrated via LangGraph for extensibility.
- Use `rag_ingest.py` to update your vector DB as needed.
