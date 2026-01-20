from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки запуска из переменных окружения и файла .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    BASE_URL: str
    API_TOKEN: str
    CLIENT_ID: str
    TIMEOUT_SECONDS: float
    VERIFY_SSL: bool
    LOG_LEVEL: str
    DB_HOST: str | None
    DB_PORT: int | None
    DB_NAME: str | None
    DB_USER: str | None
    DB_PASSWORD: str | None
    DB_ECHO: bool | None
    RABBITMQ_HOST: str | None
    RABBITMQ_PORT: int | None
    RABBITMQ_USER: str | None
    RABBITMQ_PASSWORD: str | None
    RABBITMQ_VHOST: str | None

    @property
    def DB_URL(self) -> str:
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

settings = Settings()
