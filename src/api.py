from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from fastapi import UploadFile, File
import io
import joblib

# ---------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------

model = joblib.load("model/flaky_model.pkl")

feature_columns = joblib.load("model/feature_columns.pkl")

# ---------------------------------------------------
# CREATE FASTAPI APP
# ---------------------------------------------------

app = FastAPI(
    title="FluxBasis AI",
    description="ML-powered flaky test prediction API",
    version="1.0"
)

# ---------------------------------------------------
# REQUEST SCHEMA
# ---------------------------------------------------

class TestInput(BaseModel):
    duration: float
    retry_count: int
    cpu_usage: int
    network_latency: int
    failed_before: int
    test_name: int = 0

# ---------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "FlakeGuard AI API is running"
    }

# ---------------------------------------------------
# PREDICTION ENDPOINT
# ---------------------------------------------------

@app.post("/predict")
def predict(test: TestInput):

    input_data = pd.DataFrame([{
        "test_name": test.test_name,
        "duration": test.duration,
        "retry_count": test.retry_count,
        "cpu_usage": test.cpu_usage,
        "network_latency": test.network_latency,
        "failed_before": test.failed_before
    }])

    # Ensure exact feature order
    input_data = input_data[feature_columns]

    # Prediction probability
    probability = model.predict_proba(input_data)[0][1]

    prediction = "flaky" if probability > 0.7 else "stable"

    return {
        "flaky_probability": round(float(probability), 4),
        "prediction": prediction
    }

@app.post("/predict-csv")
async def predict_csv(file: UploadFile = File(...)):

    contents = await file.read()

    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    # Remove flaky column if present
    if "flaky" in df.columns:
        df = df.drop(columns=["flaky"])

    # Keep exact feature order
    df = df[feature_columns]

    probabilities = model.predict_proba(df)[:, 1]

    predictions = []

    for i, prob in enumerate(probabilities):

        predictions.append({
            "row": i,
            "flaky_probability": round(float(prob), 4),
            "prediction": "flaky" if prob > 0.7 else "stable"
        })

    return predictions