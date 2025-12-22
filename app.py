import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="LBW Risk – Data Entry", layout="wide")
st.title("📋 Beneficiary Data Entry Form (UI – Variable Locked)")

# =====================================================
# IDENTIFICATION
# =====================================================
st.subheader("Identification Details")

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

# =====================================================
# PHYSIO FEATURES
# =====================================================
st.subheader("Physiological Details")

c1, c2, c3 = st.columns(3)
with c1:
    beneficiary_age = st.number_input("Beneficiary age (years)", 14, 60)
with c2:
    height_cm = st.number_input("Height (cm)", 120.0, 200.0)
with c3:
    hb_value = st.number_input("Measured Hb (g/dL)", 3.0, 18.0)

if hb_value < 6:
    measured_HB_risk_bin = "severe_anaemia"
elif hb_value < 8:
    measured_HB_risk_bin = "moderate_anaemia"
elif hb_value < 11:
    measured_HB_risk_bin = "mild_anaemia"
else:
    measured_HB_risk_bin = "normal"

st.info(f"Derived Hb Risk: {measured_HB_risk_bin}")

c1, c2 = st.columns(2)
with c1:
    parity = st.number_input("Child order/parity", 0, 10)
with c2:
    living_children = st.number_input("Number of living child at now", 0, 10)

month_conception = st.selectbox(
    "MonthConception",
    ["January","February","March","April","May","June",
     "July","August","September","October","November","December"]
)

# =====================================================
# PREGNANCY DATES
# =====================================================
st.subheader("Pregnancy Dates")

c1, c2 = st.columns(2)
with c1:
    lmp_date = st.date_input("LMP")
with c2:
    registration_date = st.date_input("Registration Date")

registration_bucket = None
if lmp_date and registration_date:
    gap = (registration_date - lmp_date).days
    if gap < 84:
        registration_bucket = "Early"
    elif gap <= 168:
        registration_bucket = "Mid"
    else:
        registration_bucket = "Late"

st.info(f"RegistrationBucket (Derived): {registration_bucket}")

# =====================================================
# ANC DETAILS (UNCHANGED)
# =====================================================
st.subheader("ANC Details (Trimester-linked, Optional)")

height_m = height_cm / 100 if height_cm else None
anc, anc_dates = {}, []

for i in range(1, 5):
    st.markdown(f"### ANC {i}")
    done = st.checkbox(f"ANC {i} Done", key=f"anc_done_{i}")
    anc[i] = {"done": done, "date": None, "weight": None, "bmi": None}

    if done:
        c1, c2 = st.columns(2)
        with c1:
            anc_date = st.date_input(f"ANC {i} Date", key=f"anc_date_{i}")
        with c2:
            anc_weight = st.number_input(f"ANC {i} Weight (kg)", 30.0, 120.0)

        if anc_dates and anc_date < anc_dates[-1]:
            st.error(f"ANC {i} date cannot be earlier than previous ANC")
            st.stop()

        anc_dates.append(anc_date)
        bmi = round(anc_weight / (height_m ** 2), 2) if height_m else None
        anc[i].update({"date": anc_date, "weight": anc_weight, "bmi": bmi})

BMI_PW1_Prog = anc[1]["bmi"] if anc[1]["done"] else None
BMI_PW2_Prog = anc[2]["bmi"] if anc[2]["done"] else None
BMI_PW3_Prog = anc[3]["bmi"] if anc[3]["done"] else None
BMI_PW4_Prog = anc[4]["bmi"] if anc[4]["done"] else None

anc_completed = sum(1 for i in anc.values() if i["done"])

# ANC timing
ANCBucket = None
counselling_gap_days = None
valid_anc_dates = [a["date"] for a in anc.values() if a["done"] and a["date"]]

if valid_anc_dates:
    first_anc = min(valid_anc_dates)
    gap = (first_anc - lmp_date).days
    ANCBucket = "Early" if gap < 84 else "Mid" if gap <= 168 else "Late"

if len(valid_anc_dates) >= 2:
    valid_anc_dates.sort()
    counselling_gap_days = (valid_anc_dates[1] - valid_anc_dates[0]).days

# =====================================================
# PROGRAM FEATURES (PMMVY & JSY – FIXED)
# =====================================================
st.subheader("Program Participation")

# ---- PMMVY ----
pmmvy_inst = st.selectbox(
    "PMMVY - Number of installment received",
    [0, 1, 2, 98]
)

pmmvy_inst1_date = None
pmmvy_inst2_date = None

if pmmvy_inst >= 1:
    pmmvy_inst1_date = st.date_input("PMMVY Installment 1 Date")

if pmmvy_inst >= 2:
    pmmvy_inst2_date = st.date_input("PMMVY Installment 2 Date")

LMPtoINST1 = (
    (pmmvy_inst1_date - lmp_date).days
    if pmmvy_inst1_date and lmp_date else None
)

LMPtoINST2 = (
    (pmmvy_inst2_date - lmp_date).days
    if pmmvy_inst2_date and lmp_date else None
)

LMPtoINST3 = None  # as per spec

# ---- JSY ----
jsy_inst = st.selectbox(
    "JSY - Number of installment received",
    [0, 1, 98]
)

# =====================================================
# FINAL RECORD
# =====================================================
if st.button("➕ Add Beneficiary Record"):
    record = {
        "Beneficiary age": beneficiary_age,
        "measured_HB_risk_bin": measured_HB_risk_bin,
        "Child order/parity": parity,
        "Number of living child at now": living_children,
        "MonthConception": month_conception,
        "BMI_PW1_Prog": BMI_PW1_Prog,
        "BMI_PW2_Prog": BMI_PW2_Prog,
        "BMI_PW3_Prog": BMI_PW3_Prog,
        "BMI_PW4_Prog": BMI_PW4_Prog,
        "RegistrationBucket": registration_bucket,
        "ANCBucket": ANCBucket,
        "counselling_gap_days": counselling_gap_days,
        "LMPtoINST1": LMPtoINST1,
        "LMPtoINST2": LMPtoINST2,
        "LMPtoINST3": LMPtoINST3,
        "No of ANCs completed": anc_completed,
        "PMMVY-Number of installment received": pmmvy_inst,
        "JSY-Number of installment received": jsy_inst,
        "height": height_cm,
        "LMP": lmp_date,
        "Registration Date": registration_date,
    }

    st.success("✅ Record captured (PMMVY & JSY logic applied)")
    st.dataframe(pd.DataFrame([record]))
