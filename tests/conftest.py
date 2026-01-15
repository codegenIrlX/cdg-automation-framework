import uuid

import pytest
from loguru import logger
from pika.exceptions import AMQPConnectionError
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from framework.clients import RabbitMQClient
from framework.clients.db import create_engine_from_dsn, create_session_factory
from framework.config import settings
from framework.services import BalanceService
from framework.utils.logger import setup_logger


@pytest.fixture(scope="session", autouse=True)
def configure_logging() -> None:
    setup_logger(settings.log_level)


@pytest.fixture()
def balance_service() -> BalanceService:
    return BalanceService()