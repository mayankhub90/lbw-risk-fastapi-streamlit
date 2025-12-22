import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="LBW Risk – Data Entry", layout="wide")

st.title("📋 Beneficiary Data Entry Form (UI Only)")

# =====================================================
# HOUSEHOLD ASSET WEIGHTS
# =====================================================
ASSET_WEIGHTS = {
    "Electricity": 1.0,
    "Mattress": 0.5,
    "Pressure Cooker": 0.5,
    "Chair": 0.5,
    "Cot/Bed": 0.5,
    "Table": 0.5,
    "Electric Fan": 0.75,
    "Radio/Transistor": 0.5,
    "B & W Television": 0.5,
    "Colour Television": 1.0,
    "Sewing Machine": 0.75,
    "Mobile Telephone": 1.0,
    "Landline Telephone": 0.5,
    "Internet": 1.25,
    "Computer": 1.25,
    "Refrigerator": 1.25,
    "Air Conditioner / Cooler": 1.25,
    "Washing Machine": 1.25,
    "Watch / Lock": 0.25,
    "Bicycle": 0.5,
    "Motorcycle / Scooter": 1.0,
    "Animal (Rural)": 0.5,
    "Car": 1.5,
    "Water Pump": 0.75,
    "Thresher": 0.75,
    "Tractor": 1.25,
}

# =====================================================
# IDENTIFICATION DETAILS
# =====================================================
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

# =====================================================
# BASIC DETAILS
# =====================================================
st.subheader("Basic Beneficiary Details")

col1, col2, col3 = st.columns(3)
with col1:
    beneficiary_age = st.number_input("Beneficiary age (years)", 14, 60)
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

# =====================================================
# PREGNANCY & REGISTRATION
# =====================================================
st.subheader("Pregnancy & Registration Details")

col1, col2 = st.columns(2)
with col1:
    lmp_date = st.date_input("LMP Date")
with col2:
    registration_date = st.date_input("Registration Date")

registration_bucket = None
days_gap = None

if lmp_date and registration_date:
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

# =====================================================
# PARITY
# =====================================================
st.subheader("Parity Details")

col1, col2 = st.columns(2)
with col1:
    parity = st.number_input("Child order / parity", 0, 10)
with col2:
    living_children = st.number_input("Number of living children", 0, 10)

# =====================================================
# BMI PROGRESSION
# =====================================================
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

# =====================================================
# SUBSTANCE USE
# =====================================================
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

# =====================================================
# ANC DETAILS
# =====================================================
st.subheader("ANC Details")

anc_completed = st.selectbox("No. of ANCs completed", [0, 1, 2, 3, 4])
anc_data = {}

for i in range(1, anc_completed + 1):
    st.markdown(f"**ANC {i}**")
    col1, col2 = st.columns(2)
    with col1:
        anc_date = st.date_input(f"ANC {i} Date", key=f"anc_date_{i}")
    with col2:
        anc_weight = st.number_input(f"ANC {i} Weight (kg)", key=f"anc_weight_{i}")

    anc_data[f"LMPtoINST{i}"] = (
        (anc_date - lmp_date).days if anc_date and lmp_date else None
    )

# =====================================================
# HOUSEHOLD ASSETS
# =====================================================
st.subheader("Household Assets")

st.caption("Select all assets available in the household")

asset_score = 0.0
asset_flags = {}

cols = st.columns(3)
col_idx = 0

for asset, weight in ASSET_WEIGHTS.items():
    with cols[col_idx]:
        owned = st.checkbox(asset, key=f"asset_{asset}")
        asset_flags[asset] = owned
        if owned:
            asset_score += weight
    col_idx = (col_idx + 1) % 3

st.info(f"🏠 Household Asset Score (raw): **{asset_score:.2f}**")

# =====================================================
# FINAL RECORD
# =====================================================
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
        "Household_Assets_Score_raw": asset_score,
    }

    for asset, owned in asset_flags.items():
        record[f"Household asset: {asset}"] = int(owned)

    record.update(anc_data)

    df = pd.DataFrame([record])
    st.success("✅ Record added successfully")
    st.dataframe(df)
