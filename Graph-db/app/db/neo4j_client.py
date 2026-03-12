from __future__ import annotations

from typing import Any

from neo4j import GraphDatabase
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config.settings import Settings


class Neo4jClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
            connection_timeout=3,
        )

    def close(self) -> None:
        self._driver.close()

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    def run_write(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        with self._driver.session(database=self._settings.neo4j_database) as session:
            result = session.execute_write(lambda tx: list(tx.run(query, parameters or {}).data()))
            return result

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    def run_read(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        with self._driver.session(database=self._settings.neo4j_database) as session:
            result = session.execute_read(lambda tx: list(tx.run(query, parameters or {}).data()))
            return result

    def verify_connectivity(self) -> None:
        self._driver.verify_connectivity()
