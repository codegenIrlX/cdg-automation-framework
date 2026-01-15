from pydantic import BaseModel, Field


class BalanceResponse(BaseModel):
    """Схема ответа для метода получения баланса."""

    balance: float = Field(..., description="Текущий баланс личного кабинета")


class BalanceNoticeResponse(BaseModel):
    """Схема ответа для метода получения порога баланса."""

    amount: int = Field(..., description="Порог баланса для отправки уведомления")
