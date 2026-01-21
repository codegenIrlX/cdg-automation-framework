from __future__ import annotations


class DefaultHeadersBuilder:
    """Сборщик заголовков для HTTP-клиента."""

    def __init__(self, client_id: str, api_token: str | None) -> None:
        self._client_id = client_id
        self._api_token = api_token

    def build(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Client": self._client_id,
        }
        if self._api_token:
            headers["Authorization"] = f"Bearer {self._api_token}"
        return headers
