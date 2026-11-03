# Personal Finance Analyzer 💰
A Python-based Personal Finance Analytics Dashboard built with Streamlit to track income, expenses, savings, and budgets. Features interactive data visualizations, spending pattern analysis, budget monitoring, monthly expense forecasting with historical evaluation, and CSV/PDF report generation for data-driven financial management.

## Features
- Upload bank statements as **CSV, XLSX, or XLS**
- Summary metrics: income, expenses, net savings, and savings rate
- Monthly income-versus-expense chart
- Monthly expense trends and expense grouping by description
- Simple next-month expense estimate when enough monthly history exists
- Monthly budget comparison
- Cleaned transaction table and CSV download
- Reusable data-cleaning, categorization, summary, and chart functions in `kanchan.py`

## Built with
Python · Streamlit · Pandas · NumPy · Matplotlib · scikit-learn

## Run locally

1. Clone the repository:
   ```bash
   git clone https://github.com/Ksharma-09/personal-finance-analyzer.git
   cd personal-finance-analyzer
   ```

2. (Recommended) Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
   Activate on Windows:
   ```bash
   .venv\Scripts\activate
   ```
   Activate on macOS/Linux:
   ```bash
   source .venv/bin/activate
   ```

3. Install packages:
   ```bash
   pip install streamlit pandas numpy matplotlib scikit-learn openpyxl xlrd
   ```

4. Launch:
   ```bash
   streamlit run kanchan2.py
   ```

## Input file format

Your statement should contain these columns (case-insensitive; common alternate names are supported):

| Column | Required? | Description |
|---|---|---|
| Date | Yes | Transaction date |
| Debit | Yes | Expense/withdrawal; use 0 when absent |
| Credit | Yes | Income/deposit; use 0 when absent |
| Description | No | Transaction narration used for grouping |

## Repository files
- `kanchan2.py` — Streamlit dashboard
- `kanchan.py` — reusable transaction cleaning, summaries, categories, and chart helpers
- `student.csv` — sample data, if included

## Limitations & privacy
- Expense categories use simple keyword rules; some transactions may be labeled “other.”
- The prediction is a basic trend estimate and can be unreliable with limited history. It is not financial advice.
- Budget status is calculated for the latest month in the uploaded data.
- Email alerts are currently disabled. **Never commit passwords, app passwords, API keys, or real bank statements to GitHub.** Use anonymized sample data for demos.

## Possible future improvements
- Date filters and custom categories
- Recurring expense detection
- Forecast evaluation and richer insights
- Automated tests and deployment
