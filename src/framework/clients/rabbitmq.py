import json
import time
from typing import Any

import pika
from loguru import logger
from pika.adapters.blocking_connection import BlockingChannel

from framework.config import Settings


class RabbitMQClient:
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        vhost: str,
        heartbeat: int = 30,
        blocked_connection_timeout: int = 30,
    ) -> None:
        self._parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            virtual_host=vhost,
            credentials=pika.PlainCredentials(user, password),
            heartbeat=heartbeat,
            blocked_connection_timeout=blocked_connection_timeout,
        )
        self._connection: pika.BlockingConnection | None = None
        self._channel: BlockingChannel | None = None

    @classmethod
    def from_settings(cls, settings: Settings) -> "RabbitMQClient":
        return cls(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            user=settings.rabbitmq_user,
            password=settings.rabbitmq_password,
            vhost=settings.rabbitmq_vhost,
        )

    def connect(self) -> None:
        if self._connection and self._connection.is_open:
            return

        logger.info("Подключение к RabbitMQ")
        self._connection = pika.BlockingConnection(self._parameters)
        self._channel = self._connection.channel()

    def close(self) -> None:
        if self._connection and self._connection.is_open:
            logger.info("Закрытие подключения к RabbitMQ")
            self._connection.close()

    def declare_queue(self, queue_name: str, durable: bool = True) -> None:
        self._ensure_channel()
        logger.info("Создание очереди {queue}", queue=queue_name)
        self._channel.queue_declare(queue=queue_name, durable=durable)

    def publish_json(
        self,
        queue_name: str,
        message: dict[str, Any],
        durable: bool = True,
    ) -> None:
        self._ensure_channel()
        self._channel.queue_declare(queue=queue_name, durable=durable)

        payload = json.dumps(message, ensure_ascii=False)
        logger.info("Публикация сообщения в очередь {queue}", queue=queue_name)
        self._channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=payload,
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2 if durable else 1,
            ),
        )

    def delete_queue(self, queue_name: str, if_unused: bool = False, if_empty: bool = False) -> None:
        self._ensure_channel()
        logger.info("Удаление очереди {queue}", queue=queue_name)
        self._channel.queue_delete(queue=queue_name, if_unused=if_unused, if_empty=if_empty)

    def get_json_message(
        self,
        queue_name: str,
        attempts: int = 5,
        delay_seconds: float = 0.2,
    ) -> dict[str, Any] | None:
        self._ensure_channel()
        self._channel.queue_declare(queue=queue_name, durable=True)

        for attempt in range(1, attempts + 1):
            method_frame, _, body = self._channel.basic_get(queue=queue_name, auto_ack=True)
            if method_frame and body:
                logger.info("Сообщение получено из очереди {queue}", queue=queue_name)
                return json.loads(body)

            logger.info(
                "Сообщение не найдено в очереди {queue}, попытка {attempt}/{attempts}",
                queue=queue_name,
                attempt=attempt,
                attempts=attempts,
            )
            time.sleep(delay_seconds)

        return None

    def _ensure_channel(self) -> None:
        if not self._connection or not self._connection.is_open:
            self.connect()
        if not self._channel or self._channel.is_closed:
            if not self._connection:
                self.connect()
            self._channel = self._connection.channel()
