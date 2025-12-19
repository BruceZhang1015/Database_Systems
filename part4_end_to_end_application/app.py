import pandas as pd
import numpy as np
import joblib
from typing import Tuple, Dict, Any
from database import store_claim_risk_result

from dotenv import load_dotenv
load_dotenv()

from pymongo import MongoClient
from datetime import datetime, date
import os
import streamlit as st

from ml_module import ClaimRiskModel
from database import store_claim_risk_result


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



# --------------------------------------------------
# Page setup
# --------------------------------------------------
st.set_page_config(
    page_title="Risk-Aware Insurance Underwriting",
    layout="centered"
)

st.title("Risk-Aware Insurance Underwriting System")
st.caption("End-to-end data-driven underwriting workflow (Project Part IV)")


# --------------------------------------------------
# Load ML model
# --------------------------------------------------
@st.cache_resource
def load_model():
    return ClaimRiskModel(
        model_path="../part3_physical_model_ml/models/rf_claim_model.joblib"
    )

model = load_model()


# --------------------------------------------------
# Input form (Submit Request)
# --------------------------------------------------
st.header("Submit Insurance Quote / Policy Update Request")

with st.form("underwriting_form"):
    policy_type = st.selectbox(
        "Policy Type",
        ["Auto", "Home", "Life"]
    )

    age = st.number_input("Age", min_value=18, max_value=100, value=35)
    income = st.number_input("Annual Income", min_value=0, value=60000)
    credit_score = st.number_input("Credit Score", min_value=300, max_value=850, value=700)

    past_claim_count = st.number_input("Past Claim Count", min_value=0, value=0)
    past_claim_amount_total = st.number_input(
        "Total Past Claim Amount", min_value=0.0, value=0.0
    )

    policy_start_date = st.date_input(
        "Policy Start Date", value=date(2022, 1, 1)
    )

    last_claim_date = st.date_input(
        "Last Claim Date (if any)", value=None
    )

    sentiment_score = st.slider(
        "Sentiment Score (derived from unstructured text)",
        min_value=-1.0, max_value=1.0, value=0.0, step=0.1
    )

    submitted = st.form_submit_button("Run Risk Assessment")


# --------------------------------------------------
# End-to-end workflow execution
# --------------------------------------------------
if submitted:
    st.divider()
    st.header("Underwriting Result")

    input_df = pd.DataFrame([{
        "policy_type": policy_type,
        "age": age,
        "income": income,
        "credit_score": credit_score,
        "past_claim_count": past_claim_count,
        "past_claim_amount_total": past_claim_amount_total,
        "policy_start_date": policy_start_date,
        "last_claim_date": last_claim_date,
        "sentiment_score": sentiment_score
    }])

    st.subheader("Input Summary")
    st.dataframe(input_df)

    with st.spinner("Predicting claim likelihood..."):
        claim_prob = model.predict_probability(input_df)
        risk_tier = model.predict_risk_tier(input_df)

    col1, col2 = st.columns(2)
    col1.metric("Claim Probability", f"{claim_prob:.2%}")
    col2.metric("Risk Tier", risk_tier)

    if risk_tier == "High":
        decision = "Pending Manual Review"
        st.warning("High risk detected. Manual underwriting review required.")
    else:
        decision = "Auto-Approved"
        st.success("Risk within acceptable threshold.")

    st.subheader("Final Decision")
    st.write(decision)

    # Persist to MongoDB
    record = {
        "customer_id": None,
        "policy_id": None,
        "policy_type": policy_type,
        "features": input_df.to_dict(orient="records")[0],
        "claim_probability": claim_prob,
        "risk_tier": risk_tier,
        "decision": decision
    }

    store_claim_risk_result(record)

    st.info("Decision and risk assessment successfully stored in MongoDB.")
