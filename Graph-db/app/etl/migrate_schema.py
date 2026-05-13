from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from app.config.logging import configure_logging
from app.config.settings import get_settings
from app.db.neo4j_client import Neo4jClient


@dataclass(frozen=True)
class Migration:
    version: str
    path: Path


MIGRATIONS_DIR = Path("cypher/migrations")


class MigrationRunner:
    def __init__(self, client: Neo4jClient) -> None:
        self.client = client

    def ensure_tracking(self) -> None:
        self.client.run_write(
            "CREATE CONSTRAINT schema_migration_version_unique IF NOT EXISTS FOR (m:SchemaMigration) REQUIRE m.version IS UNIQUE"
        )

    def get_applied_versions(self) -> set[str]:
        rows = self.client.run_read("MATCH (m:SchemaMigration) RETURN m.version AS version")
        return {row["version"] for row in rows}

    def discover(self) -> list[Migration]:
        migrations: list[Migration] = []
        for path in sorted(MIGRATIONS_DIR.glob("*.cypher")):
            version = path.stem.split("__", maxsplit=1)[0]
            migrations.append(Migration(version=version, path=path))
        return migrations

    def apply_pending(self) -> list[str]:
        self.ensure_tracking()
        applied = self.get_applied_versions()
        executed: list[str] = []

        for migration in self.discover():
            if migration.version in applied:
                continue

            statement = migration.path.read_text(encoding="utf-8").strip()
            if statement:
                # Migration files can contain multiple Cypher statements separated by semicolons.
                for part in [s.strip() for s in statement.split(";") if s.strip()]:
                    self.client.run_write(part)

            self.client.run_write(
                """
                MERGE (m:SchemaMigration {version: $version})
                SET m.file = $file,
                    m.appliedAt = datetime()
                """,
                {"version": migration.version, "file": migration.path.name},
            )
            executed.append(migration.path.name)

        return executed


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    client = Neo4jClient(settings)
    try:
        client.verify_connectivity()
        runner = MigrationRunner(client)
        executed = runner.apply_pending()
        logger.info("Applied migrations: %s", executed)
    finally:
        client.close()


if __name__ == "__main__":
    main()
