from __future__ import annotations

import allure
import httpx

from domains.api.plusofon.balance.api.balance_api import BalanceApi
from domains.api.plusofon.balance.contracts import BalanceNoticeResponse, BalanceResponse


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
