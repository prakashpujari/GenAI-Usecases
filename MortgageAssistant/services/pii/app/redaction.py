from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from shared.aws_clients import comprehend_client
from shared.models import PiiEntity, PiiType


@dataclass
class Detection:
    type: PiiType
    text: str
    start: int
    end: int
    confidence: float


SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
DOB_REGEX = re.compile(r"\b(\d{2}/\d{2}/\d{4})\b")
ACCOUNT_REGEX = re.compile(r"\b\d{8,12}\b")
ADDRESS_REGEX = re.compile(r"\b\d+\s+\w+\s+(Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Boulevard|Blvd)\b", re.IGNORECASE)


def detect_pii(text: str) -> List[PiiEntity]:
    entities: List[PiiEntity] = []

    response = comprehend_client().detect_pii_entities(Text=text, LanguageCode="en")
    for entity in response.get("Entities", []):
        ent_type = PiiType.other
        if entity.get("Type") == "SSN":
            ent_type = PiiType.ssn
        elif entity.get("Type") == "DATE_TIME":
            ent_type = PiiType.dob
        elif entity.get("Type") == "BANK_ACCOUNT_NUMBER":
            ent_type = PiiType.account_number
        elif entity.get("Type") == "ADDRESS":
            ent_type = PiiType.address

        entities.append(
            PiiEntity(
                type=ent_type,
                text=text[entity["BeginOffset"] : entity["EndOffset"]],
                start=entity["BeginOffset"],
                end=entity["EndOffset"],
                confidence=entity.get("Score", 0.0),
            )
        )

    for match in SSN_REGEX.finditer(text):
        entities.append(
            PiiEntity(type=PiiType.ssn, text=match.group(0), start=match.start(), end=match.end(), confidence=0.95)
        )
    for match in DOB_REGEX.finditer(text):
        entities.append(
            PiiEntity(type=PiiType.dob, text=match.group(0), start=match.start(), end=match.end(), confidence=0.9)
        )
    for match in ACCOUNT_REGEX.finditer(text):
        entities.append(
            PiiEntity(
                type=PiiType.account_number,
                text=match.group(0),
                start=match.start(),
                end=match.end(),
                confidence=0.8,
            )
        )
    for match in ADDRESS_REGEX.finditer(text):
        entities.append(
            PiiEntity(
                type=PiiType.address,
                text=match.group(0),
                start=match.start(),
                end=match.end(),
                confidence=0.85,
            )
        )

    entities.sort(key=lambda e: (e.start, e.end))
    return _dedupe_overlaps(entities)


def _dedupe_overlaps(entities: List[PiiEntity]) -> List[PiiEntity]:
    deduped: List[PiiEntity] = []
    last_end = -1
    for entity in entities:
        if entity.start >= last_end:
            deduped.append(entity)
            last_end = entity.end
    return deduped


def apply_redaction(text: str, entities: List[PiiEntity], token_map: dict, role: str) -> str:
    redacted = []
    cursor = 0

    for entity in entities:
        redacted.append(text[cursor : entity.start])
        token = token_map.get(entity.text)
        if role == "internal":
            redacted.append(f"[PII:{entity.type.value}:{token}]")
        else:
            redacted.append("[REDACTED]")
        cursor = entity.end

    redacted.append(text[cursor:])
    return "".join(redacted)
