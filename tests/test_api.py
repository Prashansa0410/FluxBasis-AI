import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from backend.app.main import health, create_prediction, analytics
from backend.app.schemas import TestInput

def test_health_ready():
    body = health()
    assert 'ready' in body

def test_prediction_validation():
    with pytest.raises(ValidationError):
        TestInput(duration=-1, retry_count=0, cpu_usage=10, network_latency=1, failed_before=0)

def test_prediction_works():
    payload = TestInput(test_name='checkout', duration=22.0, retry_count=1, cpu_usage=80, network_latency=500, failed_before=1)
    body = create_prediction(payload)
    assert 'flaky_probability' in body or hasattr(body, 'flaky_probability')
    status = body['status'] if isinstance(body, dict) else body.status
    assert status in ['Stable','At Risk','Flaky']

def test_analytics_shape():
    body = analytics()
    tests = body['tests_analyzed'] if isinstance(body, dict) else body.tests_analyzed
    assert tests > 0
