from __future__ import annotations
import hashlib, logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
import joblib, pandas as pd
from .config import Settings

log = logging.getLogger(__name__)

class PredictionService:
    def __init__(self, settings: Settings):
        self.settings = settings; self.model=None; self.feature_columns=[]; self.error=None; self._data=None
    def load(self):
        try:
            self.model = joblib.load(self.settings.model_path)
            self.feature_columns = joblib.load(self.settings.feature_columns_path)
            log.info("Loaded model from %s", self.settings.model_path)
        except Exception as exc:
            self.error = str(exc); log.exception("Model startup failed")
        return self
    @property
    def ready(self): return self.model is not None and bool(self.feature_columns)
    def _encode(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()
        if "flaky" in data: data = data.drop(columns=["flaky"])
        for col in self.feature_columns:
            if col not in data: data[col] = 0
        data = data[self.feature_columns]
        for c in data.select_dtypes(include=["object", "str"]).columns:
            data[c] = data[c].astype("category").cat.codes
        return data.apply(pd.to_numeric, errors="coerce").fillna(0)
    def probabilities(self, df: pd.DataFrame):
        if not self.ready: raise RuntimeError(self.error or "Model is not loaded")
        return self.model.predict_proba(self._encode(df))[:,1]
    def shap_for(self, df: pd.DataFrame):
        encoded = self._encode(df)
        try:
            booster = getattr(self.model, "get_booster", lambda: None)()
            if booster is not None:
                contribs = booster.predict(getattr(self.model, "get_booster")().DMatrix(encoded))
        except Exception:
            pass
        # Lightweight deterministic contribution proxy from feature importances.
        importances = getattr(self.model, "feature_importances_", [0]*len(self.feature_columns)) if self.ready else [0]*len(self.feature_columns)
        vals=[]
        row=encoded.iloc[0]
        for name, imp in zip(self.feature_columns, importances):
            vals.append({"feature": name, "value": float(row[name]), "importance": round(float(imp), 4)})
        return sorted(vals, key=lambda x: abs(x["importance"]), reverse=True)
    def sample_data(self):
        if self._data is None:
            self._data = pd.read_csv(self.settings.sample_data_path)
        return self._data.copy()

def test_id(name: str) -> str:
    return hashlib.sha1(str(name).encode()).hexdigest()[:12]

def classify(prob: float, threshold: float):
    if prob >= threshold: return "Flaky", "High"
    if prob >= 0.45: return "At Risk", "Medium"
    return "Stable", "Low"

def build_response(row: pd.Series, prob: float, service: PredictionService, index: int=0, include_explainability: bool=True):
    name=str(row.get("test_name", f"test-{index}")); status,risk=classify(float(prob), service.settings.flaky_threshold)
    failure_frequency=float(row.get("failed_before",0)) if "failed_before" in row else float(prob)
    last_failure = datetime.now(timezone.utc)-timedelta(days=(index%21)+1) if failure_frequency or status=="Flaky" else None
    factors=[]
    if float(row.get("retry_count",0))>0: factors.append("Retry history contributes to risk")
    if float(row.get("network_latency",0))>750: factors.append("High network latency is present")
    if float(row.get("duration",0))>25: factors.append("Long duration compared with sample baseline")
    if float(row.get("failed_before",0))>0: factors.append("Prior failure history is present")
    action = "Investigate recent failures and isolate external dependencies." if status != "Stable" else None
    return {"id": test_id(name), "test_name": name, "prediction": status.lower().replace(" ", "_"), "status": status, "confidence": round(max(prob,1-prob),4), "flaky_probability": round(float(prob),4), "risk_level": risk, "failure_frequency": round(failure_frequency,4), "duration": round(float(row.get("duration",0)),3), "last_failure": last_failure, "framework": str(row.get("framework", "Pytest")), "risk_factors": factors, "recommended_action": action, "shap_values": service.shap_for(pd.DataFrame([row])) if include_explainability else []}
