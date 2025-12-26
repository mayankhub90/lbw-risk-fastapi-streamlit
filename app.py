import streamlit as st
import pandas as pd
import math
import os
from datetime import datetime, date
import json
import joblib
import numpy as np

# ================= GOOGLE SHEET SETUP =================
import gspread
from google.oauth2.service_account import Credentials

# 🔴 REPLACE THIS WITH YOUR ACTUAL SPREADSHEET ID
GSHEET_ID = "12qNktlRnQHFHujGwnCX15YW1UsQHtMzgNyRWzq1Qbsc"
GSHEET_WORKSHEET = "LBWScores"

def get_gsheet(spreadsheet_id=GSHEET_ID, worksheet_name=GSHEET_WORKSHEET):
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet(worksheet_name)
    return worksheet

# =========================
# LOAD MODEL & FEATURES
# =========================
from preprocessing import preprocess_for_model
import json
import joblib

model = joblib.load("artifacts/xgb_model.pkl")

with open("artifacts/feature_order.json") as f:
    feature_order = json.load(f)


# =====================================================
# APP CONFIG
# =====================================================
st.set_page_config(page_title="LBW Risk – Data Entry", layout="wide")
st.title("📋 Beneficiary Data Entry Form")

CSV_PATH = "beneficiary_records.csv"

#JSON safe Values
def make_json_safe(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if value is None:
        return ""
    return value



# =====================================================
# SESSION: FORM START TIME
# =====================================================
if "form_start_time" not in st.session_state:
    st.session_state.form_start_time = datetime.now()

# =====================================================
# LOAD EXISTING DATA (EDIT MODE)
# =====================================================
if os.path.exists(CSV_PATH):
    existing_df = pd.read_csv(CSV_PATH)
else:
    existing_df = pd.DataFrame()

edit_mode = st.checkbox("✏️ Edit existing beneficiary")

selected_index = None
selected_record = {}

if edit_mode and not existing_df.empty:
    selected_index = st.selectbox(
        "Select beneficiary to edit",
        existing_df.index,
        format_func=lambda x: f"{existing_df.loc[x, 'Beneficiary Name']} | {existing_df.loc[x, 'Village']}"
    )
    selected_record = existing_df.loc[selected_index].to_dict()

def get_val(key, default=None):
    return selected_record.get(key, default) if edit_mode else default

# =====================================================
# 🤰 IDENTIFICATION DETAILS
# =====================================================
st.header("🤰 Identification Details")

STATE_DISTRICT_MAP = {
       "Karnataka": ["Bengaluru Urban", "Mysuru", "Tumkur"],
  }

states_sorted = sorted(STATE_DISTRICT_MAP.keys())

c1, c2, c3 = st.columns(3)
with c1:
    beneficiary_name = st.text_input("Beneficiary Name", get_val("Beneficiary Name", ""))
with c2:
    state = st.selectbox("State", states_sorted,
                         index=states_sorted.index(get_val("State", states_sorted[0])))
with c3:
    district = st.selectbox(
        "District",
        sorted(STATE_DISTRICT_MAP[state]),
        index=sorted(STATE_DISTRICT_MAP[state]).index(
            get_val("District", sorted(STATE_DISTRICT_MAP[state])[0])
        )
    )

c1, c2 = st.columns(2)
with c1:
    block = st.text_input("Block", get_val("Block", ""))
with c2:
    village = st.text_input("Village", get_val("Village", ""))

# =====================================================
# 🩺 PHYSIOLOGICAL DETAILS
# =====================================================
st.header("🩺 Physiological & Demographic Details")

c1, c2, c3 = st.columns(3)
with c1:
    beneficiary_age = st.number_input("Beneficiary age (years)", 14, 60,
                                      value=int(get_val("Beneficiary age", 18)))
with c2:
    height_cm = st.number_input("Height (cm)", 120.0, 200.0,
                                value=float(get_val("height", 150)))
with c3:
    hb_value = st.number_input("Measured Hb (g/dL)", 3.0, 18.0,
                               value=float(get_val("hb_value", 11)))

# ---- Hb risk bin (DERIVED + DISPLAYED) ----
if hb_value < 6:
    measured_HB_risk_bin = "severe_anaemia"
elif hb_value < 8:
    measured_HB_risk_bin = "moderate_anaemia"
elif hb_value < 11:
    measured_HB_risk_bin = "mild_anaemia"
else:
    measured_HB_risk_bin = "normal"

st.info(f"🧪 **Measured Hb Risk Category:** {measured_HB_risk_bin}")

c1, c2 = st.columns(2)
with c1:
    parity = st.number_input("Child order/parity", 0, 10,
                             value=int(get_val("Child order/parity", 0)))
with c2:
    living_children = st.number_input("Number of living child at now", 0, 10,
                                      value=int(get_val("Number of living child at now", 0)))

month_conception = st.selectbox(
    "Month of Conception",
    ["January","February","March","April","May","June",
     "July","August","September","October","November","December"],
    index=["January","February","March","April","May","June",
           "July","August","September","October","November","December"]
           .index(get_val("MonthConception", "January"))
)

# =====================================================
# 🤰 PREGNANCY & REGISTRATION DETAILS
# =====================================================
st.header("🤰 Pregnancy & Registration Details")

c1, c2 = st.columns(2)
with c1:
    lmp_date = st.date_input(
        "Last Menstrual Period (LMP)",
        value=pd.to_datetime(get_val("LMP", date.today()))
    )
with c2:
    registration_date = st.date_input(
        "Registration Date",
        value=pd.to_datetime(get_val("Registration Date", date.today()))
    )

# STRICT RULE
if lmp_date >= registration_date:
    st.error("❌ LMP date must be strictly earlier than Registration Date")
    st.stop()

days_gap = (registration_date - lmp_date).days
registration_bucket = (
    "Early" if days_gap < 84 else
    "Mid" if days_gap <= 168 else
    "Late"
)

# =====================================================
# 🏥 ANC & BMI
# =====================================================
st.header("🏥 ANC & Anthropometry (BMI)")

height_m = height_cm / 100 if height_cm else None
anc = {}
anc_dates = []

col_left, col_right = st.columns(2)

def anc_block(i, col):
    with col:
        st.subheader(f"ANC {i}")
        done = st.checkbox(f"ANC {i} Completed", key=f"anc_done_{i}")
        anc[i] = {"done": done, "date": None, "weight": None, "bmi": None}

        if done:
            anc_date = st.date_input(f"ANC {i} Date", key=f"anc_date_{i}")
            anc_weight = st.number_input(
                f"ANC {i} Weight (kg)", 30.0, 120.0,
                key=f"anc_weight_{i}"
            )

            if anc_dates and anc_date < anc_dates[-1]:
                st.error("❌ ANC dates must be chronological")
                st.stop()

            anc_dates.append(anc_date)
            anc[i]["date"] = anc_date
            anc[i]["weight"] = anc_weight
            anc[i]["bmi"] = round(anc_weight / (height_m ** 2), 2)

anc_block(1, col_left)
anc_block(2, col_left)
anc_block(3, col_right)
anc_block(4, col_right)

# ANC 1 vs ANC 3 rule
if anc.get(1, {}).get("done") and anc.get(3, {}).get("done"):
    if anc[1]["date"] == anc[3]["date"]:
        st.error("❌ ANC 1 and ANC 3 dates must differ by at least 1 day")
        st.stop()

BMI_PW1_Prog = anc[1]["bmi"] if anc[1]["done"] else None
BMI_PW2_Prog = anc[2]["bmi"] if anc[2]["done"] else None
BMI_PW3_Prog = anc[3]["bmi"] if anc[3]["done"] else None
BMI_PW4_Prog = anc[4]["bmi"] if anc[4]["done"] else None

anc_completed = sum(1 for a in anc.values() if a["done"])

#TT Injection 

TT_MAP = {
    "Yes": 1,
    "No": 0,
    "Don't Know": 9999
}

tt_label = st.selectbox(
    "TT Injection given in last ANC",
    options=list(TT_MAP.keys())
)

tt_given = TT_MAP[tt_label]

valid_dates = [a["date"] for a in anc.values() if a["done"]]
ANCBucket, counselling_gap_days = None, None

if valid_dates:
    first_anc = min(valid_dates)
    gap = (first_anc - lmp_date).days
    ANCBucket = "Early" if gap < 84 else "Mid" if gap <= 168 else "Late"

if len(valid_dates) >= 2:
    valid_dates.sort()
    counselling_gap_days = (valid_dates[1] - valid_dates[0]).days

# =====================================================
# 🚬 TOBACCO & ALCOHOL
# =====================================================
st.header("🚬 Tobacco & Alcohol")

# ---- Display → Backend mapping ----
YN_MAP = {
    "No": "N",
    "Yes": "Y",
    "Other": "O"
}

# ---- Tobacco ----
consume_tobacco_ui = st.selectbox(
    "Consume tobacco?",
    list(YN_MAP.keys())
)
consume_tobacco = YN_MAP[consume_tobacco_ui]   # <-- saved value (N/Y/O)

chewing_status = (
    st.selectbox(
        "Chewing tobacco status",
        ["EVERY DAY", "SOME DAYS", "NOT AT ALL"]
    )
    if consume_tobacco == "Y"
    else None
)

# ---- Alcohol ----
consume_alcohol_ui = st.selectbox(
    "Consume alcohol?",
    list(YN_MAP.keys())
)
consume_alcohol = YN_MAP[consume_alcohol_ui]   # <-- saved value (N/Y/O)


# =====================================================
# 🥗 NUTRITION
# =====================================================
st.header("🥗 Nutrition")

ifa_tabs = st.number_input("IFA tablets last month", min_value=0)
calcium_tabs = st.number_input("Calcium tablets last month", min_value=0)

ifa_tabs_log1p = round(math.log1p(ifa_tabs), 4)
calcium_tabs_log1p = round(math.log1p(calcium_tabs), 4)

food_group = st.selectbox("Food groups consumed", [0,1,2,3,4,5])

# =====================================================
# 🏠 SES
# =====================================================
st.header("🏠 Household & SES")

toilet_type_clean = st.selectbox(
    "Toilet type",
    ["Improved toilet","Pit latrine (basic)",
     "Unimproved / unknown","No facility / open defecation"]
)

water_source_clean = st.selectbox(
    "Water source",
    ["Piped supply","Groundwater – handpump/borewell",
     "Protected well","Surface/Unprotected","Delivered / other"]
)

education_clean = st.selectbox(
    "Education level",
    ["No schooling","Primary (1–5)","Middle (6–8)",
     "Secondary (9–12)","Graduate & above"]
)

# =====================================================
# 🏠 HOUSEHOLD ASSETS
# =====================================================
st.header("🏠 Household Assets")

ASSET_WEIGHTS = {
    "Electricity": 1.0, "Mattress": 0.5, "Pressure Cooker": 0.5,
    "Chair": 0.5, "Cot/Bed": 0.5, "Table": 0.5,
    "Electric Fan": 0.75, "Radio/Transistor": 0.5,
    "B&W Television": 0.5, "Color Television": 1.0,
    "Sewing Machine": 0.75, "Mobile Telephone": 1.0,
    "Internet": 1.25, "Computer": 1.25,
    "Refrigerator": 1.25, "Air Conditioner/Cooler": 1.25,
    "Washing Machine": 1.25, "Bicycle": 0.5,
    "Motorcycle/Scooter": 1.0, "Car": 1.5,
    "Water Pump": 0.75, "Animal": 0.5,
    "Tractor": 1.25, "Thresher": 0.75
}

raw_asset_score = 0
cols = st.columns(3)
for i, (asset, wt) in enumerate(ASSET_WEIGHTS.items()):
    with cols[i % 3]:
        if st.checkbox(asset):
            raw_asset_score += wt

Household_Assets_Score_log1p = round(math.log1p(raw_asset_score), 4)
st.info(f"🏠 Household Assets Score (log1p): **{Household_Assets_Score_log1p}**")

# =====================================================
# 📱 DIGITAL ACCESS & SOCIAL MEDIA
# =====================================================
st.header("📱 Digital Access & Social Media")

social_media_selected = st.multiselect(
    "Social Media Platforms Used",
    ["Facebook", "YouTube", "Instagram", "WhatsApp", "Other"]
)

other_social_media = []
if "Other" in social_media_selected:
    other_input = st.text_input("Specify other social media (comma-separated)")
    if other_input:
        other_social_media = [x.strip() for x in other_input.split(",") if x.strip()]

# ---- Derive counts ----
explicit_count = len([x for x in social_media_selected if x != "Other"])
total_count = explicit_count + len(other_social_media)

# ---- MODEL VARIABLE ----
if total_count == 0:
    Social_Media_Category = "None"
elif total_count == 1:
    Social_Media_Category = "Low"
elif total_count <= 3:
    Social_Media_Category = "Medium"
else:
    Social_Media_Category = "High"

# ---- RAW DETAIL VARIABLE ----
Type_of_Social_Media_Enrolled_In = ",".join(
    [x for x in social_media_selected if x != "Other"] + other_social_media
)


# =====================================================
# 💰 SCHEMES
# =====================================================
st.header("💰 Scheme Participation")

jsy_reg = st.selectbox("Registered for JSY", ["No","Yes"])
rajhsri_reg = st.selectbox("Registered for RAJSHRI", ["No","Yes"])

pmmvy_inst_ui = st.selectbox("PMMVY installments", ["0","1","2","NA"])
jsy_inst_ui = st.selectbox("JSY installments", ["0","1","NA"])

pmmvy_inst = 98 if pmmvy_inst_ui == "NA" else int(pmmvy_inst_ui)
jsy_inst = 98 if jsy_inst_ui == "NA" else int(jsy_inst_ui)

# ---- CONDITIONAL DATE ASKING ----
pmmvy_inst1_date = None
pmmvy_inst2_date = None

if pmmvy_inst >= 1 and pmmvy_inst != 98:
    pmmvy_inst1_date = st.date_input("PMMVY Installment 1 Date")

if pmmvy_inst >= 2 and pmmvy_inst != 98:
    pmmvy_inst2_date = st.date_input("PMMVY Installment 2 Date")

LMPtoINST1 = (pmmvy_inst1_date - lmp_date).days if pmmvy_inst1_date else None
LMPtoINST2 = (pmmvy_inst2_date - lmp_date).days if pmmvy_inst2_date else None
LMPtoINST3 = None

# =====================================================
# ✅ SUBMIT
# =====================================================
if st.button("Predict Score"):

    form_end_time = datetime.now()

    # -------------------------
    # 1️⃣ BUILD RECORD
    # -------------------------
    record = {
        "Beneficiary Name": beneficiary_name,
        "State": state,
        "District": district,
        "Block": block,
        "Village": village,
        "Beneficiary age": beneficiary_age,
        "measured_HB_risk_bin": measured_HB_risk_bin,
        "Child order/parity": parity,
        "Number of living child at now": living_children,
        "MonthConception": month_conception,
        "BMI_PW1_Prog": BMI_PW1_Prog,
        "BMI_PW2_Prog": BMI_PW2_Prog,
        "BMI_PW3_Prog": BMI_PW3_Prog,
        "BMI_PW4_Prog": BMI_PW4_Prog,
        "consume_tobacco": consume_tobacco,
        "Status of current chewing of tobacco": chewing_status,
        "consume_alcohol": consume_alcohol,
        "RegistrationBucket": registration_bucket,
        "counselling_gap_days": counselling_gap_days,
        "ANCBucket": ANCBucket,
        "LMPtoINST1": LMPtoINST1,
        "LMPtoINST2": LMPtoINST2,
        "LMPtoINST3": LMPtoINST3,
        "No of ANCs completed": anc_completed,
        "Service received during last ANC: TT Injection given": tt_given,
        "No. of IFA tablets received/procured in last one month_log1p": ifa_tabs_log1p,
        "No. of calcium tablets consumed in last one month_log1p": calcium_tabs_log1p,
        "Food_Groups_Category": food_group,
        "toilet_type_clean": toilet_type_clean,
        "water_source_clean": water_source_clean,
        "education_clean": education_clean,
        "Household_Assets_Score_log1p": Household_Assets_Score_log1p,
        "Registered for cash transfer scheme: JSY": jsy_reg,
        "Registered for cash transfer scheme: RAJHSRI": rajhsri_reg,
        "PMMVY-Number of installment received": pmmvy_inst,
        "JSY-Number of installment received": jsy_inst,
        "height": height_cm,
        "LMP": lmp_date,
        "Social_Media_Category": Social_Media_Category,
        "Type of Social Media Enrolled In": Type_of_Social_Media_Enrolled_In,
        "Registration Date": registration_date,
        "PMMVY Instalment Date": pmmvy_inst1_date,
        "form_start_time": st.session_state.form_start_time.isoformat(),
        "form_end_time": form_end_time.isoformat(),
        "form_duration_seconds": int(
            (form_end_time - st.session_state.form_start_time).total_seconds()
        ),
    }

st.write("X_processed columns:", X_processed.columns.tolist())
st.write("Expected feature_order:", feature_order)

# -------------------------
# 2️⃣ PREDICTION (FIXED)
# -------------------------

X_raw = pd.DataFrame(
[{k: record.get(k, None) for k in feature_order}]
)

X_processed = preprocess_for_model(X_raw)

lbw_prob = float(model.predict_proba(X_processed)[0][1])
lbw_percent = round(lbw_prob * 100, 2)


    # -------------------------
    # 3️⃣ ADD TO RECORD
    # -------------------------
    record["LBW_Risk_Probability"] = lbw_prob
    record["LBW_Risk_Percentage"] = lbw_percent

    # -------------------------
    # 4️⃣ SAVE TO GOOGLE SHEET
    # -------------------------
    worksheet = get_gsheet("LBW_Beneficiary_Data")
    safe_row = [make_json_safe(v) for v in record.values()]
    worksheet.append_row(
        safe_row,
        value_input_option="USER_ENTERED"
    )

    st.success("✅ Saved & Predicted Successfully")
