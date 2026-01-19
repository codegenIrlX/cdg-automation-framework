from pydantic import BaseModel, Field


class BalanceResponse(BaseModel):
    """Схема ответа для метода получения баланса."""

    balance: float = Field(..., description="Текущий баланс личного кабинета")
