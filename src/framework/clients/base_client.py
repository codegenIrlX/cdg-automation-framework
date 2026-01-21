from __future__ import annotations

from collections.abc import Callable
from typing import Any
from uuid import uuid4

import httpx

from framework.clients.headers import DefaultHeadersBuilder
from framework.config import settings
from framework.logging.api_logger import ApiLogger


class BaseAPIClient:
    """Базовый HTTP-клиент с логированием и общей конфигурацией."""

    def __init__(
        self,
        transport: httpx.BaseTransport | None = None,
        status_code_map: dict[int, str] | None = None,
        *,
        http_client: httpx.Client | None = None,
        headers_builder: DefaultHeadersBuilder | None = None,
        api_logger: ApiLogger | None = None,
        request_id_provider: Callable[[], str] | None = None,
        settings_obj=settings,
    ) -> None:
        self._settings = settings_obj
        self._headers_builder = headers_builder or DefaultHeadersBuilder(
            client_id=self._settings.CLIENT_ID,
            api_token=self._settings.API_TOKEN,
        )
        self._client = http_client or httpx.Client(
            base_url=self._settings.BASE_URL,
            timeout=self._settings.TIMEOUT_SECONDS,
            verify=self._settings.VERIFY_SSL,
            headers=self._headers_builder.build(),
            transport=transport,
        )
        self._status_code_map = status_code_map or {}
        self._logger = api_logger or ApiLogger(self._settings.LOG_LEVEL)
        self._request_id_provider = request_id_provider or (lambda: str(uuid4()))

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        request_id = kwargs.pop("request_id", None) or self._request_id_provider()
        headers = {
            **dict(self._client.headers),
            **(kwargs.get("headers") or {}),
        }
        params = kwargs.get("params")
        body = self._extract_body(kwargs)
        bound_logger = self._logger.log_request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            body=body,
            request_id=request_id,
        )

        response = self._client.request(method, url, **kwargs)
        self._logger.log_response(bound_logger, response)
        if response.status_code >= 400:
            message = self._status_code_map.get(response.status_code, response.text)
            self._logger.log_error(
                bound_logger,
                status_code=response.status_code,
                message=message,
            )
        return response

    def close(self) -> None:
        self._client.close()

    @staticmethod
    def _extract_body(kwargs: dict[str, Any]) -> Any:
        if "json" in kwargs:
            return kwargs.get("json")
        if "data" in kwargs:
            return kwargs.get("data")
        if "content" in kwargs:
            return kwargs.get("content")
        return None
