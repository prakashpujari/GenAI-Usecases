import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """Configure root logger with a structured, human-readable format."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
        force=True,  # override any prior basicConfig calls
    )
