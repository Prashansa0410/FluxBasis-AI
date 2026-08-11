# FluxBasis AI Architecture

## Current repository audit

FluxBasis AI currently contains a compact Python ML prototype:

- `src/train_model.py` trains an XGBoost classifier from `data/sample_test_results.csv`, writes `model/flaky_model.pkl`, saves the inference column order to `model/feature_columns.pkl`, and exports static report images.
- `src/api.py` exposes a minimal FastAPI API with `/`, `/predict`, and `/predict-csv`, loading the model and feature columns at import time.
- `api.py` contains an older placeholder `/predict-flaky` route that does not use the ML model.
- `src/dashboard.py` is a Streamlit upload dashboard that reuses the saved model and shows predictions plus static feature/SHAP report images.
- `src/explainability.py` creates static SHAP summary assets from the sample dataset and trained model.
- `data/sample_test_results.csv` is the only available execution dataset. There is no persistent database, no historical run store, and no production frontend.

## What works today

- Model training and persisted model artifacts are present.
- Batch and single-row prediction are possible with the saved feature order.
- Static SHAP and feature-importance images exist.
- Sample data is sufficient to derive a demo dashboard, predictions list, test details, and aggregate analytics without fabricating unrelated metrics.

## Target architecture

```text
Browser
  |
  v
Next.js frontend (TypeScript, Tailwind, Recharts)
  |
  v
FastAPI backend
  |
  +--> Prediction service
  +--> XGBoost model artifacts
  +--> SHAP/feature importance explanations
  +--> Sample test execution repository
  +--> Analytics and insights services
```

## Production approach

- Keep ML behavior stable: the XGBoost model, feature columns, and `> 0.7` flaky threshold remain the source of prediction truth.
- Replace import-time model loading with an application-lifetime prediction service that reports readiness and fails gracefully.
- Add typed versioned REST endpoints under `/api/v1` while keeping legacy `/predict` and `/predict-csv` compatibility routes.
- Use the existing CSV as a read-only repository for dashboard/test-run views. No database is introduced because the project has no ingestion workflow requiring persistence yet.
- Create a dedicated Next.js UI that consumes the FastAPI API and presents empty/error/loading states when data is unavailable.
- Keep training and explainability scripts separate from API and frontend presentation code.
