from typing import Any

from pydantic import PostgresDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants import Environment


class CustomBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class Config(CustomBaseSettings):
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    DATABASE_ASYNC_URL: str = "sqlite+aiosqlite:///./sql_app.db"
    DATABASE_POOL_SIZE: int = 16
    DATABASE_POOL_TTL: int = 60 * 20  
    DATABASE_POOL_PRE_PING: bool = True

    ENVIRONMENT: Environment = Environment.PRODUCTION
    GOOGLE_API_KEY: str = "AIzaSyA3zSglp1eXGA-k7fVF-9pwjEdf3pj0-FE"
    SENTRY_DSN: str | None = None

    CORS_ORIGINS: list[str] = ["*"]
    CORS_ORIGINS_REGEX: str | None = None
    CORS_HEADERS: list[str] = ["*"]

    APP_VERSION: str = "0.1"

    @model_validator(mode="after")
    def validate_sentry_non_local(self) -> "Config":
        if self.ENVIRONMENT.is_deployed and not self.SENTRY_DSN:
            raise ValueError("Sentry is not set")

        return self


settings = Config()

app_configs: dict[str, Any] = {"title": "DocuBot API"}
if settings.ENVIRONMENT.is_deployed:
    app_configs["root_path"] = f"/v{settings.APP_VERSION}"

if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None  
