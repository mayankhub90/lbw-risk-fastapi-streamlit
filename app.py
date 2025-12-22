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
    beneficiary_age = st.number_input("Beneficiary age (years)", 10, 60)
with c2:
    height_cm = st.number_input("Height (cm)", 120.0, 200.0)
with c3:
    hb_value = st.number_input("Measured Hb (g/dL)", 3.0, 18.0)

# Hb risk bin (derived)
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

# Registration bucket (derived)
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
# ANC DETAILS (OPTIONAL + ORDERED)
# =====================================================
st.subheader("ANC Details (Trimester-linked, Optional)")

height_m = height_cm / 100 if height_cm else None

anc = {}
anc_dates = []

for i in range(1, 5):
    st.markdown(f"### ANC {i}")
    done = st.checkbox(f"ANC {i} Done", key=f"anc_done_{i}")

    anc[i] = {
        "done": done,
        "date": None,
        "weight": None,
        "bmi": None
    }

    if done:
        c1, c2 = st.columns(2)
        with c1:
            anc_date = st.date_input(f"ANC {i} Date", key=f"anc_date_{i}")
        with c2:
            anc_weight = st.number_input(
                f"ANC {i} Weight (kg)", 30.0, 120.0, key=f"anc_weight_{i}"
            )

        # chronological validation
        if anc_dates and anc_date < anc_dates[-1]:
            st.error(f"ANC {i} date cannot be earlier than previous ANC")
            st.stop()

        anc_dates.append(anc_date)

        bmi = None
        if height_m and anc_weight:
            bmi = round(anc_weight / (height_m ** 2), 2)

        anc[i].update({
            "date": anc_date,
            "weight": anc_weight,
            "bmi": bmi
        })

        st.caption(f"Calculated BMI (ANC {i}): {bmi}")

# =====================================================
# BMI VARIABLES (BACKEND NAMES PRESERVED)
# =====================================================
BMI_PW1_Prog = anc[1]["bmi"] if anc[1]["done"] else None
BMI_PW2_Prog = anc[2]["bmi"] if anc[2]["done"] else None
BMI_PW3_Prog = anc[3]["bmi"] if anc[3]["done"] else None
BMI_PW4_Prog = anc[4]["bmi"] if anc[4]["done"] else None

# ANC count
anc_completed = sum(1 for i in anc.values() if i["done"])

# =====================================================
# ANC TIMING DERIVATIONS (PRESERVED)
# =====================================================
ANCBucket = None
counselling_gap_days = None

valid_anc_dates = [a["date"] for a in anc.values() if a["done"] and a["date"]]

if valid_anc_dates:
    first_anc = min(valid_anc_dates)
    gap = (first_anc - lmp_date).days
    if gap < 84:
        ANCBucket = "Early"
    elif gap <= 168:
        ANCBucket = "Mid"
    else:
        ANCBucket = "Later"

if len(valid_anc_dates) >= 2:
    valid_anc_dates.sort()
    counselling_gap_days = (valid_anc_dates[1] - valid_anc_dates[0]).days

# LMP to INST variables
LMPtoINST1 = (anc[1]["date"] - lmp_date).days if anc[1]["done"] and lmp_date else None
LMPtoINST2 = (anc[2]["date"] - lmp_date).days if anc[2]["done"] and lmp_date else None
LMPtoINST3 = (anc[3]["date"] - lmp_date).days if anc[3]["done"] and lmp_date else None

# =====================================================
# REMAINING VARIABLES (UNCHANGED UI)
# =====================================================
st.subheader("Remaining Features (Locked)")

consume_tobacco = st.selectbox("consume_tobacco", ["Yes","No"])
chewing_status = st.selectbox(
    "Status of current chewing of tobacco",
    ["EVERY DAY","SOME DAYS","NOT AT ALL"]
)
consume_alcohol = st.selectbox("consume_alcohol", ["Yes","No"])

tt_given = st.selectbox(
    "Service received during last ANC: TT Injection given",
    ["Yes","No"]
)

ifa_tabs = st.number_input(
    "No. of IFA tablets received/procured in last one month_log1p"
)
calcium_tabs = st.number_input(
    "No. of calcium tablets consumed in last one month_log1p"
)

food_group = st.selectbox("Food_Groups_Category", ["Low","Medium","High"])

toilet_type = st.selectbox(
    "toilet_type_clean",
    ["Improved toilet","Pit latrine (basic)",
     "Unimproved / unknown","No facility / open defecation"]
)

water_source = st.selectbox(
    "water_source_clean",
    ["Piped supply","Groundwater – handpump/borewell",
     "Protected well","Surface/Unprotected","Delivered / other"]
)

education = st.selectbox(
    "education_clean",
    ["No schooling","Primary (1–5)","Middle (6–8)",
     "Secondary (9–12)","Graduate & above"]
)

social_media_types = st.multiselect(
    "Type of Social Media Enrolled In",
    ["Facebook","YouTube","Instagram","WhatsApp","Other"]
)

sm_count = len(social_media_types)
if sm_count == 0:
    social_media_category = "None"
elif sm_count == 1:
    social_media_category = "Low"
elif sm_count <= 3:
    social_media_category = "Medium"
else:
    social_media_category = "High"

jsy_reg = st.selectbox("Registered for cash transfer scheme: JSY", ["Yes","No"])
rajhsri_reg = st.selectbox("Registered for cash transfer scheme: RAJHSRI", ["Yes","No"])
pmmvy_inst = st.selectbox("PMMVY-Number of installment received", [0,1,2,98])
jsy_inst = st.selectbox("JSY-Number of installment received", [0,1,98])
pmmvy_inst_date = st.date_input("PMMVY Instalment Date")

# =====================================================
# FINAL RECORD (ALL VARIABLES PRESENT)
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
        "No. of IFA tablets received/procured in last one month_log1p": ifa_tabs,
        "No. of calcium tablets consumed in last one month_log1p": calcium_tabs,
        "Food_Groups_Category": food_group,
        "toilet_type_clean": toilet_type,
        "water_source_clean": water_source,
        "education_clean": education,
        "Social_Media_Category": social_media_category,
        "Registered for cash transfer scheme: JSY": jsy_reg,
        "Registered for cash transfer scheme: RAJHSRI": rajhsri_reg,
        "PMMVY-Number of installment received": pmmvy_inst,
        "JSY-Number of installment received": jsy_inst,
        "height": height_cm,
        "LMP": lmp_date,
        "Registration Date": registration_date,
        "Type of Social Media Enrolled In": ",".join(social_media_types),
        "PMMVY Instalment Date": pmmvy_inst_date,
    }

    st.success("✅ Record captured (all variables retained)")
    st.dataframe(pd.DataFrame([record]))
