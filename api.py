from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class TestResult(BaseModel):
    name: str
    status: str
    duration: int
    error: Optional[str] = None

@app.post("/predict-flaky")
def predict_flaky(tests: List[TestResult]):
    # Placeholder logic for flaky prediction
    predictions = []
    for test in tests:
        is_flaky = test.status == "flaky" or (test.duration > 5000 and test.status == "failed")
        predictions.append({"name": test.name, "flaky": is_flaky})
    return {"predictions": predictions}
