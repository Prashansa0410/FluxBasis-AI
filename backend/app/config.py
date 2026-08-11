from functools import lru_cache
from pathlib import Path
from pydantic import Field
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ModuleNotFoundError:  # keeps local/test environments runnable before deps are installed
    from pydantic import BaseModel as BaseSettings
    SettingsConfigDict = dict

ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    app_name: str = "FluxBasis AI"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"])
    model_path: Path = ROOT / "model" / "flaky_model.pkl"
    feature_columns_path: Path = ROOT / "model" / "feature_columns.pkl"
    sample_data_path: Path = ROOT / "data" / "sample_test_results.csv"
    flaky_threshold: float = 0.7
    model_config = SettingsConfigDict(env_file=".env", env_prefix="FLUXBASIS_", case_sensitive=False)

@lru_cache
def get_settings() -> Settings:
    return Settings()
