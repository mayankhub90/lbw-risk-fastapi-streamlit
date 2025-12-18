# frontend/app.py
import streamlit as st
import requests
import pandas as pd

API_URL = "https://lbw-fastapi.onrender.com/predict" # local testing
# API_URL = "https://<your-backend-url>/predict"  # later for cloud

st.set_page_config(page_title="LBW Risk Predictor", layout="wide")
st.title("🤰 Low Birth Weight (LBW) Risk Assessment")

st.markdown(
    """
    Enter beneficiary details.  
    The system will **automatically derive clinical & programmatic indicators**
    and predict LBW risk.
    """
)

# ===============================
# FORM
# ===============================
with st.form("lbw_form"):

    # -------------------------
    # Section 1: Background
    # -------------------------
    st.subheader("👩 Beneficiary Background")

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input("Beneficiary age (years)", 15, 45, 25)
        living_children = st.number_input("Number of living children", 0, 6, 0)
        previous_pregnancies = st.number_input(
            "Previous pregnancies (incl. miscarriage/abortion)",
            min_value=living_children,
            max_value=10,
            value=max(living_children, 1)
        )

    with col2:
        month_conception = st.selectbox(
            "Month of conception",
            ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        )
        education = st.selectbox(
            "Education level",
            [
                "No schooling",
                "Primary (1–5)",
                "Middle (6–8)",
                "Secondary (9–12)",
                "Graduate & above"
            ]
        )

    with col3:
        toilet = st.selectbox(
            "Toilet facility",
            [
                "Improved toilet",
                "Pit latrine (basic)",
                "Unimproved / unknown",
                "No facility / open defecation"
            ]
        )
        water = st.selectbox(
            "Main source of drinking water",
            [
                "Piped supply (home/yard/stand)",
                "Groundwater – handpump/borewell",
                "Protected well",
                "Surface/Unprotected source",
                "Delivered / other"
            ]
        )

    # -------------------------
    # Section 2: Clinical & Anthropometry
    # -------------------------
    st.subheader("🩺 Clinical & Anthropometry")

    col1, col2, col3 = st.columns(3)

    with col1:
        hb = st.number_input("Hemoglobin (g/dL)", 4.0, 16.0, 11.0)
        height = st.number_input("Height (cm)", 120, 200, 155)

    with col2:
        anc_count = st.number_input("No. of ANC visits completed", 0, 10, 2)

    with col3:
        weight_pw1 = st.number_input("Weight at PW1 (kg)", 30.0, 100.0, 50.0)
        weight_pw2 = st.number_input("Weight at PW2 (kg)", 30.0, 100.0, 52.0)
        weight_pw3 = st.number_input("Weight at PW3 (kg)", 30.0, 100.0, 54.0)
        weight_pw4 = st.number_input("Weight at PW4 (kg)", 30.0, 100.0, 56.0)

    # -------------------------
    # Section 3: Nutrition & Behaviour
    # -------------------------
    st.subheader("🥗 Nutrition & Behaviour")

    col1, col2, col3 = st.columns(3)

    with col1:
        food_group = st.selectbox("Food Group Category", [1, 2, 3, 4, 5])
        ifa_tabs = st.number_input(
            "IFA tablets consumed in last 1 month",
            0, 120, 30
        )

    with col2:
        calcium_tabs = st.number_input(
            "Calcium tablets consumed in last 1 month",
            0, 120, 30
        )
        tobacco = st.selectbox("Consumes tobacco?", ["No", "Yes"])

    with col3:
        chewing = st.selectbox("Chews tobacco?", ["No", "Yes"])
        alcohol = st.selectbox("Consumes alcohol?", ["No", "Yes"])

    # -------------------------
    # Section 4: Program & Dates
    # -------------------------
    st.subheader("🏥 Program & Registration")

    col1, col2, col3 = st.columns(3)

    with col1:
        days_lmp_to_registration = st.number_input(
            "Days from LMP to registration",
            0, 300, 45
        )

    with col2:
        counselling_visits = st.number_input(
            "No. of counselling visits",
            0, 10, 2
        )

    with col3:
        tt = st.selectbox("TT injection received in last ANC?", ["No", "Yes"])

    # -------------------------
    # Section 5: Schemes & Assets
    # -------------------------
    st.subheader("💰 Schemes & Household Assets")

    col1, col2, col3 = st.columns(3)

    with col1:
        jsy = st.selectbox("Registered for JSY?", ["No", "Yes"])
        jsy_inst = st.number_input("JSY installments received", 0, 2, 0)

    with col2:
        pmmvy = st.selectbox("Registered for PMMVY?", ["No", "Yes"])
        pmmvy_inst = st.number_input("PMMVY installments received", 0, 3, 0)

    with col3:
        wm = st.checkbox("Household has washing machine")
        ac = st.checkbox("Household has AC/Cooler")
        phone = st.checkbox("Household has mobile phone")

    submit = st.form_submit_button("🔍 Predict LBW Risk")

# ===============================
# API CALL
# ===============================
if submit:
    payload = {
        "Beneficiary age": age,
        "living_children": living_children,
        "previous_pregnancies": previous_pregnancies,
        "month_conception": month_conception,
        "education_clean": education,
        "toilet_type_clean": toilet,
        "water_source_clean": water,
        "measured_HB": hb,
        "height": height,
        "No of ANCs completed": anc_count,
        "weight_pw1": weight_pw1,
        "weight_pw2": weight_pw2,
        "weight_pw3": weight_pw3,
        "weight_pw4": weight_pw4,
        "Food_Groups_Category": food_group,
        "ifa_tablets": ifa_tabs,
        "calcium_tablets": calcium_tabs,
        "consume_tobacco": tobacco,
        "Status of current chewing of tobacco": chewing,
        "consume_alcohol": alcohol,
        "days_lmp_to_registration": days_lmp_to_registration,
        "counselling_visits": counselling_visits,
        "Service received during last ANC: TT Injection given": tt,
        "Registered for cash transfer scheme: JSY": jsy,
        "JSY-Number of installment received": jsy_inst,
        "Registered for cash transfer scheme: RAJHSRI": pmmvy,
        "PMMVY-Number of installment received": pmmvy_inst,
        "has_washing_machine": wm,
        "has_ac_cooler": ac,
        "has_mobile": phone
    }

    with st.spinner("Predicting LBW risk..."):
        res = requests.post(API_URL, json=payload)

    if res.status_code != 200:
        st.error("Prediction failed. Check backend logs.")
    else:
        out = res.json()

        st.success(f"LBW Risk Probability: **{out['risk_probability']:.2f}**")
        st.info(out["risk_label"])

        st.subheader("🔎 Key Risk Drivers")
        st.bar_chart(
            pd.DataFrame(out["top_drivers"]).set_index("feature")
        )
