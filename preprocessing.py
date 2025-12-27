# preprocessing.py
import numpy as np
import pandas as pd

# --------------------------------
# Expected dtypes from training
# --------------------------------
INT_COLS = [
    "Beneficiary age",
    "Number of living child at now",
    "No of ANCs completed",
]

FLOAT_COLS = [
    "BMI_PW1_Prog",
    "BMI_PW2_Prog",
    "BMI_PW3_Prog",
    "BMI_PW4_Prog",
    "counselling_gap_days",
    "LMPtoINST1",
    "LMPtoINST2",
    "LMPtoINST3",
    "No. of IFA tablets received/procured in last one month_log1p",
    "No. of calcium tablets consumed in last one month_log1p",
    "Household_Assets_Score_log1p",
    "PMMVY-Number of installment received",
    "JSY-Number of installment received",
]

CAT_COLS = [
    "measured_HB_risk_bin",
    "Child order/parity",
    "MonthConception",
    "consume_tobacco",
    "Status of current chewing of tobacco",
    "consume_alcohol",
    "RegistrationBucket",
    "ANCBucket",
    "Service received during last ANC: TT Injection given",
    "Food_Groups_Category",
    "toilet_type_clean",
    "water_source_clean",
    "education_clean",
    "Social_Media_Category",
    "Registered for cash transfer scheme: JSY",
    "Registered for cash transfer scheme: RAJHSRI",
]

# --------------------------------
def preprocess_for_model(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ---- integers ----
    for col in INT_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")

    # ---- floats ----
    for col in FLOAT_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")

    # ---- categoricals ----
    for col in CAT_COLS:
        df[col] = df[col].astype("category")

    # ---- FINAL SAFETY CHECK ----
    bad_cols = [c for c in df.columns if df[c].dtype == "object"]
    if bad_cols:
        raise ValueError(
            f"❌ Object dtype columns found (XGBoost will fail): {bad_cols}"
        )

    return df
