import pandas as pd

from app.etl.transforms import prepare_borrowers, prepare_loans


def test_prepare_borrowers_dedupes_and_normalizes() -> None:
    df = pd.DataFrame(
        [
            {"borrowerId": " b001 ", "name": "Jane"},
            {"borrowerId": "B001", "name": "Jane Updated"},
        ]
    )
    result = prepare_borrowers(df)
    assert len(result) == 1
    assert result.iloc[0]["borrowerId"] == "B001"
    assert result.iloc[0]["name"] == "Jane Updated"


def test_prepare_loans_casts_metrics() -> None:
    df = pd.DataFrame(
        [
            {
                "loanId": " l001 ",
                "borrowerId": " b001 ",
                "propertyId": " p001 ",
                "ltv": "80",
                "dti": "41.5",
            }
        ]
    )
    result = prepare_loans(df)
    assert result.iloc[0]["loanId"] == "L001"
    assert result.iloc[0]["borrowerId"] == "B001"
    assert float(result.iloc[0]["ltv"]) == 80.0
    assert float(result.iloc[0]["dti"]) == 41.5
