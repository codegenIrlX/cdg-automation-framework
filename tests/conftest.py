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


@pytest.fixture(scope="session")
def db_engine(request: pytest.FixtureRequest) -> Engine:
    if not settings.db_dsn:
        pytest.skip("Переменная DB_DSN не задана, тесты с БД пропущены")

    logger.info("Инициализация подключения к БД для тестов")
    engine = create_engine_from_dsn(settings.db_dsn, echo=settings.db_echo)
    request.addfinalizer(engine.dispose)
    return engine


@pytest.fixture()
def db_session(db_engine: Engine):
    connection = db_engine.connect()
    transaction = connection.begin()

    session_factory = create_session_factory(connection)
    session: Session = session_factory()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def rabbitmq_client() -> RabbitMQClient:
    client = RabbitMQClient.from_settings(settings)

    try:
        client.connect()
    except AMQPConnectionError:
        pytest.skip("RabbitMQ недоступен, тест пропущен")

    yield client
    client.close()


@pytest.fixture()
def rabbitmq_queue(rabbitmq_client: RabbitMQClient) -> str:
    queue_name = f"test_queue_{uuid.uuid4()}"
    yield queue_name
    rabbitmq_client.delete_queue(queue_name)
