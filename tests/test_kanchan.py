import pandas as pd
import pytest

from kanchan import clean_transactions, load_transactions, categorize, summarize


def sample_data():
    return pd.DataFrame({
        "Date": ["2025-01-01", "2025-01-02", "invalid"],
        "Debit": [100, 0, 20],
        "Credit": [0, 500, 0],
        "Description": ["Zomato food", "Salary", "bad date"],
    })


def test_clean_transactions_normalizes_columns_and_drops_invalid_dates():
    df = clean_transactions(sample_data())
    assert list(df["date"].dt.strftime("%Y-%m-%d")) == ["2025-01-01", "2025-01-02"]
    assert list(df["month"]) == ["2025-01", "2025-01"]
    assert df.loc[0, "description"] == "Zomato food"


def test_clean_transactions_missing_required_columns():
    with pytest.raises(ValueError, match="Missing required columns"):
        clean_transactions(pd.DataFrame({"date": ["2025-01-01"], "debit": [1]}))


def test_clean_transactions_fills_missing_description():
    df = pd.DataFrame({"date": ["2025-01-01"], "debit": [2], "credit": [0]})
    result = clean_transactions(df)
    assert result.loc[0, "description"] == "Uncategorized"


def test_categorize_keyword_rules():
    assert categorize("Amazon order") == "shopping"
    assert categorize("Swiggy dinner") == "food"
    assert categorize("Petrol pump") == "travel"
    assert categorize("Electricity bill") == "bills"
    assert categorize("miscellaneous") == "other"


def test_summarize_totals_and_monthly():
    result = summarize(sample_data())
    assert result["total_income"] == 500
    assert result["total_expenses"] == 100
    assert result["net_savings"] == 400
    assert len(result["monthly"]) == 1
    assert result["monthly"].iloc[0]["savings"] == 400
