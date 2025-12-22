import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="LBW Risk – Data Entry", layout="wide")
st.title("📋 Beneficiary Data Entry Form (UI – Variable Locked)")

# =====================================================
# 🤰 IDENTIFICATION DETAILS
# =====================================================
st.header("🤰 Identification Details")

# ---- State → District master (EXTENSIBLE) ----
STATE_DISTRICT_MAP = {
    "Andhra Pradesh": ["Anantapur", "Chittoor", "Guntur"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur"],
    "Delhi": ["Central Delhi", "East Delhi", "New Delhi"],
    "Karnataka": ["Bengaluru Urban", "Mysuru", "Dharwad"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
    "Uttar Pradesh": ["Lucknow", "Kanpur Nagar", "Varanasi"],
}

states_sorted = sorted(STATE_DISTRICT_MAP.keys())

c1, c2, c3 = st.columns(3)
with c1:
    beneficiary_name = st.text_input("Beneficiary Name")
with c2:
    state = st.selectbox("State", states_sorted)
with c3:
    district = st.selectbox(
        "District",
        sorted(STATE_DISTRICT_MAP.get(state, []))
    )

c1, c2 = st.columns(2)
with c1:
    block = st.text_input("Block")
with c2:
    village = st.text_input("Village")

# =====================================================
# 🩺 PHYSIOLOGICAL & DEMOGRAPHIC DETAILS
# =====================================================
st.header("🩺 Physiological & Demographic Details")

c1, c2, c3 = st.columns(3)
with c1:
    beneficiary_age = st.number_input("Beneficiary age (years)", 14, 60)
with c2:
    height_cm = st.number_input("Height (cm)", 120.0, 200.0)
with c3:
    hb_value = st.number_input("Measured Hb (g/dL)", 3, 18)

if hb_value < 6:
    measured_HB_risk_bin = "severe_anaemia"
elif hb_value < 8:
    measured_HB_risk_bin = "moderate_anaemia"
elif hb_value < 11:
    measured_HB_risk_bin = "mild_anaemia"
else:
    measured_HB_risk_bin = "normal"

c1, c2 = st.columns(2)
with c1:
    parity = st.number_input("Child order / parity", 0, 10)
with c2:
    living_children = st.number_input("Number of living children at present", 0, 10)

MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}

month_ui = st.selectbox("Month of Conception", list(MONTH_MAP.keys()))
month_conception = MONTH_MAP[month_ui]  # BACKEND NUMERIC

# =====================================================
# 🤰 PREGNANCY & REGISTRATION DETAILS
# =====================================================
st.header("🤰 Pregnancy & Registration Details")

c1, c2 = st.columns(2)
with c1:
    lmp_date = st.date_input("Last Menstrual Period (LMP)")
with c2:
    registration_date = st.date_input("Registration Date")

if lmp_date > registration_date:
    st.error("❌ LMP date cannot be later than Registration Date")
    st.stop()

days_gap = (registration_date - lmp_date).days
registration_bucket = (
    "Early" if days_gap < 84 else "Mid" if days_gap <= 168 else "Late"
)

# =====================================================
# 🚬 TOBACCO & ALCOHOL
# =====================================================
st.header("🚬 Tobacco & Alcohol")

consume_tobacco = st.selectbox("Do you consume tobacco?", ["No", "Yes"])
chewing_status = (
    st.selectbox(
        "Status of current chewing of tobacco",
        ["EVERY DAY", "SOME DAYS", "NOT AT ALL"]
    ) if consume_tobacco == "Yes" else None
)

consume_alcohol = st.selectbox("Do you consume alcohol?", ["No", "Yes"])

# =====================================================
# 💰 SCHEME PARTICIPATION
# =====================================================
st.header("💰 Scheme Participation")

jsy_reg = st.selectbox(
    "Registered for cash transfer scheme: JSY",
    ["No", "Yes"]
)

rajhsri_reg = st.selectbox(
    "Registered for cash transfer scheme: RAJHSRI",
    ["No", "Yes"]
)

# =====================================================
# 🔍 BACKEND PREVIEW (DEBUG)
# =====================================================
st.header("🔍 Backend Preview (Raw Values)")

preview = {
    "State": state,
    "District": district,
    "MonthConception (numeric)": month_conception,
    "consume_tobacco": consume_tobacco,
    "consume_alcohol": consume_alcohol,
    "JSY Registered": jsy_reg,
    "RAJHSRI Registered": rajhsri_reg,
    "RegistrationBucket": registration_bucket,
}

st.json(preview)
