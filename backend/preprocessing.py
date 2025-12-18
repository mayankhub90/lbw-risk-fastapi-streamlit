import numpy as np
import pandas as pd

def preprocess_raw_input(raw: dict) -> pd.DataFrame:
    df = pd.DataFrame([raw])

    # ------------------------------
    # Hb risk bin
    # ------------------------------
    df["measured_HB_risk_bin"] = pd.cut(
        df["measured_HB"],
        bins=[-np.inf, 6, 8, 11, np.inf],
        labels=["severe", "moderate", "mild", "normal"],
        ordered=True
    )

    # ------------------------------
    # LMP-based calculations
    # ------------------------------
    df["LMPtoRegistration"] = (
        pd.to_datetime(df["registration_date"]) -
        pd.to_datetime(df["lmp_date"])
    ).dt.days

    df["RegistrationBucket"] = pd.cut(
        df["LMPtoRegistration"],
        bins=[-1, 30, 90, 180, 999],
        labels=["<1m", "1–3m", "3–6m", ">6m"]
    )

    # ------------------------------
    # ANC bucket
    # ------------------------------
    def anc_bucket(x):
        if x == 0: return "None"
        if x <= 2: return "Low"
        if x <= 4: return "Medium"
        return "Adequate"

    df["ANCBucket"] = df["No of ANCs completed"].apply(anc_bucket)

    # ------------------------------
    # Counselling gap
    # ------------------------------
    dates = ["pc_pw1", "pc_pw2", "pc_pw3", "pc_pw4"]
    for c in dates:
        df[c] = pd.to_datetime(df[c], errors="coerce")

    def gap(row):
        d = row[dates].dropna().sort_values()
        if len(d) < 2:
            return 999
        return (d.iloc[1] - d.iloc[0]).days

    df["counselling_gap_days"] = df.apply(gap, axis=1)

    # ------------------------------
    # LMP → Installments
    # ------------------------------
    for i in [1, 2, 3]:
        col = f"inst{i}_date"
        df[col] = pd.to_datetime(df[col], errors="coerce")
        df[f"LMPtoINST{i}"] = (
            df[col] - pd.to_datetime(df["lmp_date"])
        ).dt.days.fillna(999)

    # ------------------------------
    # Log transforms
    # ------------------------------
    df["No. of IFA tablets received/procured in last one month_log1p"] = np.log1p(
        df["ifa_tabs"]
    )
    df["No. of calcium tablets consumed in last one month_log1p"] = np.log1p(
        df["calcium_tabs"]
    )

    # ------------------------------
    # Household assets score
    # ------------------------------
    df["Household_Assets_Score_log1p"] = np.log1p(
        df["has_washing_machine"].astype(int) +
        df["has_ac_cooler"].astype(int)
    )

    return df
