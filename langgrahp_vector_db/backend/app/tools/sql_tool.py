import logging
from typing import Tuple

import psycopg2
from langchain_community.tools import QuerySQLDatabaseTool
from langchain_community.utilities import SQLDatabase

logger = logging.getLogger(__name__)

SAMPLE_EMPLOYEES = [
    ("Alice", "Software Engineer"),
    ("Bob",   "Data Engineer"),
    ("Carol", "AI Engineer"),
]


def setup_postgres(dsn: str) -> None:
    """Idempotently create and seed the employees table."""
    logger.info("Setting up PostgreSQL schema ...")
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id   SERIAL PRIMARY KEY,
            name VARCHAR(100),
            role VARCHAR(100)
        );
    """)
    cur.execute("TRUNCATE TABLE employees RESTART IDENTITY;")
    cur.executemany(
        "INSERT INTO employees (name, role) VALUES (%s, %s);",
        SAMPLE_EMPLOYEES,
    )

    conn.commit()
    cur.close()
    conn.close()
    logger.info("PostgreSQL schema ready (%d rows inserted).", len(SAMPLE_EMPLOYEES))


def build_sql_tool(dsn: str) -> Tuple[SQLDatabase, QuerySQLDatabaseTool]:
    """Return a (SQLDatabase, QuerySQLDatabaseTool) pair for the given DSN."""
    db = SQLDatabase.from_uri(dsn)
    tool = QuerySQLDatabaseTool(db=db)
    logger.info("SQL tool connected to database.")
    return db, tool
