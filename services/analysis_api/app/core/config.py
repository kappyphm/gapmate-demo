"""Application configuration (env-driven)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "GapMate Analysis API"
    pipeline_version: str = "0.3.0"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_embed_model: str = "gemini-embedding-001"
    gemini_timeout_seconds: int = 45

    internal_api_key: str = "change-me-internal-key"
    data_dir: str = "/data"


settings = Settings()
