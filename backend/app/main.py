import logging
from datetime import datetime, timezone, timedelta
import pandas as pd
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import get_settings
from .schemas import TestInput, PredictionResponse, Analytics, Insight, ModelInfo, TestRun, TestSummary
from .services import PredictionService, build_response, test_id

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
settings = get_settings()
service = PredictionService(settings).load()

app = FastAPI(title=settings.app_name, version="2.0.0", description="AI-powered flaky test prediction and CI reliability API")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=False, allow_methods=["GET","POST"], allow_headers=["*"])

@app.exception_handler(Exception)
async def all_errors(request: Request, exc: Exception):
    logging.getLogger(__name__).exception("Unhandled API error")
    return JSONResponse(status_code=500, content={"error":{"code":"internal_error","message":"Unexpected server error"}})

def require_ready():
    if not service.ready:
        raise HTTPException(status_code=503, detail={"code":"model_unavailable","message": service.error or "Model is not loaded"})

@app.get("/health")
def health():
    return {"status":"ok" if service.ready else "degraded", "ready": service.ready, "model_loaded": service.ready, "timestamp": datetime.now(timezone.utc)}

@app.post(f"{settings.api_prefix}/predictions", response_model=PredictionResponse)
def create_prediction(payload: TestInput):
    require_ready(); row = pd.Series(payload.model_dump())
    prob = service.probabilities(pd.DataFrame([row]))[0]
    return build_response(row, prob, service)

@app.get(f"{settings.api_prefix}/predictions", response_model=list[TestSummary])
def list_predictions(limit: int = 100):
    require_ready(); df=service.sample_data().head(min(limit,500)); probs=service.probabilities(df)
    return [build_response(row, prob, service, i, include_explainability=False) for i, (idx,row), prob in zip(range(len(df)), df.iterrows(), probs)]

@app.get(f"{settings.api_prefix}/tests", response_model=list[TestSummary])
def list_tests(limit: int = 100):
    return list_predictions(limit)

def runs() -> list[TestRun]:
    df=service.sample_data(); out=[]; now=datetime.now(timezone.utc)
    chunks=[df.iloc[i:i+250] for i in range(0, min(len(df),2500), 250)]
    for n, ch in enumerate(chunks):
        flaky=int(ch.get("flaky", pd.Series(dtype=int)).sum()) if "flaky" in ch else 0
        failed=int(ch.get("failed_before", pd.Series(dtype=int)).sum()) if "failed_before" in ch else flaky
        total=len(ch); passed=max(total-failed,0); rel=round((passed/total)*100,2) if total else 0
        out.append(TestRun(id=f"run-{n+1:03d}", timestamp=now-timedelta(days=len(chunks)-n), total_tests=total, passed=passed, failed=failed, flaky=flaky, duration=round(float(ch["duration"].sum()),2), reliability_score=rel))
    return out

@app.get(f"{settings.api_prefix}/tests/runs", response_model=list[TestRun])
def test_runs():
    require_ready(); return runs()

@app.get(f"{settings.api_prefix}/tests/{{test_id_value}}", response_model=TestSummary)
def get_test(test_id_value: str):
    require_ready(); df=service.sample_data(); probs=service.probabilities(df)
    for i, ((_, row), prob) in enumerate(zip(df.iterrows(), probs)):
        if test_id(str(row.get("test_name"))) == test_id_value:
            return build_response(row, prob, service, i)
    raise HTTPException(status_code=404, detail={"code":"not_found","message":"Test not found"})

@app.get(f"{settings.api_prefix}/analytics", response_model=Analytics)
def analytics():
    require_ready(); df=service.sample_data(); probs=service.probabilities(df); built=[build_response(r,p,service,i, include_explainability=False) for i, ((_,r),p) in enumerate(zip(df.iterrows(), probs))]
    flaky=[b for b in built if b["status"]=="Flaky"]; risk=[b for b in built if b["status"]=="At Risk"]
    rs=runs(); rel=sum(r.reliability_score for r in rs)/len(rs) if rs else 0
    return {"reliability_score": round(rel,2), "tests_analyzed": len(df), "flaky_tests": len(flaky), "at_risk_tests": len(risk), "model_accuracy": None, "reliability_trend": [{"date":r.timestamp.date().isoformat(),"score":r.reliability_score} for r in rs], "flaky_trend": [{"date":r.timestamp.date().isoformat(),"flaky":r.flaky} for r in rs], "outcome_distribution": [{"name":"Passed","value":int(sum(r.passed for r in rs))},{"name":"Failed","value":int(sum(r.failed for r in rs))},{"name":"Flaky","value":int(sum(r.flaky for r in rs))}], "confidence_distribution": [{"bucket":"0-50","count":int(sum(bool(b["confidence"]<.5) for b in built))},{"bucket":"50-75","count":int(sum(bool(.5<=b["confidence"]<.75) for b in built))},{"bucket":"75-100","count":int(sum(bool(b["confidence"]>=.75) for b in built))}], "recent_runs": rs[-5:][::-1], "top_flaky_tests": sorted(flaky, key=lambda x:x["flaky_probability"], reverse=True)[:8]}

@app.get(f"{settings.api_prefix}/insights", response_model=list[Insight])
def insights():
    a=analytics(); items=[]
    if a.flaky_tests: items.append({"title":"Most unstable tests need attention","description":f"{a.flaky_tests} tests are currently predicted flaky from the available sample execution data.","recommended_action":"Prioritize the highest-probability tests and inspect retry/failure history.","severity":"high"})
    if a.at_risk_tests: items.append({"title":"At-risk tests are close to the flaky threshold","description":f"{a.at_risk_tests} tests have elevated model probability but are below the flaky threshold.","recommended_action":"Monitor these tests before enabling strict CI gates.","severity":"medium"})
    if not items: items.append({"title":"No actionable reliability issues found","description":"The available dataset does not currently produce flaky or at-risk predictions.","severity":"info"})
    return items

@app.get(f"{settings.api_prefix}/model/info", response_model=ModelInfo)
def model_info():
    return {"loaded": service.ready, "model_type": type(service.model).__name__ if service.model else None, "feature_columns": service.feature_columns, "threshold": settings.flaky_threshold, "artifacts": {"model": str(settings.model_path), "features": str(settings.feature_columns_path)}}

# legacy compatibility
@app.get("/")
def root(): return {"message":"FluxBasis AI API is running", "docs":"/docs"}
@app.post("/predict")
def legacy_predict(payload: TestInput):
    r=create_prediction(payload); return {"flaky_probability": r.flaky_probability, "prediction": "flaky" if r.status=="Flaky" else "stable"}
@app.post("/predict-csv")
async def predict_csv(file: UploadFile = File(...)):
    require_ready(); df=pd.read_csv(file.file); probs=service.probabilities(df); return [{"row":i,"flaky_probability":round(float(p),4),"prediction":"flaky" if p>settings.flaky_threshold else "stable"} for i,p in enumerate(probs)]
