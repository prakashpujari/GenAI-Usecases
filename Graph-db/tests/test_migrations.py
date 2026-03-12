from __future__ import annotations

from pathlib import Path

from app.etl import migrate_schema
from app.etl.migrate_schema import MigrationRunner


class FakeNeo4jClient:
    def __init__(self) -> None:
        self.applied_versions: set[str] = set()
        self.write_calls: list[str] = []

    def run_write(self, query: str, parameters: dict | None = None):
        self.write_calls.append(query.strip())
        if "MERGE (m:SchemaMigration" in query and parameters:
            self.applied_versions.add(parameters["version"])
        return []

    def run_read(self, query: str, parameters: dict | None = None):
        if "MATCH (m:SchemaMigration)" in query:
            return [{"version": v} for v in sorted(self.applied_versions)]
        return []


def test_migration_runner_applies_once(tmp_path: Path, monkeypatch) -> None:
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir(parents=True)
    (migrations_dir / "001__first.cypher").write_text("CREATE (:X);", encoding="utf-8")
    (migrations_dir / "002__second.cypher").write_text("CREATE (:Y);", encoding="utf-8")

    monkeypatch.setattr(migrate_schema, "MIGRATIONS_DIR", migrations_dir)

    client = FakeNeo4jClient()
    runner = MigrationRunner(client)

    first_run = runner.apply_pending()
    second_run = runner.apply_pending()

    assert first_run == ["001__first.cypher", "002__second.cypher"]
    assert second_run == []
    assert client.applied_versions == {"001", "002"}
