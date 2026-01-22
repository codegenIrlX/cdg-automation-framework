# Документация: Архитектура фреймворка автоматизации: framework + domains

## Оглавление

- [1. Введение](#1-введение)
- [2. Архитектурная концепция](#2-архитектурная-концепция)
  - [2.1 Слой `framework` (инфраструктура)](#21-слой-framework-инфраструктура)
  - [2.2 Слой `domains` (продуктовые модули)](#22-слой-domains-продуктовые-модули)
  - [2.3 Работа с несколькими API-клиентами и логированием](#23-работа-с-несколькими-api-клиентами-и-логированием)
- [3. Пример структуры проекта (универсальная архитектура)](#3-пример-структуры-проекта-универсальная-архитектура)
- [4. Работа с DTO и схемами (Pydantic)](#4-работа-с-dto-и-схемами-pydantic)
  - [4.1 Паттерн раскладки DTO по методам](#41-паттерн-раскладки-dto-по-методам)
  - [4.2 Примеры нейминга](#42-примеры-нейминга)
  - [4.3 Преимущества подхода](#43-преимущества-подхода)
- [5. API слой и сервисы](#5-api-слой-и-сервисы)
  - [5.1 `api/` — тонкие клиенты](#51-api--тонкие-клиенты)
  - [5.2 `services/` — бизнес-методы и сценарии для тестов](#52-services--бизнес-методы-и-сценарии-для-тестов)
  - [5.3 `repositories/` — доступ к БД без тестовой логики](#53-repositories--доступ-к-бд-без-тестовой-логики)
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
`framework` — это «платформа» для тестов. Она не знает про конкретные эндпоинты “profiles/ledger”, но предоставляет всё, что нужно тестам и доменным модулям.

Что обычно лежит в `framework/`:
- **config/** — settings, работа с env, выбор окружения (dev/stage/prod), конфиги сервисов;
- **clients/** — базовые клиенты (httpx), таймауты/ретраи, базовый пайплайн запроса;
- **logging/** — единые механики логирования (корреляция, маскирование, правила уровней, вложения в отчёт);
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

### 2.3 Работа с несколькими API-клиентами и логированием

#### 2.3.1 Почему не стоит держать всё логирование внутри `BaseClient`
Если в проекте **ровно один** HTTP-клиент и один набор эндпоинтов, то «жирный» `BaseClient`, который делает *всё* (request_id, маскирование заголовков, выбор уровней логов, логирование тела запроса/ответа, вложения в отчёт), ещё может быть оправдан:
- быстро стартовать;
- минимум абстракций;
- один кодовый путь, один формат логов.

Но в микросервисной архитектуре (условно **5+ сервисов/эндпоинтов/клиентов**) такая схема почти гарантированно приведёт к проблемам:
- `BaseClient` начинает разрастаться (условные ветки по сервисам, разные правила маскирования/логирования);
- растёт риск «случайных» изменений логирования, которые ломают диагностику сразу во всех клиентах;
- появляется дублирование (часть логики всё равно копируется в дочерние клиенты: например, разное формирование request_id, разные заголовки, разные исключения/ошибки);
- тестировать и переиспользовать логирование сложно: оно «прошито» внутрь HTTP-клиента.

**Best practice:** инфраструктурная логика должна быть **переиспользуемой** и **независимой** от конкретного сервиса/эндпоинта.

#### 2.3.2 Рекомендуемый подход: выделить универсальный модуль логирования
Вынесите логику логирования в отдельный модуль/класс (например, `ApiLogger`, `RequestLogger`) и используйте его из любого API-клиента **без дублирования кода**.

Что обычно живёт в таком модуле:
- формирование/проброс **`request_id` / correlation_id** (из теста → в заголовки → в логи);
- **маскирование** чувствительных данных (Authorization, cookies, токены, персональные поля);
- единые правила: **когда** логировать тело запроса/ответа (по уровню, по ошибке, по флагу debug);
- стандартизированный формат логов (структурированные поля: method, url, status_code, duration, service);
- (опционально) вложения в Allure: request/response, headers, curl.

Пример структуры:

```text
src/
├── framework/
│   ├── logging/
│   │   └── api_logger.py          # универсальный логгер для всех клиентов
│   └── clients/
│       ├── base_client.py         # общий пайплайн запросов, конфигурация, хуки
│       ├── auth_client.py         # клиент конкретного сервиса (Auth)
│       └── orders_client.py       # клиент конкретного сервиса (Orders)
```

Ключевая идея: `BaseClient` должен **уметь вызывать** логгер (hook/callback), но не «владеть» деталями логирования.

#### 2.3.3 Как правильно масштабировать API-клиенты под микросервисы
Не стоит пытаться описать все эндпоинты в одном `BaseClient`.

**Правило:** *один клиент — один сервис — один набор эндпоинтов.*
- `UserClient` — только Users-сервис;
- `BillingClient` — только Billing-сервис;
- `OrdersClient` — только Orders-сервис.

При этом наследование/композиция от общего `BaseClient` остаётся полезным:
- общая конфигурация: timeout, retry, base_url, auth;
- единый способ отправки запросов (`request()`), обработки ошибок, метрик/таймингов;
- единый интерфейс для логирования через `ApiLogger`.

Пример структуры (доменные клиенты рядом с доменом):

```text
src/
├── domains/
│   ├── billing/
│   │   └── api/
│   │       └── billing_client.py
│   ├── users/
│   │   └── api/
│   │       └── user_client.py
│   └── orders/
│       └── api/
│           └── orders_client.py
└── framework/
    ├── clients/
    │   └── base_client.py
    └── logging/
        └── api_logger.py
```

Почему так лучше:
- **Читаемость:** по имени файла/пакета сразу видно, к какому сервису относится код;
- **Сопровождение:** изменения в API конкретного сервиса локализованы в одном месте;
- **Тестируемость:** каждый клиент можно тестировать отдельно (моки, контрактные тесты, негативные сценарии);
- **Переиспользование инфраструктуры:** retry, логирование, фикстуры, настройки не копируются между сервисами.

---

## 3. Пример структуры проекта (универсальная архитектура)

Ниже — универсальный пример дерева каталогов для enterprise‑проекта с микросервисами и автотестами **REST / MQ / DB**.
Он сохраняет принцип разделения **`framework/` (инфраструктура)** и **`domains/` (предметные модули)**, но без привязки к конкретному продукту.

```text
cdg-automation-framework/
├── .github/workflows/                # CI пайплайны (линт, тесты, отчёты, артефакты)
├── docker-compose.yml                # окружение для локального запуска (DB/MQ/etc.)
├── init/
│   └── db/seed.sql                   # сиды для тестовой БД (опционально)
├── docs/
│   ├── framework/                    # документация по инфраструктуре (pytest/httpx/db/allure)
│   └── test_cases/                   # тест-кейсы/сценарии/чек-листы (если ведутся отдельно)
├── src/
│   ├── framework/
│   │   ├── config/                   # settings.py, выбор окружений, env loader
│   │   ├── clients/                  # BaseClient (httpx), retry, timeouts, auth
│   │   ├── logging/                  # ApiLogger/RequestLogger, mask rules, correlation id
│   │   ├── db/                       # SQLAlchemy engine/session, helpers, migrations hooks
│   │   ├── assertions/               # smart asserts, diff, soft asserts, matchers
│   │   ├── utils/                    # утилиты (dates, mask, random, generators)
│   │   ├── fixtures/                 # инфраструктурные фикстуры (api_client, db_session, etc.)
│   │   └── reporting/                # allure helpers, attach, стандарт шагов/артефактов
│   ├── domains/
│   │   ├── api/                      # домены, работающие через HTTP-интерфейсы (REST/gRPC gateway и т.п.)
│   │   │   ├── product_core/
│   │   │   │   ├── contracts/        # DTO/контракты запросов и ответов
│   │   │   │   ├── api/              # тонкие API-клиенты и вызовы методов
│   │   │   │   ├── services/         # сценарии и бизнес-методы для тестов
│   │   │   │   ├── repositories/     # доступ к данным (ORM/SQL), без логики тестов
│   │   │   │   └── testdata/         # builders/factories и наборы данных
│   │   │   └── product_number/
│   │   │       ├── contracts/        # DTO/контракты запросов и ответов
│   │   │       ├── api/              # тонкие API-клиенты и вызовы методов
│   │   │       ├── services/         # сценарии и бизнес-методы для тестов
│   │   │       ├── repositories/     # доступ к данным (ORM/SQL), без логики тестов
│   │   │       └── testdata/         # builders/factories и наборы данных
│   │   ├── mq/                       # домены, интегрирующиеся через брокеры сообщений (Kafka/Rabbit/NATS и т.п.)
│   │   │   ├── message_broker/
│   │   │   │   ├── contracts/        # DTO/контракты сообщений и событий
│   │   │   │   ├── api/              # тонкие клиенты/обёртки для MQ
│   │   │   │   ├── services/         # сценарии обработки и проверки событий
│   │   │   │   ├── repositories/     # доступ к данным (ORM/SQL), без логики тестов
│   │   │   │   └── testdata/         # builders/factories и наборы данных
│   │   │   └── event_engine/
│   │   │       ├── contracts/        # DTO/контракты сообщений и событий
│   │   │       ├── api/              # тонкие клиенты/обёртки для MQ
│   │   │       ├── services/         # сценарии обработки и проверки событий
│   │   │       ├── repositories/     # доступ к данным (ORM/SQL), без логики тестов
│   │   │       └── testdata/         # builders/factories и наборы данных
│   │   └── db/                       # домены, работающие с предметными данными из БД (reference/identity/permissions и т.п.)
│   │       ├── user_profile/
│   │       │   ├── contracts/        # DTO/контракты запросов и ответов
│   │       │   ├── api/              # (опционально) API над БД/админ-интерфейс, если есть
│   │       │   ├── services/         # сценарии для тестов: подготовка/проверка данных
│   │       │   ├── repositories/     # доступ к данным (ORM/SQL), без логики тестов
│   │       │   └── testdata/         # builders/factories и наборы данных
│   │       └── permissions/
│   │           ├── contracts/        # DTO/контракты запросов и ответов
│   │           ├── api/              # (опционально) API над БД/админ-интерфейс, если есть
│   │           ├── services/         # сценарии для тестов: подготовка/проверка данных
│   │           ├── repositories/     # доступ к данным (ORM/SQL), без логики тестов
│   │           └── testdata/         # builders/factories и наборы данных
├── tests/
│   ├── conftest.py                   # «тонкие» фикстуры уровня тестов (композиция)
│   ├── _fixtures/                    # тестовые фикстуры (domain fixtures, builders access)
│   ├── api/                          # тесты API (по слоям: component/contract/integration/e2e)
│   ├── db/                           # тесты БД (проверки миграций, запросы, консистентность)
│   ├── mq/                           # тесты MQ (если есть)
│   ├── _data/                        # статические данные (json/xml), если нужны
│   └── _helpers/                     # тестовые хелперы (локально для tests/, не в src/)
├── pyproject.toml                    # зависимости, инструменты (ruff, mypy, pytest config)
├── README.md                         # общий обзор проекта├── .env.example                    # шаблон переменных окружения (без секретов)
├── .env                            # базовые дефолты (локально; не коммитится)
└── .{ENVIRONMENT}.env              # overrides под выбранное окружение (пример: .test.env, .stage.env; не коммитится)
```

### Пояснение контекстов `domains/`

- **`api/`** — домены, работающие через HTTP‑интерфейсы (REST/gRPC gateway). Здесь живут обёртки над эндпоинтами, DTO и сценарии, которые используют тесты.
- **`mq/`** — интеграции через брокеры сообщений и события. Отличается тем, что коммуникация асинхронная и часто требуется «ожидание/проверка доставки».
- **`db/`** — домены, завязанные на предметные данные БД. Отличается от `framework/db`: здесь — предметные репозитории и DTO, а в `framework/db` — инфраструктура подключения/сессий.

> Важно: названия доменов внутри контекстов (`product_core`, `event_engine`, `user_profile`, …) — нейтральные примеры. В реальном проекте используйте те же границы, что и в продуктовой архитектуре (bounded contexts).

### Как добавлять новые домены и контексты

1) **Добавление нового домена в существующий контекст**
- если новая функциональность относится к уже существующей зоне (например, ещё один HTTP‑сервис или новая таблица/сущность в БД), добавляйте пакет уровня:
  - `domains/api/<new_domain>/...` или `domains/mq/<new_domain>/...` или `domains/db/<new_domain>/...`
- придерживайтесь одинаковой внутренней раскладки (`contracts/api/services/repositories/testdata`) — это ускоряет навигацию и снижает порог входа.

2) **Добавление нового контекста (новой технологической зоны)**
- если появляется новая «плоскость интеграции», которая заметно отличается по механике (например, `grpc/`, `s3/`, `cache/`, `ui/`), выделяйте отдельный контекст:
  - `domains/<context>/...`
- критерий: у контекста обычно появляется свой тип клиентов/фикстур/паттернов ожидания (например, подписки на события, polling, транзакционность и т.п.).

### Чем отличаются `framework/`, `domains/` и `tests/`

- **`src/framework/`** — переиспользуемая инфраструктура.
  - *Можно (и нужно) переиспользовать везде.*
  - Не содержит бизнес‑терминов продукта и конкретных эндпоинтов/таблиц.

- **`src/domains/`** — предметные модули (bounded contexts).
  - *Переиспользуется тестами*, но уже содержит бизнес‑термины и предметные DTO/репозитории/сервисы.
  - Здесь живут тонкие клиенты (`api/`), сценарии (`services/`) и доступ к данным (`repositories/`).

- **`tests/`** — сами тесты и их «клей».
  - Здесь не должно быть повторно используемой доменной логики (она живёт в `src/`).
  - Допустимы локальные хелперы и композиция фикстур, специфичная для конкретного набора тестов.

### Что и где должно лежать (и что переиспользуется)

- **Переиспользуемое между доменами** → `src/framework/` (клиенты, конфиг, db‑сессии, ассёрты, репортинг, генераторы).
- **Переиспользуемое внутри домена** → `src/domains/<context>/<domain>/...` (DTO, API‑обёртки, сервисы сценариев, репозитории, factories).
- **Только для тестов** → `tests/` (`conftest.py`, тестовые фикстуры‑композиции, локальные хелперы, статические данные).

---

## 4. Работа с DTO и схемами (Pydantic)

### 4.1 Паттерн раскладки DTO по методам
Для масштабирования DTO важно:
- избегать «папки со всеми схемами подряд»;
- группировать DTO **по операции/методу**, а внутри — разделять `req`/`res`;
- держать общие схемы рядом (`common.py`).

Рекомендуемый паттерн в домене:
```text
src/domains/db/user_profile/contracts/
  create_profile/
    req.py
    res.py
  get_profile/
    req.py
    res.py
  common.py
```

Или вариант (как правило команды):
- `contracts/<method_name>/req.py`
- `contracts/<method_name>/res.py`
- `contracts/common.py`

### 4.2 Примеры нейминга
- метод = *глагол + сущность*: `create_profile`, `update_profile`, `get_profile`, `list_profiles`
- DTO классы:
  - `CreateUserProfileRequest`, `CreateUserProfileResponse`
  - `GetUserProfileResponse`
  - общие: `UserProfileDTO`, `PermissionDTO`, `ErrorDTO`

Пример `contracts/get_profile/res.py`:
```python
from pydantic import BaseModel

class PermissionDTO(BaseModel):
    name: str

class UserProfileDTO(BaseModel):
    id: int
    name: str
    permissions: list[PermissionDTO]

class GetUserProfileResponse(BaseModel):
    data: UserProfileDTO
```

### 4.3 Преимущества подхода
- легко найти DTO по операции;
- проще поддерживать версионирование (`get_profile_v2/` или `/api/v2/` на уровне api/service);
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

> Best practice для микросервисов: **один API-клиент = один сервис = один набор эндпоинтов**. Не смешивайте Users/Billing/Orders в одном классе.

Пример `src/domains/db/user_profile/api/user_profile_api.py`:
```python
import allure
from src.framework.clients.base_api_client import BaseAPIClient
from src.domains.db.user_profile.contracts.get_profile.res import GetUserProfileResponse

class UserProfileApi:
    def __init__(self, client: BaseAPIClient):
        self._client = client

    @allure.step("GET /api/v1/profiles/{profile_id}")
    def get_profile(self, profile_id: int) -> GetUserProfileResponse:
        r = self._client.request("GET", f"/api/v1/profiles/{profile_id}")
        return GetUserProfileResponse.model_validate(r.json())
```

### 5.2 `services/` — бизнес-методы и сценарии для тестов
`services/` отвечает за:
- сценарии (создать пользователя и проверить, что он доступен);
- ретраи (если система eventually consistent);
- композицию шагов и удобные методы для тестов;
- Allure step’ы, чтобы отчёт был читаемым.

Пример `src/domains/db/user_profile/services/user_profile_service.py`:
```python
import allure
from src.domains.db.user_profile.api.users_api import UserProfileApi
from src.domains.db.user_profile.contracts.get_profile.res import GetUserProfileResponse

class UserProfileService:
    def __init__(self, api: UserProfileApi):
        self._api = api

    @allure.step("Получить пользователя profile_id={profile_id}")
    def get(self, profile_id: int) -> GetUserProfileResponse:
        return self._api.get_profile(profile_id)
```

### 5.3 `repositories/` — доступ к БД без тестовой логики
`repositories/` делает:
- SELECT/INSERT/UPDATE на уровне SQLAlchemy/text();
- возвращает DTO/словарь/модель, но без assert-логики и «сценариев теста».

Пример `src/domains/db/user_profile/repositories/user_profile_repo.py`:
```python
from sqlalchemy import text
from sqlalchemy.orm import Session

class UserProfileRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_profile_row(self, profile_id: int) -> dict:
        row = self._session.execute(
            text("SELECT id, name FROM user_profile WHERE id=:id"),
            {"id": profile_id},
        ).mappings().first()
        return dict(row) if row else {}
```

### 5.4 Рекомендации по именованию
- API: `UserProfileApi`, `ProductCoreApi`
- Service: `UserProfileService`, `ProductCoreService`
- Repository: `UserProfileRepository`, `ProductCoreRepository`
- Методы:
  - API: `get_profile`, `create_profile` (в терминах endpoint)
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
- `test_product_core_get.py`
- `test_profile_create.py`
- `test_profile_update.py`

### 6.3 AAA или Given-When-Then
Оба стиля допустимы — главное, чтобы команда придерживалась единого стандарта.

**AAA (Arrange-Act-Assert)**:
```python
def test_get_product_core(product_core_service):
    # Arrange
    profile_id = 1

    # Act
    resp = balance_service.get_balance(profile_id)

    # Assert
    assert resp.data is not None
```

**Given-When-Then**:
```python
def test_create_profile(users_service, user_factory):
    # Given
    req = user_factory.build_create_profile()

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
from src.domains.db.user_profile.contracts.create_profile.req import CreateUserProfileRequest

class UserProfileFactory:
    def build_create_profile(self, **overrides) -> CreateUserProfileRequest:
        data = {"display_name": "test", "permission": "basic"} | overrides
        return CreateUserProfileRequest(**data)
```

### 7.3 Где и как располагать тест-данные
- доменные генераторы DTO — в `src/domains/<domain>/testdata/`;
- статические json/xml — в `tests/_data/` (или ближе к домену, если так удобнее);
- общие генераторы и маскирование — в `src/framework/utils/`.

---