import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="LBW Risk – Data Entry", layout="wide")
st.title("📋 Beneficiary Data Entry Form (UI – Feature Complete)")

# =====================================================
# ASSET WEIGHTS
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
    "Animal": 0.5,
    "Car": 1.5,
    "Water Pump": 0.75,
    "Thresher": 0.75,
    "Tractor": 1.25,
}

# =====================================================
# IDENTIFICATION
# =====================================================
st.subheader("Identification Details")

c1, c2, c3 = st.columns(3)
with c1:
    beneficiary_name = st.text_input("Beneficiary Name")
with c2:
    state = st.text_input("State")
with c3:
    district = st.text_input("District")

c1, c2 = st.columns(2)
with c1:
    block = st.text_input("Block")
with c2:
    village = st.text_input("Village")

# =====================================================
# PHYSIO FEATURES
# =====================================================
st.subheader("Physiological Details")

c1, c2, c3 = st.columns(3)
with c1:
    beneficiary_age = st.number_input("Beneficiary age (years)", 14, 60)
with c2:
    height = st.number_input("Height (cm)", 120, 200)
with c3:
    hb_level = st.number_input("Measured Hb (g/dL)", 3.0, 18.0)

# Derived Hb risk
if hb_level < 6:
    measured_HB_risk_bin = "Severe Anaemia"
elif hb_level < 8:
    measured_HB_risk_bin = "Moderate Anaemia"
elif hb_level < 11:
    measured_HB_risk_bin = "Mild Anaemia"
else:
    measured_HB_risk_bin = "Normal"

st.info(f"🩸 Hb Risk Category (Derived): **{measured_HB_risk_bin}**")

c1, c2 = st.columns(2)
with c1:
    parity = st.number_input("Child order / parity", 0, 10)
with c2:
    living_children = st.number_input("Number of living children", 0, 10)

month_conception = st.selectbox(
    "Month of Conception",
    ["January","February","March","April","May","June",
     "July","August","September","October","November","December"]
)

# =====================================================
# PREGNANCY & REGISTRATION
# =====================================================
st.subheader("Pregnancy & Registration")

c1, c2 = st.columns(2)
with c1:
    lmp_date = st.date_input("LMP Date")
with c2:
    registration_date = st.date_input("Registration Date")

registration_bucket = None
if lmp_date and registration_date:
    diff = (registration_date - lmp_date).days
    if diff < 84:
        registration_bucket = "Early"
    elif diff <= 168:
        registration_bucket = "Mid"
    else:
        registration_bucket = "Late"

st.info(f"📌 Registration Bucket (Derived): **{registration_bucket}**")

# =====================================================
# ANC DETAILS
# =====================================================
st.subheader("ANC Details")

anc_completed = st.selectbox("No. of ANCs completed", [0,1,2,3,4])
anc_dates, anc_weights = {}, {}

for i in range(1, anc_completed + 1):
    st.markdown(f"**ANC {i}**")
    c1, c2 = st.columns(2)
    with c1:
        anc_dates[i] = st.date_input(f"ANC {i} Date", key=f"anc_date_{i}")
    with c2:
        anc_weights[i] = st.number_input(f"ANC {i} Weight (kg)", key=f"anc_weight_{i}")

# Derived ANC timing
anc_bucket = None
if anc_dates:
    first_anc = min(d for d in anc_dates.values() if d)
    gap = (first_anc - lmp_date).days
    if gap < 84:
        anc_bucket = "Early"
    elif gap <= 168:
        anc_bucket = "Mid"
    else:
        anc_bucket = "Late"

# Counselling gap
counselling_gap_days = None
if len(anc_dates) >= 2:
    sorted_dates = sorted(anc_dates.values())
    counselling_gap_days = (sorted_dates[1] - sorted_dates[0]).days

# =====================================================
# BMI PROGRESSION
# =====================================================
st.subheader("BMI Progression")

bmi_pw1 = st.number_input("BMI PW1")
bmi_pw2 = st.number_input("BMI PW2") if anc_completed >= 2 else None
bmi_pw3 = st.number_input("BMI PW3") if anc_completed >= 3 else None
bmi_pw4 = st.number_input("BMI PW4") if anc_completed >= 4 else None

# =====================================================
# TOBACCO & ALCOHOL
# =====================================================
st.subheader("Tobacco & Alcohol")

consume_tobacco = st.selectbox("Consume tobacco", ["No","Yes"])
chewing_status = st.selectbox(
    "Status of current chewing of tobacco",
    ["EVERY DAY","SOME DAYS","NOT AT ALL"]
)
consume_alcohol = st.selectbox("Consume alcohol", ["No","Yes"])

# =====================================================
# NUTRITION
# =====================================================
st.subheader("Nutrition")

ifa_tabs = st.number_input("IFA tablets (last month)")
calcium_tabs = st.number_input("Calcium tablets (last month)")

food_group = st.selectbox(
    "Food Groups Category",
    ["Low","Medium","High"]
)

# =====================================================
# HOUSEHOLD ASSETS
# =====================================================
st.subheader("Household Assets")

asset_score = 0
asset_flags = {}

cols = st.columns(3)
i = 0
for asset, weight in ASSET_WEIGHTS.items():
    with cols[i % 3]:
        owned = st.checkbox(asset)
        asset_flags[asset] = owned
        if owned:
            asset_score += weight
    i += 1

st.info(f"🏠 Household Asset Score (raw): **{asset_score:.2f}**")

# =====================================================
# SES
# =====================================================
st.subheader("Socio-economic Status")

toilet_type = st.selectbox(
    "Toilet Type",
    ["Improved toilet","Pit latrine (basic)",
     "Unimproved / unknown","No facility / open defecation"]
)

water_source = st.selectbox(
    "Water Source",
    ["Piped supply","Groundwater – handpump/borewell",
     "Protected well","Surface / Unprotected","Delivered / other"]
)

education = st.selectbox(
    "Education",
    ["No schooling","Primary (1–5)","Middle (6–8)",
     "Secondary (9–12)","Graduate & above"]
)

# =====================================================
# DIGITAL FEATURES
# =====================================================
st.subheader("Digital Exposure")

social_media_types = st.multiselect(
    "Type of Social Media Enrolled In",
    ["Facebook","YouTube","Instagram","WhatsApp","Other"]
)

count_sm = len(social_media_types)
if count_sm == 0:
    social_media_category = "None"
elif count_sm == 1:
    social_media_category = "Low"
elif count_sm <= 3:
    social_media_category = "Medium"
else:
    social_media_category = "High"

# =====================================================
# PROGRAM FEATURES
# =====================================================
st.subheader("Program Participation")

jsy_reg = st.selectbox("Registered for JSY", ["No","Yes"])
rajhsri_reg = st.selectbox("Registered for RAJHSRI", ["No","Yes"])
pmmvy_inst = st.selectbox("PMMVY – Installments received", [0,1,2,98])
jsy_inst = st.selectbox("JSY – Installments received", [0,1,98])
pmmvy_inst_date = st.date_input("PMMVY Installment Date")

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
        "measured_HB_risk_bin": measured_HB_risk_bin,
        "Child order/parity": parity,
        "Number of living child at now": living_children,
        "MonthConception": month_conception,
        "BMI_PW1_Prog": bmi_pw1,
        "BMI_PW2_Prog": bmi_pw2,
        "BMI_PW3_Prog": bmi_pw3,
        "BMI_PW4_Prog": bmi_pw4,
        "consume_tobacco": consume_tobacco,
        "Status of current chewing of tobacco": chewing_status,
        "consume_alcohol": consume_alcohol,
        "RegistrationBucket": registration_bucket,
        "ANCBucket": anc_bucket,
        "counselling_gap_days": counselling_gap_days,
        "No of ANCs completed": anc_completed,
        "Service received during last ANC: TT Injection given": None,
        "No. of IFA tablets received/procured in last one month_log1p": ifa_tabs,
        "No. of calcium tablets consumed in last one month_log1p": calcium_tabs,
        "Food_Groups_Category": food_group,
        "Household_Assets_Score_raw": asset_score,
        "toilet_type_clean": toilet_type,
        "water_source_clean": water_source,
        "education_clean": education,
        "Social_Media_Category": social_media_category,
        "Registered for cash transfer scheme: JSY": jsy_reg,
        "Registered for cash transfer scheme: RAJHSRI": rajhsri_reg,
        "PMMVY-Number of installment received": pmmvy_inst,
        "JSY-Number of installment received": jsy_inst,
        "height": height,
        "LMP": lmp_date,
        "Registration Date": registration_date,
        "PMMVY Instalment Date": pmmvy_inst_date,
    }

    st.success("✅ Record captured")
    st.dataframe(pd.DataFrame([record]))
