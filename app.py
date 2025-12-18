# app.py
import streamlit as st
import json, joblib, pandas as pd
import shap
from preprocessing import preprocess_payload

# -------------------------
# Load artifacts
# -------------------------

@st.cache_resource
def load_artifacts():
    model = joblib.load("artifacts/xgb_model.json")
    features = json.load(open("artifacts/features.json"))
    background = pd.read_csv("artifacts/background.csv")
    return model, features, background

model, FEATURES, BACKGROUND = load_artifacts()

st.set_page_config(page_title="LBW Risk Predictor", layout="wide")
st.title("🤰 Low Birth Weight (LBW) Risk Assessment")

# =========================
# FORM
# =========================
with st.form("lbw_form"):

    st.subheader("👩 Beneficiary Background")
    age = st.number_input("Beneficiary age", 15, 45, 25)
    living = st.number_input("Number of living children", 0, 6, 0)
    prev_preg = st.number_input("Previous pregnancies (incl. miscarriage)", living, 10, max(living, 1))
    month = st.selectbox("Month of conception", list(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]))
    education = st.selectbox("Education", ["No schooling","Primary (1–5)","Middle (6–8)","Secondary (9–12)","Graduate & above"])
    social_media = st.selectbox("Social media exposure", ["Yes","No"])

    st.subheader("🩺 Clinical & Anthropometry")
    hb = st.number_input("Hemoglobin (g/dL)", 4.0, 16.0, 11.0)
    height = st.number_input("Height (cm)", 120, 200, 155)
    anc = st.number_input("No of ANCs completed", 0, 10, 2)

    weights = {}
    for i in range(1, min(anc,4)+1):
        weights[f"weight_pw{i}"] = st.number_input(f"Weight PW{i} (kg)", 30.0, 100.0, 50.0)

    st.subheader("🥗 Nutrition & Behaviour")
    food = st.selectbox("Food Group Category", [1,2,3,4,5])
    ifa = st.number_input("IFA tablets (last month)", 0, 120, 30)
    calcium = st.number_input("Calcium tablets (last month)", 0, 120, 30)
    tobacco = st.selectbox("Consumes tobacco", ["Yes","No"])
    chew = st.selectbox("Chews tobacco", ["Yes","No"])
    alcohol = st.selectbox("Consumes alcohol", ["Yes","No"])

    st.subheader("🏥 Registration & Services")
    days_reg = st.number_input("Days from LMP to registration", 0, 300, 45)
    counselling = st.number_input("Counselling visits", 0, 10, 2)
    tt = st.selectbox("TT injection received", ["Yes","No"])

    st.subheader("🏠 Household & Schemes")
    toilet = st.selectbox("Toilet facility", ["Improved toilet","Pit latrine (basic)","Unimproved / unknown","No facility / open defecation"])
    water = st.selectbox("Water source", ["Piped supply (home/yard/stand)","Groundwater – handpump/borewell","Protected well","Surface/Unprotected source","Delivered / other"])
    wm = st.checkbox("Washing machine")
    ac = st.checkbox("AC / Cooler")
    phone = st.checkbox("Mobile phone")

    jsy = st.selectbox("Registered for JSY", ["Yes","No"])
    jsy_inst = st.number_input("JSY installments", 0, 2, 0)
    raj = st.selectbox("Registered for RAJHSRI", ["Yes","No"])
    pmmvy_inst = st.number_input("PMMVY installments", 0, 3, 0)

    submit = st.form_submit_button("🔍 Predict LBW Risk")

# =========================
# PREDICTION
# =========================
if submit:
    payload = {
        "Beneficiary age": age,
        "Number of living child at now": living,
        "previous_pregnancies": prev_preg,
        "month_conception": month,
        "education_clean": education,
        "Social_Media_Category": social_media,
        "measured_HB": hb,
        "height": height,
        "No of ANCs completed": anc,
        "Food_Groups_Category": food,
        "ifa_tablets": ifa,
        "calcium_tablets": calcium,
        "consume_tobacco": tobacco,
        "Status of current chewing of tobacco": chew,
        "consume_alcohol": alcohol,
        "days_lmp_to_registration": days_reg,
        "counselling_visits": counselling,
        "Service received during last ANC: TT Injection given": tt,
        "toilet_type_clean": toilet,
        "water_source_clean": water,
        "Registered for cash transfer scheme: JSY": jsy,
        "Registered for cash transfer scheme: RAJHSRI": raj,
        "PMMVY-Number of installment received": pmmvy_inst,
        "JSY-Number of installment received": jsy_inst,
        "has_washing_machine": wm,
        "has_ac_cooler": ac,
        "has_mobile": phone,
        **weights
    }

    X = preprocess_payload(payload, FEATURES)
    prob = model.predict_proba(X)[0,1]

    st.success(f"LBW Risk Probability: {prob:.2f}")
