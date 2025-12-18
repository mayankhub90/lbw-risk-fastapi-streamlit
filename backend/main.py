from fastapi import FastAPI
import joblib, json
import pandas as pd
from preprocessing import preprocess_raw_input

app = FastAPI(title="LBW Risk API")

MODEL_PATH = "artifacts/xgb_model.pkl"
FEATURES_PATH = "artifacts/features.json"

model = joblib.load(MODEL_PATH)
FEATURES = json.load(open(FEATURES_PATH))

@app.post("/predict")
def predict(payload: dict):
    df = preprocess_raw_input(payload)
    X = df[FEATURES]

    prob = model.predict_proba(X)[0, 1]

    return {
        "risk_probability": round(float(prob), 3),
        "risk_label": "High LBW risk" if prob >= 0.5 else "Lower LBW risk"
    }
