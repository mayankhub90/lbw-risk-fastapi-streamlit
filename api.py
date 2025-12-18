# api.py
import json
import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
import shap

# ------------------------
# Load artifacts (ONCE)
# ------------------------
ARTIFACT_DIR = "artifacts"

model = joblib.load(f"{ARTIFACT_DIR}/xgb_model.pkl")

with open(f"{ARTIFACT_DIR}/features.json") as f:
    FEATURES = json.load(f)

BACKGROUND = pd.read_csv(f"{ARTIFACT_DIR}/background.csv")

explainer = shap.TreeExplainer(model, BACKGROUND)

# ------------------------
# FastAPI app
# ------------------------
app = FastAPI(title="LBW Risk Prediction API")

# ------------------------
# Input schema (RAW INPUTS)
# ------------------------
class LBWInput(BaseModel):
    Beneficiary_age: int
    measured_HB: float
    BMI_PW2_Prog: float
    consume_tobacco: str          # Yes / No
    consume_alcohol: str          # Yes / No
    No_of_ANCs_completed: int
    Food_Groups_Category: int
    toilet_type_clean: str        # Yes / No
    education_clean: str
    PMMVY_installments: int
    JSY_installments: int

# ------------------------
# Preprocessing logic
# ------------------------
def preprocess(inp: LBWInput) -> pd.DataFrame:
    row = {}

    # numeric
    row["Beneficiary age"] = inp.Beneficiary_age
    row["BMI_PW2_Prog"] = inp.BMI_PW2_Prog
    row["No of ANCs completed"] = inp.No_of_ANCs_completed
    row["Food_Groups_Category"] = inp.Food_Groups_Category
    row["PMMVY-Number of installment received"] = inp.PMMVY_installments
    row["JSY-Number of installment received"] = inp.JSY_installments

    # binary
    row["consume_tobacco"] = 1 if inp.consume_tobacco == "Yes" else 0
    row["consume_alcohol"] = 1 if inp.consume_alcohol == "Yes" else 0
    row["toilet_type_clean"] = 1 if inp.toilet_type_clean == "Yes" else 0

    # education mapping (same as training)
    edu_map = {
        "Illiterate": 0,
        "Primary": 1,
        "Upper Primary": 2,
        "Secondary": 3,
        "Senior Secondary": 4,
        "Graduate": 5,
        "Graduate and Above": 6
    }
    row["education_clean"] = edu_map.get(inp.education_clean, 0)

    # Hb risk bin
    hb = inp.measured_HB
    if hb < 7:
        row["measured_HB_risk_bin"] = 3
    elif hb < 8:
        row["measured_HB_risk_bin"] = 2
    elif hb < 11:
        row["measured_HB_risk_bin"] = 1
    else:
        row["measured_HB_risk_bin"] = 0

    df = pd.DataFrame([row])

    # enforce correct order
    for f in FEATURES:
        if f not in df.columns:
            df[f] = 0

    return df[FEATURES]

# ------------------------
# Prediction endpoint
# ------------------------
@app.post("/predict")
def predict(inp: LBWInput):
    X = preprocess(inp)
    prob = model.predict_proba(X)[0, 1]

    label = "High Risk (LBW)" if prob >= 0.5 else "Low Risk"

    # SHAP
    shap_vals = explainer.shap_values(X)
    shap_row = shap_vals[0]

    shap_df = (
        pd.DataFrame({
            "feature": FEATURES,
            "shap_value": shap_row
        })
        .assign(abs_val=lambda d: d.shap_value.abs())
        .sort_values("abs_val", ascending=False)
        .head(10)
    )

    return {
        "risk_probability": round(float(prob), 3),
        "risk_label": label,
        "top_drivers": shap_df.to_dict(orient="records")
    }
