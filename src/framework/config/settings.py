from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки запуска из переменных окружения и файла .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    base_url: str = Field("https://restapi.plusofon.ru", alias="BASE_URL")
    api_token: str | None = Field(default=None, alias="API_TOKEN")
    client_id: str = Field("10553", alias="CLIENT_ID")
    timeout_seconds: float = Field(10.0, alias="TIMEOUT_SECONDS")
    verify_ssl: bool = Field(True, alias="VERIFY_SSL")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    db_dsn: str | None = Field(default=None, alias="DB_DSN")
    db_echo: bool = Field(False, alias="DB_ECHO")
    rabbitmq_host: str = Field("localhost", alias="RABBITMQ_HOST")
    rabbitmq_port: int = Field(5672, alias="RABBITMQ_PORT")
    rabbitmq_user: str = Field("guest", alias="RABBITMQ_USER")
    rabbitmq_password: str = Field("guest", alias="RABBITMQ_PASSWORD")
    rabbitmq_vhost: str = Field("/", alias="RABBITMQ_VHOST")


settings = Settings()
