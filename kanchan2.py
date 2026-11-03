"""Personal Finance Analyzer — interactive Streamlit application."""
from pathlib import Path
import io
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from kanchan import clean_transactions, categorize
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage

st.set_page_config(page_title="Personal Finance Analyzer", page_icon="💰", layout="wide")
st.title("💰 Personal Finance Analyzer")
st.caption("Understand your income, expenses, savings, and monthly spending patterns.")

@st.cache_data
def load_default_data():
    path = Path(__file__).resolve().parent / "student.csv"
    if not path.exists():
        raise FileNotFoundError("student.csv was not found. Upload a CSV or Excel bank statement.")
    return pd.read_csv(path)

def normalize_columns(data):
    """Compatibility wrapper: use the shared cleaning pipeline in kanchan.py."""
    return clean_transactions(data)


def classify(description):
    """Map shared category labels to dashboard display labels."""
    labels = {
        "shopping": "Shopping",
        "food": "Food",
        "travel": "Travel",
        "bills": "Bills",
        "other": "Other",
    }
    return labels.get(categorize(description), "Other")

uploaded = st.file_uploader("Upload bank statement", type=["csv", "xlsx", "xls"])
df = None
try:
    if uploaded is not None:
        raw = pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
    else:
        raw = load_default_data()
    df = normalize_columns(raw)
except Exception as exc:
    st.error(f"Unable to load data: {exc}")
    st.stop()

if df is None:
    st.error("Data could not be initialized. Please upload a valid CSV or Excel file.")
    st.stop()
if df.empty:
    st.warning("The file has no valid dated transactions.")
    st.stop()

df["category"] = df["description"].apply(classify)
min_date, max_date = df["date"].min().date(), df["date"].max().date()
with st.sidebar:
    st.header("Filters")
    date_range = st.date_input("Transaction date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    categories = sorted(df["category"].unique())
    selected_categories = st.multiselect("Expense categories", categories, default=categories)
    st.caption("Filters apply to the dashboard and exported data.")

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    if start_date > end_date:
        st.warning("Start date must be on or before end date.")
        st.stop()
    filtered = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)]
elif isinstance(date_range, (tuple, list)) and len(date_range) == 1:
    selected_date = date_range[0]
    filtered = df[df["date"].dt.date == selected_date]
elif hasattr(date_range, "year") and hasattr(date_range, "month") and hasattr(date_range, "day"):
    filtered = df[df["date"].dt.date == date_range]
else:
    filtered = df.copy()
# Category selection should filter expenses, not remove income transactions.
filtered = filtered[(filtered["credit"] > 0) | (filtered["category"].isin(selected_categories))]
if filtered.empty:
    st.warning("No transactions match these filters. Adjust the date range or categories.")
    st.stop()

income = float(filtered["credit"].sum())
expense = float(filtered["debit"].sum())
net_savings = income - expense
savings_rate = net_savings / income * 100 if income > 0 else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Income", f"₹{income:,.2f}")
m2.metric("Total Expenses", f"₹{expense:,.2f}")
m3.metric("Net Savings", f"₹{net_savings:,.2f}")
m4.metric("Savings Rate", f"{savings_rate:.1f}%")

st.divider()
monthly = filtered.groupby("month")[["credit", "debit"]].sum().sort_index()
monthly["savings"] = monthly["credit"] - monthly["debit"]
left, right = st.columns([1, 2])
with left:
    budget = st.number_input("Monthly expense budget (₹)", min_value=0.0, value=0.0, step=500.0)
    if budget > 0:
        st.subheader("Monthly budget status")
        status = monthly["debit"].to_frame("Expenses")
        status["Budget"] = budget
        status["Remaining"] = budget - status["Expenses"]
        st.dataframe(status.style.format("₹{:,.2f}"), use_container_width=True)
        over = status[status["Expenses"] > budget]
        if not over.empty:
            st.warning(f"Budget exceeded in {len(over)} month(s) in the selected period.")
        else:
            st.success("All months in the selected period are within budget.")
    if income <= 0:
        st.info("Income is zero in this selection; savings rate cannot be interpreted.")
    elif net_savings < 0:
        st.warning("Expenses exceed income for the selected period.")
    elif savings_rate >= 20:
        st.success("Good savings rate in this selected period.")
    else:
        st.info("Review discretionary spending to potentially increase savings.")
with right:
    st.subheader("Monthly Income vs Expenses")
    fig, ax = plt.subplots(figsize=(9, 3.8), facecolor="#0e1117")
    ax.set_facecolor("#0e1117")
    monthly[["credit", "debit"]].rename(columns={"credit": "Income", "debit": "Expenses"}).plot(
        kind="bar", ax=ax, width=0.78, color=["#48A9E6", "#F39C4A"]
    )
    ax.set_xlabel("Month", color="#d6d6d6")
    ax.set_ylabel("Amount (₹)", color="#d6d6d6")
    ax.tick_params(axis="x", rotation=35, labelsize=8, colors="#d6d6d6")
    ax.tick_params(axis="y", colors="#d6d6d6")
    ax.grid(axis="y", alpha=0.2)
    ax.legend(loc="upper right", facecolor="#20242c", labelcolor="#f2f2f2")
    for spine in ax.spines.values():
        spine.set_color("#444a55")
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

c1, c2 = st.columns([1, 1])
with c1:
    st.subheader("Monthly Expenses")
    fig, ax = plt.subplots(figsize=(7, 3.6), facecolor="#0e1117")
    ax.set_facecolor("#0e1117")
    monthly["debit"].plot(kind="bar", ax=ax, color="#69BDF8", width=0.72)
    ax.set_xlabel("Month", color="#d6d6d6")
    ax.set_ylabel("Expenses (₹)", color="#d6d6d6")
    ax.tick_params(axis="x", rotation=35, labelsize=8, colors="#d6d6d6")
    ax.tick_params(axis="y", colors="#d6d6d6")
    ax.grid(axis="y", alpha=0.2)
    for spine in ax.spines.values():
        spine.set_color("#444a55")
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
with c2:
    st.subheader("Expenses by Category")
    category_totals = filtered.groupby("category")["debit"].sum().sort_values(ascending=False)
    category_totals = category_totals[category_totals > 0]
    if not category_totals.empty:
        fig, ax = plt.subplots(figsize=(6, 3.6), facecolor="#0e1117")
        ax.set_facecolor("#0e1117")
        wedges, _, autotexts = ax.pie(
            category_totals, labels=None, autopct="%1.1f%%", startangle=90,
            pctdistance=0.68, textprops={"fontsize": 9, "color": "#ffffff"},
            wedgeprops={"edgecolor": "#0e1117", "linewidth": 1.2}
        )
        ax.legend(wedges, category_totals.index, title="Category",
                 loc="center left", bbox_to_anchor=(1, 0.02, 0.4, 0.96),
                 fontsize=8, title_fontsize=9, facecolor="#20242c", labelcolor="#f2f2f2")
        ax.set_title("Expense distribution", color="#f2f2f2", fontsize=11)
        ax.axis("equal")
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    else:
        st.info("No expenses in the selected period.")

st.subheader("Next-Month Expense Estimate")
monthly_series = filtered.set_index("date").resample("MS")["debit"].sum()
if len(monthly_series) >= 3:
    recent = monthly_series.tail(6)
    positive_months = recent[recent > 0]
    if not positive_months.empty:
        estimate = float(positive_months.median())
        next_period = monthly_series.index[-1] + pd.offsets.MonthBegin(1)
        st.metric(f"Estimated expenses for {next_period.strftime('%B %Y')}", f"₹{estimate:,.2f}")
        st.caption("Estimate uses the median of recent non-zero expense months; irregular spending may make it inaccurate. Not financial advice.")
    else:
        st.info("No positive expenses in the latest 6 calendar months to estimate from")
else:
    st.info("At least 3 calendar months of transactions are needed for this baseline estimate.")

with st.expander("View filtered transactions"):
    st.dataframe(filtered.drop(columns=["month"]), use_container_width=True)

csv_bytes = filtered.drop(columns=["month"]).to_csv(index=False).encode("utf-8")
st.download_button("Download filtered transactions (CSV)", csv_bytes, "filtered_transactions.csv", "text/csv")

def make_pdf_report(summary, monthly_table, figures):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Personal Finance Analyzer — Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Total income: ₹{summary['income']:,.2f}", styles["BodyText"]),
        Paragraph(f"Total expenses: ₹{summary['expense']:,.2f}", styles["BodyText"]),
        Paragraph(f"Net savings: ₹{summary['savings']:,.2f}", styles["BodyText"]),
        Paragraph(f"Savings rate: {summary['rate']:.1f}%", styles["BodyText"]),
        Spacer(1, 12),
        Paragraph("Monthly summary", styles["Heading2"]),
    ]
    table_data = [["Month", "Income (₹)", "Expenses (₹)", "Savings (₹)"]]
    for idx, row in monthly_table.iterrows():
        table_data.append([str(idx), f"{row['credit']:,.2f}", f"{row['debit']:,.2f}", f"{row['savings']:,.2f}"])
    from reportlab.platypus import Table, TableStyle
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24476B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    for title, series in [("Monthly expenses", monthly_table["debit"]), ("Monthly savings", monthly_table["savings"])]:
        fig, ax = plt.subplots(figsize=(6, 2.8))
        series.plot(kind="bar", ax=ax, title=title)
        fig.tight_layout()
        image_buffer = io.BytesIO()
        fig.savefig(image_buffer, format="png", dpi=140)
        plt.close(fig)
        image_buffer.seek(0)
        story.extend([Spacer(1, 12), RLImage(image_buffer, width=440, height=205)])
    doc.build(story)
    buffer.seek(0)
    return buffer

pdf = make_pdf_report({"income": income, "expense": expense, "savings": net_savings, "rate": savings_rate}, monthly, {})
st.download_button("📄 Download PDF report", pdf, "personal_finance_report.pdf", "application/pdf")
