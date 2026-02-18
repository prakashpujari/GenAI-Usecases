from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class PiiMatch:
    label: str
    value: str


_PII_PATTERNS: list[tuple[str, re.Pattern]] = [
    # SSN - Catches SSN patterns with separators OR with "SSN" label, including test SSNs like 999-99-9999
    # Matches: SSN: 999-99-9999, 123-45-6789, 123 45 6789, SSN 123456789, SSN: 123456789
    # For security, we redact even "invalid" SSNs since they might be test data or placeholders
    # Note: Plain 9-digit numbers without "SSN" label are caught by ROUTING pattern instead
    ("SSN", re.compile(r"(?:\bSSN[-:\s]+\d{9}\b|\b\d{3}[-\s]\d{2}[-\s]\d{4}\b)", re.IGNORECASE)),
    ("DOB", re.compile(r"\b(0[1-9]|1[0-2])[\/\-](0[1-9]|[12]\d|3[01])[\/\-](19\d{2}|20\d{2})\b")),
    ("PHONE", re.compile(r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")),
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("EIN", re.compile(r"\b\d{2}-\d{7}\b")),
    ("ROUTING", re.compile(r"\b\d{9}\b")),
    ("ACCOUNT", re.compile(r"\b\d{10,17}\b")),
    ("ADDRESS", re.compile(r"\b\d{1,6}\s+[A-Za-z0-9.\s]{2,}\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way|Wy)\b", re.IGNORECASE)),
]


def detect_pii(text: str) -> list[PiiMatch]:
    matches: list[PiiMatch] = []
    for label, pattern in _PII_PATTERNS:
        for match in pattern.finditer(text):
            matches.append(PiiMatch(label=label, value=match.group(0)))
    return matches


def contains_pii(text: str) -> bool:
    return any(pattern.search(text) for _, pattern in _PII_PATTERNS)


def redact_pii(text: str) -> str:
    redacted = text
    for label, pattern in _PII_PATTERNS:
        redacted = pattern.sub(f"[{label}_REDACTED]", redacted)
    return redacted


def redact_items(items: Iterable[str]) -> list[str]:
    return [redact_pii(item) for item in items]
