import streamlit as st
import pandas as pd
import kanchan
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
st.set_page_config(page_title="finance Dashboard",layout="wide")

import streamlit as st

st.markdown("""
<style>
.stApp{
            backgrund-color:#000000;
            color:black;
            }
</style>""",
unsafe_allow_html=True)


st.markdown('<div class="stApp">', unsafe_allow_html=True)
st.markdown("""
<style>
}
.card{
Padding:15px;
border-radius:12px;
colour:white;
text-align:center;
font-size:20px;
hieght:90px;
box-shadow: 0 4px 8px rgba(0,0,0,0.1);
display:flex;
jistify-content:center;
}
/*GAP REMOVE*/
.block-countainer{
            padding-top:1rem;
}
.card-value{
font-size:28px;
font-weight:bold;
}
.blue{
    background:#2b7de9;
}
.red{
    background:#e74c3c;

}
.green{
    background:#27ae60
}
.grey{
    background:#ecf0f1;color:black
            
}

            
</style>""",unsafe_allow_html=True)
st.title("FINANCE DASHBOARD")
import yagmail

def send_email_alert(expens,budget,reciever):
    sender_email="k03421723@gmail.com"
    sender_password="eyjm kzfj fpom ejcm"

    yag=yagmail.SMTP(sender_email,sender_password)
    message=f"""
    BUDGET ALERT 
    budget:{budget}
    expense:{expens}
    your monthly budget has been exceeded"""
    yag.send(to=receiver,subject="finance dashboard budget alert",contents=message)
col1,col2=st.columns(2)
with col1:
       st.markdown('<div class="section">', unsafe_allow_html=True)
       uploaded_file=st.file_uploader("upload bank statement",type=["csv","xlsx","xls"])
       if uploaded_file is not None:
           if uploaded_file.name.endswith("csv"):
                df=pd.read_csv(uploaded_file)
           elif uploaded_file.name.endswith(".xlsx") or uploaded_file.name.endswith(".xls"):
                 df=pd.read_excel(uploaded_file)        
       else:
            df=pd.read_csv("student.csv")
            st.markdown('</div',unsafe_allow_html=True)
            
with col2:
    budget=st.number_input("set monthly budget",min_value=0)
    if budget>0:
          if kanchan.total_expens>budget:
              st.error("budget crossed")
              receiver=st.text_input("enter your email")
              if receiver:
                    send_email_alert(kanchan.total_expens,budget,receiver)
          else:
              st.success("within budget")
col1,col2,col3,col4=st.columns(4)
with col1:
    st.markdown(
        f"<div class='card blue'>total_income<br>{kanchan.total_income}</div>",unsafe_allow_html=True)
with col2:
    st.markdown(
        f"<div class='card red'>total_expense<br>{kanchan.total_expens}</div>",unsafe_allow_html=True)
with col3:
    st.markdown(
        f"<div class='card green'>saving<br>{kanchan.savings}</div>",unsafe_allow_html=True)
with col4:
    from sklearn.linear_model import LinearRegression
    import numpy as np
    kanchan.df["Date"]=pd.to_datetime(kanchan.df["Date"])
    monthly_exp=kanchan.df.groupby(pd.to_datetime(kanchan.df["Date"]).dt.month)["debit"].sum()
    if len(monthly_exp.index)>1:
        x=np.array(monthly_exp.index).reshape(-1,1)
        y=np.array(monthly_exp.values)
        model=LinearRegression()
        model.fit(x,y)
        next_month=np.array([[max(monthly_exp.index)+1]])
        prediction=model.predict(next_month)
   # st.subheader("next month expense prediction")
        next_month_expense=abs(round(prediction[0]))
    st.markdown(
                f"""<div class='card grey'>NEXT MONTH PREDICTION<br>{next_month_expense}</div>""",unsafe_allow_html=True)
st.divider()

col1,col2,col3,col4,col5=st.columns(5)
with col1:
    st.pyplot(kanchan.fig_monthly,use_container_width=True)
with col2:
    
    st.pyplot(kanchan.fig_income_expense,use_container_width=True)

with col3:
    
    st.pyplot(kanchan.fig_saving,use_container_width=True)
with col4:
    
    st.pyplot(kanchan.fig_category_expens,use_container_width=True)
with col5:
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    st.subheader("SMART INSIGHTS")
    if kanchan.total_expens>kanchan.total_income:
        st.warning("expenses high as compare to income ")
    elif kanchan.savings<kanchan.total_income*0.2:
        st.info("saving increase ,unnecessary expenses cut ")
    else:
        st.success("great!your saving are going well")
    if kanchan.total_expens>budget:
        st.warning("your bugdet has been exceeded")
    else:
        st.success("budget has been controled ")

    if kanchan.total_expens>kanchan.total_income*0.2:
        st.info("dining and shopping expenses.")
    df["Date"]=pd.to_datetime(df["Date"])
    monthly=df.groupby(df["Date"].dt.month)["debit"].sum()
    if len(monthly)>=2:
        if monthly.iloc[-1]>monthly.iloc[-2]:
            st.warning("expenses have increased compared to last month.")
        else:
            st.success("expenses have decreased last months")
    score=int((kanchan.savings/kanchan.total_income)*100)
    if score>40:
        st.warning(f"financial score:{score}"("good"))
    elif score>20:
        st.warning(f"financial{score}(average)")
    else:
        st.error(f"financial score:{score}(poor)")
    if "prediction" in locals():
        st.info(f"NEXT MONTH EXPECTED EXPENSE{round(prediction[0])}")
    st.markdown('</div',unsafe_allow_html=True)



from reportlab.platypus import SimpleDocTemplate,Paragraph,Image
from reportlab.lib.styles import getSampleStyleSheet
import os
Styles=getSampleStyleSheet()
doc=SimpleDocTemplate("project/finance_report.pdf")
os.makedirs("project",exist_ok=True)

kanchan.fig_monthly.savefig("project/monthly_expense.png")
kanchan.fig_income_expense.savefig("project/income vs expense.png")
kanchan.fig_saving.savefig("project/monthly_saving.png")
kanchan.fig_category_expens.savefig("project/expens_category.png") 
content=[
    Paragraph(f"Total Income:{kanchan.total_income}",Styles["Normal"]),
    Paragraph(f"total expense:{kanchan.total_expens}",Styles["Normal"]),
    Paragraph(f"savings:{kanchan.savings}",Styles["Normal"]),
    Image("project/monthly_expense.png"),
    Image("project/income vs expense.png"),
    Image("project/monthly_saving.png"),
    Image("project/expens_category.png"),

]





with open("project/finance_report.pdf","rb") as file:
    st.download_button(
        label="Download finance report pdf",
        data=file,
        file_name="finance_report.pdf",
        mime="applicaltion/pdf")
    

