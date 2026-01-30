from pydantic import BaseModel, Field


class AutopayResponse(BaseModel):
    """Схема ответа для метода получения статуса автоплатежа."""

    access: bool = Field(..., description="Доступность услуги автоплатежа")
    active: bool = Field(..., description="Активность услуги автоплатежа")
    sum: int | None = Field(
        ..., description="Сумма счёта для автоплатежа (может отсутствовать)"
    )
    success: bool = Field(..., description="Статус успешности запроса")
