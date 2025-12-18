# app.py
import streamlit as st
import pandas as pd
import joblib
import json
from pathlib import Path

st.set_page_config(page_title="LBW Risk Predictor", layout="wide")
st.title("🤰 Low Birth Weight (LBW) Risk Assessment")

# -----------------------
# LOAD ARTIFACTS
# -----------------------
ARTIFACT_DIR = Path("model")

@st.cache_resource
def load_artifacts():
    model = joblib.load(ARTIFACT_DIR / "xgb_model.pkl")
    with open(ARTIFACT_DIR / "features.json") as f:
        features = json.load(f)
    background = pd.read_csv(ARTIFACT_DIR / "background.csv")
    return model, features, background

model, FEATURES, BACKGROUND = load_artifacts()

st.success("✅ Model loaded successfully")

# -----------------------
# INPUT FORM
# -----------------------
with st.form("lbw_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input("Beneficiary Age", 15, 45, 25)
        hb = st.number_input("Hemoglobin (g/dL)", 4.0, 16.0, 11.0)
        bmi = st.number_input("BMI (PW2)", 14.0, 40.0, 22.0)

    with col2:
        tobacco = st.selectbox("Consumes Tobacco?", ["No", "Yes"])
        alcohol = st.selectbox("Consumes Alcohol?", ["No", "Yes"])
        anc = st.number_input("No. of ANCs Completed", 0, 10, 2)

    with col3:
        food = st.selectbox("Food Group Category", [1, 2, 3, 4, 5])
        toilet = st.selectbox("Improved Toilet?", ["Yes", "No"])
        education = st.selectbox(
            "Education Level",
            ["Illiterate", "Primary", "Upper Primary", "Secondary",
             "Senior Secondary", "Graduate", "Graduate and Above"]
        )

    pm = st.number_input("PMMVY Installments Received", 0, 3, 0)
    jsy = st.number_input("JSY Installments Received", 0, 2, 0)

    submitted = st.form_submit_button("🔍 Predict Risk")

# -----------------------
# PREDICTION
# -----------------------
if submitted:
    row = {
        "Beneficiary age": age,
        "measured_HB": hb,
        "BMI_PW2_Prog": bmi,
        "consume_tobacco": 1 if tobacco == "Yes" else 0,
        "consume_alcohol": 1 if alcohol == "Yes" else 0,
        "No of ANCs completed": anc,
        "Food_Groups_Category": food,
        "toilet_type_clean": toilet,
        "education_clean": education,
        "PMMVY-Number of installment received": pm,
        "JSY-Number of installment received": jsy,
    }

    X = pd.DataFrame([row])

    # Align features
    for f in FEATURES:
        if f not in X.columns:
            X[f] = 0

    X = X[FEATURES]

    prob = model.predict_proba(X)[0, 1]

    st.subheader("📊 Prediction Result")
    st.metric("LBW Risk Probability", f"{prob:.2%}")

    if prob >= 0.5:
        st.error("⚠️ High Risk of Low Birth Weight")
    else:
        st.success("✅ Lower Risk of Low Birth Weight")
