import pandas as pd
import numpy as np
import psycopg2
from textblob import TextBlob
from dotenv import load_dotenv
import os

# ----------------------------------------
# 1. Load .env environment variables
# ----------------------------------------
load_dotenv()

DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")

# ----------------------------------------
# 2. Connect to PostgreSQL
# ----------------------------------------
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)

# ----------------------------------------
# 3. Load relational data
# ----------------------------------------
customer = pd.read_sql("SELECT * FROM insurance.customer", conn)
policy = pd.read_sql("SELECT * FROM insurance.policy", conn)
claim = pd.read_sql("SELECT * FROM insurance.claim", conn)
behavior = pd.read_sql("SELECT * FROM insurance.behavior_metrics", conn)

# ----------------------------------------
# 4. Claims Aggregation
# ----------------------------------------
claim_agg = claim.groupby("policy_id").agg(
    past_claim_count=("claim_id", "count"),
    past_claim_amount_total=("claim_amount", "sum"),
    max_severity=("severity_level", "max"),
    last_claim_date=("claim_date", "max")
).reset_index()

claim_agg["days_since_last_claim"] = (
    pd.to_datetime("2025-01-01") - pd.to_datetime(claim_agg["last_claim_date"])
).dt.days

# ----------------------------------------
# 5. Merge all structured tables
# ----------------------------------------
df = (
    policy.merge(customer, on="customer_id")
          .merge(behavior, on="customer_id", how="left")
          .merge(claim_agg, on="policy_id", how="left")
)

df["past_claim_count"] = df["past_claim_count"].fillna(0).astype(int)
df["past_claim_amount_total"] = df["past_claim_amount_total"].fillna(0)
df["max_severity"] = df["max_severity"].fillna(1)
df["days_since_last_claim"] = df["days_since_last_claim"].fillna(9999)

# ----------------------------------------
# 6. Synthetic Features (More Realistic)
# ----------------------------------------
np.random.seed(42)

df["driving_score"] = np.random.normal(70, 12, len(df)).clip(0, 100)
df["bmi"] = np.random.normal(27, 6, len(df)).clip(15, 45)
df["smoker_flag"] = np.random.binomial(1, 0.18, len(df))
df["property_risk_index"] = np.random.randint(1, 6, len(df))

# ----------------------------------------
# 7. NLP Features
# ----------------------------------------
texts = [
    "Minor accident but resolved quickly",
    "Severe collision with significant damage",
    "Windshield cracked by falling debris",
    "Water leak caused interior damage",
    "Medical treatment needed after incident",
    "Small scratch, almost no damage",
    "Theft incident reported in neighborhood",
    "Car vandalized overnight",
    "Minor injury claim submitted"
]

df["raw_text"] = np.random.choice(texts, size=len(df))

def compute_sentiment(t):
    return TextBlob(t).sentiment.polarity

df["sentiment_score"] = df["raw_text"].apply(compute_sentiment)

# ----------------------------------------
# 8. Expand to ~1000 rows
# ----------------------------------------
df_big = pd.concat([df]*100, ignore_index=True)

# Add realistic noise
df_big["income"] += np.random.normal(0, 4000, len(df_big))
df_big["credit_score"] += np.random.normal(0, 15, len(df_big)).astype(int)
df_big["driving_score"] += np.random.normal(0, 4, len(df_big))
df_big["sentiment_score"] += np.random.normal(0, 0.05, len(df_big))

df_big["credit_score"] = df_big["credit_score"].clip(300, 850)
df_big["driving_score"] = df_big["driving_score"].clip(0, 100)

# ----------------------------------------
# 9. Create ML Label (Realistic)
# ----------------------------------------
risk = (
    0.25*(df_big["past_claim_count"] > 0).astype(int)
    + 0.15*(df_big["max_severity"] >= 4).astype(int)
    + 0.10*(df_big["smoker_flag"])
    + 0.10*(df_big["credit_score"] < 620).astype(int)
    + 0.12*(df_big["engagement_score"] < 60).astype(int)
    + 0.10*(df_big["driving_score"] < 50).astype(int)
    + 0.10*(df_big["sentiment_score"] < 0).astype(int)
    + np.random.normal(0, 0.05, len(df_big))
)

# Logistic-like transformation
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

prob = sigmoid(risk)
df_big["will_file_claim"] = np.random.binomial(1, prob)

# ----------------------------------------
# 10. Save final dataset
# ----------------------------------------
df_big.to_csv("dataset.csv", index=False)
df_big.to_parquet("dataset.parquet", index=False)

print("Generated dataset:", df_big.shape)
print(df_big.head())
