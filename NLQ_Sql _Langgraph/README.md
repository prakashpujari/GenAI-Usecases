---
# Mortgage Insights NLQ

![Mortgage Insights NLQ Architecture](nlq_sql/Images/Mortgage+Insights+NLQ+Architecture.png)

> **Production-grade Natural Language to SQL for Mortgage Data**

## Features
- Schema awareness (auto-detects DB schema)
- Guardrails (only safe SELECT queries allowed)
- Validation and error handling
- Execution pipeline with observability (logs all LLM calls)
- Extensible for enterprise use
- Modern Streamlit UI with configuration and fallback
- Fallback to SQLite and GPT-3.5-turbo if main DB/LLM fails

## Setup
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Set up your PostgreSQL database (or use SQLite fallback automatically).
3. Set your OpenAI API key as an environment variable:
   ```sh
   export OPENAI_API_KEY=sk-...
   ```

## Running the App
Launch the Streamlit UI:
```sh
streamlit run app.py
```
- Open [http://localhost:8501](http://localhost:8501) in your browser.
- Enter your DB connection string and LLM model in the sidebar (defaults provided).
- Ask questions like:
  - "How many mortgage applications are pending?"
  - "Show all approved applications in the last 30 days."

## Fallback Behavior
- If the main database is unavailable, the app will automatically use a local SQLite database.
- If the main LLM (e.g., GPT-4) fails, it will fallback to GPT-3.5-turbo.
- Fallback status is shown in the UI.

## Logging & Observability
- All LLM calls (inputs and outputs) are logged to `llm_calls.log` for traceability.
- Errors and validation issues are shown in the UI and logs.

## Extending
- Add more SQL validators in `validate_sql()`
- Enhance schema introspection for relationships, types, etc.
- Swap LLMs (OpenAI, Azure, etc.)
- Add logging, tracing, and error handling as needed
- Customize the Streamlit UI for your enterprise branding

---
