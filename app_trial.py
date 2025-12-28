import streamlit as st
import pandas as pd
import numpy as np
import json
import joblib
import math
from datetime import datetime, date

# =========================
# GOOGLE SHEETS
# =========================
import gspread
from google.oauth2.service_account import Credentials

GSHEET_ID = "12qNktlRnQHFHujGwnCX15YW1UsQHtMzgNyRWzq1Qbsc"
GSHEET_WORKSHEET = "LBWScores"

def get_gsheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(creds)
    return client.open_by_key(GSHEET_ID).worksheet(GSHEET_WORKSHEET)


def make_json_safe(v):
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return ""
    return v


# =========================
# LOAD MODEL & ARTIFACTS
# =========================
from preprocessing import preprocess_for_model

model = joblib.load("artifacts/xgb_model.pkl")

with open("artifacts/features.json") as f:
    FEATURES_ORDER = json.load(f)


# =========================
# STREAMLIT CONFIG
# =========================
st.set_page_config(page_title="LBW Risk Predictor", layout="wide")
st.title("📋 LBW Risk – Beneficiary Entry")

# =========================
# SESSION TIMER
# =========================
if "form_start_time" not in st.session_state:
    st.session_state.form_start_time = datetime.now()


# =========================
# IDENTIFICATION
# =========================
st.header("👩‍🍼 Identification")

c1, c2, c3 = st.columns(3)
with c1:
    beneficiary_name = st.text_input("Beneficiary Name")
with c2:
    state = st.text_input("State")
with c3:
    district = st.text_input("District")

c1, c2 = st.columns(2)
with c1:
    block = st.text_input("Block")
with c2:
    village = st.text_input("Village")


# =========================
# PHYSIOLOGICAL
# =========================
st.header("🩺 Physiological")

c1, c2, c3 = st.columns(3)
with c1:
    beneficiary_age = st.number_input("Beneficiary age", 14, 60, 18)
with c2:
    parity = st.number_input("Child order/parity", 0, 10, 0)
with c3:
    living_children = st.number_input("Number of living child at now", 0, 10, 0)

month_conception = st.selectbox(
    "MonthConception",
    ["January","February","March","April","May","June",
     "July","August","September","October","November","December"]
)

hb_value = st.number_input("Measured Hb (g/dL)", 3.0, 18.0, 11.0)

if hb_value < 6:
    measured_HB_risk_bin = "severe_anaemia"
elif hb_value < 8:
    measured_HB_risk_bin = "moderate_anaemia"
elif hb_value < 11:
    measured_HB_risk_bin = "mild_anaemia"
else:
    measured_HB_risk_bin = "normal"

st.info(f"🧪 Hb Category: **{measured_HB_risk_bin}**")


# =========================
# ANC & BMI
# =========================
st.header("🏥 ANC & BMI")

height_cm = st.number_input("Height (cm)", 120.0, 200.0, 150.0)
height_m = height_cm / 100

BMI_PW1_Prog = st.number_input("BMI PW1", value=np.nan)
BMI_PW2_Prog = st.number_input("BMI PW2", value=np.nan)
BMI_PW3_Prog = st.number_input("BMI PW3", value=np.nan)
BMI_PW4_Prog = st.number_input("BMI PW4", value=np.nan)

anc_completed = st.number_input("No of ANCs completed", 0, 6, 0)

ANCBucket = st.selectbox("ANCBucket", ["Early", "Mid", "Late"])
RegistrationBucket = st.selectbox("RegistrationBucket", ["Early", "Mid", "Late"])

counselling_gap_days = st.number_input("Counselling gap days", value=np.nan)

tt_given = st.selectbox(
    "TT Injection given",
    options=[0, 1, 9999],
    format_func=lambda x: {0:"No",1:"Yes",9999:"Don't Know"}[x]
)


# =========================
# NUTRITION
# =========================
st.header("🥗 Nutrition")

ifa_tabs = st.number_input("IFA tablets last month", 0)
calcium_tabs = st.number_input("Calcium tablets last month", 0)

ifa_tabs_log1p = round(math.log1p(ifa_tabs), 4)
calcium_tabs_log1p = round(math.log1p(calcium_tabs), 4)

Food_Groups_Category = st.selectbox("Food Groups Category", [0,1,2,3,4,5])


# =========================
# SES
# =========================
st.header("🏠 SES")

toilet_type_clean = st.selectbox(
    "Toilet type",
    ["Improved toilet","Pit latrine (basic)",
     "Unimproved / unknown","No facility / open defecation"]
)

water_source_clean = st.selectbox(
    "Water source",
    ["Piped supply (home/yard/stand)",
     "Groundwater – handpump/borewell",
     "Protected well",
     "Surface/Unprotected source",
     "Delivered / other"]
)

education_clean = st.selectbox(
    "Education",
    ["No schooling","Primary (1–5)","Middle (6–8)",
     "Secondary (9–12)","Graduate & above"]
)

Household_Assets_Score_log1p = st.number_input(
    "Household Assets Score (log1p)", value=0.0
)


# =========================
# SOCIAL MEDIA
# =========================
st.header("📱 Social Media")

Social_Media_Category = st.selectbox(
    "Social Media Category",
    ["None","Low","Medium","High"]
)

Type_of_Social_Media_Enrolled_In = st.text_input(
    "Type of Social Media Enrolled In"
)


# =========================
# SCHEMES
# =========================
st.header("💰 Schemes")

jsy_reg = st.selectbox("Registered for JSY", ["No","Yes"])
rajhsri_reg = st.selectbox("Registered for RAJHSRI", ["No","Yes"])

pmmvy_inst = st.number_input("PMMVY installments", 0, 3, 0)
jsy_inst = st.number_input("JSY installments", 0, 3, 0)

LMPtoINST1 = st.number_input("LMPtoINST1", value=np.nan)
LMPtoINST2 = st.number_input("LMPtoINST2", value=np.nan)
LMPtoINST3 = st.number_input("LMPtoINST3", value=np.nan)


# =========================
# PREDICT & SAVE
# =========================
if st.button("Predict Score"):
    form_end_time = datetime.now()

    record = {
        # Identification
        "Beneficiary Name": beneficiary_name,
        "State": state,
        "District": district,
        "Block": block,
        "Village": village,

        # Model features
        "Beneficiary age": beneficiary_age,
        "measured_HB_risk_bin": measured_HB_risk_bin,
        "Child order/parity": parity,
        "Number of living child at now": living_children,
        "MonthConception": month_conception,
        "BMI_PW1_Prog": BMI_PW1_Prog,
        "BMI_PW2_Prog": BMI_PW2_Prog,
        "BMI_PW3_Prog": BMI_PW3_Prog,
        "BMI_PW4_Prog": BMI_PW4_Prog,
        "consume_tobacco": None,
        "Status of current chewing of tobacco": None,
        "consume_alcohol": None,
        "RegistrationBucket": RegistrationBucket,
        "counselling_gap_days": counselling_gap_days,
        "ANCBucket": ANCBucket,
        "LMPtoINST1": LMPtoINST1,
        "LMPtoINST2": LMPtoINST2,
        "LMPtoINST3": LMPtoINST3,
        "No of ANCs completed": anc_completed,
        "Service received during last ANC: TT Injection given": tt_given,
        "No. of IFA tablets received/procured in last one month_log1p": ifa_tabs_log1p,
        "No. of calcium tablets consumed in last one month_log1p": calcium_tabs_log1p,
        "Food_Groups_Category": Food_Groups_Category,
        "Household_Assets_Score_log1p": Household_Assets_Score_log1p,
        "toilet_type_clean": toilet_type_clean,
        "water_source_clean": water_source_clean,
        "education_clean": education_clean,
        "Social_Media_Category": Social_Media_Category,
        "Registered for cash transfer scheme: JSY": jsy_reg,
        "Registered for cash transfer scheme: RAJHSRI": rajhsri_reg,
        "PMMVY-Number of installment received": pmmvy_inst,
        "JSY-Number of installment received": jsy_inst,

        # Audit
        "Type of Social Media Enrolled In": Type_of_Social_Media_Enrolled_In,
        "form_start_time": st.session_state.form_start_time.isoformat(),
        "form_end_time": form_end_time.isoformat(),
        "form_duration_seconds": int(
            (form_end_time - st.session_state.form_start_time).total_seconds()
        ),
    }

    # Model input
    X_raw = pd.DataFrame([{k: record.get(k, None) for k in FEATURES_ORDER}])
    X_processed = preprocess_for_model(X_raw)

    lbw_prob = float(model.predict_proba(X_processed)[0][1])
    lbw_percent = round(lbw_prob * 100, 2)

    record["lbw_prob"] = lbw_prob
    record["lbw_percent"] = lbw_percent

    st.metric("Predicted LBW Risk", f"{lbw_percent}%")

    # Save to Google Sheet
    worksheet = get_gsheet()
    headers = [h.strip() for h in worksheet.row_values(1)]
    row = [make_json_safe(record.get(h, "")) for h in headers]
    worksheet.append_row(row, value_input_option="USER_ENTERED")

    st.success("✅ Saved & Predicted Successfully")
