"""Application configuration (env-driven)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "GapMate Analysis API"
    pipeline_version: str = "0.1.0"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    gemini_embed_model: str = "text-embedding-004"

    internal_api_key: str = "change-me-internal-key"
    data_dir: str = "/data"


settings = Settings()
