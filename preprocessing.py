import numpy as np
import pandas as pd

# =====================================================
# CATEGORY → NUMERIC MAPPINGS
# =====================================================

HB_MAP = {
    "severe_anaemia": 0,
    "moderate_anaemia": 1,
    "mild_anaemia": 2,
    "normal": 3
}

REG_BUCKET_MAP = {"Early": 0, "Mid": 1, "Late": 2}
ANC_BUCKET_MAP = {"Early": 0, "Mid": 1, "Late": 2}

SOCIAL_MEDIA_MAP = {
    "None": 0,
    "Low": 1,
    "Medium": 2,
    "High": 3
}

YES_NO_MAP = {
    "N": 0,
    "Y": 1,
    "O": np.nan,   # Other treated as missing (matches training best practice)
    "No": 0,
    "Yes": 1
}

MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}

TOILET_MAP = {
    "No facility / open defecation": 0,
    "Unimproved / unknown": 1,
    "Pit latrine (basic)": 2,
    "Improved toilet": 3
}

WATER_MAP = {
    "Surface/Unprotected": 0,
    "Delivered / other": 1,
    "Protected well": 2,
    "Groundwater – handpump/borewell": 3,
    "Piped supply": 4
}

EDU_MAP = {
    "No schooling": 0,
    "Primary (1–5)": 1,
    "Middle (6–8)": 2,
    "Secondary (9–12)": 3,
    "Graduate & above": 4
}

# =====================================================
# MAIN PREPROCESS FUNCTION
# =====================================================

def preprocess_for_model(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts raw Streamlit input dataframe into
    numeric dataframe expected by XGBoost model.
    """

    X = df.copy()

    # ---- Ordinal / rule-based encodings ----
    X["measured_HB_risk_bin"] = X["measured_HB_risk_bin"].map(HB_MAP)
    X["RegistrationBucket"] = X["RegistrationBucket"].map(REG_BUCKET_MAP)
    X["ANCBucket"] = X["ANCBucket"].map(ANC_BUCKET_MAP)
    X["Social_Media_Category"] = X["Social_Media_Category"].map(SOCIAL_MEDIA_MAP)

    # ---- Binary variables ----
    X["consume_tobacco"] = X["consume_tobacco"].map(YES_NO_MAP)
    X["consume_alcohol"] = X["consume_alcohol"].map(YES_NO_MAP)
    X["Registered for cash transfer scheme: JSY"] = X[
        "Registered for cash transfer scheme: JSY"
    ].map(YES_NO_MAP)
    X["Registered for cash transfer scheme: RAJHSRI"] = X[
        "Registered for cash transfer scheme: RAJHSRI"
    ].map(YES_NO_MAP)

    # ---- Categorical ordinals ----
    X["MonthConception"] = X["MonthConception"].map(MONTH_MAP)
    X["toilet_type_clean"] = X["toilet_type_clean"].map(TOILET_MAP)
    X["water_source_clean"] = X["water_source_clean"].map(WATER_MAP)
    X["education_clean"] = X["education_clean"].map(EDU_MAP)

    # ---- Replace remaining None with NaN ----
    X = X.replace({None: np.nan})

    return X
