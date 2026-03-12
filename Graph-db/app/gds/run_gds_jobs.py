from __future__ import annotations

import logging

from app.config.logging import configure_logging
from app.config.settings import get_settings
from app.db.neo4j_client import Neo4jClient
from app.gds.jobs import GDSJobs


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    client = Neo4jClient(settings)
    try:
        client.verify_connectivity()
        GDSJobs(client).run_all()
        logger.info("GDS jobs completed")
    finally:
        client.close()


if __name__ == "__main__":
    main()
