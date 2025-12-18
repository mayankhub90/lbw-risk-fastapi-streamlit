from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import json
import shap
import numpy as np

# -----------------------
# LOAD ARTIFACTS (ONCE)
# -----------------------
MODEL_PATH = "artifacts/xgb_model.pkl"
FEATURES_PATH = "artifacts/features.json"
BACKGROUND_PATH = "artifacts/background.csv"

model = joblib.load(MODEL_PATH)

FEATURES = json.load(open(FEATURES_PATH))
BACKGROUND = pd.read_csv(BACKGROUND_PATH)

# categorical columns (from training)
CATEGORICAL_COLS = [
    "measured_HB_risk_bin",
    "Child order/parity",
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

# SHAP explainer
explainer = shap.TreeExplainer(model)

app = FastAPI(title="LBW Risk API")

# -----------------------
# INPUT SCHEMA (RAW)
# -----------------------
class LBWInput(BaseModel):
    Beneficiary_age: int
    measured_HB: float
    BMI_PW2_Prog: float

    consume_tobacco: str
    Status_of_current_chewing_of_tobacco: str
    consume_alcohol: str

    No_of_ANCs_completed: int
    Food_Groups_Category: int

    toilet_type_clean: str
    water_source_clean: str
    education_clean: str

    PMMVY_installments: int
    JSY_installments: int


# -----------------------
# PREPROCESSING
# -----------------------
def preprocess(inp: LBWInput) -> pd.DataFrame:
    d = inp.dict()

    # ---- derived features (MATCH TRAINING) ----
    hb = d["measured_HB"]
    if hb < 6:
        d["measured_HB_risk_bin"] = "severe_anaemia"
    elif hb < 8:
        d["measured_HB_risk_bin"] = "moderate_anaemia"
    elif hb < 11:
        d["measured_HB_risk_bin"] = "mild_anaemia"
    else:
        d["measured_HB_risk_bin"] = "normal"

    d["No of ANCs completed"] = d.pop("No_of_ANCs_completed")
    d["PMMVY-Number of installment received"] = d.pop("PMMVY_installments")
    d["JSY-Number of installment received"] = d.pop("JSY_installments")
    d["Status of current chewing of tobacco"] = d.pop("Status_of_current_chewing_of_tobacco")

    # ---- create dataframe ----
    X = pd.DataFrame([d])

    # add missing columns
    for col in FEATURES:
        if col not in X.columns:
            X[col] = np.nan

    X = X[FEATURES]

    # categorical casting
    for col in CATEGORICAL_COLS:
        if col in X.columns:
            X[col] = X[col].astype("category")

    # numeric safety
    for col in X.columns:
        if col not in CATEGORICAL_COLS:
            X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0)

    return X


# -----------------------
# PREDICT ENDPOINT
# -----------------------
@app.post("/predict")
def predict(inp: LBWInput):
    X = preprocess(inp)

    prob = float(model.predict_proba(X)[0, 1])
    label = "High LBW Risk" if prob >= 0.5 else "Lower LBW Risk"

    shap_vals = explainer.shap_values(X)[0]
    shap_df = (
        pd.DataFrame({
            "feature": FEATURES,
            "shap_value": shap_vals
        })
        .assign(abs_val=lambda d: d.shap_value.abs())
        .sort_values("abs_val", ascending=False)
        .head(8)
    )

    return {
        "risk_probability": round(prob, 3),
        "risk_label": label,
        "top_drivers": shap_df[["feature", "shap_value"]].to_dict(orient="records")
    }
