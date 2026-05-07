import pandas as pd
import joblib
from pathlib import Path
from sklearn.preprocessing import LabelEncoder

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Paths
MODEL_PATH = BASE_DIR / "model" / "flaky_model.pkl"
INPUT_CSV = BASE_DIR / "data" / "sample_test_results.csv"
OUTPUT_DIR = BASE_DIR / "reports"

# Create reports directory
OUTPUT_DIR.mkdir(exist_ok=True)

print("Loading model...")

# Load model
model = joblib.load(MODEL_PATH)

print("Loading dataset...")

# Load dataset
data = pd.read_csv(INPUT_CSV)

print("Preprocessing dataset...")

# Remove target column if exists
if "flaky" in data.columns:
    data = data.drop(columns=["flaky"])

# Encode categorical columns
for column in data.select_dtypes(include=["object"]).columns:
    le = LabelEncoder()
    data[column] = le.fit_transform(data[column].astype(str))

print("Generating predictions...")

# Predictions
prediction_labels = model.predict(data)

# Prediction probabilities
prediction_probs = model.predict_proba(data)[:, 1]

# Final results
results = data.copy()

results["prediction"] = prediction_labels
results["flaky_probability"] = prediction_probs

# Save predictions
output_file = OUTPUT_DIR / "predictions.csv"

results.to_csv(output_file, index=False)

print(f"Predictions saved successfully to: {output_file}")