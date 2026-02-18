from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from pypdf import PdfReader


@dataclass(frozen=True)
class DocumentText:
    path: Path
    text: str


FIELD_PATTERNS: dict[str, re.Pattern] = {
    "employee_name": re.compile(r"\bEmployee(?:\s+Name)?\s*[:\-]\s*(.+)", re.IGNORECASE),
    "employer_name": re.compile(r"\bEmployer(?:\s+Name)?\s*[:\-]\s*(.+)", re.IGNORECASE),
    "pay_period": re.compile(r"\bPay\s*Period\s*[:\-]\s*(.+)", re.IGNORECASE),
    "pay_date": re.compile(r"\bPay\s*Date\s*[:\-]\s*(.+)", re.IGNORECASE),
    "gross_pay": re.compile(r"\bGross\s*Pay\s*[:\-]\s*\$?([0-9,]+\.?\d{0,2})", re.IGNORECASE),
    "net_pay": re.compile(r"\bNet\s*Pay\s*[:\-]\s*\$?([0-9,]+\.?\d{0,2})", re.IGNORECASE),
    "ytd_gross": re.compile(r"\bYTD\s*Gross\s*[:\-]\s*\$?([0-9,]+\.?\d{0,2})", re.IGNORECASE),
    "hourly_rate": re.compile(r"\bHourly\s*Rate\s*[:\-]\s*\$?([0-9,]+\.?\d{0,2})", re.IGNORECASE),
    "w2_box1_wages": re.compile(r"\bWages,\s*tips,\s*other\s*compensation\s*\$?([0-9,]+\.?\d{0,2})", re.IGNORECASE),
    "w2_box2_federal_withheld": re.compile(r"\bFederal\s*income\s*tax\s*withheld\s*\$?([0-9,]+\.?\d{0,2})", re.IGNORECASE),
    "w2_box3_social_security_wages": re.compile(r"\bSocial\s*security\s*wages\s*\$?([0-9,]+\.?\d{0,2})", re.IGNORECASE),
    "w2_box5_medicare_wages": re.compile(r"\bMedicare\s*wages\s*and\s*tips\s*\$?([0-9,]+\.?\d{0,2})", re.IGNORECASE),
}


def extract_text_from_pdf(path: Path) -> DocumentText:
    reader = PdfReader(str(path))
    pages_text: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text:
            pages_text.append(text)
    return DocumentText(path=path, text="\n".join(pages_text))


def extract_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for key, pattern in FIELD_PATTERNS.items():
        match = pattern.search(text)
        if match:
            fields[key] = match.group(1).strip()
    return fields
