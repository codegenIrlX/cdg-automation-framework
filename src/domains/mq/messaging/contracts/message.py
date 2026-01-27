from pydantic import BaseModel, Field


class RabbitMQMessage(BaseModel):
    event: str = Field(..., description="Тип события")
    payload: dict[str, int | str | float | bool | dict | list | None] = Field(
        ..., description="Полезная нагрузка сообщения"
    )


class KafkaMessage(BaseModel):
    event: str = Field(..., description="Тип события")
    payload: dict[str, int | str | float | bool | dict | list | None] = Field(
        ..., description="Полезная нагрузка сообщения"
    )
