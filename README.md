# 💰 Personal Finance Analyzer

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/Tests-pytest-brightgreen)](https://pytest.org/)

A personal finance analytics dashboard built with Python and Streamlit. Upload a bank statement, explore income and spending patterns, review savings and budgets, and export cleaned data and reports.

## Features
- Import bank statements in CSV, XLSX, or XLS formats
- Summary metrics for income, expenses, net savings, and savings rate
- Monthly income-versus-expense and expense trend visualizations
- Expense grouping and category insights
- Monthly budget comparison
- Basic next-month expense baseline with historical MAE evaluation when enough monthly history is available
- Cleaned transaction table and CSV download
- PDF report generation

## Tech stack
Python · Streamlit · Pandas · NumPy · Matplotlib · scikit-learn · OpenPyXL · xlrd · pytest

## Run locally
Python 3.10 or 3.11 is recommended.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

python -m pip install -r requirements.txt
streamlit run kanchan2.py
```

## Input data
The uploaded statement should include:
- `Date`: transaction date
- `Debit`: expense/withdrawal amount (use 0 if absent)
- `Credit`: income/deposit amount (use 0 if absent)
- `Description` (optional): transaction narration for grouping

Common alternative column names are supported by the data-cleaning pipeline.

## Validation
GitHub Actions runs the pytest suite, compiles Python files, checks Streamlit import, and smoke-tests the included sample CSV.

## Limitations and privacy
- Categories are assigned using keyword-based rules; some records may fall into “Other.”
- Forecasts are simple baselines and may be unreliable with limited history; they are not financial advice.
- Budget status reflects the latest month in the uploaded data.
- Use anonymized sample statements for demos. **Never upload real bank statements, passwords, app passwords, or API keys to a public repository.**
