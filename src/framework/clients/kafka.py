from __future__ import annotations

import json
import time
from typing import Any
from uuid import uuid4

from confluent_kafka import Consumer, KafkaException, Producer
from confluent_kafka.admin import AdminClient, NewTopic
from loguru import logger

from framework.config import Settings


class KafkaClient:
    def __init__(self, host: str, port: int) -> None:
        self._bootstrap_server = f"{host}:{port}"
        self._client: AdminClient | None = None
        self._producer: Producer | None = None

    @classmethod
    def from_settings(cls, settings: Settings) -> "KafkaClient":
        return cls(
            host=settings.KAFKA_HOST,
            port=settings.KAFKA_PORT,
        )

    def connect(self) -> None:
        if self._client is not None:
            return
        logger.info("Подключение к Kafka")
        self._client = AdminClient(
            {
                "bootstrap.servers": self._bootstrap_server,
                "broker.address.family": "v4",
            }
        )
        self._ensure_connection()
        self._producer = Producer(
            {
                "bootstrap.servers": self._bootstrap_server,
                "broker.address.family": "v4",
            }
        )

    def close(self) -> None:
        if self._client is not None:
            logger.info("Закрытие подключения к Kafka")
            self._client = None
        if self._producer is not None:
            self._producer.flush(5)
            self._producer = None

    def create_topic(
        self,
        name: str,
        num_partitions: int = 1,
        replication_factor: int = 1,
    ) -> None:
        client = self._ensure_client()
        logger.info("Создание топика Kafka {topic}", topic=name)
        topic = NewTopic(
            topic=name,
            num_partitions=num_partitions,
            replication_factor=replication_factor,
        )
        futures = client.create_topics([topic])
        for future in futures.values():
            future.result()

    def delete_topic(self, name: str) -> None:
        client = self._ensure_client()
        logger.info("Удаление топика Kafka {topic}", topic=name)
        futures = client.delete_topics([name])
        for future in futures.values():
            future.result()

    def publish_message(
        self,
        topic: str,
        message: dict[str, Any],
        key: str | None = None,
    ) -> None:
        producer = self._ensure_producer()
        payload = json.dumps(message, ensure_ascii=False).encode("utf-8")
        logger.info("Публикация сообщения в Kafka {topic}", topic=topic)
        producer.produce(topic=topic, key=key, value=payload)
        producer.flush(5)

    def consume_message(
        self,
        topic: str,
        timeout_seconds: float = 5.0,
        poll_interval: float = 0.2,
    ) -> dict[str, Any] | None:
        logger.info("Чтение сообщения из Kafka {topic}", topic=topic)
        consumer = Consumer(
            {
                "bootstrap.servers": self._bootstrap_server,
                "broker.address.family": "v4",
                "group.id": f"test-consumer-{uuid4()}",
                "auto.offset.reset": "earliest",
                "enable.auto.commit": False,
            }
        )

        try:
            consumer.subscribe([topic])
            deadline = time.time() + timeout_seconds
            while time.time() < deadline:
                message = consumer.poll(timeout=poll_interval)
                if message is None:
                    continue
                if message.error():
                    raise KafkaException(message.error())
                if message.value() is None:
                    continue
                return json.loads(message.value().decode("utf-8"))
        finally:
            consumer.close()

        return None

    def list_topics(self) -> set[str]:
        client = self._ensure_client()
        metadata = client.list_topics(timeout=10)
        return set(metadata.topics.keys())

    def _ensure_client(self) -> AdminClient:
        if self._client is None:
            self.connect()
        if self._client is None:
            raise RuntimeError("Kafka client не инициализирован")
        return self._client

    def _ensure_producer(self) -> Producer:
        if self._producer is None:
            self.connect()
        if self._producer is None:
            raise RuntimeError("Kafka producer не инициализирован")
        return self._producer

    def _ensure_connection(self) -> None:
        if self._client is None:
            raise RuntimeError("Kafka client не инициализирован")
        try:
            self._client.list_topics(timeout=10)
        except KafkaException as exc:
            self._client = None
            raise exc
