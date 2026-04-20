import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
from preprocessing import preprocess_for_model

st.title("📂 LBW Bulk Prediction (Raw Data → Auto Features → Score)")

# =========================
# LOAD MODEL
# =========================
model = joblib.load("artifacts/xgb_model.pkl")

with open("artifacts/features.json") as f:
    FEATURES_ORDER = json.load(f)

# =========================
# 🔥 FEATURE ENGINEERING
# =========================
def build_features(df):

    df = df.copy()

    # HB bin
    def hb_bin(hb):
        if pd.isna(hb): return np.nan
        elif hb < 6: return "severe_anaemia"
        elif hb < 8: return "moderate_anaemia"
        elif hb < 11: return "mild_anaemia"
        else: return "normal"

    df["measured_HB_risk_bin"] = df["hb_value"].apply(hb_bin)

    # Dates
    df["LMP"] = pd.to_datetime(df["LMP"])
    df["Registration Date"] = pd.to_datetime(df["Registration Date"])
    df["ANC1_Date"] = pd.to_datetime(df["ANC1_Date"])
    df["ANC2_Date"] = pd.to_datetime(df["ANC2_Date"])

    # Month
    df["MonthConception"] = df["LMP"].dt.month_name()

    # Registration bucket
    gap = (df["Registration Date"] - df["LMP"]).dt.days
    df["RegistrationBucket"] = np.select(
        [gap <= 84, gap <= 168],
        ["Early", "Mid"],
        default="Late"
    )

    # ANC bucket
    anc_gap = (df["ANC1_Date"] - df["LMP"]).dt.days
    df["ANCBucket"] = np.select(
        [anc_gap <= 84, anc_gap <= 168],
        ["Early", "Mid"],
        default="Late"
    )

    # Counselling gap
    df["counselling_gap_days"] = (df["ANC2_Date"] - df["ANC1_Date"]).dt.days

    # BMI
    height_m = df["height"] / 100
    for i in range(1, 5):
        df[f"BMI_PW{i}_Prog"] = df[f"ANC{i}_Weight"] / (height_m ** 2)

    # ANC count
    df["No of ANCs completed"] = df[
        ["ANC1_Weight","ANC2_Weight","ANC3_Weight","ANC4_Weight"]
    ].notna().sum(axis=1)

    # IFA / Calcium
    df["No. of IFA tablets received/procured in last one month_log1p"] = np.log1p(df["ifa_tabs"])
    df["No. of calcium tablets consumed in last one month_log1p"] = np.log1p(df["calcium_tabs"])

    # Social media
    def sm_cat(x):
        if x == 0: return "None"
        elif x == 1: return "Low"
        elif x <= 3: return "Medium"
        else: return "High"

    df["Social_Media_Category"] = df["social_media_count"].apply(sm_cat)

    # Installments
    df["inst1_date"] = pd.to_datetime(df["inst1_date"])
    df["inst2_date"] = pd.to_datetime(df["inst2_date"])

    df["LMPtoINST1"] = (df["inst1_date"] - df["LMP"]).dt.days
    df["LMPtoINST2"] = (df["inst2_date"] - df["LMP"]).dt.days
    df["LMPtoINST3"] = np.nan

    return df

# =========================
# FILE UPLOAD
# =========================
uploaded_file = st.file_uploader("Upload raw dataset", type=["xlsx","csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)

    st.subheader("Preview")
    st.dataframe(df.head())

    if st.button("🚀 Run Full Pipeline"):

        with st.spinner("Running full pipeline..."):

            try:
                # 1️⃣ Feature engineering
                df = build_features(df)

                # 2️⃣ Align features
                for col in FEATURES_ORDER:
                    if col not in df.columns:
                        df[col] = np.nan

                X = df[FEATURES_ORDER]

                # 3️⃣ Preprocess
                X_processed = preprocess_for_model(X)

                # 4️⃣ Predict
                probs = model.predict_proba(X_processed)[:, 1]

                df["lbw_prob"] = probs
                df["lbw_percent"] = (probs * 100).round(2)

                # 5️⃣ Risk category
                df["risk_category"] = np.select(
                    [df["lbw_percent"] < 35, df["lbw_percent"] < 50],
                    ["No Risk", "Mild Risk"],
                    default="High Risk"
                )

                st.success("✅ Done!")

                st.dataframe(df)

                # Download
                st.download_button(
                    "📥 Download Results",
                    df.to_csv(index=False).encode("utf-8"),
                    "LBW_results.csv",
                    "text/csv"
                )

            except Exception as e:
                st.error(f"❌ Error: {e}")
