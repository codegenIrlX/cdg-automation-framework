from __future__ import annotations

import os

from dotenv import dotenv_values
from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_env_files() -> tuple[str, ...]:
    environment = os.getenv("ENVIRONMENT")
    if not environment:
        environment = dotenv_values(".env").get("ENVIRONMENT")
    if environment:
        return ".env", f".{environment}.env"
    return (".env",)


class Settings(BaseSettings):
    """Настройки запуска из переменных окружения и файла .env."""

    model_config = SettingsConfigDict(
        env_file=_resolve_env_files(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENVIRONMENT: str | None = None
    BASE_URL: str
    API_TOKEN: str | None
    CLIENT_ID: str
    TIMEOUT_SECONDS: float
    VERIFY_SSL: bool
    LOG_LEVEL: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_ECHO: bool
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_VHOST: str

    @property
    def DB_URL(self) -> str:
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
