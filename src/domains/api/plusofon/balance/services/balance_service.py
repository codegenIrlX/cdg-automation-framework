from __future__ import annotations

import allure
import httpx

from domains.api.plusofon.balance.api.balance_api import BalanceApi
from domains.api.plusofon.balance.contracts import (
    AutopayResponse,
    BalanceNoticeResponse,
    BalanceResponse,
    PaymentHistoryResponse,
)


class BalanceService:
    """Сценарные методы для работы с балансом и платежами."""

    def __init__(self, api: BalanceApi | None = None) -> None:
        self._api = api or BalanceApi()

    @allure.step("Получить баланс текущего личного кабинета")
    def get_balance(self) -> tuple[httpx.Response, BalanceResponse]:
        return self._api.get_balance()

    @allure.step("Получить порог баланса для уведомления")
    def get_balance_notice(self) -> tuple[httpx.Response, BalanceNoticeResponse]:
        return self._api.get_balance_notice()

    @allure.step("Получить историю операций")
    def get_payment_history(
        self, operation_type: str
    ) -> tuple[httpx.Response, PaymentHistoryResponse]:
        return self._api.get_payment_history(operation_type)

    @allure.step("Получить статус автоплатежа")
    def get_autopay(self) -> tuple[httpx.Response, AutopayResponse]:
        return self._api.get_autopay()
