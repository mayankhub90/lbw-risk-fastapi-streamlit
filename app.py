import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="LBW Risk Predictor", layout="wide")
st.title("🤰 Low Birth Weight (LBW) Risk Assessment")

st.markdown("Enter beneficiary details. Prediction is done securely via AI model.")

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
        chew = st.selectbox("Chews Tobacco?", ["No", "Yes"])
        alcohol = st.selectbox("Consumes Alcohol?", ["No", "Yes"])
        anc = st.number_input("No. of ANCs Completed", 0, 10, 2)

    with col3:
        food = st.selectbox("Food Group Category", [1, 2, 3, 4, 5])
        toilet = st.selectbox("Improved Toilet?", ["Yes", "No"])
        water = st.selectbox(
            "Water Source",
            ["Piped supply (home/yard/stand)",
             "Groundwater – handpump/borewell",
             "Protected well",
             "Surface/Unprotected source",
             "Delivered / other"]
        )
        education = st.selectbox(
            "Education Level",
            ["No schooling", "Primary (1–5)", "Middle (6–8)", "Secondary (9–12)", "Graduate & above"]
        )

    pm = st.number_input("PMMVY Installments Received", 0, 3, 0)
    jsy = st.number_input("JSY Installments Received", 0, 2, 0)

    submitted = st.form_submit_button("🔍 Predict Risk")

# -----------------------
# CALL FASTAPI
# -----------------------
if submitted:
    payload = {
        "Beneficiary_age": age,
        "measured_HB": hb,
        "BMI_PW2_Prog": bmi,
        "consume_tobacco": tobacco,
        "Status_of_current_chewing_of_tobacco": chew,
        "consume_alcohol": alcohol,
        "No_of_ANCs_completed": anc,
        "Food_Groups_Category": food,
        "toilet_type_clean": toilet,
        "water_source_clean": water,
        "education_clean": education,
        "PMMVY_installments": pm,
        "JSY_installments": jsy
    }

    with st.spinner("Predicting risk..."):
        # 🔴 IMPORTANT: local FastAPI URL
        resp = requests.post("http://localhost:8000/predict", json=payload)

    if resp.status_code != 200:
        st.error("Prediction failed. Check FastAPI server.")
    else:
        out = resp.json()

        st.subheader("📊 Prediction Result")
        st.metric("LBW Risk Probability", out["risk_probability"])
        st.success(out["risk_label"])

        st.subheader("🔎 Key Risk Drivers")
        shap_df = pd.DataFrame(out["top_drivers"])
        st.bar_chart(shap_df.set_index("feature")["shap_value"])
