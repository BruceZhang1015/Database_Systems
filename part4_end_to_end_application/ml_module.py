import pandas as pd
import numpy as np
import joblib
from typing import Tuple


# --------------------------------------------------
# 1. Preprocessing function
# --------------------------------------------------
def preprocess_input(df: pd.DataFrame, features: list) -> pd.DataFrame:
    df_proc = df.copy()

    categorical_cols = [
        "policy_type", "gender", "marital_status",
        "region", "employment_status", "risk_zone"
    ]

    df_proc = pd.get_dummies(df_proc, columns=categorical_cols, drop_first=True)
    X = df_proc.reindex(columns=features, fill_value=0)

    return X



# --------------------------------------------------
# 2. Claim Risk Model wrapper
# --------------------------------------------------
class ClaimRiskModel:
    def __init__(self, model_path: str):
        bundle = joblib.load(model_path)
        self.model = bundle["model"]
        self.features = bundle["features"]

    def predict_probability(self, df_input: pd.DataFrame) -> float:
        X = preprocess_input(df_input, self.features)
        return float(self.model.predict_proba(X)[:, 1][0])


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
