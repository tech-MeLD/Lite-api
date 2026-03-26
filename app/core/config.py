from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Standard RESTful API"
    api_v1_prefix: str = "/api/v1"
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    api_key: str = Field(default="change-me-local-dev", alias="API_KEY")
    github_api_base_url: str = Field(default="https://api.github.com", alias="GITHUB_API_BASE_URL")
    weather_api_base_url: str = Field(
        default="https://api.open-meteo.com/v1",
        alias="WEATHER_API_BASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    github_cache_ttl_seconds: int = Field(default=300, alias="GITHUB_CACHE_TTL_SECONDS")
    weather_cache_ttl_seconds: int = Field(default=1800, alias="WEATHER_CACHE_TTL_SECONDS")
    sqlite_url: str = Field(default="sqlite+aiosqlite:///./data/weather.db", alias="SQLITE_URL")
    request_timeout_seconds: float = Field(default=10.0, alias="REQUEST_TIMEOUT_SECONDS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
