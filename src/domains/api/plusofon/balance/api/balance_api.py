from __future__ import annotations

import allure
import httpx
from loguru import logger
from pydantic import ValidationError

from domains.api.plusofon.balance.contracts import (
    BalanceNoticeResponse,
    BalanceResponse,
    PaymentHistoryResponse,
)
from domains.api.plusofon.contracts import PLUSOFON_STATUS_CODES
from framework.clients.base_client import BaseAPIClient


class BalanceApi:
    """Тонкий API-клиент для методов баланса и платежей."""

    def __init__(self, client: BaseAPIClient | None = None) -> None:
        self._client = client or BaseAPIClient(status_code_map=PLUSOFON_STATUS_CODES)

    @allure.step("GET /api/v1/payment/balance")
    def get_balance(self) -> tuple[httpx.Response, BalanceResponse]:
        response = self._client.request("GET", "api/v1/payment/balance")
        response.raise_for_status()
        return response, self._parse_balance_response(response)

    @allure.step("GET /api/v1/payment/notice")
    def get_balance_notice(self) -> tuple[httpx.Response, BalanceNoticeResponse]:
        response = self._client.request("GET", "api/v1/payment/notice")
        response.raise_for_status()
        return response, self._parse_balance_notice_response(response)

    @allure.step("GET /api/v1/payment/history/{operation_type}")
    def get_payment_history(
        self, operation_type: str
    ) -> tuple[httpx.Response, PaymentHistoryResponse]:
        response = self._client.request(
            "GET",
            f"api/v1/payment/history/{operation_type}",
        )
        response.raise_for_status()
        return response, self._parse_payment_history_response(response)

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

    @staticmethod
    def _parse_payment_history_response(
        response: httpx.Response,
    ) -> PaymentHistoryResponse:
        try:
            return PaymentHistoryResponse.model_validate(response.json())
        except ValidationError as exc:
            logger.error(
                "Код 422: Ошибка валидации истории операций: {error}",
                error=exc,
            )
            raise
