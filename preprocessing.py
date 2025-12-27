# preprocessing.py
import json
import numpy as np
import pandas as pd
from pathlib import Path

ARTIFACTS_DIR = Path("artifacts")

with open(ARTIFACTS_DIR / "features.json") as f:
    FEATURES = json.load(f)

with open(ARTIFACTS_DIR / "dtypes.json") as f:
    DTYPES = json.load(f)

with open(ARTIFACTS_DIR / "category_maps.json") as f:
    CATEGORY_MAPS = json.load(f)


def preprocess_for_model(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strict preprocessing to EXACTLY match XGBoost training data:
    - column order
    - dtypes
    - categorical universes
    """

    # 1️⃣ Enforce feature order
    df = df[FEATURES].copy()

    # 2️⃣ Coerce numeric columns
    for col, dtype in DTYPES.items():
        if dtype.startswith("int"):
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        elif dtype.startswith("float"):
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)

    # 3️⃣ Apply categorical dtype WITH TRAINED CATEGORIES
    for col, categories in CATEGORY_MAPS.items():
        df[col] = pd.Categorical(
            df[col],
            categories=categories,
            ordered=True
        )

    # 4️⃣ Final sanity check (THIS SAVES YOU FROM SILENT MODEL FAILURE)
    bad_object_cols = [c for c in df.columns if df[c].dtype == "object"]
    if bad_object_cols:
        raise ValueError(
            f"❌ Object dtype columns found (model will fail): {bad_object_cols}"
        )

    return df
