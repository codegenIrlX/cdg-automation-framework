import uuid

import pytest
from loguru import logger
from pika.exceptions import AMQPConnectionError
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from sipplus_framework.clients import RabbitMQClient
from sipplus_framework.clients.db import create_engine_from_dsn, create_session_factory
from sipplus_framework.config import settings
from sipplus_framework.services import BalanceService
from sipplus_framework.utils.logger import setup_logger


@pytest.fixture(scope="session", autouse=True)
def configure_logging() -> None:
    setup_logger(settings.log_level)


@pytest.fixture()
def balance_service() -> BalanceService:
    return BalanceService()