import pandas as pd
import matplotlib.pyplot as plt
import os
os.makedirs("project",exist_ok=True)
df=pd.read_csv("student.csv")
print(df)
df.fillna(0,inplace=True)
df["Date"]=pd.to_datetime(df["Date"])
print(df.head())
def categorize(desc):
    desc=desc.lower()
    if "amazon" in desc:
        return"shopping"
    elif "zomato" in desc:
        return"food"
    elif "petrol" in desc:
        return"travel"
    else:
        return"other" 
df["categorize"]=df["description"].apply(categorize)
monthly=df.groupby(df["Date"].dt.month)["debit"].sum()
plt.figure(figsize=(6,3))
monthly.plot(kind="bar")
plt.title("monthly Expenses")
plt.tight_layout()
plt.savefig("project/monthly_expense.png")
plt.show()
income=df.groupby(df["Date"].dt.month)["credit"].sum()
expens=df.groupby(df["Date"].dt.month)["debit"].sum()
months=income.index
plt.figure(figsize=(6,3))
plt.bar(months,income,alpha=0.5)
plt.bar(months,expens,alpha=0.5)
plt.title("income vs expense")
plt.xlabel("month")
plt.ylabel("Amount")
plt.legend()
plt.tight_layout()
plt.savefig("project/ income vs expense.png")
plt.show()
savings=income-expens
plt.figure(figsize=(4,4))
plt.bar(savings.index,savings)
plt.title("monthly savings")
plt.xlabel("month")
plt.ylabel("savings")
plt.tight_layout()
plt.savefig("project/monthly_saving.png")
plt.show()


Category_expens=df.groupby("categorize")["debit"].sum()
df.groupby("categorize")["debit"].sum()
fig_category_expens=plt.figure(figsize=(4,4))
plt.pie(Category_expens,labels=Category_expens.index,autopct="%1.1f%%")
plt.title("expense by category")
plt.tight_layout()
plt.savefig("project/expens_category.png")
plt.show()
total_income = df["credit"].sum()
total_expens = df["debit"].sum()
savings=total_income-total_expens
print("INCOME",total_income)
print("TOTAL EXPENSE",total_expens)
print("SAVING",savings)
fig_monthly=plt.figure(figsize=(4,4))
plt.bar(monthly.index,monthly.values)
plt.title("monthly expense")
fig_income_expense=plt.figure()
plt.bar(months,income,alpha=0.5)
plt.bar(months,expens,alpha=0.5)
plt.title("income vs expense")
plt.legend(["income","expense"])

monthly_income=df.groupby(df["Date"].dt.month)["credit"].sum()
monthly_expens=df.groupby(df["Date"].dt.month)["debit"].sum()
monthly_savings=monthly_income-monthly_expens
fig_saving=plt.figure()
plt.bar(monthly_savings.index,monthly_savings.values)
plt.title("monthly saving")


from reportlab.platypus import SimpleDocTemplate,Paragraph,Image
from reportlab.lib.styles import getSampleStyleSheet
doc=SimpleDocTemplate("project/finance_report.pdf")
Styles=getSampleStyleSheet()
content=[
    Paragraph(f"Total Income:{total_income}",Styles["Normal"]),
    Paragraph(f"total expense:{total_expens}",Styles["Normal"]),
    Paragraph(f"savings:{savings}",Styles["Normal"]),

]
doc.build(content)
