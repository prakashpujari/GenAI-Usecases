import logging
import sys
from pythonjsonlogger import jsonlogger


def configure_logging(service_name: str) -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(service)s %(request_id)s"
    )
    handler.setFormatter(formatter)

    logger.handlers = [handler]
    logger = logging.getLogger(service_name)
    logger.info("logger_initialized", extra={"service": service_name, "request_id": "-"})
