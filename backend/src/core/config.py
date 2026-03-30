from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "Stock Sentiment Tracker"
    app_version: str = "1.0.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    secret_key: str = Field(..., min_length=32)
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    database_url: PostgresDsn = Field(...)
    database_url_sync: str = Field(...)
    db_pool_size: int = 10
    db_max_overflow: int = 20

    redis_url: RedisDsn = Field(...)
    redis_cache_ttl: int = 300

    celery_broker_url: str = Field(...)
    celery_result_backend: str = Field(...)

    alpha_vantage_api_key: str = Field(...)
    binance_api_key: str = ""
    binance_api_secret: str = ""
    news_api_key: str = Field(...)
    finnhub_api_key: str = Field(...)
    reddit_client_id: str = Field(...)
    reddit_client_secret: str = Field(...)
    reddit_user_agent: str = "StockSentimentTracker/1.0"

    finbert_model_path: str = "ProsusAI/finbert"
    ml_batch_size: int = 32
    use_gpu: bool = False

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["json", "text"] = "json"
    log_file: str = "logs/app.log"

    prometheus_enabled: bool = True
    sentry_dsn: str = ""

    rate_limit_per_minute: int = 60

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
