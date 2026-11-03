import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Personal Finance Analyzer", page_icon="💰", layout="wide")

st.title("💰 Personal Finance Analyzer")
st.caption("Track income, expenses, savings, and monthly spending patterns.")

@st.cache_data
def load_default_data():
    return pd.read_csv("student.csv")

def normalize_columns(data):
    data = data.copy()
    data.columns = [str(c).strip().lower() for c in data.columns]
    aliases = {
        "date": ["date", "transaction date", "trans_date"],
        "description": ["description", "narration", "details", "transaction"],
        "debit": ["debit", "withdrawal", "expense", "expenses"],
        "credit": ["credit", "deposit", "income", "incomes"],
    }
    rename = {}
    for target, options in aliases.items():
        for option in options:
            if option in data.columns:
                rename[option] = target
                break
    data = data.rename(columns=rename)
    required = ["date", "debit", "credit"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing) +
                         ". Please upload a CSV/Excel file containing Date, Debit, and Credit.")
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data["debit"] = pd.to_numeric(data["debit"], errors="coerce").fillna(0)
    data["credit"] = pd.to_numeric(data["credit"], errors="coerce").fillna(0)
    data = data.dropna(subset=["date"])
    if "description" not in data.columns:
        data["description"] = "Uncategorized"
    data["description"] = data["description"].fillna("Uncategorized").astype(str)
    data["month"] = data["date"].dt.to_period("M").astype(str)
    return data

uploaded = st.file_uploader("Upload bank statement (CSV or Excel)", type=["csv", "xlsx", "xls"])
try:
    if uploaded is not None:
        raw = pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
    else:
        raw = load_default_data()
    df = normalize_columns(raw)
except Exception as exc:
    st.error(f"Could not load data: {exc}")
    st.stop()

if df.empty:
    st.warning("No valid transactions found in the selected file.")
    st.stop()

total_income = float(df["credit"].sum())
total_expense = float(df["debit"].sum())
net_savings = total_income - total_expense
savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0.0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Income", f"₹{total_income:,.2f}")
c2.metric("Total Expenses", f"₹{total_expense:,.2f}")
c3.metric("Net Savings", f"₹{net_savings:,.2f}")
c4.metric("Savings Rate", f"{savings_rate:.1f}%")

st.divider()
left, right = st.columns([1, 2])
with left:
    budget = st.number_input("Monthly expense budget (₹)", min_value=0.0, value=0.0, step=500.0)
    if budget > 0:
        month_expenses = df.groupby("month")["debit"].sum()
        latest_month = month_expenses.index.max()
        latest_expense = float(month_expenses.loc[latest_month])
        if latest_expense > budget:
            st.error(f"Budget exceeded for {latest_month}: ₹{latest_expense:,.2f} / ₹{budget:,.2f}")
        else:
            st.success(f"{latest_month} expenses are within budget: ₹{latest_expense:,.2f} / ₹{budget:,.2f}")
    if total_income == 0:
        st.info("Add credit/income transactions to calculate a savings rate.")
    elif savings_rate >= 20:
        st.success("Good savings progress. Keep tracking consistently!")
    elif net_savings >= 0:
        st.info("Consider reviewing recurring and discretionary expenses to grow savings.")
    else:
        st.warning("Expenses exceed income in the selected data. Review spending categories.")
with right:
    monthly = df.groupby("month")[["credit", "debit"]].sum().sort_index()
    st.subheader("Monthly Income vs Expenses")
    st.line_chart(monthly.rename(columns={"credit": "Income", "debit": "Expenses"}))

chart1, chart2 = st.columns(2)
with chart1:
    st.subheader("Expense by Month")
    monthly_expense = df.groupby("month")["debit"].sum().sort_index()
    st.bar_chart(monthly_expense)
with chart2:
    st.subheader("Expenses by Description")
    category_expense = df.groupby("description")["debit"].sum().sort_values(ascending=False).head(10)
    if category_expense.sum() > 0:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.pie(category_expense, labels=category_expense.index, autopct="%1.1f%%")
        ax.set_ylabel("")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    else:
        st.info("No debit transactions available for category analysis.")

st.subheader("Next-Month Expense Estimate")
monthly_numeric = df.groupby(df["date"].dt.to_period("M").dt.month)["debit"].sum().sort_index()
if len(monthly_numeric) >= 2:
    X = monthly_numeric.index.to_numpy().reshape(-1, 1)
    y = monthly_numeric.values
    model = LinearRegression().fit(X, y)
    next_month = int(monthly_numeric.index.max() % 12 + 1)
    estimate = max(0.0, float(model.predict(np.array([[next_month]]))[0]))
    st.metric("Estimated expense (simple linear trend)", f"₹{estimate:,.2f}")
    st.caption("This is a basic historical trend estimate, not financial advice. Results may be unreliable with few months of data.")
else:
    st.info("At least two distinct months of transactions are needed for a simple estimate.")

with st.expander("View cleaned transactions"):
    st.dataframe(df.drop(columns=["month"]), use_container_width=True)

csv_data = df.drop(columns=["month"]).to_csv(index=False).encode("utf-8")
st.download_button("Download cleaned transactions (CSV)", csv_data, "cleaned_transactions.csv", "text/csv")
