# Архитектура фреймворка автоматизации: framework + domains

## Оглавление

- [1. Введение](#1-введение)
- [2. Архитектурная концепция](#2-архитектурная-концепция)
  - [2.1 Слой `framework` (инфраструктура)](#21-слой-framework-инфраструктура)
  - [2.2 Слой `domains` (продуктовые модули)](#22-слой-domains-продуктовые-модули)
- [3. Пример структуры проекта (архитектура)](#3-пример-структуры-проекта-архитектура)
- [4. Работа с DTO и схемами (Pydantic)](#4-работа-с-dto-и-схемами-pydantic)
  - [4.1 Паттерн раскладки DTO по методам](#41-паттерн-раскладки-dto-по-методам)
  - [4.2 Примеры нейминга](#42-примеры-нейминга)
  - [4.3 Преимущества подхода](#43-преимущества-подхода)
- [5. API слой и сервисы](#5-api-слой-и-сервисы)
  - [5.1 `api/` — тонкие клиенты](#51-api-тонкие-клиенты)
  - [5.2 `services/` — бизнес-методы и сценарии для тестов](#52-services-бизнес-методы-и-сценарии-для-тестов)
  - [5.3 `repositories/` — доступ к БД без тестовой логики](#53-repositories-доступ-к-бд-без-тестовой-логики)
  - [5.4 Рекомендации по именованию](#54-рекомендации-по-именованию)
- [6. Структура и стили тестов](#6-структура-и-стили-тестов)
  - [6.1 Разделение на `component`, `contract`, `integration`, `e2e`](#61-разделение-на-component-contract-integration-e2e)
  - [6.2 Один файл на одну операцию](#62-один-файл-на-одну-операцию)
  - [6.3 AAA или Given-When-Then](#63-aaa-или-given-when-then)
  - [6.4 Примеры оформления тестов](#64-примеры-оформления-тестов)
- [7. Организация фикстур и тест-данных](#7-организация-фикстур-и-тест-данных)
  - [7.1 Уровни фикстур: инфраструктурные, тестовые, доменные](#71-уровни-фикстур-инфраструктурные-тестовые-доменные)
  - [7.2 Builders и factories вместо копипасты](#72-builders-и-factories-вместо-копипасты)
  - [7.3 Где и как располагать тест-данные](#73-где-и-как-располагать-тест-данные)
- [8. Маркеры и test-pyramid](#8-маркеры-и-test-pyramid)
  - [8.1 Использование `pytest.mark` для разных слоёв](#81-использование-pytestmark-для-разных-слоёв)
  - [8.2 Как это помогает масштабируемости и CI/CD](#82-как-это-помогает-масштабируемости-и-cicd)

---


## 1. Введение

Этот документ описывает рекомендуемую архитектуру фреймворка автоматизации (API/DB/MQ) с прицелом на масштабирование до сотен и тысяч тестов.

Цели:
- сделать проект **понятным новым участникам** команды;
- обеспечить **масштабируемость** (рост числа доменов, сервисов, DTO, тестов);
- повысить **переиспользуемость** инфраструктуры (клиенты, конфиг, репортинг, ассёрты);
- снизить стоимость поддержки за счёт чётких границ ответственности.

Ключевая идея: разделить код на два слоя:
- **`framework/`** — инфраструктура и общие механики (не зависит от конкретного продукта/домена),
- **`domains/`** — продуктовые модули (контракты, API-слой, сервисы, репозитории, тестовые данные).

---

## 2. Архитектурная концепция

### 2.1 Слой `framework` (инфраструктура)
`framework` — это «платформа» для тестов. Она не знает про конкретные эндпоинты “users/balance”, но предоставляет всё, что нужно тестам и доменным модулям:

Что обычно лежит в `framework/`:
- **config/** — settings, работа с env, выбор окружения (dev/stage/prod), конфиги сервисов;
- **clients/** — базовые клиенты (httpx), ретраи/таймауты, перехват/логирование;
- **db/** — engine/session SQLAlchemy, утилиты для работы с БД, миграции/сиды;
- **assertions/** — ассёрт-хелперы, «умные» проверки, diff для DTO/JSON;
- **fixtures/** — инфраструктурные фикстуры (клиенты, сессии, подключения, миграции);
- **utils/** — утилиты (date/time, генераторы, маскирование, random/uuid и т.п.);
- **reporting/** — Allure-обвязка, вложения, стандартизация шагов и артефактов.

Зачем выделять это отдельно:
- инфраструктура переиспользуется всеми доменами;
- изменения в инфраструктуре не должны требовать правок тестов по всему проекту;
- единый стиль логирования/отчётности/ретраев/ошибок.

### 2.2 Слой `domains` (продуктовые модули)
`domains` — это «то, что тестируем». Каждый домен содержит всё, что относится к конкретной зоне ответственности продукта: контракты (DTO), API-обёртки, сервисы сценариев, репозитории БД, тестовые данные.

Что лежит в `domains/<domain_name>/`:
- **contracts/** — Pydantic DTO для запросов/ответов;
- **api/** — тонкий слой вызовов (методы, URL, параметры, преобразование ответа → DTO);
- **services/** — бизнес-методы для тестов (сценарии, композиция шагов, ретраи);
- **repositories/** — доступ к БД (только data access, без тестовой логики);
- **testdata/** — наборы данных, builders/factories, «готовые» объекты для сценариев.

Почему это масштабируемо:
- добавление нового домена = новый пакет в `domains/`, без влияния на остальные;
- DTO и логика не смешиваются в «общую свалку»;
- тесты становятся «тонкими»: сценарии живут в сервисах, инфраструктура — во framework.

---

## 3. Пример структуры проекта (архитектура)

Ниже — пример дерева каталогов, где видно разделение `framework`/`domains` и то, как укладываются тесты и вспомогательные ресурсы.

```text
cdg-automation-framework/
├── .github/workflows/                # CI пайплайны (линт, тесты, отчёты, артефакты)
├── docker/
│   ├── docker-compose.yml            # окружение для локального запуска (DB/MQ/etc.)
│   └── db/seed.sql                   # сиды для тестовой БД (опционально)
├── docs/
│   ├── framework/                    # документация по инфраструктуре (pytest/httpx/db/allure)
│   └── test_cases/                   # тест-кейсы/сценарии/чек-листы (если ведутся отдельно)
├── src/
│   ├── framework/
│   │   ├── config/                   # settings.py, выбор окружений, env loader
│   │   ├── clients/                  # BaseAPIClient (httpx), retry, timeouts, auth
│   │   ├── db/                       # SQLAlchemy engine/session, helpers, migrations hooks
│   │   ├── assertions/               # smart asserts, diff, soft asserts, matchers
│   │   ├── utils/                    # утилиты (dates, mask, random, generators)
│   │   ├── fixtures/                 # инфраструктурные фикстуры (api_client, db_session, etc.)
│   │   └── reporting/                # allure helpers, attach, стандарт шагов/артефактов
│   ├── domains/
│   │   ├── users/
│   │   │   ├── contracts/            # DTO (req/res/common), разложенные по методам
│   │   │   ├── api/                  # низкоуровневые вызовы /users (http)
│   │   │   ├── services/             # сценарии: create_user, get_user, ensure_user_exists
│   │   │   ├── repositories/         # запросы к БД: users, roles
│   │   │   └── testdata/             # builders/factories для пользователей
│   │   └── balance_payments/
│   │       ├── contracts/
│   │       ├── api/
│   │       ├── services/
│   │       ├── repositories/
│   │       └── testdata/
├── tests/
│   ├── conftest.py                   # "тонкие" фикстуры уровня тестов (композиция)
│   ├── _fixtures/                    # тестовые фикстуры (domain fixtures, builders access)
│   ├── api/                          # тесты API (по слоям: component/contract/integration/e2e)
│   ├── db/                           # тесты БД (проверки миграций, запросы, консистентность)
│   ├── mq/                           # тесты MQ (если есть)
│   ├── _data/                        # статические данные (json/xml), если нужны
│   └── _helpers/                     # тестовые хелперы (локально для tests/, не в src/)
├── pyproject.toml                    # зависимости, инструменты (ruff, mypy, pytest config)
├── README.md                         # общий обзор проекта
└── .env / .env.example               # конфигурация окружения
```

Рекомендации:
- всё, что можно переиспользовать — держим в `src/` (framework/domains);
- `tests/` — только тесты, композиция фикстур и тестовые утилиты локального уровня;
- документацию по инструментам — в `docs/framework/`.

---

## 4. Работа с DTO и схемами (Pydantic)

### 4.1 Паттерн раскладки DTO по методам
Для масштабирования DTO важно:
- избегать «папки со всеми схемами подряд»;
- группировать DTO **по операции/методу**, а внутри — разделять `req`/`res`;
- держать общие схемы рядом (`common.py`).

Рекомендуемый паттерн в домене:
```text
src/domains/users/contracts/
  create_user/
    req.py
    res.py
  get_user/
    req.py
    res.py
  common.py
```

Или вариант (как правило команды):
- `contracts/<method_name>/req.py`
- `contracts/<method_name>/res.py`
- `contracts/common.py`

### 4.2 Примеры нейминга
- метод = *глагол + сущность*: `create_user`, `update_user`, `get_user`, `list_users`
- DTO классы:
  - `CreateUserRequest`, `CreateUserResponse`
  - `GetUserResponse`
  - общие: `UserDTO`, `RoleDTO`, `ErrorDTO`

Пример `contracts/get_user/res.py`:
```python
from pydantic import BaseModel

class RoleDTO(BaseModel):
    name: str

class UserDTO(BaseModel):
    id: int
    name: str
    roles: list[RoleDTO]

class GetUserResponse(BaseModel):
    data: UserDTO
```

### 4.3 Преимущества подхода
- легко найти DTO по операции;
- проще поддерживать версионирование (`get_user_v2/` или `/api/v2/` на уровне api/service);
- уменьшается риск конфликтов имён и «случайных импортов».

---

## 5. API слой и сервисы

Ключевая идея: **три слоя** с разной ответственностью.

### 5.1 `api/` — тонкие клиенты
`api/` делает только:
- собрать URL/метод/параметры;
- вызвать http клиент;
- распарсить ответ в DTO;
- бросить понятную ошибку (если надо — доменную).

**Не делает**:
- бизнес-сценарии;
- ретраи сценариев;
- проверки (assert) уровня тестов.

Пример `src/domains/users/api/users_api.py`:
```python
import allure
from src.framework.clients.base_api_client import BaseAPIClient
from src.domains.users.contracts.get_user.res import GetUserResponse

class UsersApi:
    def __init__(self, client: BaseAPIClient):
        self._client = client

    @allure.step("GET /api/v1/users/{user_id}")
    def get_user(self, user_id: int) -> GetUserResponse:
        r = self._client.request("GET", f"/api/v1/users/{user_id}")
        return GetUserResponse.model_validate(r.json())
```

### 5.2 `services/` — бизнес-методы и сценарии для тестов
`services/` отвечает за:
- сценарии (создать пользователя и проверить, что он доступен);
- ретраи (если система eventually consistent);
- композицию шагов и удобные методы для тестов;
- Allure step’ы, чтобы отчёт был читаемым.

Пример `src/domains/users/services/users_service.py`:
```python
import allure
from src.domains.users.api.users_api import UsersApi
from src.domains.users.contracts.get_user.res import GetUserResponse

class UsersService:
    def __init__(self, api: UsersApi):
        self._api = api

    @allure.step("Получить пользователя user_id={user_id}")
    def get(self, user_id: int) -> GetUserResponse:
        return self._api.get_user(user_id)
```

### 5.3 `repositories/` — доступ к БД без тестовой логики
`repositories/` делает:
- SELECT/INSERT/UPDATE на уровне SQLAlchemy/text();
- возвращает DTO/словарь/модель, но без assert-логики и «сценариев теста».

Пример `src/domains/users/repositories/users_repo.py`:
```python
from sqlalchemy import text
from sqlalchemy.orm import Session

class UsersRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_user_row(self, user_id: int) -> dict:
        row = self._session.execute(
            text("SELECT id, name FROM users WHERE id=:id"),
            {"id": user_id},
        ).mappings().first()
        return dict(row) if row else {}
```

### 5.4 Рекомендации по именованию
- API: `UsersApi`, `BalanceApi`
- Service: `UsersService`, `BalanceService`
- Repository: `UsersRepository`, `BalanceRepository`
- Методы:
  - API: `get_user`, `create_user` (в терминах endpoint)
  - Service: `get`, `create`, `ensure_exists`, `create_and_wait` (в терминах сценариев)

---

## 6. Структура и стили тестов

### 6.1 Разделение на `component`, `contract`, `integration`, `e2e`
Рекомендуем делить тесты по «уровням»:
- **component** — быстрые проверки отдельных операций/компонентов;
- **contract** — проверка контрактов (DTO, обязательные поля, типы, схемы);
- **integration** — взаимодействие нескольких сервисов/БД/очередей;
- **e2e** — сквозные сценарии пользовательского уровня.

Пример структуры:
```text
tests/api/component/
tests/api/contract/
tests/api/integration/
tests/api/e2e/
```

### 6.2 Один файл на одну операцию
Принцип: **1 файл = 1 операция**:
- `test_balance_get.py`
- `test_user_create.py`
- `test_user_update.py`

### 6.3 AAA или Given-When-Then
Оба стиля допустимы — главное, чтобы команда придерживалась единого стандарта.

**AAA (Arrange-Act-Assert)**:
```python
def test_get_balance(balance_service):
    # Arrange
    user_id = 1

    # Act
    resp = balance_service.get_balance(user_id)

    # Assert
    assert resp.data.amount >= 0
```

**Given-When-Then**:
```python
def test_create_user(users_service, user_factory):
    # Given
    req = user_factory.build_create_user()

    # When
    resp = users_service.create(req)

    # Then
    assert resp.data.id is not None
```

### 6.4 Примеры оформления тестов
- тесты должны быть **короткими** и «говорящими»;
- сложная логика — в `services/` и `framework/assertions`;
- DTO валидируют контракт; тесты проверяют бизнес-ожидания.

---

## 7. Организация фикстур и тест-данных

### 7.1 Уровни фикстур: инфраструктурные, тестовые, доменные
Рекомендуем 3 уровня:

1) **Инфраструктурные** (`src/framework/fixtures`):
- http клиент, settings, db session, mq connection, миграции.

2) **Доменные** (`tests/_fixtures` и/или `src/domains/<domain>/testdata`):
- сервисы домена, API-объекты, репозитории домена, factories.

3) **Тестовые/композиция** (`tests/conftest.py`):
- сборка и настройка под конкретный набор тестов.

### 7.2 Builders и factories вместо копипасты
Паттерны для тестовых данных:
- `Builder` — строит объект пошагово;
- `Factory` — создаёт готовые DTO/requests с дефолтами.

Пример factory:
```python
from src.domains.users.contracts.create_user.req import CreateUserRequest

class UserFactory:
    def build_create_user(self, **overrides) -> CreateUserRequest:
        data = {"name": "test", "role": "user"} | overrides
        return CreateUserRequest(**data)
```

### 7.3 Где и как располагать тест-данные
- доменные генераторы DTO — в `src/domains/<domain>/testdata/`;
- статические json/xml — в `tests/_data/` (или ближе к домену, если так удобнее);
- общие генераторы и маскирование — в `src/framework/utils/`.

---
