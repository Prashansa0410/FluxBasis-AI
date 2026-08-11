# Deployment

## Frontend (Vercel)
Set `NEXT_PUBLIC_API_URL` to the deployed backend URL, then deploy the repository with the Next.js project at the repository root.

## Backend (Render or Railway)
Use `Dockerfile.backend` or run `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` after installing `requirements.txt`.

## Environment variables
- `FLUXBASIS_ENVIRONMENT`: `production` for deployed services.
- `FLUXBASIS_CORS_ORIGINS`: JSON list of allowed frontend origins.
- `NEXT_PUBLIC_API_URL`: browser-visible backend base URL.

## Model artifacts
The backend expects `model/flaky_model.pkl` and `model/feature_columns.pkl`. Keep these files with the backend image or attach them as deployment artifacts.

## Health checks
Use `/health`; readiness is true only when model artifacts load successfully.

## Troubleshooting
If predictions return `503`, verify model artifact paths and container working directory. If the browser cannot reach the API, check CORS and `NEXT_PUBLIC_API_URL`.
