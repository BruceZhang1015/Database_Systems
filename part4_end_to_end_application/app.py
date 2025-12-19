import pandas as pd
import numpy as np
import joblib
from typing import Tuple
from database import store_claim_risk_result

from dotenv import load_dotenv
load_dotenv()

from pymongo import MongoClient
from datetime import datetime
import os
from typing import Dict, Any


# --------------------------------------------------
# 1. Preprocessing function
# --------------------------------------------------
def preprocess_input(df: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
    """
    Apply the same preprocessing steps used during training.
    Returns processed X and feature list.
    """

    df = df.copy()

    # -------------------------
    # One-hot encode policy_type
    # -------------------------
    categorical_cols = ["policy_type"]
    df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

    # -------------------------
    # Datetime → numeric
    # -------------------------
    df_encoded["policy_start_date"] = pd.to_datetime(
        df_encoded["policy_start_date"], errors="coerce"
    )
    df_encoded["last_claim_date"] = pd.to_datetime(
        df_encoded["last_claim_date"], errors="coerce"
    )

    reference_date = pd.to_datetime("2025-01-01")

    df_encoded["policy_age_days"] = (
        reference_date - df_encoded["policy_start_date"]
    ).dt.days

    if "days_since_last_claim" not in df_encoded.columns:
        df_encoded["days_since_last_claim"] = (
            reference_date - df_encoded["last_claim_date"]
        ).dt.days.fillna(9999)

    # -------------------------
    # Drop raw datetime columns
    # -------------------------
    datetime_cols_to_drop = [
        "policy_start_date",
        "last_claim_date",
    ]
    df_encoded = df_encoded.drop(columns=datetime_cols_to_drop, errors="ignore")

    # -------------------------
    # Feature selection
    # -------------------------
    exclude_cols = [
        "raw_text",
        "will_file_claim",
        "policy_id",
        "customer_id",
    ]

    features = [c for c in df_encoded.columns if c not in exclude_cols]

    X = df_encoded[features]

    return X, features


# --------------------------------------------------
# 2. Claim Risk Model wrapper
# --------------------------------------------------
class ClaimRiskModel:
    def __init__(self, model_path: str):
        """
        Load trained Random Forest model.
        """
        self.model = joblib.load(model_path)

    def predict_probability(self, df_input: pd.DataFrame) -> float:
        """
        Predict probability of filing a claim.
        """
        X, _ = preprocess_input(df_input)

        prob = self.model.predict_proba(X)[:, 1]

        # single-row input → return scalar
        return float(prob[0])

    def predict_risk_tier(self, df_input: pd.DataFrame) -> str:
        """
        Convert probability into business-friendly risk tier.
        """
        prob = self.predict_probability(df_input)

        if prob < 0.3:
            return "Low"
        elif prob < 0.6:
            return "Medium"
        else:
            return "High"
