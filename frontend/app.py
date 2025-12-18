# frontend/app.py
import streamlit as st
import requests
import datetime

st.set_page_config(
    page_title="LBW Risk Assessment",
    layout="wide"
)

st.title("🤰 Low Birth Weight (LBW) Risk Assessment")
st.caption("Enter beneficiary details. All preprocessing is handled securely at the backend.")

API_URL = "http://localhost:8000/predict"  # change after deploy

# =========================
# FORM START
# =========================
with st.form("lbw_form", clear_on_submit=True):

    # --------------------------------------------------
    # SECTION A — BENEFICIARY BACKGROUND
    # --------------------------------------------------
    st.subheader("🧍 Beneficiary Background")

    col1, col2, col3 = st.columns(3)

    with col1:
        beneficiary_age = st.number_input(
            "Beneficiary Age (years)", 15, 49, 25, key="age"
        )
        parity = st.number_input(
            "Child Order / Parity", 0, 6, 1, key="parity"
        )

    with col2:
        living_children = st.number_input(
            "Number of Living Children", 0, 6, 1, key="living_children"
        )
        education_clean = st.selectbox(
            "Education Level",
            [
                "No schooling",
                "Primary (1–5)",
                "Middle (6–8)",
                "Secondary (9–12)",
                "Graduate & above"
            ],
            key="education"
        )

    # --------------------------------------------------
    # SECTION B — CLINICAL & ANTHROPOMETRY
    # --------------------------------------------------
    st.subheader("🩺 Clinical & Anthropometry")

    col1, col2, col3 = st.columns(3)

    with col1:
        hemoglobin = st.number_input(
            "Hemoglobin (g/dL)", 4.0, 16.0, 11.0, step=0.1, key="hb"
        )
        height_cm = st.number_input(
            "Height (cm)", 120.0, 190.0, 155.0, step=0.1, key="height"
        )

    with col2:
        weight_pw1 = st.number_input(
            "Weight PW1 (kg)", 30.0, 120.0, 50.0, step=0.1, key="w1"
        )
        weight_pw2 = st.number_input(
            "Weight PW2 (kg)", 30.0, 120.0, 52.0, step=0.1, key="w2"
        )

    with col3:
        weight_pw3 = st.number_input(
            "Weight PW3 (kg)", 0.0, 120.0, 0.0, step=0.1, key="w3"
        )
        weight_pw4 = st.number_input(
            "Weight PW4 (kg)", 0.0, 120.0, 0.0, step=0.1, key="w4"
        )

    anc_completed = st.number_input(
        "Number of ANCs Completed", 0, 10, 2, key="anc"
    )

    tt_injection = st.selectbox(
        "TT Injection given in last ANC?",
        ["Yes", "No"],
        key="tt"
    )

    # --------------------------------------------------
    # SECTION C — NUTRITION INTAKE
    # --------------------------------------------------
    st.subheader("🥗 Nutrition Intake (Last 1 Month)")

    col1, col2, col3 = st.columns(3)

    with col1:
        ifa_tabs = st.number_input(
            "IFA Tablets Received", 0, 120, 30, key="ifa"
        )

    with col2:
        calcium_tabs = st.number_input(
            "Calcium Tablets Consumed", 0, 120, 30, key="calcium"
        )

    with col3:
        food_group = st.selectbox(
            "Food Group Category",
            [1, 2, 3, 4, 5],
            key="food"
        )

    # --------------------------------------------------
    # SECTION D — BEHAVIOURAL FACTORS
    # --------------------------------------------------
    st.subheader("🚬 Behavioural Factors")

    col1, col2, col3 = st.columns(3)

    with col1:
        consume_tobacco = st.selectbox(
            "Consumes Tobacco?", ["No", "Yes"], key="tobacco"
        )

    with col2:
        chewing_tobacco = st.selectbox(
            "Currently Chewing Tobacco?", ["No", "Yes"], key="chew"
        )

    with col3:
        consume_alcohol = st.selectbox(
            "Consumes Alcohol?", ["No", "Yes"], key="alcohol"
        )

    # --------------------------------------------------
    # SECTION E — HOUSEHOLD & ACCESS
    # --------------------------------------------------
    st.subheader("🏠 Household & Access")

    col1, col2, col3 = st.columns(3)

    with col1:
        toilet_type_clean = st.selectbox(
            "Improved Toilet Facility?", ["Yes", "No"], key="toilet"
        )

    with col2:
        water_source_clean = st.selectbox(
            "Improved Water Source?", ["Yes", "No"], key="water"
        )

    with col3:
        social_media = st.selectbox(
            "Social Media Exposure?", ["Yes", "No"], key="social"
        )

    st.markdown("**Household Assets (select all that apply)**")
    assets = st.multiselect(
        "",
        [
            "Electricity",
            "Television",
            "Refrigerator",
            "Mobile Phone",
            "Two-wheeler",
            "Four-wheeler"
        ],
        key="assets"
    )

    # --------------------------------------------------
    # SECTION F — REGISTRATION & DATES
    # --------------------------------------------------
    st.subheader("📅 Registration & Dates")

    col1, col2, col3 = st.columns(3)

    with col1:
        lmp_date = st.date_input(
            "LMP Date", datetime.date(2024, 1, 1), key="lmp"
        )

    with col2:
        registration_date = st.date_input(
            "Registration Date", datetime.date(2024, 2, 1), key="reg"
        )

    with col3:
        last_anc_date = st.date_input(
            "Last ANC Date (if available)",
            value=None,
            key="last_anc"
        )

    # --------------------------------------------------
    # SECTION G — SCHEME EXPOSURE
    # --------------------------------------------------
    st.subheader("💰 Scheme Exposure")

    col1, col2, col3 = st.columns(3)

    with col1:
        pmmvy_count = st.number_input(
            "PMMVY Installments Received", 0, 3, 0, key="pmmvy"
        )

    with col2:
        jsy_count = st.number_input(
            "JSY Installments Received", 0, 2, 0, key="jsy"
        )

    with col3:
        jsy_registered = st.selectbox(
            "Registered for JSY?", ["No", "Yes"], key="jsy_reg"
        )

    rajhshri_registered = st.selectbox(
        "Registered for RAJHSRI?", ["No", "Yes"], key="raj"
    )

    # --------------------------------------------------
    # SUBMIT
    # --------------------------------------------------
    submitted = st.form_submit_button("🔍 Predict LBW Risk")

# =========================
# FORM SUBMISSION
# =========================
if submitted:

    payload = {
        "beneficiary_age": beneficiary_age,
        "parity": parity,
        "living_children": living_children,
        "education_clean": education_clean,
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
        "social_media": social_media,
        "household_assets": assets,
        "lmp_date": str(lmp_date),
        "registration_date": str(registration_date),
        "last_anc_date": str(last_anc_date) if last_anc_date else None,
        "pmmvy_count": pmmvy_count,
        "jsy_count": jsy_count,
        "jsy_registered": jsy_registered,
        "rajhshri_registered": rajhshri_registered
    }

    with st.spinner("Predicting LBW risk..."):
        response = requests.post(API_URL, json=payload)

    if response.status_code != 200:
        st.error("Prediction failed. Please check backend logs.")
    else:
        result = response.json()
        st.success(f"🧠 LBW Risk Probability: **{result['risk_probability']:.2f}**")
        st.info(result["risk_label"])
