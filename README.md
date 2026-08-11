# FluxBasis AI

FluxBasis AI is an AI-powered flaky test prediction and CI reliability platform. It combines a FastAPI prediction backend, an XGBoost flaky-test model, SHAP-style feature explanations, and a polished Next.js dashboard.

> Make CI reliability predictable.

## Product overview

FluxBasis helps engineering teams understand which automated tests are stable, at risk, or flaky before they become recurring CI blockers. The current implementation uses the repository's trained model artifacts and sample test execution dataset to power predictions, analytics, insights, and test detail pages.

## Architecture

```text
Browser → Next.js frontend → FastAPI backend
                           ├─ Prediction service
                           ├─ XGBoost model artifacts
                           ├─ Feature/SHAP explanations
                           ├─ Sample test execution data
                           └─ Analytics and insights
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the audit and target design.

## ML workflow

- `src/train_model.py` trains the XGBoost classifier from `data/sample_test_results.csv`.
- `model/flaky_model.pkl` contains the trained model.
- `model/feature_columns.pkl` preserves inference column order.
- `src/explainability.py` generates static SHAP report images in `reports/`.
- The production backend keeps the existing `> 0.7` flaky threshold.

## API

- `GET /health`
- `POST /api/v1/predictions`
- `GET /api/v1/predictions`
- `GET /api/v1/tests`
- `GET /api/v1/tests/{test_id}`
- `GET /api/v1/tests/runs`
- `GET /api/v1/analytics`
- `GET /api/v1/insights`
- `GET /api/v1/model/info`

Legacy `/predict` and `/predict-csv` routes remain for compatibility.

## Frontend

The Next.js frontend includes:

- Landing page
- Overview dashboard
- Predictions table with search and filtering
- Test detail page with feature importance explanations
- Test runs page
- Insights page
- Settings/status page

The UI uses TypeScript, Tailwind CSS, and Recharts with a calm, minimalist design.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

In another terminal:

```bash
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Open <http://localhost:3000>.

## Docker setup

```bash
docker compose up --build
```

The frontend runs on <http://localhost:3000> and the backend runs on <http://localhost:8000>.

## Environment variables

Copy `.env.example` and adjust values as needed.

- `FLUXBASIS_ENVIRONMENT`
- `FLUXBASIS_CORS_ORIGINS`
- `NEXT_PUBLIC_API_URL`

## Deployment

Use Vercel for the frontend and Render/Railway for the backend. See [DEPLOYMENT.md](DEPLOYMENT.md) for environment variables, CORS, model artifacts, health checks, and troubleshooting.

## CI/CD integration

GitHub Actions run backend tests, frontend tests, frontend builds, and Docker build verification.

## Supported frameworks

The current product messaging and parser workflow covers Selenium, Playwright, Pytest, and TestNG style test execution data. Additional dedicated ingestion adapters are roadmap items.

## Screenshots

Existing prototype screenshots are available in `screenshots/` for SHAP, classification reports, Swagger, and the original Streamlit dashboard.

## Roadmap

- Add authenticated project workspaces.
- Add real CI ingestion endpoints and durable storage.
- Add trend analytics from persisted test runs.
- Export model artifacts using native XGBoost model serialization.
- Add richer parser support for JUnit XML and Playwright reports.
