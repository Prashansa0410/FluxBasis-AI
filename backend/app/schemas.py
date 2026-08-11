from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field

class TestInput(BaseModel):
    test_name: str | int = Field(default=0)
    duration: float = Field(ge=0)
    retry_count: int = Field(ge=0)
    cpu_usage: int = Field(ge=0, le=100)
    network_latency: int = Field(ge=0)
    failed_before: int = Field(ge=0, le=1)
    framework: str | None = None

class PredictionResponse(BaseModel):
    id: str
    test_name: str
    prediction: str
    status: str
    confidence: float
    flaky_probability: float
    risk_level: str
    failure_frequency: float
    duration: float
    last_failure: datetime | None
    framework: str
    risk_factors: list[str]
    recommended_action: str | None
    shap_values: list[dict]

class TestSummary(PredictionResponse):
    pass

class TestRun(BaseModel):
    id: str
    timestamp: datetime
    total_tests: int
    passed: int
    failed: int
    flaky: int
    duration: float
    reliability_score: float

class Analytics(BaseModel):
    reliability_score: float
    tests_analyzed: int
    flaky_tests: int
    at_risk_tests: int
    model_accuracy: float | None
    reliability_trend: list[dict]
    flaky_trend: list[dict]
    outcome_distribution: list[dict]
    confidence_distribution: list[dict]
    recent_runs: list[TestRun]
    top_flaky_tests: list[TestSummary]

class Insight(BaseModel):
    title: str
    description: str
    recommended_action: str | None = None
    severity: str = "info"
    test_id: str | None = None

class ModelInfo(BaseModel):
    loaded: bool
    model_type: str | None
    feature_columns: list[str]
    threshold: float
    artifacts: dict
