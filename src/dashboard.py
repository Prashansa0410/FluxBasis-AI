import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="FluxBasis AI",
    layout="wide"
)

st.title("FluxBasis AI Dashboard")

st.markdown("ML-powered flaky test prediction platform")

# ---------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------

model = joblib.load("model/flaky_model.pkl")

feature_columns = joblib.load("model/feature_columns.pkl")

# ---------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload Test Results CSV",
    type=["csv"]
)

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    st.subheader("Uploaded Dataset")

    st.dataframe(df.head())

    original_df = df.copy()

    # Remove flaky column if present
    if "flaky" in df.columns:
        df = df.drop(columns=["flaky"])

    # Keep feature order
    df = df[feature_columns]
    # Convert test_name to numeric

    if "test_name" in df.columns:
        df["test_name"] = df["test_name"].astype("category").cat.codes

    probabilities = model.predict_proba(df)[:, 1]

    predictions = [
        "flaky" if p > 0.7 else "stable"
        for p in probabilities
    ]

    original_df["flaky_probability"] = probabilities

    original_df["prediction"] = predictions

    # ---------------------------------------------------
    # METRICS
    # ---------------------------------------------------

    total_tests = len(original_df)

    flaky_tests = len(
        original_df[
            original_df["prediction"] == "flaky"
        ]
    )

    stable_tests = total_tests - flaky_tests

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Tests", total_tests)

    col2.metric("Flaky Tests", flaky_tests)

    col3.metric("Stable Tests", stable_tests)

    # ---------------------------------------------------
    # RESULTS TABLE
    # ---------------------------------------------------

    st.subheader("Prediction Results")

    st.dataframe(original_df)

    # ---------------------------------------------------
    # DOWNLOAD CSV
    # ---------------------------------------------------

    csv = original_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Predictions CSV",
        csv,
        "predictions.csv",
        "text/csv"
    )

    # ---------------------------------------------------
    # FEATURE IMPORTANCE IMAGE
    # ---------------------------------------------------

    st.subheader("Feature Importance")

    st.image("reports/feature_importance.png")

    # ---------------------------------------------------
    # SHAP IMAGE
    # ---------------------------------------------------

    st.subheader("SHAP Explainability")

    st.image("reports/shap_summary.png")