from __future__ import annotations

import logging

from app.config.logging import configure_logging
from app.config.settings import get_settings
from app.db.neo4j_client import Neo4jClient
from app.etl.loader import ETLLoader


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    client = Neo4jClient(settings)
    try:
        client.verify_connectivity()
        summary = ETLLoader(client, settings.data_path).run_full_load()
        logger.info("ETL completed: %s", summary)
    finally:
        client.close()


if __name__ == "__main__":
    main()
