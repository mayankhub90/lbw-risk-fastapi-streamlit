import streamlit as st
import requests

st.set_page_config("LBW Risk Assessment", layout="wide")
st.title("🤰 Low Birth Weight Risk Assessment")

API_URL = "http://localhost:8000/predict"

with st.form("lbw_form"):

    st.header("Mother & Health")
    age = st.number_input("Age", 15, 45, 25)
    hb = st.number_input("Hemoglobin (g/dL)", 4.0, 16.0, 11.0)

    st.header("Nutrition")
    ifa = st.number_input("IFA tablets last month", 0, 120, 30)
    calcium = st.number_input("Calcium tablets last month", 0, 120, 30)

    st.header("ANC & Timeline")
    anc = st.number_input("No. of ANCs completed", 0, 10, 2)
    lmp = st.date_input("LMP Date")
    reg = st.date_input("Registration Date")

    st.header("Household Assets")
    wm = st.selectbox("Washing Machine", ["No", "Yes"])
    ac = st.selectbox("AC/Cooler", ["No", "Yes"])

    submitted = st.form_submit_button("🔍 Predict")

if submitted:
    payload = {
        "Beneficiary age": age,
        "measured_HB": hb,
        "ifa_tabs": ifa,
        "calcium_tabs": calcium,
        "No of ANCs completed": anc,
        "lmp_date": str(lmp),
        "registration_date": str(reg),
        "has_washing_machine": wm == "Yes",
        "has_ac_cooler": ac == "Yes",
        "pc_pw1": None,
        "pc_pw2": None,
        "pc_pw3": None,
        "pc_pw4": None,
        "inst1_date": None,
        "inst2_date": None,
        "inst3_date": None
    }

    res = requests.post(API_URL, json=payload).json()

    st.metric("LBW Risk Probability", res["risk_probability"])
    st.success(res["risk_label"])
