from __future__ import annotations

from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.config.settings import Settings, normalize_postgres_dsn


class PostgresClient:
    def __init__(self, settings: Settings) -> None:
        self._dsn = normalize_postgres_dsn(settings.postgres_dsn)

    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(self._dsn, row_factory=dict_row)

    def ensure_schema(self) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS loan_ingest_events (
                        loan_id TEXT PRIMARY KEY,
                        payload JSONB NOT NULL,
                        violations JSONB NOT NULL DEFAULT '[]'::jsonb,
                        status TEXT NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                    )
                    """
                )
            conn.commit()

    def upsert_ingest_event(self, loan_id: str, payload: dict[str, Any], violations: list[dict[str, Any]]) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO loan_ingest_events (loan_id, payload, violations, status)
                    VALUES (%s, %s::jsonb, %s::jsonb, %s)
                    ON CONFLICT (loan_id)
                    DO UPDATE SET
                        payload = EXCLUDED.payload,
                        violations = EXCLUDED.violations,
                        status = EXCLUDED.status,
                        updated_at = now()
                    """,
                    (loan_id, Jsonb(payload), Jsonb(violations), "ingested"),
                )
            conn.commit()
