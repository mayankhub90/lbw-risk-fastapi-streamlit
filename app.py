import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="LBW Risk – Data Entry", layout="wide")

st.title("📋 Beneficiary Data Entry Form (UI Only)")

# ===============================
# IDENTIFICATION DETAILS
# ===============================
st.subheader("Identification Details")

col1, col2, col3 = st.columns(3)

with col1:
    beneficiary_name = st.text_input("Beneficiary Name")

with col2:
    state = st.text_input("State")

with col3:
    district = st.text_input("District")

col1, col2 = st.columns(2)

with col1:
    block = st.text_input("Block")

with col2:
    village = st.text_input("Village")

# ===============================
# BASIC DETAILS
# ===============================
st.subheader("Basic Beneficiary Details")

col1, col2, col3 = st.columns(3)

with col1:
    beneficiary_age = st.number_input("Beneficiary age (years)", 10, 60)

with col2:
    height = st.number_input("Height (cm)", 120, 200)

with col3:
    month_conception = st.selectbox(
        "Month of Conception",
        [
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December"
        ]
    )

# ===============================
# PREGNANCY & REGISTRATION
# ===============================
st.subheader("Pregnancy & Registration Details")

col1, col2 = st.columns(2)

with col1:
    lmp_date = st.date_input("LMP Date")

with col2:
    registration_date = st.date_input("Registration Date")

# 🔹 Derived Registration Bucket
registration_bucket = None
days_gap = None

if registration_date and lmp_date:
    days_gap = (registration_date - lmp_date).days

    if days_gap < 84:
        registration_bucket = "Early"
    elif 84 <= days_gap <= 168:
        registration_bucket = "Mid"
    else:
        registration_bucket = "Late"

st.info(
    f"📌 Registration Bucket (Derived): **{registration_bucket}** "
    f"(Gap: {days_gap} days)"
    if registration_bucket else
    "📌 Registration Bucket will be derived automatically"
)

# ===============================
# PARITY & HOUSEHOLD
# ===============================
st.subheader("Parity & Household Information")

col1, col2, col3 = st.columns(3)

with col1:
    parity = st.number_input("Child order / parity", 0, 10)

with col2:
    living_children = st.number_input("Number of living children", 0, 10)

with col3:
    household_assets = st.number_input(
        "Household Assets Score (log1p)", 0.0
    )

# ===============================
# BMI PROGRESSION
# ===============================
st.subheader("BMI Progression")

col1, col2, col3, col4 = st.columns(4)

with col1:
    bmi_pw1 = st.number_input("BMI PW1")

with col2:
    bmi_pw2 = st.number_input("BMI PW2")

with col3:
    bmi_pw3 = st.number_input("BMI PW3")

with col4:
    bmi_pw4 = st.number_input("BMI PW4")

# ===============================
# SUBSTANCE USE
# ===============================
st.subheader("Substance Use")

col1, col2, col3 = st.columns(3)

with col1:
    consume_tobacco = st.selectbox("Consume tobacco", ["No", "Yes"])

with col2:
    chewing_status = st.selectbox(
        "Status of current chewing of tobacco",
        ["Never", "Stopped", "Currently chewing"]
    )

with col3:
    consume_alcohol = st.selectbox("Consume alcohol", ["No", "Yes"])

# ===============================
# ANC DETAILS (DYNAMIC)
# ===============================
st.subheader("ANC Details")

anc_completed = st.selectbox("No. of ANCs completed", [0, 1, 2, 3, 4])
anc_data = {}

for i in range(1, anc_completed + 1):
    st.markdown(f"**ANC {i}**")
    col1, col2 = st.columns(2)

    with col1:
        anc_date = st.date_input(f"ANC {i} Date", key=f"anc_date_{i}")

    with col2:
        anc_weight = st.number_input(
            f"ANC {i} Weight (kg)", key=f"anc_weight_{i}"
        )

    anc_data[f"LMPtoINST{i}"] = (
        (anc_date - lmp_date).days if anc_date and lmp_date else None
    )

# ===============================
# FINAL RECORD
# ===============================
if st.button("➕ Add Beneficiary Record"):
    record = {
        "Beneficiary Name": beneficiary_name,
        "State": state,
        "District": district,
        "Block": block,
        "Village": village,
        "Beneficiary age": beneficiary_age,
        "height": height,
        "MonthConception": month_conception,
        "LMP": lmp_date,
        "Registration Date": registration_date,
        "RegistrationBucket": registration_bucket,
        "Child order/parity": parity,
        "Number of living child at now": living_children,
        "BMI_PW1_Prog": bmi_pw1,
        "BMI_PW2_Prog": bmi_pw2,
        "BMI_PW3_Prog": bmi_pw3,
        "BMI_PW4_Prog": bmi_pw4,
        "consume_tobacco": consume_tobacco,
        "Status of current chewing of tobacco": chewing_status,
        "consume_alcohol": consume_alcohol,
        "No of ANCs completed": anc_completed,
        "Household_Assets_Score_log1p": household_assets,
    }

    record.update(anc_data)

    df = pd.DataFrame([record])
    st.success("Record added successfully")
    st.dataframe(df)
