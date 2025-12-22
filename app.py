import streamlit as st
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="LBW Risk – Data Entry", layout="wide")
st.title("📋 Beneficiary Data Entry Form (UI – Variable Locked)")

# =====================================================
# ⏱ FORM START TIME (SESSION LEVEL)
# =====================================================
if "form_start_time" not in st.session_state:
    st.session_state.form_start_time = datetime.now()

# =====================================================
# 🤰 IDENTIFICATION DETAILS
# =====================================================
st.header("🤰 Identification Details")

STATE_DISTRICT_MAP = {
    "Andhra Pradesh": ["Anantapur", "Chittoor", "Guntur"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur"],
    "Delhi": ["Central Delhi", "East Delhi", "New Delhi"],
    "Karnataka": ["Bengaluru Urban", "Mysuru", "Dharwad"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
    "Uttar Pradesh": ["Lucknow", "Kanpur Nagar", "Varanasi"]
}

states_sorted = sorted(STATE_DISTRICT_MAP.keys())

c1, c2, c3 = st.columns(3)
with c1:
    beneficiary_name = st.text_input("Beneficiary Name")
with c2:
    state = st.selectbox("State", states_sorted)
with c3:
    district = st.selectbox("District", sorted(STATE_DISTRICT_MAP[state]))

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
month_conception = MONTH_MAP[month_ui]

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
# 📍 GEOLOCATION (OPTIONAL)
# =====================================================
st.header("📍 Location (Optional)")

capture_location = st.checkbox("Capture GPS coordinates")

latitude = None
longitude = None

if capture_location:
    c1, c2 = st.columns(2)
    with c1:
        latitude = st.number_input("Latitude", min_value=-90.0, max_value=90.0)
    with c2:
        longitude = st.number_input("Longitude", min_value=-180.0, max_value=180.0)

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
# 🥗 NUTRITION
# =====================================================
st.header("🥗 Nutrition")

ifa_tabs = st.number_input(
    "No. of IFA tablets received/procured in last one month", min_value=0
)
calcium_tabs = st.number_input(
    "No. of calcium tablets consumed in last one month", min_value=0
)

food_group = st.selectbox(
    "How many food groups have you consumed?",
    [0, 1, 2, 3, 4, 5]
)

# =====================================================
# 💰 SCHEME PARTICIPATION
# =====================================================
st.header("💰 Scheme Participation")

jsy_reg = st.selectbox("Registered for cash transfer scheme: JSY", ["No", "Yes"])
rajhsri_reg = st.selectbox("Registered for cash transfer scheme: RAJHSRI", ["No", "Yes"])

# =====================================================
# ✅ SUBMIT & REVIEW
# =====================================================
st.header("✅ Submit & Review")

if st.button("➕ Add Beneficiary Record"):
    form_end_time = datetime.now()
    duration_seconds = int(
        (form_end_time - st.session_state.form_start_time).total_seconds()
    )

    record = {
        # --- core variables (unchanged) ---
        "Beneficiary age": beneficiary_age,
        "measured_HB_risk_bin": measured_HB_risk_bin,
        "Child order/parity": parity,
        "Number of living child at now": living_children,
        "MonthConception": month_conception,
        "consume_tobacco": consume_tobacco,
        "Status of current chewing of tobacco": chewing_status,
        "consume_alcohol": consume_alcohol,
        "RegistrationBucket": registration_bucket,
        "No. of IFA tablets received/procured in last one month_log1p": ifa_tabs,
        "No. of calcium tablets consumed in last one month_log1p": calcium_tabs,
        "Food_Groups_Category": food_group,
        "Registered for cash transfer scheme: JSY": jsy_reg,
        "Registered for cash transfer scheme: RAJHSRI": rajhsri_reg,
        "height": height_cm,
        "LMP": lmp_date,
        "Registration Date": registration_date,

        # --- metadata (NEW) ---
        "form_start_time": st.session_state.form_start_time.isoformat(),
        "form_end_time": form_end_time.isoformat(),
        "form_duration_seconds": duration_seconds,
        "latitude": latitude,
        "longitude": longitude
    }

    st.success("✅ Record captured successfully")
    st.subheader("🔍 Final Saved Record (Backend View)")
    st.json(record)
