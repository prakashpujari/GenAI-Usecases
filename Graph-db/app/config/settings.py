from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Mortgage Graph Platform"
    env: str = "dev"
    log_level: str = "INFO"
    timezone: str = "UTC"

    neo4j_uri: str = "neo4j+s://5e8389cd.databases.neo4j.io"
    neo4j_user: str = "5e8389cd"
    neo4j_password: str = "X5jQWpBNYLpnRtZEI13ntnWnpKCz1vkOOecIyWiGVwc"
    neo4j_database: str = "5e8389cd"

    storage_backend: Literal["neo4j", "postgres"] = "neo4j"
    postgres_dsn: str = "postgresql://localhost:5432/postgres"

    data_path: str = "./data/sample"
    export_path: str = "./exports"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def normalize_postgres_dsn(value: str) -> str:
    """Accept both JDBC and standard PostgreSQL DSN formats."""
    if value.startswith("jdbc:"):
        return value.removeprefix("jdbc:")
    return value
