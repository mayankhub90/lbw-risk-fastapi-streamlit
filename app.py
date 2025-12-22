import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="LBW Risk – Data Entry", layout="wide")
st.title("📋 Beneficiary Data Entry Form (UI – Variable Locked)")

# =====================================================
# 🧍 IDENTIFICATION DETAILS
# =====================================================
st.header("🧍 Identification Details")

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
# 🩺 PHYSIOLOGICAL & DEMOGRAPHIC DETAILS
# =====================================================
st.header("🩺 Physiological & Demographic Details")

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

st.caption(f"Derived Hb Risk Category: **{measured_HB_risk_bin}**")

c1, c2 = st.columns(2)
with c1:
    parity = st.number_input("Child order / parity", 0, 10)
with c2:
    living_children = st.number_input("Number of living children at present", 0, 10)

month_conception = st.selectbox(
    "Month of Conception",
    ["January","February","March","April","May","June",
     "July","August","September","October","November","December"]
)

# =====================================================
# 🤰 PREGNANCY & REGISTRATION DETAILS
# =====================================================
st.header("🤰 Pregnancy & Registration Details")

c1, c2 = st.columns(2)
with c1:
    lmp_date = st.date_input("Last Menstrual Period (LMP)")
with c2:
    registration_date = st.date_input("Registration Date")

registration_bucket = None
if lmp_date and registration_date:
    days_gap = (registration_date - lmp_date).days
    registration_bucket = "Early" if days_gap < 84 else "Mid" if days_gap <= 168 else "Late"

# =====================================================
# 🏥 ANC & ANTHROPOMETRY (BMI)
# =====================================================
st.header("🏥 ANC & Anthropometry (BMI)")

height_m = height_cm / 100 if height_cm else None
anc, anc_dates = {}, []

col_left, col_right = st.columns(2)

def anc_block(i, container):
    with container:
        st.subheader(f"ANC {i}")
        done = st.checkbox(f"ANC {i} Completed", key=f"anc_done_{i}")
        anc[i] = {"done": done, "date": None, "weight": None, "bmi": None}

        if done:
            anc_date = st.date_input(f"ANC {i} Date", key=f"anc_date_{i}")
            anc_weight = st.number_input(
                f"ANC {i} Weight (kg)", 30.0, 120.0, key=f"anc_weight_{i}"
            )

            if anc_dates and anc_date < anc_dates[-1]:
                st.error("ANC dates must be chronological.")
                st.stop()

            anc_dates.append(anc_date)
            bmi = round(anc_weight / (height_m ** 2), 2) if height_m else None
            anc[i].update({"date": anc_date, "weight": anc_weight, "bmi": bmi})
            st.caption(f"Calculated BMI: **{bmi}**")

anc_block(1, col_left)
anc_block(2, col_left)
anc_block(3, col_right)
anc_block(4, col_right)

BMI_PW1_Prog = anc.get(1, {}).get("bmi") if anc.get(1, {}).get("done") else None
BMI_PW2_Prog = anc.get(2, {}).get("bmi") if anc.get(2, {}).get("done") else None
BMI_PW3_Prog = anc.get(3, {}).get("bmi") if anc.get(3, {}).get("done") else None
BMI_PW4_Prog = anc.get(4, {}).get("bmi") if anc.get(4, {}).get("done") else None

anc_completed = sum(1 for a in anc.values() if a["done"])

# TT Injection (moved here)
tt_given = st.selectbox(
    "Service received during last ANC: TT Injection given",
    ["Yes", "No"]
)

valid_dates = [a["date"] for a in anc.values() if a["done"] and a["date"]]
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

consume_tobacco = st.selectbox("Do you consume tobacco?", ["Yes", "No"])
chewing_status = (
    st.selectbox("Status of current chewing of tobacco",
                 ["EVERY DAY", "SOME DAYS", "NOT AT ALL"])
    if consume_tobacco == "Yes" else None
)

consume_alcohol = st.selectbox("Do you consume alcohol?", ["Yes", "No"])

# =====================================================
# 🥗 NUTRITION
# =====================================================
st.header("🥗 Nutrition")

ifa_tabs = st.number_input(
    "No. of IFA tablets received/procured in last one month", min_value=0
)

calcium_tabs = st.number_input(
    "No. of calcium tablets consumed in last one month", min_value=0
)

food_group = st.selectbox(
    "How many food groups have you consumed?",
    [0, 1, 2, 3, 4, 5]
)

# =====================================================
# 📱 DIGITAL ACCESS
# =====================================================
st.header("📱 Digital Access")

social_media_selected = st.multiselect(
    "Social Media Platforms Used",
    ["Facebook", "YouTube", "Instagram", "WhatsApp", "Other"]
)

other_social_media = []
if "Other" in social_media_selected:
    other_input = st.text_input("Specify other social media (comma-separated)")
    if other_input:
        other_social_media = [x.strip() for x in other_input.split(",") if x.strip()]

explicit_count = len([x for x in social_media_selected if x != "Other"])
total_count = explicit_count + len(other_social_media)

if total_count == 0:
    social_media_category = "None"
elif total_count == 1:
    social_media_category = "Low"
elif total_count <= 3:
    social_media_category = "Medium"
else:
    social_media_category = "High"

# =====================================================
# 💰 PROGRAM PARTICIPATION
# =====================================================
st.header("💰 Program Participation")

jsy_reg = st.selectbox("Registered for cash transfer scheme: JSY", ["Yes", "No"])
rajhsri_reg = st.selectbox("Registered for cash transfer scheme: RAJHSRI", ["Yes", "No"])

inst_options = ["0", "1", "2", "NA"]
pmmvy_inst_ui = st.selectbox("PMMVY-Number of installment received", inst_options)
jsy_inst_ui = st.selectbox("JSY-Number of installment received", ["0", "1", "NA"])

pmmvy_inst = 98 if pmmvy_inst_ui == "NA" else int(pmmvy_inst_ui)
jsy_inst = 98 if jsy_inst_ui == "NA" else int(jsy_inst_ui)

pmmvy_inst1_date = None
pmmvy_inst2_date = None

if pmmvy_inst >= 1 and pmmvy_inst != 98:
    pmmvy_inst1_date = st.date_input("PMMVY Installment 1 Date")

if pmmvy_inst >= 2 and pmmvy_inst != 98:
    pmmvy_inst2_date = st.date_input("PMMVY Installment 2 Date")

LMPtoINST1 = (pmmvy_inst1_date - lmp_date).days if pmmvy_inst1_date and lmp_date else None
LMPtoINST2 = (pmmvy_inst2_date - lmp_date).days if pmmvy_inst2_date and lmp_date else None
LMPtoINST3 = None

# =====================================================
# ✅ SUBMIT & REVIEW
# =====================================================
st.header("✅ Submit & Review")

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
        "toilet_type_clean": None,   # unchanged, assumed handled earlier
        "water_source_clean": None,  # unchanged, assumed handled earlier
        "education_clean": None,     # unchanged, assumed handled earlier
        "Social_Media_Category": social_media_category,
        "Registered for cash transfer scheme: JSY": jsy_reg,
        "Registered for cash transfer scheme: RAJHSRI": rajhsri_reg,
        "PMMVY-Number of installment received": pmmvy_inst,
        "JSY-Number of installment received": jsy_inst,
        "height": height_cm,
        "LMP": lmp_date,
        "Registration Date": registration_date,
        "Type of Social Media Enrolled In":
            ",".join([x for x in social_media_selected if x != "Other"] + other_social_media),
        "PMMVY Instalment Date": pmmvy_inst1_date,
    }

    st.success("✅ Record captured successfully")
    st.dataframe(pd.DataFrame([record]))
