from typing import Annotated

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Finance Dashboard Backend"
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    api_v1_prefix: str = ""
    database_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/finance_dashboard",
        alias="DATABASE_URL",
    )
    jwt_secret_key: str = Field(default="change-this-secret", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=60, alias="JWT_EXPIRE_MINUTES")
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
        ],
        alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if not value:
            return []
        return [origin.strip() for origin in value.split(",") if origin.strip()]

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: bool | str) -> bool:
        if isinstance(value, bool):
            return value
        normalized = str(value).strip().lower()
        if normalized in {"1", "true", "yes", "on", "debug", "development"}:
            return True
        if normalized in {"0", "false", "no", "off", "release", "production"}:
            return False
        return bool(value)

    @field_validator("jwt_algorithm", mode="before")
    @classmethod
    def parse_jwt_algorithm(cls, value: str) -> str:
        normalized = str(value).strip().upper()
        typo_map = {
            "H256": "HS256",
            "H384": "HS384",
            "H512": "HS512",
        }
        return typo_map.get(normalized, normalized)


@lru_cache
def get_settings() -> Settings:
    return Settings()
