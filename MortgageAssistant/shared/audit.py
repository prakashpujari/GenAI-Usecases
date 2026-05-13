from __future__ import annotations

import logging
from datetime import datetime


logger = logging.getLogger("audit")


def audit_log(event: str, details: dict) -> None:
    logger.info(
        "audit_event",
        extra={
            "event": event,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
