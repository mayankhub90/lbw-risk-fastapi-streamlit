import streamlit as st
import requests
import datetime

st.set_page_config(page_title="LBW Risk Assessment", layout="wide")
st.title("🤰 Low Birth Weight (LBW) Risk Assessment")

API_URL = "http://localhost:8000/predict"  # change after deploy

with st.form("lbw_form", clear_on_submit=True):

    # ===============================
    # A. Beneficiary Background
    # ===============================
    st.subheader("🧍 Beneficiary Background")

    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.number_input("Beneficiary Age (years)", 15, 49, 25)
        parity = st.number_input("Child order / parity", 0, 6, 1)

    with c2:
        living_children = st.number_input("Number of living children", 0, 6, 1)
        education = st.selectbox(
            "Education level",
            ["No schooling", "Primary (1–5)", "Middle (6–8)", "Secondary (9–12)", "Graduate & above"]
        )

    with c3:
        month_conception = st.selectbox("Month of conception", list(range(1, 13)))

    # ===============================
    # B. Registration & Dates
    # ===============================
    st.subheader("📅 Registration & Dates")

    c1, c2 = st.columns(2)
    with c1:
        lmp_date = st.date_input("LMP Date", datetime.date(2024, 1, 1))
    with c2:
        registration_date = st.date_input("Registration Date", datetime.date(2024, 2, 1))

    # ===============================
    # C. Clinical & Anthropometry
    # ===============================
    st.subheader("🩺 Clinical & Anthropometry")

    c1, c2, c3 = st.columns(3)
    with c1:
        hb = st.number_input("Hemoglobin (g/dL)", 4.0, 16.0, 11.0, step=0.1)
        height_cm = st.number_input("Height (cm)", 120.0, 190.0, 155.0)

    with c2:
        anc_completed = st.number_input("Number of ANCs completed", 0, 6, 2)
        tt_given = st.selectbox("TT injection given in last ANC?", ["Yes", "No"])

    with c3:
        weight_pw1 = st.number_input("Weight PW1 (kg)", 0.0, 120.0, 50.0) if anc_completed >= 1 else None
        weight_pw2 = st.number_input("Weight PW2 (kg)", 0.0, 120.0, 52.0) if anc_completed >= 2 else None
        weight_pw3 = st.number_input("Weight PW3 (kg)", 0.0, 120.0, 0.0) if anc_completed >= 3 else None
        weight_pw4 = st.number_input("Weight PW4 (kg)", 0.0, 120.0, 0.0) if anc_completed >= 4 else None

    # ===============================
    # D. Nutrition Intake
    # ===============================
    st.subheader("🥗 Nutrition Intake (last one month)")

    c1, c2, c3 = st.columns(3)
    with c1:
        food_group = st.selectbox("Food Groups Category", [1, 2, 3, 4, 5])
    with c2:
        ifa_tabs = st.number_input("IFA tablets consumed", 0, 120, 30)
    with c3:
        calcium_tabs = st.number_input("Calcium tablets consumed", 0, 120, 30)

    # ===============================
    # E. Behavioural Factors
    # ===============================
    st.subheader("🚬 Behavioural Factors")

    c1, c2, c3 = st.columns(3)
    with c1:
        consume_tobacco = st.selectbox("Consumes tobacco?", ["No", "Yes"])
    with c2:
        chewing_tobacco = st.selectbox("Chewing tobacco?", ["No", "Yes"])
    with c3:
        consume_alcohol = st.selectbox("Consumes alcohol?", ["No", "Yes"])

    # ===============================
    # F. Household & Access
    # ===============================
    st.subheader("🏠 Household & Access")

    c1, c2, c3 = st.columns(3)
    with c1:
        washing_machine = st.selectbox("Washing machine available?", ["No", "Yes"])
        ac_cooler = st.selectbox("Air conditioner / cooler available?", ["No", "Yes"])

    with c2:
        toilet_type = st.selectbox(
            "Toilet facility",
            [
                "Improved toilet",
                "Pit latrine (basic)",
                "Unimproved / unknown",
                "No facility / open defecation"
            ]
        )

    with c3:
        water_source = st.selectbox(
            "Main drinking water source",
            [
                "Piped supply (home/yard/stand)",
                "Groundwater – handpump/borewell",
                "Protected well",
                "Surface/Unprotected source",
                "Delivered / other"
            ]
        )

    social_media = st.selectbox("Exposure to social media?", ["No", "Yes"])

    # ===============================
    # G. Scheme Exposure
    # ===============================
    st.subheader("💰 Scheme Exposure")

    c1, c2, c3 = st.columns(3)
    with c1:
        pmmvy = st.number_input("PMMVY installments received", 0, 3, 0)
    with c2:
        jsy = st.number_input("JSY installments received", 0, 2, 0)
    with c3:
        jsy_reg = st.selectbox("Registered under JSY?", ["No", "Yes"])
        raj_reg = st.selectbox("Registered under RAJHSRI?", ["No", "Yes"])

    submitted = st.form_submit_button("🔍 Predict LBW Risk")

# ===============================
# SUBMIT
# ===============================
if submitted:
    payload = {
        "beneficiary_age": age,
        "parity": parity,
        "living_children": living_children,
        "education_clean": education,
        "month_conception": month_conception,
        "lmp_date": str(lmp_date),
        "registration_date": str(registration_date),
        "hemoglobin": hb,
        "height_cm": height_cm,
        "anc_completed": anc_completed,
        "tt_given": tt_given,
        "weight_pw1": weight_pw1,
        "weight_pw2": weight_pw2,
        "weight_pw3": weight_pw3,
        "weight_pw4": weight_pw4,
        "food_group": food_group,
        "ifa_tabs": ifa_tabs,
        "calcium_tabs": calcium_tabs,
        "consume_tobacco": consume_tobacco,
        "chewing_tobacco": chewing_tobacco,
        "consume_alcohol": consume_alcohol,
        "washing_machine": washing_machine,
        "ac_cooler": ac_cooler,
        "toilet_type_clean": toilet_type,
        "water_source_clean": water_source,
        "social_media": social_media,
        "pmmvy_count": pmmvy,
        "jsy_count": jsy,
        "jsy_registered": jsy_reg,
        "raj_registered": raj_reg
    }

    with st.spinner("Predicting risk..."):
        res = requests.post(API_URL, json=payload)

    if res.status_code != 200:
        st.error("Prediction failed. Check backend logs.")
    else:
        out = res.json()
        st.success(f"LBW Risk Probability: {out['risk_probability']:.2f}")
        st.info(out["risk_label"])
