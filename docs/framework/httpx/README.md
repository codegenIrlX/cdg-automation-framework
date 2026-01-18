# Документация: httpx для автоматизации API: REST + SOAP best practices (микросервисы)

---

## Оглавление

- [1. Введение](#1-введение)
  - [1.1. Что такое httpx и зачем он используется](#11-что-такое-httpx-и-зачем-он-используется)
  - [1.2. Особенности httpx](#12-особенности-httpx)
  - [1.3. Почему httpx удобен в автоматизации и микросервисах](#13-почему-httpx-удобен-в-автоматизации-и-микросервисах)
- [2. Настройка httpx-клиента](#2-настройка-httpx-клиента)
  - [2.1. Конфигурация через .env / pydantic-settings](#21-конфигурация-через-env-pydantic-settings)
  - [2.2. Базовый BaseAPIClient: base_url, timeout, verify, headers](#22-базовый-baseapiclient-baseurl-timeout-verify-headers)
  - [2.3. Управление сессией и transport](#23-управление-сессией-и-transport)
  - [2.4. Логирование запросов/ответов + маскирование токенов](#24-логирование-запросовответов-маскирование-токенов)
- [3. Работа с REST API](#3-работа-с-rest-api)
  - [3.1. GET / POST / PUT / DELETE](#31-get-post-put-delete)
  - [3.2. params / json / headers / files](#32-params-json-headers-files)
  - [3.3. Обработка ошибок: raise_for_status() и кастомные ошибки](#33-обработка-ошибок-raiseforstatus-и-кастомные-ошибки)
  - [3.4. Логирование уровней DEBUG/INFO](#34-логирование-уровней-debuginfo)
  - [3.5. Пример: BalanceService + парсинг моделей через Pydantic](#35-пример-balanceservice-парсинг-моделей-через-pydantic)
- [4. Обработка сложных структур ответов](#4-обработка-сложных-структур-ответов)
  - [4.1. Pydantic для валидации схем ответа](#41-pydantic-для-валидации-схем-ответа)
  - [4.2. Обработка 422 и 400 ошибок](#42-обработка-422-и-400-ошибок)
  - [4.3. Централизованный парсинг и логика обработки](#43-централизованный-парсинг-и-логика-обработки)
- [5. Работа с множеством микросервисных эндпоинтов](#5-работа-с-множеством-микросервисных-эндпоинтов)
  - [5.1. Рекомендуемая структура кода](#51-рекомендуемая-структура-кода)
  - [5.2. Версионирование API (/api/v1/, /api/v2/)](#52-версионирование-api-apiv1-apiv2)
  - [5.3. Организация сервисов по зонам ответственности](#53-организация-сервисов-по-зонам-ответственности)
- [6. SOAP-запросы через httpx](#6-soap-запросы-через-httpx)
  - [6.1. Отправка XML через httpx](#61-отправка-xml-через-httpx)
  - [6.2. Парсинг SOAP-ответа (xml.etree / lxml)](#62-парсинг-soap-ответа-xmletree-lxml)
- [7. Best Practices](#7-best-practices)
  - [7.1. `allure.step` в сервисах](#71-allurestep-в-сервисах)
  - [7.2. Маскирование чувствительных данных](#72-маскирование-чувствительных-данных)
  - [7.3. Общие настройки в settings.py](#73-общие-настройки-в-settingspy)
  - [7.4. Мокинг и изоляция от прод-эндпоинтов](#74-мокинг-и-изоляция-от-прод-эндпоинтов)
  - [7.5. pytest-фикстуры для клиента и сервисов](#75-pytest-фикстуры-для-клиента-и-сервисов)
- [8. Асинхронный httpx](#8-асинхронный-httpx)
  - [8.1. Когда использовать AsyncClient](#81-когда-использовать-asyncclient)
  - [8.2. Пример async вызова](#82-пример-async-вызова)
  - [8.3. pytest-asyncio: советы](#83-pytest-asyncio-советы)
- [9. Заключение](#9-заключение)
- [10. Приложения](#10-приложения)
  - [10.1. Полный пример BaseAPIClient (event_hooks + маскирование)](#101-полный-пример-baseapiclient-eventhooks-маскирование)
  - [10.2. BalanceService с allure.step](#102-balanceservice-с-allurestep)
  - [10.3. Pydantic-модель ответа (пример)](#103-pydantic-модель-ответа-пример)
  - [10.4. SOAP-запрос (пример)](#104-soap-запрос-пример)

---

## 1. Введение

### 1.1. Что такое httpx и зачем он используется
**httpx** — современная HTTP‑клиент библиотека для Python, часто используемая как альтернатива `requests`.

Типичные причины выбрать httpx:
- единый API для **синхронных** и **асинхронных** запросов,
- удобные **таймауты**, **прокси**, **SSL**, **транспортный слой**,
- хорошие возможности для **тестирования** (MockTransport/стабы) и интеграции с микросервисами.

### 1.2. Особенности httpx
- **Sync/Async**: `httpx.Client` и `httpx.AsyncClient`.
- **Timeouts**: общий таймаут или по фазам (connect/read/write/pool).
- **Proxy/SSL**: прокси, `verify`, кастомные CA, клиентские сертификаты.
- **Transports**: `httpx.MockTransport` для тестов, кастомные транспорты.
- **Connection pooling**: управление пулом соединений через параметры лимитов.

### 1.3. Почему httpx удобен в автоматизации и микросервисах
- Хорошо ложится на архитектуру: **BaseAPIClient → сервисные классы → тесты**.
- Удобно централизовать:
  - заголовки/авторизацию,
  - корреляционные id,
  - обработку ошибок и стандартов ответа,
  - логирование и метрики времени.
- В микросервисах важно быстро понимать, *какой сервис*, *какой endpoint*, *какой payload* вызвал ошибку — и httpx позволяет это собрать в одном месте.

---

## 2. Настройка httpx-клиента

Ниже — рекомендованный паттерн для автоматизации: один базовый клиент, который:
- хранит `base_url`, дефолтные headers,
- управляет таймаутами, verify/SSL,
- логирует запрос/ответ,
- превращает ошибки в читаемые исключения.

---

### 2.1. Конфигурация через .env / pydantic-settings

`settings.py`:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_BASE_URL: str
    API_TOKEN: str | None = None
    VERIFY_SSL: bool = True
    TIMEOUT_SECONDS: float = 10.0

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")

settings = Settings()
```

`.env` пример:
```dotenv
APP_API_BASE_URL=https://api.example.local
APP_API_TOKEN=secret-token
APP_VERIFY_SSL=true
APP_TIMEOUT_SECONDS=10
```

---

### 2.2. Базовый BaseAPIClient: base_url, timeout, verify, headers

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import httpx


@dataclass(frozen=True)
class ClientConfig:
    base_url: str
    timeout_seconds: float = 10.0
    verify_ssl: bool = True
    default_headers: Mapping[str, str] | None = None


class ApiError(RuntimeError):
    """Базовое исключение для ошибок API-клиента."""


class BaseAPIClient:
    def __init__(self, config: ClientConfig):
        self._config = config
        self._client = httpx.Client(
            base_url=config.base_url,
            timeout=httpx.Timeout(config.timeout_seconds),
            verify=config.verify_ssl,
            headers=dict(config.default_headers or {}),
        )

    def close(self) -> None:
        self._client.close()

    def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
        files: Any | None = None,
    ) -> httpx.Response:
        try:
            resp = self._client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                headers=headers,
                files=files,
            )
            resp.raise_for_status()
            return resp
        except httpx.HTTPStatusError as e:
            raise ApiError(self._format_http_error(e)) from e
        except httpx.RequestError as e:
            raise ApiError(f"Network error: {e}") from e

    @staticmethod
    def _format_http_error(e: httpx.HTTPStatusError) -> str:
        r = e.response
        return f"HTTP {r.status_code} for {r.request.method} {r.request.url} | body={r.text[:2000]}"
```

> Важно: клиент нужно **закрывать** (`close()`), чтобы корректно освобождать соединения. В pytest это удобно делать через фикстуру.

---

### 2.3. Управление сессией и transport

`Client/AsyncClient` держит пул соединений и переиспользует keep-alive — это ускоряет тесты.

Рекомендации:
- создавайте клиент **на scope=session** (если нет конфликтов состояния),
- используйте `limits`, если тесты параллелятся (xdist) или запросов много:

```python
limits = httpx.Limits(max_connections=50, max_keepalive_connections=20)
client = httpx.Client(base_url=..., limits=limits)
```

**Transport**:
- для тестов: `httpx.MockTransport` (полная изоляция от сети),
- для кастомной маршрутизации/перехвата.

---

### 2.4. Логирование запросов/ответов + маскирование токенов

Ключевая практика: логируем **структурированно**, но **маскируем секреты** (Authorization, cookies, passwords).

Пример маскирования:
```python
import httpx

SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie"}

def mask_headers(headers: httpx.Headers) -> dict[str, str]:
    result: dict[str, str] = {}
    for k, v in headers.items():
        result[k] = "***" if k.lower() in SENSITIVE_HEADERS else v
    return result
```

**Event hooks** httpx (удобно для централизованного логирования):
```python
import time
import httpx

def log_request(request: httpx.Request) -> None:
    request.extensions["start_time"] = time.time()

def log_response(response: httpx.Response) -> None:
    start = response.request.extensions.get("start_time")
    duration_ms = (time.time() - start) * 1000 if start else None
    # логируйте method/url/status/duration, headers (masked), body (по правилам)
    # IMPORTANT: не логируйте секреты

client = httpx.Client(
    base_url="https://api.example.local",
    event_hooks={"request": [log_request], "response": [log_response]},
)
```

Практика:
- на `INFO`: метод/URL/статус/время + correlation id,
- на `DEBUG`: body, но с ограничением размера и маскированием.

---

## 3. Работа с REST API

### 3.1. GET / POST / PUT / DELETE
```python
r = client.request("GET", "/users", params={"limit": 10})
data = r.json()

r = client.request("POST", "/users", json={"name": "Ivan"})
created = r.json()

r = client.request("PUT", "/users/1", json={"name": "New Name"})
r = client.request("DELETE", "/users/1")
```

### 3.2. params / json / headers / files
```python
r = client.request("GET", "/search", params={"q": "test", "page": 1})
r = client.request("POST", "/items", json={"id": 1, "name": "Item"})
r = client.request("GET", "/secure", headers={"X-Request-ID": "abc-123"})

with open("file.txt", "rb") as f:
    r = client.request("POST", "/upload", files={"file": ("file.txt", f, "text/plain")})
```

### 3.3. Обработка ошибок: raise_for_status() и кастомные ошибки
`raise_for_status()` выбрасывает `httpx.HTTPStatusError` для 4xx/5xx.  
Хорошая практика — превращать это в доменные исключения и прикладывать контекст.

```python
class HttpStatusError(ApiError):
    def __init__(self, status_code: int, url: str, body: str):
        super().__init__(f"HTTP {status_code} for {url}")
        self.status_code = status_code
        self.url = url
        self.body = body
```

### 3.4. Логирование уровней DEBUG/INFO
- `INFO`: method + url + status + duration + correlation id
- `DEBUG`: request/response bodies (ограниченные), headers (masked)

---

### 3.5. Пример: BalanceService + парсинг моделей через Pydantic

DTO:
```python
from pydantic import BaseModel, Field

class BalanceDTO(BaseModel):
    user_id: int
    amount: float = Field(ge=0)
    currency: str
```

Service:
```python
import allure

class BalanceService:
    def __init__(self, client: BaseAPIClient):
        self._client = client

    @allure.step("Get balance for user_id={user_id}")
    def get_balance(self, user_id: int) -> BalanceDTO:
        r = self._client.request("GET", f"/api/v1/balance/{user_id}")
        return BalanceDTO.model_validate(r.json())
```

Test:
```python
def test_balance_is_non_negative(balance_service: BalanceService):
    dto = balance_service.get_balance(1)
    assert dto.amount >= 0
    assert dto.currency in {"RUB", "USD", "EUR"}
```

---

## 4. Обработка сложных структур ответов

### 4.1. Pydantic для валидации схем ответа
Паттерн: **в сервисном слое** валидировать JSON через DTO, а в тесте проверять смысл.

```python
dto = ResponseDTO.model_validate(response.json())
```

### 4.2. Обработка 422 и 400 ошибок
Часто встречаются:
- `400 Bad Request`,
- `422 Unprocessable Entity` (часто FastAPI).

Практика:
- парсить тело ошибки в DTO (если есть стандарт),
- или выбрасывать доменное исключение, включающее `status_code` и `body`.

DTO ошибки (пример для 422):
```python
from pydantic import BaseModel

class ValidationErrorItem(BaseModel):
    loc: list[str | int]
    msg: str
    type: str

class Error422DTO(BaseModel):
    detail: list[ValidationErrorItem]
```

### 4.3. Централизованный парсинг и логика обработки
Рекомендация:
- parsing (`r.json()` + `DTO.model_validate`) держать в сервисе,
- общие правила ошибок — в BaseAPIClient или ErrorHandler.

---

## 5. Работа с множеством микросервисных эндпоинтов

### 5.1. Рекомендуемая структура кода
```
src/
  config/
    settings.py
  clients/
    base_client.py
  services/
    balance.py
    users.py
  dto/
    balance.py
    users.py
tests/
  conftest.py
  test_balance.py
```

### 5.2. Версионирование API (/api/v1/, /api/v2/)
```python
class UserService:
    def __init__(self, client: BaseAPIClient, api_prefix: str = "/api/v1"):
        self._client = client
        self._prefix = api_prefix

    def get_user(self, user_id: int):
        return self._client.request("GET", f"{self._prefix}/users/{user_id}")
```

### 5.3. Организация сервисов по зонам ответственности
- один сервис = один bounded context/домены,
- DTO рядом с сервисом или в общем `dto/` (по договорённости),
- не делайте «мегасервис» на весь проект.

---

## 6. SOAP-запросы через httpx

### 6.1 Отправка XML через httpx
```python
soap_xml = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetBalance xmlns="http://example.com/soap">
      <UserId>1</UserId>
    </GetBalance>
  </soap:Body>
</soap:Envelope>
"""

headers = {"Content-Type": "application/xml"}
r = client.request("POST", "/soap", data=soap_xml, headers=headers)
```

> Иногда SOAP требует `text/xml` и/или `SOAPAction` — зависит от сервиса.

### 6.2. Парсинг SOAP-ответа (xml.etree / lxml)
`xml.etree.ElementTree`:
```python
import xml.etree.ElementTree as ET

root = ET.fromstring(r.text)
```

`lxml`:
```python
from lxml import etree

root = etree.fromstring(r.content)
value = root.xpath("//Balance/text()")
```

---

## 7. Best Practices

### 7.1. `allure.step` в сервисах
```python
import allure

@allure.step("POST /api/v1/users: create user")
def create_user(...):
    ...
```

### 7.2. Маскирование чувствительных данных
- маскируйте `Authorization`, cookies, пароли, токены,
- режьте большие тела,
- учитывайте доступность логов/артефактов в CI.

### 7.3. Общие настройки в settings.py
- base_url, таймауты, verify_ssl, proxy, api prefix,
- режимы окружений через `MODE`.

### 7.4. Мокинг и изоляция от прод-эндпоинтов
Варианты:
- `httpx.MockTransport` (встроенно),
- `respx` (удобный роутинг моков для httpx).

MockTransport пример:
```python
import httpx

def handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/api/v1/balance/1":
        return httpx.Response(200, json={"user_id": 1, "amount": 100.0, "currency": "RUB"})
    return httpx.Response(404, json={"error": "not found"})

transport = httpx.MockTransport(handler)
client = httpx.Client(base_url="https://mock.local", transport=transport)
```

### 7.5. pytest-фикстуры для клиента и сервисов
```python
import pytest

@pytest.fixture(scope="session")
def api_client(settings):
    cfg = ClientConfig(
        base_url=settings.API_BASE_URL,
        timeout_seconds=settings.TIMEOUT_SECONDS,
        verify_ssl=settings.VERIFY_SSL,
        default_headers={"Authorization": f"Bearer {settings.API_TOKEN}"} if settings.API_TOKEN else {},
    )
    client = BaseAPIClient(cfg)
    yield client
    client.close()

@pytest.fixture
def balance_service(api_client):
    return BalanceService(api_client)
```

---

## 8. Асинхронный httpx

### 8.1. Когда использовать AsyncClient
Async имеет смысл, если:
- много запросов параллельно (fan-out),
- нужна высокая производительность на I/O,
- проект/инфраструктура уже async.

### 8.2. Пример async вызова
```python
import httpx

async def fetch_user(base_url: str):
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        r = await client.get("/api/v1/users/1")
        r.raise_for_status()
        return r.json()
```

### 8.3. pytest-asyncio: советы
```python
import pytest
import httpx

@pytest.mark.asyncio
async def test_async_health():
    async with httpx.AsyncClient(base_url="https://api.example.local") as client:
        r = await client.get("/health")
        assert r.status_code == 200
```

---

## 9. Заключение

Рекомендуемая архитектура:
- **BaseAPIClient**: общие настройки, ошибки, логирование,
- **Services**: методы для конкретных endpoints,
- **DTO (Pydantic)**: валидируем контракты,
- **pytest fixtures**: жизненный цикл клиента,
- **MockTransport/respx**: unit-тесты сервисов.

---

## 10. Приложения

### 10.1. Полный пример BaseAPIClient (event_hooks + маскирование)
```python
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Mapping

import httpx

SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie"}

def mask_headers(headers: httpx.Headers) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in headers.items():
        out[k] = "***" if k.lower() in SENSITIVE_HEADERS else v
    return out

def truncate(text: str, limit: int = 10_000) -> str:
    return text if len(text) <= limit else text[:limit] + "...<truncated>"

@dataclass(frozen=True)
class ClientConfig:
    base_url: str
    timeout_seconds: float = 10.0
    verify_ssl: bool = True
    default_headers: Mapping[str, str] | None = None

class ApiError(RuntimeError):
    pass

class BaseAPIClient:
    def __init__(self, config: ClientConfig):
        def on_request(request: httpx.Request) -> None:
            request.extensions["start_time"] = time.time()

        def on_response(response: httpx.Response) -> None:
            start = response.request.extensions.get("start_time")
            duration_ms = (time.time() - start) * 1000 if start else None
            print(
                json.dumps(
                    {
                        "method": response.request.method,
                        "url": str(response.request.url),
                        "status": response.status_code,
                        "duration_ms": duration_ms,
                        "req_headers": mask_headers(response.request.headers),
                        "resp_headers": mask_headers(response.headers),
                    },
                    ensure_ascii=False,
                )
            )

        self._client = httpx.Client(
            base_url=config.base_url,
            timeout=httpx.Timeout(config.timeout_seconds),
            verify=config.verify_ssl,
            headers=dict(config.default_headers or {}),
            event_hooks={"request": [on_request], "response": [on_response]},
        )

    def close(self) -> None:
        self._client.close()

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        try:
            resp = self._client.request(method=method, url=url, **kwargs)
            resp.raise_for_status()
            return resp
        except httpx.HTTPStatusError as e:
            r = e.response
            raise ApiError(
                f"HTTP {r.status_code} {r.request.method} {r.request.url} | body={truncate(r.text)}"
            ) from e
        except httpx.RequestError as e:
            raise ApiError(f"Network error: {e}") from e
```

### 10.2. BalanceService с allure.step
```python
import allure
from pydantic import BaseModel, Field

class BalanceDTO(BaseModel):
    user_id: int
    amount: float = Field(ge=0)
    currency: str

class BalanceService:
    def __init__(self, client: BaseAPIClient):
        self._client = client

    @allure.step("GET /api/v1/balance/{user_id}")
    def get_balance(self, user_id: int) -> BalanceDTO:
        r = self._client.request("GET", f"/api/v1/balance/{user_id}")
        return BalanceDTO.model_validate(r.json())
```

### 10.3. Pydantic-модель ответа (пример)
```python
from pydantic import BaseModel

class RoleDTO(BaseModel):
    name: str

class UserDTO(BaseModel):
    id: int
    name: str
    roles: list[RoleDTO]
```

### 10.4. SOAP-запрос (пример)
```python
soap_xml = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <Ping xmlns="http://example.com/soap">
      <Message>Hello</Message>
    </Ping>
  </soap:Body>
</soap:Envelope>
"""

headers = {"Content-Type": "application/xml"}
r = client.request("POST", "/soap", data=soap_xml, headers=headers)
assert r.status_code == 200
```
