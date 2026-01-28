from __future__ import annotations

from typing import Any

import pycamunda
import pycamunda.processdef
import pycamunda.processinst
import requests
from loguru import logger

from framework.config import Settings


class CamundaClient:
    def __init__(self, base_url: str, auth_token: str | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._auth_token = auth_token
        self._session: requests.Session | None = None

    @classmethod
    def from_settings(cls, settings: Settings) -> "CamundaClient":
        if not settings.CAMUNDA_BASE_URL:
            raise ValueError("CAMUNDA_BASE_URL не задан")
        return cls(
            base_url=settings.CAMUNDA_BASE_URL,
            auth_token=settings.CAMUNDA_AUTH_TOKEN,
        )

    def connect(self) -> None:
        if self._session is not None:
            return

        logger.info("Подключение к Camunda")
        session = requests.Session()
        if self._auth_token:
            session.headers.update({"Authorization": f"Bearer {self._auth_token}"})
        self._session = session

    def close(self) -> None:
        if self._session is None:
            return

        logger.info("Закрытие подключения к Camunda")
        self._session.close()
        self._session = None

    def ping(self) -> None:
        request = pycamunda.processdef.GetList(url=self._base_url, max_results=1)
        request.session = self._ensure_session()
        request()

    def start_process(
        self,
        process_key: str,
        variables: dict[str, Any] | None = None,
        business_key: str | None = None,
    ) -> pycamunda.processinst.ProcessInstance:
        logger.info("Запуск процесса Camunda {process_key}", process_key=process_key)
        request = pycamunda.processdef.StartInstance(
            url=self._base_url,
            key=process_key,
            business_key=business_key,
        )
        request.session = self._ensure_session()
        if variables:
            for name, value in variables.items():
                request.add_variable(name, value)
        return request()

    def _ensure_session(self) -> requests.Session:
        if self._session is None:
            self.connect()
        if self._session is None:
            raise RuntimeError("Camunda session не инициализирована")
        return self._session
