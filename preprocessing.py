# preprocessing.py
import pandas as pd
import numpy as np

# -------------------------
# Helper mappings
# -------------------------

MONTH_MAP = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

def hb_to_risk(hb):
    if hb < 6:
        return "severe"
    elif hb < 8:
        return "moderate"
    elif hb < 11:
        return "mild"
    return "normal"

def anc_bucket(n):
    if n == 0:
        return "none"
    elif n <= 2:
        return "low"
    elif n <= 4:
        return "adequate"
    return "high"

def registration_bucket(days):
    if days <= 30:
        return "early"
    elif days <= 90:
        return "mid"
    return "late"

# -------------------------
# Main preprocessing
# -------------------------

def preprocess_payload(payload: dict, features: list) -> pd.DataFrame:
    df = pd.DataFrame([payload])

    # --- Hb ---
    df["measured_HB_risk_bin"] = df["measured_HB"].apply(hb_to_risk)

    # --- Parity ---
    df["Child order/parity"] = df[["Number of living child at now", "previous_pregnancies"]].max(axis=1) + 1

    # --- Month ---
    df["MonthConception"] = df["month_conception"].map(MONTH_MAP)

    # --- BMI ---
    for i in range(1, 5):
        w = f"weight_pw{i}"
        df[f"BMI_PW{i}_Prog"] = np.where(
            df[w].notna(),
            df[w] / (df["height"] / 100) ** 2,
            np.nan
        )

    # --- ANC ---
    df["ANCBucket"] = df["No of ANCs completed"].apply(anc_bucket)

    # --- Registration ---
    df["RegistrationBucket"] = df["days_lmp_to_registration"].apply(registration_bucket)

    # --- Counselling ---
    df["counselling_gap_days"] = df["counselling_visits"] * 30

    # --- Installment timing (proxy) ---
    df["LMPtoINST1"] = df["days_lmp_to_registration"] + 30
    df["LMPtoINST2"] = df["days_lmp_to_registration"] + 60
    df["LMPtoINST3"] = df["days_lmp_to_registration"] + 90

    # --- Log transforms ---
    df["No. of IFA tablets received/procured in last one month_log1p"] = np.log1p(df["ifa_tablets"])
    df["No. of calcium tablets consumed in last one month_log1p"] = np.log1p(df["calcium_tablets"])

    # --- Household asset score ---
    asset_score = (
        df["has_washing_machine"].astype(int) +
        df["has_ac_cooler"].astype(int) +
        df["has_mobile"].astype(int)
    )
    df["Household_Assets_Score_log1p"] = np.log1p(asset_score)

    # --- FINAL STRICT ALIGNMENT ---
    df_final = df[features]

    return df_final
