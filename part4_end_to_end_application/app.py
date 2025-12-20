import pandas as pd
from datetime import date
from pathlib import Path
import streamlit as st

from dotenv import load_dotenv
load_dotenv()

from ml_module import ClaimRiskModel
from database import store_claim_risk_result


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
    base_dir = Path(__file__).resolve().parents[1]
    model_path = base_dir / "part3_physical_model_ml" / "models" / "rf_claim_model.joblib"
    return ClaimRiskModel(model_path=str(model_path))


model = load_model()


# --------------------------------------------------
# Input form
# --------------------------------------------------
st.header("Submit Insurance Quote / Policy Update Request")

with st.form("underwriting_form"):

    # -------- Core policy info --------
    policy_type = st.selectbox("Policy Type", ["Auto", "Home", "Life"])
    age = st.number_input("Age", min_value=18, max_value=100, value=35)
    income = st.number_input("Annual Income (USD)", min_value=0, value=60000)
    credit_score = st.number_input("Credit Score", min_value=300, max_value=850, value=700)

    # -------- Claim history --------
    past_claim_count = st.number_input("Past Claim Count", min_value=0, value=0)
    past_claim_amount_total = st.number_input(
        "Total Past Claim Amount", min_value=0.0, value=0.0
    )

    # -------- Required categorical features --------
    gender = st.selectbox("Gender", ["Male", "Female"])
    marital_status = st.selectbox("Marital Status", ["Single", "Married"])
    region = st.selectbox("Region", ["North", "South", "East", "West"])
    employment_status = st.selectbox(
        "Employment Status",
        ["Employed", "Self-employed", "Unemployed"]
    )
    risk_zone = st.selectbox("Risk Zone", ["Low", "Medium", "High"])

    # -------- Other features --------
    sentiment_score = st.slider(
        "Sentiment Score (from unstructured text)",
        min_value=-1.0, max_value=1.0, value=0.0, step=0.1
    )

    submitted = st.form_submit_button("Run Risk Assessment")


# --------------------------------------------------
# End-to-end workflow execution
# --------------------------------------------------
if submitted:
    st.divider()
    st.header("Underwriting Result")

    # -------- Build input DataFrame (FULL schema) --------
    input_df = pd.DataFrame([{
        "policy_type": policy_type,
        "age": age,
        "income": income,
        "credit_score": credit_score,
        "past_claim_count": past_claim_count,
        "past_claim_amount_total": past_claim_amount_total,
        "gender": gender,
        "marital_status": marital_status,
        "region": region,
        "employment_status": employment_status,
        "risk_zone": risk_zone,
        "sentiment_score": sentiment_score
    }])

    st.subheader("Input Summary")
    st.dataframe(input_df)

    # -------- ML inference --------
    with st.spinner("Predicting claim likelihood..."):
        claim_prob = model.predict_probability(input_df)
        risk_tier = model.predict_risk_tier(input_df)

    col1, col2 = st.columns(2)
    col1.metric("Claim Probability", f"{claim_prob:.2%}")
    col2.metric("Risk Tier", risk_tier)

    # -------- Decision logic --------
    if risk_tier == "High":
        decision = "Pending Manual Review"
        st.warning("High risk detected. Manual underwriting review required.")
    else:
        decision = "Auto-Approved"
        st.success("Risk within acceptable threshold.")

    st.subheader("Final Decision")
    st.write(decision)

    # -------- Persist to MongoDB --------
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
