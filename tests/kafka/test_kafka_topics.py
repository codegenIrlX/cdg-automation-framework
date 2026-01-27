import uuid

import allure
import pytest

from framework.clients import KafkaClient
from domains.mq.messaging.contracts import KafkaMessage
from framework.utils import RetryHelper


@allure.parent_suite("Kafka")
@allure.title("Kafka: создание топика и публикация сообщения")
@pytest.mark.smoke
def test_kafka_create_and_publish_positive(
    kafka_client: KafkaClient,
    kafka_topic: str,
) -> None:
    # Arrange
    trace_id = str(uuid.uuid4())
    message = KafkaMessage(event="test", payload={"trace_id": trace_id, "value": 42})

    # Act
    with allure.step("Опубликовать сообщение в Kafka"):
        kafka_client.publish_message(kafka_topic, message.model_dump(), key=trace_id)

    with allure.step("Прочитать сообщение из Kafka"):
        retry_helper = RetryHelper()

        def _consume() -> dict:
            received_message = kafka_client.consume_message(
                kafka_topic
            )
            if received_message is None:
                raise ValueError("Сообщение не найдено в топике")
            return received_message

        received = retry_helper.run(_consume)

    # Assert
    with allure.step("Проверить, что сообщение опубликовано и совпадает с ожиданием"):
        assert received is not None
        assert received == message.model_dump()
