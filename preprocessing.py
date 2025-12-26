import numpy as np
import pandas as pd

def preprocess_for_model(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --------------------------------------------------
    # 1. WATER SOURCE CLEANING (Step 3)
    # --------------------------------------------------
    water_map = {
        "Piped into dwelling": "Piped supply (home/yard/stand)",
        "Piped into yard/plot": "Piped supply (home/yard/stand)",
        "Public tap/standpipe": "Piped supply (home/yard/stand)",
        "Hand pump": "Groundwater – handpump/borewell",
        "Tube/borewell": "Groundwater – handpump/borewell",
        "Protected well": "Protected well",
        "Unprotected well": "Surface/Unprotected source",
        "River/dam/lake/pond/canal/irrigation": "Surface/Unprotected source",
        "Tanker/truck": "Delivered / other",
        "Cart with small tank": "Delivered / other",
        "Others": "Delivered / other",
    }

    water_order = [
        "Piped supply (home/yard/stand)",
        "Groundwater – handpump/borewell",
        "Protected well",
        "Surface/Unprotected source",
        "Delivered / other",
    ]

    if "water_source_clean" in df.columns:
        df["water_source_clean"] = pd.Categorical(
            df["water_source_clean"].fillna("Delivered / other"),
            categories=water_order,
            ordered=True
        )

    # --------------------------------------------------
    # 2. EDUCATION CLEANING (Step 4)
    # --------------------------------------------------
    edu_order = [
        "No schooling",
        "Primary (1–5)",
        "Middle (6–8)",
        "Secondary (9–12)",
        "Graduate & above"
    ]

    if "education_clean" in df.columns:
        df["education_clean"] = pd.Categorical(
            df["education_clean"].fillna("No schooling"),
            categories=edu_order,
            ordered=True
        )

    # --------------------------------------------------
    # 3. TOILET TYPE (Step 5)
    # --------------------------------------------------
    toilet_order = [
        "Improved toilet",
        "Pit latrine (basic)",
        "Unimproved / unknown",
        "No facility / open defecation"
    ]

    if "toilet_type_clean" in df.columns:
        df["toilet_type_clean"] = pd.Categorical(
            df["toilet_type_clean"].fillna("Unimproved / unknown"),
            categories=toilet_order,
            ordered=True
        )

    # --------------------------------------------------
    # 4. Hb RISK BIN (Step 16 logic)
    # --------------------------------------------------
    if "measured_HB_risk_bin" in df.columns:
        df["measured_HB_risk_bin"] = pd.Categorical(
            df["measured_HB_risk_bin"],
            categories=["severe_anaemia", "moderate_anaemia", "mild_anaemia", "normal"],
            ordered=True
        )

    # --------------------------------------------------
    # 5. SOCIAL MEDIA CATEGORY
    # --------------------------------------------------
    if "Social_Media_Category" in df.columns:
        df["Social_Media_Category"] = df["Social_Media_Category"].astype("category")

    # --------------------------------------------------
    # 6. FORCE CATEGORICAL TYPES
    # --------------------------------------------------
    categorical_cols = [
        "MonthConception",
        "consume_tobacco",
        "consume_alcohol",
        "Status of current chewing of tobacco",
        "RegistrationBucket",
        "ANCBucket",
        "Registered for cash transfer scheme: JSY",
        "Registered for cash transfer scheme: RAJHSRI",
        "Child order/parity"
    ]

    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype("category")

    return df
