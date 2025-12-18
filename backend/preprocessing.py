import pandas as pd
import numpy as np
from datetime import datetime

# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def compute_bmi(weight, height_cm):
    if weight is None or weight <= 0:
        return np.nan
    h_m = height_cm / 100.0
    return round(weight / (h_m ** 2), 2)


def hb_risk_bin(hb):
    if hb < 6:
        return "severe_anaemia"
    elif hb < 8:
        return "moderate_anaemia"
    elif hb < 11:
        return "mild_anaemia"
    else:
        return "normal"


def registration_bucket(days):
    if days <= 60:
        return "early"
    elif days <= 120:
        return "mid"
    else:
        return "late"


def anc_bucket(n):
    if n == 0:
        return "none"
    elif n <= 2:
        return "low"
    elif n <= 4:
        return "adequate"
    else:
        return "high"


def log1p_safe(x):
    return np.log1p(max(0, x))


# --------------------------------------------------
# MAIN preprocessing function
# --------------------------------------------------

def preprocess_payload(payload: dict) -> pd.DataFrame:
    """
    Takes raw UI payload and returns ONE ROW dataframe
    exactly matching model feature expectations.
    """

    # -----------------------------
    # Dates
    # -----------------------------
    lmp = datetime.fromisoformat(payload["lmp_date"])
    reg = datetime.fromisoformat(payload["registration_date"])

    lmp_to_reg = (reg - lmp).days

    # -----------------------------
    # ANC Installment inference
    # -----------------------------
    # Simple proportional inference (as agreed)
    lmp_to_inst1 = lmp_to_reg + 30
    lmp_to_inst2 = lmp_to_inst1 + 30
    lmp_to_inst3 = lmp_to_inst2 + 30

    # -----------------------------
    # BMI calculation
    # -----------------------------
    bmi_pw1 = compute_bmi(payload["weight_pw1"], payload["height_cm"])
    bmi_pw2 = compute_bmi(payload["weight_pw2"], payload["height_cm"])
    bmi_pw3 = compute_bmi(payload["weight_pw3"], payload["height_cm"])
    bmi_pw4 = compute_bmi(payload["weight_pw4"], payload["height_cm"])

    # -----------------------------
    # Household asset score
    # -----------------------------
    asset_score = 0
    if payload["washing_machine"] == "Yes":
        asset_score += 1
    if payload["ac_cooler"] == "Yes":
        asset_score += 1
    if payload["social_media"] == "Yes":
        asset_score += 2  # phone + electricity

    # -----------------------------
    # Build final row
    # -----------------------------
    row = {
        "Beneficiary age": payload["beneficiary_age"],
        "measured_HB_risk_bin": hb_risk_bin(payload["hemoglobin"]),
        "Child order/parity": payload["parity"],
        "Number of living child at now": payload["living_children"],
        "MonthConception": payload["month_conception"],

        "BMI_PW1_Prog": bmi_pw1,
        "BMI_PW2_Prog": bmi_pw2,
        "BMI_PW3_Prog": bmi_pw3,
        "BMI_PW4_Prog": bmi_pw4,

        "consume_tobacco": payload["consume_tobacco"],
        "Status of current chewing of tobacco": payload["chewing_tobacco"],
        "consume_alcohol": payload["consume_alcohol"],

        "RegistrationBucket": registration_bucket(lmp_to_reg),
        "counselling_gap_days": np.nan,  # no counselling dates provided
        "ANCBucket": anc_bucket(payload["anc_completed"]),

        "LMPtoINST1": lmp_to_inst1,
        "LMPtoINST2": lmp_to_inst2,
        "LMPtoINST3": lmp_to_inst3,

        "No of ANCs completed": payload["anc_completed"],
        "Service received during last ANC: TT Injection given": payload["tt_given"],

        "No. of IFA tablets received/procured in last one month_log1p":
            log1p_safe(payload["ifa_tabs"]),
        "No. of calcium tablets consumed in last one month_log1p":
            log1p_safe(payload["calcium_tabs"]),

        "Food_Groups_Category": payload["food_group"],
        "Household_Assets_Score_log1p": log1p_safe(asset_score),

        "toilet_type_clean": payload["toilet_type_clean"],
        "water_source_clean": payload["water_source_clean"],
        "education_clean": payload["education_clean"],

        "Social_Media_Category": payload["social_media"],

        "Registered for cash transfer scheme: JSY": payload["jsy_registered"],
        "Registered for cash transfer scheme: RAJHSRI": payload["raj_registered"],

        "PMMVY-Number of installment received": payload["pmmvy_count"],
        "JSY-Number of installment received": payload["jsy_count"],
    }

    return pd.DataFrame([row])
