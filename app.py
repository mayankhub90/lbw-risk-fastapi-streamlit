import streamlit as st
import pandas as pd
import numpy as np
import joblib

from preprocessing import preprocess_payload


# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="LBW Risk Assessment",
    layout="wide"
)

st.title("🤰 Low Birth Weight (LBW) Risk Assessment")

st.markdown(
    """
    Enter beneficiary details below.  
    All clinical derivations (BMI, anemia category, buckets, log transforms)  
    are handled **automatically in the backend**.
    """
)

# --------------------------------------------------
# Load model (cached)
# --------------------------------------------------
@st.cache_resource
def load_model():
    return joblib.load("artifacts/xgb_model.pkl")

model = load_model()

# --------------------------------------------------
# SECTION A — Beneficiary Background
# --------------------------------------------------
st.header("A. Beneficiary Background")

col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Beneficiary Age (years)", 15, 49, 25)

with col2:
    living_children = st.number_input("Number of Living Children", 0, 6, 0)

with col3:
    pregnancy_losses = st.number_input(
        "Miscarriages / Abortions / Stillbirths",
        0, 6, 0
    )

parity = living_children + pregnancy_losses + 1
st.info(f"**Child order / parity (auto-derived): {parity}**")

education_clean = st.selectbox(
    "Education Level",
    [
        "No schooling",
        "Primary (1–5)",
        "Middle (6–8)",
        "Secondary (9–12)",
        "Graduate & above"
    ]
)

# --------------------------------------------------
# SECTION B — Registration Dates
# --------------------------------------------------
st.header("B. Registration Details")

col1, col2 = st.columns(2)

with col1:
    lmp_date = st.date_input("LMP Date")

with col2:
    registration_date = st.date_input("Registration Date")

# --------------------------------------------------
# SECTION C — Clinical & Anthropometry
# --------------------------------------------------
st.header("C. Clinical & Anthropometry")

col1, col2, col3 = st.columns(3)

with col1:
    hemoglobin = st.number_input("Hemoglobin (g/dL)", 4.0, 16.0, 11.0)

with col2:
    height_cm = st.number_input("Height (cm)", 120.0, 190.0, 155.0)

with col3:
    anc_completed = st.number_input("Number of ANC Visits Completed", 0, 8, 0)

# Conditional weight inputs
weight_pw1 = weight_pw2 = weight_pw3 = weight_pw4 = None

if anc_completed >= 1:
    weight_pw1 = st.number_input("Weight at ANC 1 (kg)", 30.0, 120.0)

if anc_completed >= 2:
    weight_pw2 = st.number_input("Weight at ANC 2 (kg)", 30.0, 120.0)

if anc_completed >= 3:
    weight_pw3 = st.number_input("Weight at ANC 3 (kg)", 30.0, 120.0)

if anc_completed >= 4:
    weight_pw4 = st.number_input("Weight at ANC 4 (kg)", 30.0, 120.0)

tt_injection = st.selectbox(
    "TT Injection given in last ANC?",
    ["Yes", "No"]
)

# --------------------------------------------------
# SECTION D — Nutrition Intake
# --------------------------------------------------
st.header("D. Nutrition Intake")

col1, col2, col3 = st.columns(3)

with col1:
    ifa_tabs = st.number_input(
        "IFA tablets received last month",
        0, 120, 0
    )

with col2:
    calcium_tabs = st.number_input(
        "Calcium tablets consumed last month",
        0, 120, 0
    )

with col3:
    food_group = st.selectbox(
        "Food Group Category",
        [1, 2, 3, 4, 5]
    )

# --------------------------------------------------
# SECTION E — Behavioural Factors
# --------------------------------------------------
st.header("E. Behavioural Factors")

col1, col2, col3 = st.columns(3)

with col1:
    consume_tobacco = st.selectbox("Consumes Tobacco?", ["No", "Yes"])

with col2:
    chewing_tobacco = st.selectbox(
        "Currently Chewing Tobacco?",
        ["No", "Yes"]
    )

with col3:
    consume_alcohol = st.selectbox("Consumes Alcohol?", ["No", "Yes"])

# --------------------------------------------------
# SECTION F — Household & Access
# --------------------------------------------------
st.header("F. Household & Living Conditions")

col1, col2, col3 = st.columns(3)

with col1:
    toilet_type_clean = st.selectbox(
        "Toilet Facility",
        [
            "Improved toilet",
            "Pit latrine (basic)",
            "Unimproved / unknown",
            "No facility / open defecation"
        ]
    )

with col2:
    water_source_clean = st.selectbox(
        "Main Drinking Water Source",
        [
            "Piped supply (home/yard/stand)",
            "Groundwater – handpump/borewell",
            "Protected well",
            "Surface/Unprotected source",
            "Delivered / other"
        ]
    )

with col3:
    social_media = st.selectbox(
        "Exposure to Social Media",
        ["No", "Yes"]
    )

washing_machine = st.selectbox(
    "Washing Machine in Household?",
    ["No", "Yes"]
)

ac_cooler = st.selectbox(
    "Air Conditioner / Cooler in Household?",
    ["No", "Yes"]
)

# --------------------------------------------------
# SECTION G — Scheme Exposure
# --------------------------------------------------
st.header("G. Scheme Exposure")

col1, col2 = st.columns(2)

with col1:
    pmmvy_count = st.number_input(
        "PMMVY Installments Received",
        0, 3, 0
    )

with col2:
    jsy_count = st.number_input(
        "JSY Installments Received",
        0, 2, 0
    )

jsy_registered = st.selectbox(
    "Registered for JSY?",
    ["Yes", "No"]
)

rajshri_registered = st.selectbox(
    "Registered for RAJHSRI?",
    ["Yes", "No"]
)

# --------------------------------------------------
# PREDICTION
# --------------------------------------------------
st.divider()

if st.button("🔍 Predict LBW Risk"):
    payload = {
        "beneficiary_age": age,
        "parity": parity,
        "living_children": living_children,
        "education_clean": education_clean,
        "lmp_date": lmp_date,
        "registration_date": registration_date,
        "hemoglobin": hemoglobin,
        "height_cm": height_cm,
        "weight_pw1": weight_pw1,
        "weight_pw2": weight_pw2,
        "weight_pw3": weight_pw3,
        "weight_pw4": weight_pw4,
        "anc_completed": anc_completed,
        "tt_injection": tt_injection,
        "ifa_tabs": ifa_tabs,
        "calcium_tabs": calcium_tabs,
        "food_group": food_group,
        "consume_tobacco": consume_tobacco,
        "chewing_tobacco": chewing_tobacco,
        "consume_alcohol": consume_alcohol,
        "toilet_type_clean": toilet_type_clean,
        "water_source_clean": water_source_clean,
        "washing_machine": washing_machine,
        "ac_cooler": ac_cooler,
        "social_media": social_media,
        "pmmvy_count": pmmvy_count,
        "jsy_count": jsy_count,
        "jsy_registered": jsy_registered,
        "rajshri_registered": rajshri_registered
    }

    X = preprocess_payload(payload)
    prob = model.predict_proba(X)[0, 1]

    st.subheader("📊 Prediction Result")
    st.metric("LBW Risk Probability", f"{prob:.2%}")

    if prob >= 0.5:
        st.error("⚠️ High Risk of Low Birth Weight")
    else:
        st.success("✅ Lower Risk of Low Birth Weight")
