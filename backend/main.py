from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import json
from pathlib import Path

from preprocessing import preprocess_payload

# -----------------------------
# Load artifacts
# -----------------------------
ARTIFACT_DIR = Path("backend/artifacts")

model = joblib.load(ARTIFACT_DIR / "xgb_model.pkl")
FEATURES = json.load(open(ARTIFACT_DIR / "features.json"))
BACKGROUND = pd.read_csv(ARTIFACT_DIR / "background.csv")

app = FastAPI(title="LBW Risk API")

# -----------------------------
# Input schema
# -----------------------------
class LBWInput(BaseModel):
    beneficiary_age: int
    parity: int
    living_children: int
    education_clean: str
    month_conception: int

    lmp_date: str
    registration_date: str

    hemoglobin: float
    height_cm: float
    anc_completed: int
    tt_given: str

    weight_pw1: float | None = None
    weight_pw2: float | None = None
    weight_pw3: float | None = None
    weight_pw4: float | None = None

    food_group: int
    ifa_tabs: int
    calcium_tabs: int

    consume_tobacco: str
    chewing_tobacco: str
    consume_alcohol: str

    washing_machine: str
    ac_cooler: str
    social_media: str

    toilet_type_clean: str
    water_source_clean: str

    pmmvy_count: int
    jsy_count: int
    jsy_registered: str
    raj_registered: str


# -----------------------------
# Prediction endpoint
# -----------------------------
@app.post("/predict")
def predict(input: LBWInput):

    df = preprocess_payload(input.dict())

    # 🔒 Feature alignment safeguard
    df = df[FEATURES]

    prob = model.predict_proba(df)[0, 1]

    label = "High LBW Risk" if prob >= 0.5 else "Lower LBW Risk"

    return {
        "risk_probability": round(float(prob), 3),
        "risk_label": label
    }
