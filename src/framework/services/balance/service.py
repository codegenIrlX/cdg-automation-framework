from __future__ import annotations

import allure
import httpx
from loguru import logger
from pydantic import ValidationError

from framework.clients.base_client import BaseAPIClient
from framework.schemas import BalanceNoticeResponse, BalanceResponse


class BalanceService:
    """Сервис для работы с методами баланса и платежей."""

    def __init__(self, client: BaseAPIClient | None = None) -> None:
        self._client = client or BaseAPIClient()

    @allure.step("Получить баланс текущего личного кабинета")
    def get_balance(self) -> tuple[httpx.Response, BalanceResponse]:
        """Получить баланс текущего личного кабинета."""

        response = self._client.request("GET", "api/v1/payment/balance")
        response.raise_for_status()
        return response, self._parse_balance_response(response)

    @allure.step("Получить порог баланса для уведомления")
    def get_balance_notice(self) -> tuple[httpx.Response, BalanceNoticeResponse]:
        """Получить порог баланса для уведомления."""

        response = self._client.request("GET", "api/v1/payment/notice")
        response.raise_for_status()
        return response, self._parse_balance_notice_response(response)

    @staticmethod
    def _parse_balance_response(response: httpx.Response) -> BalanceResponse:
        try:
            return BalanceResponse.model_validate(response.json())
        except ValidationError as exc:
            logger.error(
                "Код 422: Ошибка валидации ответа баланса: {error}",
                error=exc,
            )
            raise

    @staticmethod
    def _parse_balance_notice_response(
        response: httpx.Response,
    ) -> BalanceNoticeResponse:
        try:
            return BalanceNoticeResponse.model_validate(response.json())
        except ValidationError as exc:
            logger.error(
                "Код 422: Ошибка валидации ответа порога баланса: {error}",
                error=exc,
            )
            raise
