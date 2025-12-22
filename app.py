import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="LBW Risk – Data Entry", layout="wide")
st.title("📋 Beneficiary Data Entry Form (UI – BMI & ANC Logic Applied)")

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
# BASIC DETAILS
# =====================================================
st.subheader("Basic Details")

c1, c2 = st.columns(2)
with c1:
    beneficiary_age = st.number_input("Beneficiary age (years)", 10, 60)
with c2:
    height_cm = st.number_input("Height (cm)", 120.0, 200.0)

height_m = height_cm / 100 if height_cm else None

# =====================================================
# PREGNANCY DATES
# =====================================================
st.subheader("Pregnancy Dates")

c1, c2 = st.columns(2)
with c1:
    lmp_date = st.date_input("LMP Date")
with c2:
    registration_date = st.date_input("Registration Date")

# =====================================================
# ANC DETAILS (WITH VALIDATION + OPTIONAL)
# =====================================================
st.subheader("ANC Details (Trimester-linked)")

anc_info = {}
anc_dates = {}

for i in range(1, 5):
    st.markdown(f"### ANC {i}")

    done = st.checkbox(f"ANC {i} Done", key=f"anc_done_{i}")
    anc_info[i] = {"done": done, "date": None, "weight": None, "bmi": None}

    if done:
        c1, c2 = st.columns(2)
        with c1:
            anc_date = st.date_input(f"ANC {i} Date", key=f"anc_date_{i}")
        with c2:
            anc_weight = st.number_input(
                f"ANC {i} Weight (kg)", 30.0, 120.0, key=f"anc_weight_{i}"
            )

        # Chronological validation
        if i > 1 and anc_dates.get(i - 1):
            if anc_date < anc_dates[i - 1]:
                st.error(f"❌ ANC {i} date cannot be earlier than ANC {i-1}")
                st.stop()

        anc_dates[i] = anc_date

        # BMI calculation
        bmi = None
        if height_m and anc_weight:
            bmi = round(anc_weight / (height_m ** 2), 2)

        anc_info[i].update({
            "date": anc_date,
            "weight": anc_weight,
            "bmi": bmi
        })

        st.info(f"📐 BMI (ANC {i}) calculated: **{bmi}**")

# =====================================================
# DERIVED BMI VARIABLES (BACKEND SAFE)
# =====================================================
BMI_PW1_Prog = anc_info[1]["bmi"] if anc_info[1]["done"] else None
BMI_PW2_Prog = anc_info[2]["bmi"] if anc_info[2]["done"] else None
BMI_PW3_Prog = anc_info[3]["bmi"] if anc_info[3]["done"] else None
BMI_PW4_Prog = anc_info[4]["bmi"] if anc_info[4]["done"] else None

# =====================================================
# ANC COUNT
# =====================================================
anc_completed = sum(1 for i in anc_info.values() if i["done"])
st.success(f"✅ No of ANCs completed: {anc_completed}")

# =====================================================
# FINAL RECORD
# =====================================================
if st.button("➕ Add Beneficiary Record"):
    record = {
        "Beneficiary Name": beneficiary_name,
        "State": state,
        "District": district,
        "Block": block,
        "Village": village,
        "Beneficiary age": beneficiary_age,
        "height": height_cm,
        "LMP": lmp_date,
        "Registration Date": registration_date,
        "No of ANCs completed": anc_completed,
        "BMI_PW1_Prog": BMI_PW1_Prog,
        "BMI_PW2_Prog": BMI_PW2_Prog,
        "BMI_PW3_Prog": BMI_PW3_Prog,
        "BMI_PW4_Prog": BMI_PW4_Prog,
    }

    # ANC timing variables
    for i in range(1, 4):
        if anc_info[i]["done"] and anc_info[i]["date"] and lmp_date:
            record[f"LMPtoINST{i}"] = (anc_info[i]["date"] - lmp_date).days
        else:
            record[f"LMPtoINST{i}"] = None

    st.success("✅ Record captured successfully")
    st.dataframe(pd.DataFrame([record]))
