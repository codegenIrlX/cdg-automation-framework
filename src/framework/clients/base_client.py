from __future__ import annotations

from typing import Any
from uuid import uuid4

import httpx
from loguru import logger

from framework.config import settings


class BaseAPIClient:
    """Базовый HTTP-клиент с логированием и общей конфигурацией."""

    def __init__(
        self,
        transport: httpx.BaseTransport | None = None,
        status_code_map: dict[int, str] | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=settings.BASE_URL,
            timeout=settings.TIMEOUT_SECONDS,
            verify=settings.VERIFY_SSL,
            headers=self._build_headers(),
            transport=transport,
        )
        self._status_code_map = status_code_map or {}

    @staticmethod
    def _build_headers() -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Client": settings.CLIENT_ID,
        }
        if settings.API_TOKEN:
            headers["Authorization"] = f"Bearer {settings.API_TOKEN}"
        return headers

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        request_id = kwargs.pop("request_id", None) or str(uuid4())
        bound_logger = logger.bind(request_id=request_id)
        bound_logger.info("Запрос {method} {url}", method=method, url=url)

        if settings.LOG_LEVEL.upper() == "DEBUG":
            headers = {
                **dict(self._client.headers),
                **(kwargs.get("headers") or {}),
            }
            masked_headers = self._mask_sensitive_headers(headers)
            params = kwargs.get("params")
            body = None
            if "json" in kwargs:
                body = kwargs.get("json")
            elif "data" in kwargs:
                body = kwargs.get("data")
            elif "content" in kwargs:
                body = kwargs.get("content")

            bound_logger.debug(
                "Request details:\n"
                "  Headers: {headers}\n"
                "  Params: {params}\n"
                "  Body: {body}",
                headers=masked_headers,
                params=params,
                body=body,
            )

        response = self._client.request(method, url, **kwargs)
        bound_logger.info("Ответ {status_code}", status_code=response.status_code)
        if settings.LOG_LEVEL.upper() == "DEBUG":
            bound_logger.debug(
                "Response details:\n"
                "  Headers: {headers}\n"
                "  Body: {body}",
                headers=dict(response.headers),
                body=response.text,
            )
        if response.status_code >= 400:
            message = self._status_code_map.get(response.status_code, response.text)
            bound_logger.error(
                "Код {status_code}: {message}",
                status_code=response.status_code,
                message=message,
            )
        return response

    def close(self) -> None:
        self._client.close()

    @staticmethod
    def _mask_sensitive_headers(headers: dict[str, Any]) -> dict[str, Any]:
        masked = dict(headers)
        if "authorization" in masked:
            masked["authorization"] = "***"
        if "Authorization" in masked:
            masked["Authorization"] = "***"
        return masked
