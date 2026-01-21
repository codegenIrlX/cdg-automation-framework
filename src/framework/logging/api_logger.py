from __future__ import annotations

from typing import Any, Mapping

import httpx
from loguru import logger as loguru_logger

from framework.logging.masking import SensitiveHeadersMasker


class ApiLogger:
    """Логирование HTTP-запросов и ответов."""

    def __init__(
        self,
        log_level: str,
        masker: SensitiveHeadersMasker | None = None,
        logger=loguru_logger,
    ) -> None:
        self._log_level = log_level.upper()
        self._masker = masker or SensitiveHeadersMasker()
        self._logger = logger

    def log_request(
        self,
        *,
        method: str,
        url: str,
        headers: Mapping[str, Any],
        params: Any,
        body: Any,
        request_id: str,
    ) -> Any:
        bound_logger = self._logger.bind(request_id=request_id)
        bound_logger.info("Запрос {method} {url}", method=method, url=url)
        if self._log_level == "DEBUG":
            bound_logger.debug(
                "Request details:\n"
                "  Headers: {headers}\n"
                "  Params: {params}\n"
                "  Body: {body}",
                headers=self._masker.mask(headers),
                params=params,
                body=body,
            )
        return bound_logger

    def log_response(self, bound_logger: Any, response: httpx.Response) -> None:
        bound_logger.info("Ответ {status_code}", status_code=response.status_code)
        if self._log_level == "DEBUG":
            bound_logger.debug(
                "Response details:\n"
                "  Headers: {headers}\n"
                "  Body: {body}",
                headers=dict(response.headers),
                body=response.text,
            )

    def log_error(
        self,
        bound_logger: Any,
        *,
        status_code: int,
        message: str,
    ) -> None:
        bound_logger.error(
            "Код {status_code}: {message}",
            status_code=status_code,
            message=message,
        )
