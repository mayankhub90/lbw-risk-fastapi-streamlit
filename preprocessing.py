# preprocessing.py
import pandas as pd
import numpy as np


def preprocess_for_model(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ---------------------------
    # 1️⃣ Explicit categorical columns
    # ---------------------------
    categorical_cols = [
        "measured_HB_risk_bin",
        "MonthConception",
        "Status of current chewing of tobacco",
        "RegistrationBucket",
        "ANCBucket",
        "toilet_type_clean",
        "water_source_clean",
        "education_clean",
        "Social_Media_Category",
        "Registered for cash transfer scheme: JSY",
        "Registered for cash transfer scheme: RAJHSRI",
    ]

    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # ---------------------------
    # 2️⃣ Force numeric columns
    # ---------------------------
    numeric_cols = [
        "Beneficiary age",
        "Child order/parity",
        "Number of living child at now",
        "BMI_PW1_Prog",
        "BMI_PW2_Prog",
        "BMI_PW3_Prog",
        "BMI_PW4_Prog",
        "counselling_gap_days",
        "LMPtoINST1",
        "LMPtoINST2",
        "LMPtoINST3",
        "No of ANCs completed",
        "Service received during last ANC: TT Injection given",
        "No. of IFA tablets received/procured in last one month_log1p",
        "No. of calcium tablets consumed in last one month_log1p",
        "Food_Groups_Category",
        "Household_Assets_Score_log1p",
        "PMMVY-Number of installment received",
        "JSY-Number of installment received",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ---------------------------
    # 3️⃣ Final safety check
    # ---------------------------
    bad_cols = df.select_dtypes(include="object").columns.tolist()
    if bad_cols:
        raise ValueError(
            f"❌ Object dtype columns found (XGBoost will fail): {bad_cols}"
        )

    return df
