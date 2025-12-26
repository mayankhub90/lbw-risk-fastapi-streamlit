# preprocessing.py
import numpy as np
import pandas as pd


def preprocess_for_model(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess input dataframe so that it EXACTLY matches
    the structure and dtypes used during XGBoost training.
    """

    df = df.copy()

    # =====================================================
    # 1️⃣ WATER SOURCE CLEANING
    # =====================================================
    water_map = {
        "Piped into dwelling": "Piped supply (home/yard/stand)",
        "Piped into yard/plot": "Piped supply (home/yard/stand)",
        "Public tap/standpipe": "Piped supply (home/yard/stand)",
        "Hand pump": "Groundwater – handpump/borewell",
        "Tube/borewell": "Groundwater – handpump/borewell",
        "Protected well": "Protected well",
        "Unprotected well": "Surface/Unprotected",
        "River/dam/lake/pond/canal/irrigation": "Surface/Unprotected",
        "Tanker/truck": "Delivered / other",
        "Cart with small tank": "Delivered / other",
        "Others": "Delivered / other",
    }

    if "water_source_clean" in df.columns:
        df["water_source_clean"] = (
            df["water_source_clean"]
            .map(water_map)
            .fillna("Delivered / other")
        )

    water_order = [
        "Piped supply (home/yard/stand)",
        "Groundwater – handpump/borewell",
        "Protected well",
        "Surface/Unprotected",
        "Delivered / other",
    ]

    if "water_source_clean" in df.columns:
        df["water_source_clean"] = pd.Categorical(
            df["water_source_clean"],
            categories=water_order,
            ordered=True,
        )

    # =====================================================
    # 2️⃣ EDUCATION CLEANING
    # =====================================================
    edu_map = {
        "No schooling/illiterate": "No schooling",
        "Primary education (up to class 5)": "Primary (1–5)",
        "Middle School (up to class 8)": "Middle (6–8)",
        "High School (up to class 10)": "Secondary (9–12)",
        "Higher secondary (10+2)": "Secondary (9–12)",
        "Undergrad/ Bachelors/ Professional Masters degree": "Graduate & above",
    }

    if "education_clean" in df.columns:
        df["education_clean"] = (
            df["education_clean"]
            .map(edu_map)
            .fillna("No schooling")
        )

    edu_order = [
        "No schooling",
        "Primary (1–5)",
        "Middle (6–8)",
        "Secondary (9–12)",
        "Graduate & above",
    ]

    if "education_clean" in df.columns:
        df["education_clean"] = pd.Categorical(
            df["education_clean"],
            categories=edu_order,
            ordered=True,
        )

    # =====================================================
    # 3️⃣ TOILET TYPE CLEANING
    # =====================================================
    toilet_map = {
        "Flush to Piped Sewer System / Flush Pit Latrine / Septic Tank": "Improved toilet",
        "Improved Pit": "Improved toilet",
        "Pit Latrine With / Without Slab": "Pit latrine (basic)",
        "No Facility / Uses open space or field": "No facility / open defecation",
        "bade jedhani ke yha he en ke ghr me nhi he": "Unimproved / unknown",
        "नही हैं": "Unimproved / unknown",
    }

    if "toilet_type_clean" in df.columns:
        df["toilet_type_clean"] = (
            df["toilet_type_clean"]
            .map(toilet_map)
            .fillna("Unimproved / unknown")
        )

    toilet_order = [
        "Improved toilet",
        "Pit latrine (basic)",
        "Unimproved / unknown",
        "No facility / open defecation",
    ]

    if "toilet_type_clean" in df.columns:
        df["toilet_type_clean"] = pd.Categorical(
            df["toilet_type_clean"],
            categories=toilet_order,
            ordered=True,
        )

    # =====================================================
    # 4️⃣ NUMERIC COERCION (CRITICAL)
    # =====================================================
    numeric_cols = [
        "Beneficiary age",
        "BMI_PW1_Prog",
        "BMI_PW2_Prog",
        "BMI_PW3_Prog",
        "BMI_PW4_Prog",
        "counselling_gap_days",
        "LMPtoINST1",
        "LMPtoINST2",
        "LMPtoINST3",
        "No of ANCs completed",
        "Household_Assets_Score_log1p",
        "No. of IFA tablets received/procured in last one month_log1p",
        "No. of calcium tablets consumed in last one month_log1p",
        "PMMVY-Number of installment received",
        "JSY-Number of installment received",
        "Service received during last ANC: TT Injection given",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # =====================================================
    # 5️⃣ FINAL SAFETY COERCION (XGBOOST FIX)
    # =====================================================
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype("category")

    return df
