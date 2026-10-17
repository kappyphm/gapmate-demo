"""Application configuration (env-driven)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "GapMate Core API"

    # DB
    database_url: str = "postgresql+asyncpg://gapmate:gapmate@postgres:5432/gapmate"

    # Auth
    jwt_secret: str = "change-me-to-a-long-random-string"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    google_client_id: str = ""
    google_client_secret: str = ""

    # Internal analysis service
    analysis_api_url: str = "http://analysis_api:8001"
    internal_api_key: str = "change-me-internal-key"

    # CORS
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
