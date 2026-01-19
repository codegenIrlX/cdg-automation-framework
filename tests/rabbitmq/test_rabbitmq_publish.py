import allure

from framework.clients import RabbitMQClient
from domains.mq.messaging.contracts import RabbitMQMessage


@allure.title("RabbitMQ: создание очереди и публикация сообщения")
def test_rabbitmq_create_and_publish_positive(
    rabbitmq_client: RabbitMQClient,
    rabbitmq_queue: str,
) -> None:
    # Arrange
    message = RabbitMQMessage(event="test", payload={"value": 42})

    # Act
    with allure.step("Создать очередь"):
        rabbitmq_client.declare_queue(rabbitmq_queue)

    with allure.step("Опубликовать JSON-сообщение"):
        rabbitmq_client.publish_json(rabbitmq_queue, message.model_dump())

    with allure.step("Получить сообщение обратно"):
        received = rabbitmq_client.get_json_message(rabbitmq_queue)

    # Assert
    with allure.step("Проверить, что сообщение опубликовано и совпадает с ожиданием"):
        assert received is not None
        assert received == message.model_dump()
