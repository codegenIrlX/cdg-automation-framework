from pydantic import BaseModel, ConfigDict, Field


class PaymentHistoryItem(BaseModel):
    """Схема записи истории операций."""

    money: int = Field(..., description="Сумма операции")
    datetime: str = Field(..., description="Дата и время операции")
    comment: str = Field(..., description="Комментарий операции")


class PaymentHistoryResponse(BaseModel):
    """Схема ответа для истории операций."""

    model_config = ConfigDict(populate_by_name=True)

    history: list[PaymentHistoryItem] = Field(
        ..., alias="data", description="Список операций по выбранному типу"
    )
    success: bool = Field(..., description="Статус успешности запроса")
