from __future__ import annotations

import pandas as pd


def normalize_id(value: str) -> str:
    return str(value).strip().upper()


def dedupe_by_key(df: pd.DataFrame, key: str) -> pd.DataFrame:
    if key not in df.columns:
        raise KeyError(f"Missing dedupe key: {key}")
    return df.drop_duplicates(subset=[key], keep="last").reset_index(drop=True)


def prepare_borrowers(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["borrowerId"] = data["borrowerId"].map(normalize_id)
    return dedupe_by_key(data, "borrowerId")


def prepare_loans(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["loanId"] = data["loanId"].map(normalize_id)
    data["borrowerId"] = data["borrowerId"].map(normalize_id)
    data["propertyId"] = data["propertyId"].map(normalize_id)
    data["ltv"] = pd.to_numeric(data["ltv"], errors="coerce").fillna(0.0)
    data["dti"] = pd.to_numeric(data["dti"], errors="coerce").fillna(0.0)
    return dedupe_by_key(data, "loanId")
