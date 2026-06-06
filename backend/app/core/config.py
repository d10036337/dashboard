from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Taiwan Tradovate (TTX Trader)"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    backend_cors_origins: str = "http://localhost:5173,http://localhost:8080"

    database_url: str = "postgresql+psycopg://ttx:ttx_password@localhost:5432/ttx_trader"
    redis_url: str = "redis://localhost:6379/0"

    shioaji_api_key: str = Field(default="", repr=False)
    shioaji_secret_key: str = Field(default="", repr=False)
    shioaji_person_id: str = Field(default="", repr=False)
    shioaji_ca_path: str = Field(default="", repr=False)
    shioaji_ca_password: str = Field(default="", repr=False)

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
