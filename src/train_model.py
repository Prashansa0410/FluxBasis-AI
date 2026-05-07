import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

from xgboost import XGBClassifier, plot_importance


print("TRAIN MODEL FILE STARTED")

# ---------------------------------------------------
# CREATE REQUIRED FOLDERS
# ---------------------------------------------------

os.makedirs("model", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# ---------------------------------------------------
# LOAD DATASET
# ---------------------------------------------------

print("Loading dataset...")

data_path = "data/sample_test_results.csv"

data = pd.read_csv(data_path)

# ---------------------------------------------------
# PREPROCESSING
# ---------------------------------------------------

print("Preprocessing data...")

# Fill missing numeric values
data.fillna(data.median(numeric_only=True), inplace=True)

# Encode categorical columns
label_encoders = {}

for column in data.select_dtypes(include=["object"]).columns:

    if column != "flaky":

        le = LabelEncoder()

        data[column] = le.fit_transform(data[column])

        label_encoders[column] = le

# ---------------------------------------------------
# FEATURES / TARGET
# ---------------------------------------------------

X = data.drop("flaky", axis=1)

y = data["flaky"]

# Save feature columns for SHAP/inference consistency
feature_columns = X.columns.tolist()

joblib.dump(feature_columns, "model/feature_columns.pkl")

print("Feature columns saved!")

print("Training shape:", X.shape)

# ---------------------------------------------------
# TRAIN / TEST SPLIT
# ---------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# ---------------------------------------------------
# TRAIN MODEL
# ---------------------------------------------------

print("Training XGBoost model...")

model = XGBClassifier(
    eval_metric="logloss",
    random_state=42
)

model.fit(X_train, y_train)

# ---------------------------------------------------
# PREDICTIONS
# ---------------------------------------------------

print("Evaluating model...")

y_pred = model.predict(X_test)

# ---------------------------------------------------
# METRICS
# ---------------------------------------------------

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(y_test, y_pred)

recall = recall_score(y_test, y_pred)

f1 = f1_score(y_test, y_pred)

print("\nModel Metrics")

print(f"Accuracy : {accuracy:.4f}")

print(f"Precision: {precision:.4f}")

print(f"Recall   : {recall:.4f}")

print(f"F1 Score : {f1:.4f}")

print("\nClassification Report:")

report = classification_report(y_test, y_pred)

print(report)

# Save report to file
with open("reports/classification_report.txt", "w") as f:
    f.write(report)

# ---------------------------------------------------
# SAVE MODEL
# ---------------------------------------------------

print("Saving model...")

joblib.dump(model, "model/flaky_model.pkl")

print("Model saved successfully!")

# ---------------------------------------------------
# FEATURE IMPORTANCE
# ---------------------------------------------------

print("Generating feature importance chart...")

plt.figure(figsize=(10, 6))

plot_importance(model)

plt.title("Feature Importance")

plt.tight_layout()

plt.savefig("reports/feature_importance.png")

plt.close()

print("Feature importance chart saved!")

print("\nTraining completed successfully!")