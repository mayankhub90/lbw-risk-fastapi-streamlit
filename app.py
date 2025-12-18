import streamlit as st
import joblib
import json
import pandas as pd
import numpy as np
import os

# --------------------
# CONFIG
# --------------------
st.set_page_config(page_title="LBW Risk Predictor", layout="wide")

ARTIFACT_DIR = "artifacts"
MODEL_PATH = os.path.join(ARTIFACT_DIR, "xgb_model.pkl")
FEATURES_PATH = os.path.join(ARTIFACT_DIR, "features.json")

# --------------------
# LOAD ARTIFACTS
# --------------------
@st.cache_resource
def load_model():
    model = joblib.load(MODEL_PATH)
    features = json.load(open(FEATURES_PATH))
    return model, features

model, FEATURES = load_model()

# --------------------
# UI
# --------------------
st.title("🤰 Low Birth Weight (LBW) Risk Assessment")
st.markdown("Enter beneficiary details to predict LBW risk.")

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
        food = st.selectbox("Food Groups Category", [1, 2, 3, 4, 5])
        toilet = st.selectbox("Improved toilet?", ["Yes", "No"])
        education = st.selectbox(
            "Education level",
            [
                "Illiterate",
                "Primary",
                "Upper Primary",
                "Secondary",
                "Senior Secondary",
                "Graduate",
                "Graduate and Above",
            ],
        )

    pm = st.number_input("PMMVY installments received", 0, 3, 0)
    jsy = st.number_input("JSY installments received", 0, 2, 0)

    submitted = st.form_submit_button("🔍 Predict Risk")

# --------------------
# PREDICTION
# --------------------
if submitted:
    # Build raw input row using EXACT feature names
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

    # Create dataframe with ALL features (missing → NaN)
    X = pd.DataFrame([{f: row.get(f, np.nan) for f in FEATURES}])

    prob = model.predict_proba(X)[0, 1]

    label = "⚠️ High LBW Risk" if prob >= 0.5 else "✅ Lower LBW Risk"

    st.subheader("📊 Prediction Result")
    st.metric("LBW Risk Probability", f"{prob:.2%}")
    st.success(label)

    st.info("Explainability (SHAP) will be added in the next version.")
