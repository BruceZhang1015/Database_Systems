import pandas as pd
import numpy as np

np.random.seed(42)

def generate_dataset(n=20000):
    # --------------------------
    # 1. Basic demographic info
    # --------------------------
    age = np.random.randint(20, 80, n)
    income = np.random.normal(70000, 20000, n).clip(20000, 150000)
    credit_score = np.random.normal(700, 40, n).clip(550, 850)
    driving_score = np.random.normal(80, 10, n).clip(40, 99)
    engagement_score = np.random.normal(70, 15, n).clip(20, 100)
    sentiment_score = np.random.normal(0, 0.3, n).clip(-1, 1)
    bmi = np.random.normal(26, 4, n).clip(16, 40)
    smoker_flag = np.random.binomial(1, 0.15, n)

    # --------------------------
    # 2. Policy & behavior info
    # --------------------------
    premium = np.random.normal(1200, 300, n).clip(400, 3000)
    coverage_amount = np.random.normal(200000, 50000, n).clip(50000, 500000)
    deductible = np.random.randint(200, 2000, n)

    past_claim_count = np.random.poisson(0.6, n).clip(0, 5)
    past_claim_amount_total = (past_claim_count *
                               np.random.normal(3000, 1200, n).clip(500, 8000))
    max_severity = np.random.randint(1, 6, n)

    # policy age
    policy_age_days = np.random.randint(300, 2500, n)

    days_since_last_claim = np.array([
        np.random.randint(30, 2000) if c > 0 else 9999
        for c in past_claim_count
    ])

    mobile_app_logins = np.random.poisson(8, n).clip(0, 30)
    response_time_minutes = np.random.normal(20, 8, n).clip(5, 60)
    property_risk_index = np.random.normal(0.5, 0.2, n).clip(0, 1)
    risk_zone = np.random.randint(1, 5, n)

    # Categorical variables
    policy_type = np.random.choice(["Health", "Life", "Home"], n)
    gender = np.random.choice(["Male", "Female"], n)
    marital_status = np.random.choice(["Single", "Married", "Widowed"], n)
    employment_status = np.random.choice(["Employed", "Unemployed",
                                          "Student", "Self-Employed"], n)
    region = np.random.choice(["New York", "Florida",
                               "Texas", "Nevada",
                               "California"], n)

    # ---------------------------------------------------
    # 3. STRONG SIGNAL CLAIM PROBABILITY (LOGISTIC MODEL)
    # ---------------------------------------------------

    # non-linear risk factors
    logit = (
        # Driving quality (strong)
        -0.10 * (driving_score - 70)
        # Credit score (strong)
        -0.012 * (credit_score - 680)
        # Engagement (medium)
        -0.04 * (engagement_score - 60)
        # Sentiment (medium)
        +0.7 * sentiment_score
        # Past claim counts
        +0.45 * past_claim_count
        # Property risk
        +1.2 * property_risk_index
        # High BMI (slightly risky)
        +0.03 * (bmi - 25)
        # Smoking
        +0.8 * smoker_flag
        # Very low income slightly increases fraud probability
        -0.000012 * income
    )

    # small noise (keeps model learnable)
    logit += np.random.normal(0, 0.25, n)

    p = 1 / (1 + np.exp(-logit))

    # probability clipping
    p = p.clip(0.01, 0.99)

    will_file_claim = np.random.binomial(1, p)

    # ---------------------------------
    # 4. Put into DataFrame
    # ---------------------------------
    df = pd.DataFrame({
        "policy_id": np.arange(n),
        "customer_id": np.arange(n) + 10000,
        "policy_type": policy_type,
        "premium": premium,
        "coverage_amount": coverage_amount,
        "deductible": deductible,
        "age": age,
        "gender": gender,
        "marital_status": marital_status,
        "region": region,
        "income": income,
        "credit_score": credit_score,
        "employment_status": employment_status,
        "engagement_score": engagement_score,
        "mobile_app_logins": mobile_app_logins,
        "response_time_minutes": response_time_minutes,
        "risk_zone": risk_zone,
        "past_claim_count": past_claim_count,
        "past_claim_amount_total": past_claim_amount_total,
        "max_severity": max_severity,
        "days_since_last_claim": days_since_last_claim,
        "driving_score": driving_score,
        "bmi": bmi,
        "smoker_flag": smoker_flag,
        "property_risk_index": property_risk_index,
        "sentiment_score": sentiment_score,
        "policy_age_days": policy_age_days,
        "will_file_claim": will_file_claim
    })

    return df


if __name__ == "__main__":
    df = generate_dataset(20000)
    df.to_csv("dataset_strong.csv", index=False)
    df.to_parquet("dataset_strong.parquet", index=False)
    print("Done! Strong-signal dataset generated.")
