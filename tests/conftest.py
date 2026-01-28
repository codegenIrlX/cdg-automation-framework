import uuid

import pycamunda
import pytest
from confluent_kafka import KafkaException
from loguru import logger
from pika.exceptions import AMQPConnectionError
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from framework.clients import CamundaClient, KafkaClient, RabbitMQClient
from framework.db import create_engine_from_dsn, create_session_factory
from framework.config import settings
from domains.api.plusofon.balance import BalanceService
from framework.utils.logger import setup_logger


@pytest.fixture(scope="session", autouse=True)
def configure_logging() -> None:
    setup_logger(settings.LOG_LEVEL)


@pytest.fixture()
def balance_service() -> BalanceService:
    return BalanceService()


@pytest.fixture(scope="session")
def db_engine(request: pytest.FixtureRequest) -> Engine:
    logger.info("Инициализация подключения к БД")
    engine = create_engine_from_dsn(settings.DB_URL, echo=settings.DB_ECHO)
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
        pytest.skip("RabbitMQ недоступен")

    yield client
    client.close()


@pytest.fixture()
def rabbitmq_queue(rabbitmq_client: RabbitMQClient) -> str:
    queue_name = f"test_queue_{uuid.uuid4()}"
    yield queue_name
    rabbitmq_client.delete_queue(queue_name)


@pytest.fixture()
def kafka_client() -> KafkaClient:
    client = KafkaClient.from_settings(settings)

    try:
        client.connect()
    except KafkaException:
        pytest.skip("Kafka недоступна")

    yield client
    client.close()


@pytest.fixture()
def kafka_topic(kafka_client: KafkaClient) -> str:
    topic_name = f"test_topic_{uuid.uuid4()}"
    kafka_client.create_topic(topic_name)
    yield topic_name
    try:
        kafka_client.delete_topic(topic_name)
    except KafkaException:
        pass


@pytest.fixture()
def camunda_client() -> CamundaClient:
    if not settings.CAMUNDA_BASE_URL:
        pytest.skip("CAMUNDA_BASE_URL не задан")

    client = CamundaClient.from_settings(settings)
    try:
        client.connect()
        client.ping()
    except pycamunda.PyCamundaException:
        pytest.skip("Camunda недоступна")

    yield client
    client.close()
