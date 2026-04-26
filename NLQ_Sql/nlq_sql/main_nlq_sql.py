"""
Production-grade NLQ → SQL pipeline for a Customer Data Platform (CDP) using LangChain.
Includes: schema awareness, guardrails, validation, execution pipeline, and extensibility.
"""

import re
from sqlalchemy import create_engine, inspect, text
import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

logging.basicConfig(filename='llm_calls.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# 1. Schema Awareness
def get_schema_metadata(engine):
    inspector = inspect(engine)
    schema = {}
    for table in inspector.get_table_names():
        columns = inspector.get_columns(table)
        schema[table] = [col['name'] for col in columns]
    return schema

def schema_to_prompt(schema):
    lines = []
    for table, cols in schema.items():
        lines.append(f"Table: {table} (columns: {', '.join(cols)})")
    return "\n".join(lines)

# 2. Guardrails & Validation
def validate_sql(sql, schema):
    sql_lower = sql.strip().lower()
    if not sql_lower.startswith("select"):
        raise ValueError("Only SELECT statements are allowed.")
    if ";" in sql:
        raise ValueError("Multiple statements not allowed.")
    if re.search(r"\\b(drop|delete|update|insert|alter)\\b", sql, re.I):
        raise ValueError("Dangerous SQL keyword detected.")
    # Optionally: check table/column names against schema
    # ...add more checks as needed...
    return True

# 3. NLQ → SQL Pipeline
def nlq_to_sql(nlq, schema, llm):
    schema_prompt = schema_to_prompt(schema)
    prompt = ChatPromptTemplate.from_template(
        """
You are an expert SQL generator for a Mortgage Application Data Platform (PostgreSQL).
Given the following schema:
{schema}

Translate the user's question into a safe, syntactically correct SQL SELECT query for a mortgage application use case.
User question: {question}
SQL:"""
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    logging.info(f"LLM INPUT | NLQ: {nlq}\nSCHEMA: {schema_prompt}")
    sql_output = chain.run({"schema": schema_prompt, "question": nlq})
    logging.info(f"LLM OUTPUT | SQL: {sql_output}")
    # Extract only the first valid SELECT statement (with or without semicolon)
    select_pattern = re.compile(r"(SELECT[\s\S]+?)(;|$)", re.IGNORECASE)
    match = select_pattern.search(sql_output)
    if match:
        sql = match.group(1).strip()
        if not sql.endswith(';'):
            sql += ';'
    else:
        # Fallback: take everything up to the first semicolon or the whole output
        sql = sql_output.split(';')[0].strip()
        if not sql.lower().startswith('select'):
            raise ValueError("No valid SELECT statement found in LLM output.")
        sql += ';'
    return sql.strip()

# 4. Execution
def execute_sql(engine, sql):
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        # Use .mappings() for SQLAlchemy 1.4+
        return [dict(row) for row in result.mappings()]

# 5. Main Pipeline
def nlq_pipeline(nlq, engine, llm):
    schema = get_schema_metadata(engine)
    sql = nlq_to_sql(nlq, schema, llm)
    # Remove trailing semicolon for validation to avoid false positive
    sql_for_validation = sql.rstrip().rstrip(';')
    try:
        validate_sql(sql_for_validation, schema)
    except Exception as e:
        return {"sql": sql, "results": f"Validation error: {e}"}
    # Only execute if it is a SELECT statement
    if not sql_for_validation.lower().startswith("select"):
        return {"sql": sql, "results": "Only SELECT (retrieve) operations are supported. No other SQL statements will be executed."}
    try:
        results = execute_sql(engine, sql)
    except Exception as e:
        return {"sql": sql, "results": f"SQL execution error: {e}"}
    return {"sql": sql, "results": results}

# --- Usage Example ---
if __name__ == "__main__":
    # Use provided JDBC connection details
    engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/postgres")

    # Create tables if they do not exist
    with engine.connect() as conn:
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS applicants (
            applicant_id SERIAL PRIMARY KEY,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            date_of_birth DATE,
            ssn VARCHAR(11) UNIQUE,
            email VARCHAR(255),
            phone VARCHAR(20)
        );
        CREATE TABLE IF NOT EXISTS properties (
            property_id SERIAL PRIMARY KEY,
            address VARCHAR(255),
            city VARCHAR(100),
            state VARCHAR(50),
            zip_code VARCHAR(10),
            value NUMERIC(15,2)
        );
        CREATE TABLE IF NOT EXISTS mortgage_applications (
            application_id SERIAL PRIMARY KEY,
            applicant_id INTEGER REFERENCES applicants(applicant_id),
            property_id INTEGER REFERENCES properties(property_id),
            application_date DATE,
            status VARCHAR(50),
            loan_amount NUMERIC(15,2),
            interest_rate NUMERIC(5,2),
            term_months INTEGER,
            approval_date DATE
        );
        '''))

    llm = ChatOpenAI(model="gpt-4", temperature=0)
    nlq = "Show me all mortgage applications approved in the last 30 days"
    output = nlq_pipeline(nlq, engine, llm)
    print("Generated SQL:", output["sql"])
    print("Results:", output["results"])
