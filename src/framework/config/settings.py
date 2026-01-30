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


def _get_env_value(name: str) -> str | None:
    value = os.getenv(name)
    if value is not None:
        return value
    for env_file in _resolve_env_files():
        env_value = dotenv_values(env_file).get(name)
        if env_value:
            return env_value
    return None


class Settings(BaseSettings):
    """Настройки запуска из переменных окружения и файла .env."""

    model_config = SettingsConfigDict(
        env_file=_resolve_env_files(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENVIRONMENT: str | None = None
    BASE_URL: str
    ZEPHYR_URL: str | None = None
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
    KAFKA_HOST: str
    KAFKA_PORT: int

    @property
    def CAMUNDA_BASE_URL(self) -> str | None:
        return _get_env_value("CAMUNDA_BASE_URL")

    @property
    def CAMUNDA_AUTH_TOKEN(self) -> str | None:
        return _get_env_value("CAMUNDA_AUTH_TOKEN")

    @property
    def DB_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
