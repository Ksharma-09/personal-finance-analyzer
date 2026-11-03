"""Reusable data-cleaning and analysis helpers for Personal Finance Analyzer."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path("project")


def clean_transactions(data):
    """Validate and clean a DataFrame containing Date, Debit, Credit."""
    data = data.copy()
    data.columns = [str(c).strip().lower() for c in data.columns]
    aliases = {
        "date": ("date", "transaction date", "trans_date"),
        "description": ("description", "narration", "details", "transaction"),
        "debit": ("debit", "withdrawal", "expense", "expenses"),
        "credit": ("credit", "deposit", "income", "incomes"),
    }
    rename = {}
    for target, candidates in aliases.items():
        for candidate in candidates:
            if candidate in data.columns:
                rename[candidate] = target
                break
    data = data.rename(columns=rename)
    missing = {"date", "debit", "credit"} - set(data.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
    data["date"] = pd.to_datetime(data["date"], errors="coerce", dayfirst=True)
    data["debit"] = pd.to_numeric(data["debit"], errors="coerce").fillna(0)
    data["credit"] = pd.to_numeric(data["credit"], errors="coerce").fillna(0)
    data = data.dropna(subset=["date"])
    if "description" not in data:
        data["description"] = "Uncategorized"
    data["description"] = data["description"].fillna("Uncategorized").astype(str)
    data["month"] = data["date"].dt.to_period("M").astype(str)
    return data


def load_transactions(file_or_path):
    """Load CSV or Excel bank statement and clean it."""
    name = str(getattr(file_or_path, "name", file_or_path)).lower()
    if name.endswith(".csv"):
        data = pd.read_csv(file_or_path)
    elif name.endswith((".xlsx", ".xls")):
        data = pd.read_excel(file_or_path)
    else:
        raise ValueError("Supported file formats: CSV, XLSX, XLS")
    return clean_transactions(data)


def categorize(description):
    """Simple keyword-based category assignment."""
    text = str(description).lower()
    rules = {
        "shopping": ("amazon", "flipkart", "myntra"),
        "food": ("zomato", "swiggy", "restaurant", "food"),
        "travel": ("petrol", "fuel", "uber", "ola", "railway"),
        "bills": ("electricity", "recharge", "internet", "bill"),
    }
    for category, words in rules.items():
        if any(word in text for word in words):
            return category
    return "other"


def summarize(data):
    """Return cleaned transactions, totals, and monthly summary."""
    df = clean_transactions(data)
    income = float(df["credit"].sum())
    expenses = float(df["debit"].sum())
    monthly = df.groupby(df["date"].dt.to_period("M"))[["credit", "debit"]].sum()
    monthly["savings"] = monthly["credit"] - monthly["debit"]
    return {
        "transactions": df,
        "total_income": income,
        "total_expenses": expenses,
        "net_savings": income - expenses,
        "monthly": monthly,
    }


def create_charts(data):
    """Create figures without saving files or calling plt.show()."""
    df = clean_transactions(data)
    df["category"] = df["description"].apply(categorize)
    monthly = df.groupby(df["date"].dt.to_period("M"))[["credit", "debit"]].sum()

    figures = {}
    figures["monthly"] = plt.subplots(figsize=(8, 4))[0]
    ax = figures["monthly"].axes[0]
    monthly["debit"].plot(kind="bar", ax=ax, title="Monthly Expenses")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    figures["monthly"].tight_layout()

    figures["income_expense"], ax = plt.subplots(figsize=(8, 4))
    monthly[["credit", "debit"]].plot(kind="bar", ax=ax, title="Income vs Expenses")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    ax.legend(["Income", "Expenses"])
    figures["income_expense"].tight_layout()

    figures["savings"], ax = plt.subplots(figsize=(8, 4))
    (monthly["credit"] - monthly["debit"]).plot(kind="bar", ax=ax, title="Monthly Savings")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    figures["savings"].tight_layout()

    figures["category_expense"], ax = plt.subplots(figsize=(6, 6))
    category_totals = df.groupby("category")["debit"].sum()
    if category_totals.sum() > 0:
        ax.pie(category_totals, labels=category_totals.index, autopct="%1.1f%%")
        ax.set_title("Expenses by Category")
    else:
        ax.text(0.5, 0.5, "No expense data", ha="center", va="center")
        ax.axis("off")
    figures["category_expense"].tight_layout()
    return figures


if __name__ == "__main__":
    PROJECT_DIR.mkdir(exist_ok=True)
    sample = Path("student.csv")
    if not sample.exists():
        raise SystemExit("student.csv not found. Use load_transactions() with your own CSV/Excel file.")
    data = load_transactions(sample)
    result = summarize(data)
    print(f"Income: {result['total_income']:,.2f}")
    print(f"Expenses: {result['total_expenses']:,.2f}")
    print(f"Net savings: {result['net_savings']:,.2f}")
    for name, fig in create_charts(data).items():
        fig.savefig(PROJECT_DIR / f"{name}.png", dpi=150, bbox_inches="tight")
    print("Charts saved in project/")
