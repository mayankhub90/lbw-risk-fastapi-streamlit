import streamlit as st
import requests

st.set_page_config(page_title="LBW Risk Assessment", layout="wide")
st.title("🤰 Low Birth Weight (LBW) Risk Assessment")

st.markdown("Enter beneficiary details. All calculations are handled securely at the backend.")

# -------------------------
# FORM
# -------------------------
with st.form("lbw_form"):

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input(
            "Beneficiary Age (years)",
            min_value=15,
            max_value=45,
            value=25,
            key="age"
        )

        height = st.number_input(
            "Height (cm)",
            min_value=120.0,
            max_value=190.0,
            value=155.0,
            key="height"
        )

        hb = st.number_input(
            "Hemoglobin (g/dL)",
            min_value=4.0,
            max_value=16.0,
            value=11.0,
            key="hb"
        )

    with col2:
        weight_pw1 = st.number_input(
            "Weight PW1 (kg)",
            min_value=30.0,
            max_value=120.0,
            value=50.0,
            key="w_pw1"
        )

        consume_tobacco = st.selectbox(
            "Consumes Tobacco?",
            ["No", "Yes"],
            key="tobacco"
        )

        consume_alcohol = st.selectbox(
            "Consumes Alcohol?",
            ["No", "Yes"],
            key="alcohol"
        )

    with col3:
        anc_completed = st.number_input(
            "Number of ANCs Completed",
            min_value=0,
            max_value=10,
            value=2,
            key="anc"
        )

        food_group = st.selectbox(
            "Food Group Category",
            [1, 2, 3, 4, 5],
            key="food"
        )

        education = st.selectbox(
            "Education Level",
            [
                "Illiterate",
                "Primary",
                "Upper Primary",
                "Secondary",
                "Senior Secondary",
                "Graduate",
                "Graduate and Above"
            ],
            key="education"
        )

    submitted = st.form_submit_button("🔍 Predict LBW Risk")

# -------------------------
# CALL BACKEND
# -------------------------
if submitted:
    payload = {
        "beneficiary_age": age,
        "height_cm": height,
        "hb_g_dl": hb,
        "weight_pw1_kg": weight_pw1,
        "consume_tobacco": consume_tobacco,
        "consume_alcohol": consume_alcohol,
        "anc_completed": anc_completed,
        "food_group_category": food_group,
        "education": education
    }

    with st.spinner("Calculating risk..."):
        response = requests.post(
            "http://localhost:8000/predict",  # will change on cloud
            json=payload,
            timeout=30
        )

    if response.status_code != 200:
        st.error("Prediction failed. Please try again.")
    else:
        result = response.json()
        st.metric("LBW Risk Probability", f"{result['risk_probability']:.2%}")
        st.success(result["risk_label"])
