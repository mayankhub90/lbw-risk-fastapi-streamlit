# backend/preprocessing.py
import pandas as pd
import numpy as np
from datetime import datetime

# -----------------------------
# Helper functions
# -----------------------------

def hb_to_risk_bin(hb):
    if hb < 6:
        return "severe"
    elif hb < 8:
        return "moderate"
    elif hb < 11:
        return "mild"
    else:
        return "normal"

def anc_bucket(n):
    if n == 0:
        return "none"
    elif n <= 2:
        return "low"
    elif n <= 4:
        return "adequate"
    else:
        return "high"

def registration_bucket(days):
    if days <= 30:
        return "early"
    elif days <= 90:
        return "mid"
    else:
        return "late"

def month_to_code(month):
    return {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }[month]

# -----------------------------
# Main preprocessing
# -----------------------------

def preprocess_payload(payload: dict) -> pd.DataFrame:
    df = pd.DataFrame([payload])

    # --- Hb risk ---
    df["measured_HB_risk_bin"] = df["measured_HB"].apply(hb_to_risk_bin)

    # --- BMI ---
    for i in [1, 2, 3, 4]:
        w = f"weight_pw{i}"
        if w in df.columns and not pd.isna(df[w].iloc[0]):
            df[f"BMI_PW{i}_Prog"] = df[w] / (df["height"] / 100) ** 2
        else:
            df[f"BMI_PW{i}_Prog"] = np.nan

    # --- Parity logic ---
    # parity > living children (accounts for miscarriage/abortion)
    df["Child order/parity"] = df["living_children"] + df["previous_pregnancies"]

    # --- Month of conception ---
    df["MonthConception"] = df["month_conception"].apply(month_to_code)

    # --- Registration bucket ---
    df["RegistrationBucket"] = df["days_lmp_to_registration"].apply(registration_bucket)

    # --- ANC bucket ---
    df["ANCBucket"] = df["No of ANCs completed"].apply(anc_bucket)

    # --- Counselling gap ---
    df["counselling_gap_days"] = df["counselling_visits"] * 30

    # --- Installment timing ---
    for i in [1, 2, 3]:
        df[f"LMPtoINST{i}"] = df["days_lmp_to_registration"] + (i * 30)

    # --- Log transforms ---
    df["No. of IFA tablets received/procured in last one month_log1p"] = np.log1p(
        df["ifa_tablets"]
    )
    df["No. of calcium tablets consumed in last one month_log1p"] = np.log1p(
        df["calcium_tablets"]
    )

    # --- Household assets score ---
    asset_score = (
        df["has_washing_machine"].astype(int) +
        df["has_ac_cooler"].astype(int) +
        df["has_mobile"].astype(int)
    )
    df["Household_Assets_Score_log1p"] = np.log1p(asset_score)

    return df
