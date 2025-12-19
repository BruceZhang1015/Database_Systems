import os
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from pymongo import MongoClient

# ---- Optional: load .env robustly ----
try:
    from dotenv import load_dotenv, find_dotenv

    # 1) Try: find .env from current working directory upward
    env_path = find_dotenv(usecwd=True)

    # 2) Fallback: assume project root is parent of this file's folder
    if not env_path:
        env_path = str(Path(__file__).resolve().parents[1] / ".env")

    load_dotenv(env_path, override=False)
except Exception:
    # If python-dotenv isn't installed, we will rely on Streamlit secrets or real env vars
    env_path = None


def _get_mongo_uri() -> str:
    """
    Resolve MongoDB URI from:
    1) OS env var MONGO_URI
    2) Streamlit secrets (MONGO_URI or mongo.uri)
    """
    uri = os.getenv("MONGO_URI")
    if uri:
        return uri

    # Streamlit secrets fallback (works great for Streamlit)
    try:
        import streamlit as st

        # allow either flat key or nested
        if "MONGO_URI" in st.secrets:
            return st.secrets["MONGO_URI"]

        if "mongo" in st.secrets and "uri" in st.secrets["mongo"]:
            return st.secrets["mongo"]["uri"]
    except Exception:
        pass

    raise ValueError(
        "MONGO_URI is not set. "
        "Set it in OS env, in a .env file, or in .streamlit/secrets.toml."
    )


# --------------------------------------------------
# MongoDB connection
# --------------------------------------------------
MONGO_URI = _get_mongo_uri()
client = MongoClient(MONGO_URI)

db = client["insurance_db"]
claims_collection = db["claims_ds"]


def store_claim_risk_result(record: Dict[str, Any]) -> None:
    document = {
        "customer_id": record.get("customer_id"),
        "policy_id": record.get("policy_id"),
        "policy_type": record.get("policy_type"),

        "features": record.get("features"),

        "claim_probability": record.get("claim_probability"),
        "risk_tier": record.get("risk_tier"),

        "decision": record.get("decision"),

        "model_version": record.get("model_version", "rf_v1"),
        "created_at": datetime.utcnow(),
    }

    claims_collection.insert_one(document)


def fetch_recent_predictions(limit: int = 5):
    return list(
        claims_collection.find()
        .sort("created_at", -1)
        .limit(limit)
    )
