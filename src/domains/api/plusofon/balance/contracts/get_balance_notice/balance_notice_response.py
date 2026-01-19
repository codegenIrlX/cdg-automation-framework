from pydantic import BaseModel, Field


class BalanceNoticeResponse(BaseModel):
    """Схема ответа для метода получения порога баланса."""

    amount: int = Field(..., description="Порог баланса для отправки уведомления")
