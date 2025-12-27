import pandas as pd
import numpy as np

CATEGORICAL_COLS = [
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

NUMERIC_COLS = [
    "Beneficiary age",
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
    "No. of IFA tablets received/procured in last one month_log1p",
    "No. of calcium tablets consumed in last one month_log1p",
    "Household_Assets_Score_log1p",
    "PMMVY-Number of installment received",
    "JSY-Number of installment received",
]

def preprocess_for_model(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # numeric coercion
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # categorical coercion
    for col in CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # 🚨 hard safety check
    bad = df.select_dtypes(include=["object"]).columns.tolist()
    if bad:
        raise ValueError(f"❌ Object dtype columns found: {bad}")

    return df
