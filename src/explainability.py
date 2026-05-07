import os
import joblib
import shap
import pandas as pd
import matplotlib.pyplot as plt

print("Loading feature columns...")

feature_columns = joblib.load("model/feature_columns.pkl")

print("Loading dataset...")

df = pd.read_csv("data/sample_test_results.csv")

# Prepare features
X = df.drop(columns=["flaky"])

# Keep exact same feature order
X = X[feature_columns]

# Ensure numeric
X = X.apply(pd.to_numeric, errors="coerce").fillna(0)

print("SHAP shape:", X.shape)

print("Loading model...")

model = joblib.load("model/flaky_model.pkl")

print("Generating SHAP explainer...")

# IMPORTANT:
# Use new SHAP API
explainer = shap.Explainer(model, X)

print("Calculating SHAP values...")

# IMPORTANT:
# New API usage
shap_values = explainer(X)

os.makedirs("reports", exist_ok=True)

print("Generating beeswarm plot...")

plt.figure()

shap.plots.beeswarm(
    shap_values,
    show=False
)

plt.tight_layout()

plt.savefig(
    "reports/shap_summary.png",
    bbox_inches="tight"
)

plt.close()

print("Generating feature importance plot...")

plt.figure()

shap.plots.bar(
    shap_values,
    show=False
)

plt.tight_layout()

plt.savefig(
    "reports/shap_feature_importance.png",
    bbox_inches="tight"
)

plt.close()

print("SHAP reports generated successfully!")