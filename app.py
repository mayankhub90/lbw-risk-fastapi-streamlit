import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="LBW Risk – Data Entry", layout="wide")
st.title("📋 Beneficiary Data Entry Form (UI – Variable Locked)")

# =====================================================
# 1. IDENTIFICATION DETAILS
# =====================================================
st.header("1️⃣ Identification Details")

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
# 2. PHYSIOLOGICAL & DEMOGRAPHIC DETAILS
# =====================================================
st.header("2️⃣ Physiological & Demographic Details")

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
# 3. PREGNANCY & REGISTRATION DETAILS
# =====================================================
st.header("3️⃣ Pregnancy & Registration Details")

c1, c2 = st.columns(2)
with c1:
    lmp_date = st.date_input("Last Menstrual Period (LMP)")
with c2:
    registration_date = st.date_input("Registration Date")

registration_bucket = None
if lmp_date and registration_date:
    days_gap = (registration_date - lmp_date).days
    registration_bucket = (
        "Early" if days_gap < 84 else
        "Mid" if days_gap <= 168 else
        "Late"
    )

st.caption(f"Registration Timing Category: **{registration_bucket}**")

# =====================================================
# 4. ANC & ANTHROPOMETRY (BMI)
# =====================================================
st.header("4️⃣ ANC & Anthropometry (BMI)")

height_m = height_cm / 100 if height_cm else None
anc, anc_dates = {}, []

for i in range(1, 5):
    st.subheader(f"ANC {i}")

    done = st.checkbox(f"ANC {i} Completed", key=f"anc_done_{i}")
    anc[i] = {"done": done, "date": None, "weight": None, "bmi": None}

    if done:
        c1, c2 = st.columns(2)
        with c1:
            anc_date = st.date_input(f"ANC {i} Date", key=f"anc_date_{i}")
        with c2:
            anc_weight = st.number_input(
                f"ANC {i} Weight (kg)",
                30.0, 120.0,
                key=f"anc_weight_{i}"
            )

        if anc_dates and anc_date < anc_dates[-1]:
            st.error("ANC dates must be chronological.")
            st.stop()

        anc_dates.append(anc_date)

        bmi = round(anc_weight / (height_m ** 2), 2) if height_m else None
        anc[i].update({"date": anc_date, "weight": anc_weight, "bmi": bmi})

        st.caption(f"Calculated BMI: **{bmi}**")

BMI_PW1_Prog = anc[1]["bmi"] if anc[1]["done"] else None
BMI_PW2_Prog = anc[2]["bmi"] if anc[2]["done"] else None
BMI_PW3_Prog = anc[3]["bmi"] if anc[3]["done"] else None
BMI_PW4_Prog = anc[4]["bmi"] if anc[4]["done"] else None

anc_completed = sum(1 for a in anc.values() if a["done"])

ANCBucket, counselling_gap_days = None, None
valid_dates = [a["date"] for a in anc.values() if a["done"] and a["date"]]

if valid_dates:
    first_anc = min(valid_dates)
    gap = (first_anc - lmp_date).days
    ANCBucket = "Early" if gap < 84 else "Mid" if gap <= 168 else "Late"

if len(valid_dates) >= 2:
    valid_dates.sort()
    counselling_gap_days = (valid_dates[1] - valid_dates[0]).days

# =====================================================
# 5. TOBACCO & ALCOHOL
# =====================================================
st.header("5️⃣ Tobacco & Alcohol Use")

consume_tobacco = st.selectbox("Do you consume tobacco?", ["Yes", "No"])
chewing_status = (
    st.selectbox(
        "Status of current chewing of tobacco",
        ["EVERY DAY", "SOME DAYS", "NOT AT ALL"]
    ) if consume_tobacco == "Yes" else None
)

consume_alcohol = st.selectbox("Do you consume alcohol?", ["Yes", "No"])

# =====================================================
# 6. NUTRITION
# =====================================================
st.header("6️⃣ Nutrition")

ifa_tabs = st.number_input(
    "No. of IFA tablets received/procured in last one month",
    min_value=0
)

calcium_tabs = st.number_input(
    "No. of calcium tablets consumed in last one month",
    min_value=0
)

food_group = st.selectbox(
    "Food Groups Consumption Category",
    ["Low", "Medium", "High"]
)

# =====================================================
# 7. SOCIO-ECONOMIC STATUS (SES)
# =====================================================
st.header("7️⃣ Socio-Economic Status (SES)")

toilet_type = st.selectbox(
    "Type of Toilet Facility",
    ["Improved toilet","Pit latrine (basic)",
     "Unimproved / unknown","No facility / open defecation"]
)

water_source = st.selectbox(
    "Primary Drinking Water Source",
    ["Piped supply","Groundwater – handpump/borewell",
     "Protected well","Surface/Unprotected","Delivered / other"]
)

education = st.selectbox(
    "Highest Education Level",
    ["No schooling","Primary (1–5)","Middle (6–8)",
     "Secondary (9–12)","Graduate & above"]
)

# =====================================================
# 8. DIGITAL ACCESS
# =====================================================
st.header("8️⃣ Digital Access")

social_media_selected = st.multiselect(
    "Social Media Platforms Used",
    ["Facebook","YouTube","Instagram","WhatsApp","Other"]
)

other_social_media = []
if "Other" in social_media_selected:
    other_input = st.text_input(
        "Specify other social media platforms (comma-separated)"
    )
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
# 9. PROGRAM PARTICIPATION (PMMVY & JSY)
# =====================================================
st.header("9️⃣ Program Participation")

tt_given = st.selectbox(
    "Service received during last ANC: TT Injection given",
    ["Yes", "No"]
)

jsy_reg = st.selectbox(
    "Registered for cash transfer scheme: JSY",
    ["Yes", "No"]
)

rajhsri_reg = st.selectbox(
    "Registered for cash transfer scheme: RAJHSRI",
    ["Yes", "No"]
)

# ---- PMMVY ----
pmmvy_inst = st.selectbox(
    "PMMVY-Number of installment received",
    [0, 1, 2, 98]
)

pmmvy_inst1_date, pmmvy_inst2_date = None, None

if pmmvy_inst >= 1:
    pmmvy_inst1_date = st.date_input("PMMVY Installment 1 Date")

if pmmvy_inst >= 2:
    pmmvy_inst2_date = st.date_input("PMMVY Installment 2 Date")

LMPtoINST1 = (pmmvy_inst1_date - lmp_date).days if pmmvy_inst1_date and lmp_date else None
LMPtoINST2 = (pmmvy_inst2_date - lmp_date).days if pmmvy_inst2_date and lmp_date else None
LMPtoINST3 = None

# ---- JSY ----
jsy_inst = st.selectbox(
    "JSY-Number of installment received",
    [0, 1, 98]
)

# =====================================================
# 10. SUBMIT & REVIEW
# =====================================================
st.header("🔟 Submit & Review")

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
        "Type of Social Media Enrolled In":
            ",".join([x for x in social_media_selected if x != "Other"] + other_social_media),
        "PMMVY Instalment Date": pmmvy_inst1_date,
    }

    st.success("✅ Record captured successfully")
    st.dataframe(pd.DataFrame([record]))
