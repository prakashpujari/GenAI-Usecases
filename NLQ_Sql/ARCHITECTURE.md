# Mortgage Insights NLQ Architecture

![Mortgage Insights NLQ Architecture](nlq_sql/Images/Mortgage+Insights+NLQ+Architecture.png)



- Users interact with the Streamlit UI by entering natural language queries (NLQ).
- The NLQ pipeline processes the query with schema awareness, calls the LLM (OpenAI), validates the generated SQL, and executes it on the database.
- If the main database or LLM fails, the system automatically falls back to SQLite or GPT-3.5-turbo.
- All results are validated and returned to the user with clear feedback.
