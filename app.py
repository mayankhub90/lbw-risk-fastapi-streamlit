# app.py
import json
import joblib
import pandas as pd
import streamlit as st
import numpy as np

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config("LBW Risk Predictor", layout="wide")
st.title("🤰 Low Birth Weight (LBW) Risk Assessment")

ARTIFACT_DIR = "artifacts"

# ----------------------------
# LOAD ARTIFACTS
# ----------------------------
@st.cache_resource
def load_model():
    model = joblib.load(f"{ARTIFACT_DIR}/xgb_model.pkl")
    with open(f"{ARTIFACT_DIR}/features.json") as f:
        features = json.load(f)
    return model, features

model, FEATURES = load_model()

# ----------------------------
# MAPPINGS
# ----------------------------
YES_NO = {"No": 0, "Yes": 1}

EDU = {
    "No schooling": 0,
    "Primary": 1,
    "Upper Primary": 2,
    "Secondary": 3,
    "Senior Secondary": 4,
    "Graduate & above": 5
}

TOILET = {
    "Improved toilet": 0,
    "Pit latrine": 1,
    "Open defecation": 2
}

# ----------------------------
# DERIVED FUNCTIONS
# ----------------------------
def hb_risk(hb):
    if hb < 7: return 3
    if hb < 8: return 2
    if hb < 11: return 1
    return 0

# ----------------------------
# UI
# ----------------------------
with st.form("lbw_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input("Beneficiary age", 15, 45, 25)
        hb = st.number_input("Hemoglobin (g/dL)", 4.0, 16.0, 11.0)
        bmi = st.number_input("BMI (PW2)", 14.0, 40.0, 22.0)

    with col2:
        tobacco = st.selectbox("Consumes tobacco?", ["No", "Yes"])
        alcohol = st.selectbox("Consumes alcohol?", ["No", "Yes"])
        anc = st.number_input("No of ANCs completed", 0, 10, 2)

    with col3:
        education = st.selectbox("Education level", list(EDU.keys()))
        toilet = st.selectbox("Toilet type", list(TOILET.keys()))

    submit = st.form_submit_button("🔍 Predict Risk")

# ----------------------------
# PREDICTION
# ----------------------------
if submit:
    row = {
        "Beneficiary age": age,
        "measured_HB_risk_bin": hb_risk(hb),
        "BMI_PW2_Prog": bmi,
        "consume_tobacco": YES_NO[tobacco],
        "consume_alcohol": YES_NO[alcohol],
        "No of ANCs completed": anc,
        "education_clean": EDU[education],
        "toilet_type_clean": TOILET[toilet],
    }

    # Fill missing model features with 0
    for f in FEATURES:
        row.setdefault(f, 0)

    X = pd.DataFrame([row])[FEATURES]

    prob = model.predict_proba(X)[0, 1]

    st.subheader("📊 Prediction Result")
    st.metric("LBW Risk Probability", f"{prob:.2%}")

    if prob >= 0.5:
        st.error("⚠ High Risk of Low Birth Weight")
    else:
        st.success("✅ Lower Risk of Low Birth Weight")
