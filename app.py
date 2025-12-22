import streamlit as st
import pandas as pd
import math
import os
from datetime import datetime, date

# =====================================================
# APP CONFIG
# =====================================================
st.set_page_config(page_title="LBW Risk – Data Entry", layout="wide")
st.title("📋 Beneficiary Data Entry Form")

CSV_PATH = "beneficiary_records.csv"

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
    "Andhra Pradesh": ["Anantapur", "Chittoor", "Guntur"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur"],
    "Delhi": ["Central Delhi", "East Delhi", "New Delhi"],
    "Karnataka": ["Bengaluru Urban", "Mysuru", "Dharwad", "Tumkur"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
    "Uttar Pradesh": ["Lucknow", "Kanpur Nagar", "Varanasi"]
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

if hb_value < 6:
    measured_HB_risk_bin = "severe_anaemia"
elif hb_value < 8:
    measured_HB_risk_bin = "moderate_anaemia"
elif hb_value < 11:
    measured_HB_risk_bin = "mild_anaemia"
else:
    measured_HB_risk_bin = "normal"

# ✅ SHOW DERIVED HB RISK BIN
st.info(f"🩸 Derived Hb Risk Category: **{measured_HB_risk_bin}**")

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
    lmp_date = st.date_input("Last Menstrual Period (LMP)",
                             value=pd.to_datetime(get_val("LMP", date.today())))
with c2:
    registration_date = st.date_input("Registration Date",
                                      value=pd.to_datetime(get_val("Registration Date", date.today())))

if lmp_date >= registration_date:
    st.error("❌ LMP date must be strictly earlier than Registration Date")
    st.stop()

days_gap = (registration_date - lmp_date).days
registration_bucket = "Early" if days_gap < 84 else "Mid" if days_gap <= 168 else "Late"

# =====================================================
# 🏥 ANC & BMI
# =====================================================
st.header("🏥 ANC & Anthropometry (BMI)")

height_m = height_cm / 100
anc, anc_dates = {}, []

col_left, col_right = st.columns(2)

def anc_block(i, col):
    with col:
        st.subheader(f"ANC {i}")
        done = st.checkbox(f"ANC {i} Completed", key=f"anc_done_{i}")
        anc[i] = {"done": done, "date": None, "weight": None, "bmi": None}

        if done:
            anc_date = st.date_input(f"ANC {i} Date", key=f"anc_date_{i}")
            anc_weight = st.number_input(f"ANC {i} Weight (kg)", 30.0, 120.0,
                                         key=f"anc_weight_{i}")

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

if anc.get(1, {}).get("done") and anc.get(3, {}).get("done"):
    if anc[1]["date"] == anc[3]["date"]:
        st.error("❌ ANC 1 and ANC 3 dates must differ by at least 1 day")
        st.stop()

BMI_PW1_Prog = anc[1]["bmi"] if anc[1]["done"] else None
BMI_PW2_Prog = anc[2]["bmi"] if anc[2]["done"] else None
BMI_PW3_Prog = anc[3]["bmi"] if anc[3]["done"] else None
BMI_PW4_Prog = anc[4]["bmi"] if anc[4]["done"] else None

anc_completed = sum(1 for a in anc.values() if a["done"])

tt_given = st.selectbox("TT Injection given in last ANC", ["Yes","No"])

# =====================================================
# 💰 SCHEME PARTICIPATION (FIXED LOGIC)
# =====================================================
st.header("💰 Scheme Participation")

jsy_reg = st.selectbox("Registered for JSY", ["No","Yes"])
rajhsri_reg = st.selectbox("Registered for RAJSHRI", ["No","Yes"])

pmmvy_inst_ui = st.selectbox("PMMVY installments received", ["0","1","2","NA"])
jsy_inst_ui = st.selectbox("JSY installments received", ["0","1","NA"])

pmmvy_inst = 98 if pmmvy_inst_ui == "NA" else int(pmmvy_inst_ui)
jsy_inst = 98 if jsy_inst_ui == "NA" else int(jsy_inst_ui)

pmmvy_inst1_date = None
pmmvy_inst2_date = None

# ✅ ASK DATES ONLY AFTER SELECTION
if pmmvy_inst == 1:
    pmmvy_inst1_date = st.date_input("PMMVY Installment 1 Date")
elif pmmvy_inst == 2:
    pmmvy_inst1_date = st.date_input("PMMVY Installment 1 Date")
    pmmvy_inst2_date = st.date_input("PMMVY Installment 2 Date")

LMPtoINST1 = (pmmvy_inst1_date - lmp_date).days if pmmvy_inst1_date else None
LMPtoINST2 = (pmmvy_inst2_date - lmp_date).days if pmmvy_inst2_date else None
LMPtoINST3 = None

# =====================================================
# ✅ SUBMIT
# =====================================================
if st.button("➕ Add / Update Record"):
    form_end_time = datetime.now()

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
        "ANCBucket": None,
        "LMPtoINST1": LMPtoINST1,
        "LMPtoINST2": LMPtoINST2,
        "LMPtoINST3": None,
        "No of ANCs completed": anc_completed,
        "Service received during last ANC: TT Injection given": tt_given,
        "PMMVY-Number of installment received": pmmvy_inst,
        "JSY-Number of installment received": jsy_inst,
        "height": height_cm,
        "LMP": lmp_date,
        "Registration Date": registration_date,
        "PMMVY Instalment Date": pmmvy_inst1_date,
        "form_start_time": st.session_state.form_start_time.isoformat(),
        "form_end_time": form_end_time.isoformat(),
        "form_duration_seconds": int((form_end_time - st.session_state.form_start_time).total_seconds())
    }

    df = pd.DataFrame([record])

    if edit_mode:
        existing_df.loc[selected_index] = record
        existing_df.to_csv(CSV_PATH, index=False)
    else:
        df.to_csv(CSV_PATH, mode="a", header=not os.path.exists(CSV_PATH), index=False)

    st.success("✅ Record saved successfully")
    st.json(record)
