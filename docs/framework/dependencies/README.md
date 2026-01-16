# Библиотеки Python для фреймворка автоматизации тестирования

Этот документ описывает ключевые Python-библиотеки, используемые в типовом QA-фреймворке автоматизации (API/UI/интеграционные тесты), и то, **какую роль они играют в архитектуре**: тест-раннер, HTTP-клиент, отчётность, конфигурация, логирование, доступ к БД, генерация тестовых данных и интеграции (например, очереди сообщений).

> Версии в требованиях:  
> `pytest>=8.3.0`, `httpx>=0.27.0`, `allure-pytest>=2.13.5`, `pydantic>=2.7.0`, `pydantic-settings>=2.3.0`,  
> `loguru>=0.7.2`, `python-dotenv>=1.0.1`, `sqlalchemy>=2.0.35`, `psycopg2-binary>=2.9.9`,  
> `mimesis>=17.0.0`, `pika>=1.3.2`

---

## Оглавление

- [1. Общая картина: где эти библиотеки в архитектуре](#1-общая-картина-где-эти-библиотеки-в-архитектуре)
- [2. Документация по библиотекам](#2-документация-по-библиотекам)
  - [pytest](#pytest)
  - [httpx](#httpx)
  - [allure-pytest](#allure-pytest)
  - [pydantic](#pydantic)
  - [pydantic-settings](#pydantic-settings)
  - [loguru](#loguru)
  - [python-dotenv](#python-dotenv)
  - [SQLAlchemy](#sqlalchemy)
  - [psycopg2-binary](#psycopg2-binary)
  - [mimesis](#mimesis)
  - [pika](#pika)
- [3. Рекомендованный “скелет” слоёв фреймворка (пример)](#3-рекомендованный-скелет-слоёв-фреймворка-пример)
- [Скачать файл](#скачать-файл)

---

## 1. Общая картина: где эти библиотеки в архитектуре

Ниже — упрощённая карта слоёв, чтобы было проще связать библиотеки с местом в проекте:

- **Test Runner / Orchestration**: `pytest`  
- **Репортинг**: `allure-pytest`  
- **Интеграции с сервисами**: `httpx` (HTTP), `pika` (RabbitMQ/AMQP)  
- **Модели данных / валидация**: `pydantic`  
- **Конфигурация / настройки**: `pydantic-settings`, `python-dotenv`  
- **Логирование**: `loguru`  
- **Данные / подготовка тестов**: `mimesis`  
- **Доступ к БД**: `sqlalchemy` + драйвер `psycopg2-binary` для PostgreSQL

---

## 2. Документация по библиотекам

### pytest

**Что это:** фреймворк и раннер для тестов на Python: фикстуры, параметризация, маркеры, плагины, гибкий запуск.  
**Зачем в автоматизации:** основной “двигатель” тестов (API/UI/интеграционные), который управляет жизненным циклом тестов и окружения.

#### Роль библиотеки во фреймворке
- Точка входа: запуск тестов, сбор тест-кейсов.
- Управление зависимостями тестов: **fixtures** (например, клиент API, подключение к БД, тестовые данные).
- Теги/маркеры: разделение smoke/regression/integration и т.п.
- Расширяемость: плагины (в т.ч. Allure).

#### Мини-пример
```python
# test_healthcheck.py
import pytest

@pytest.mark.smoke
def test_healthcheck(api_client):
    r = api_client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

# conftest.py
import pytest
import httpx

@pytest.fixture
def api_client(settings):
    return httpx.Client(base_url=settings.api_base_url, timeout=10)
```

---

### httpx

**Что это:** HTTP-клиент (sync и async) с удобным API, таймаутами, куками, прокси, HTTP/2 (по необходимости).  
**Зачем в автоматизации:** отправка запросов в API тестируемого сервиса и сервисов-зависимостей (auth, billing, feature flags и т.д.).

#### Роль библиотеки во фреймворке
- Реализация слоя **API Client** (обёртки над endpoint’ами).
- Поддержка **async** тестов/клиентов (полезно для высоконагруженных интеграционных сценариев).
- Хуки/логирование запросов (через transport / event hooks — при необходимости).

#### Мини-пример
```python
import httpx

def get_user(base_url: str, user_id: str) -> dict:
    with httpx.Client(base_url=base_url, timeout=10) as client:
        r = client.get(f"/users/{user_id}")
        r.raise_for_status()
        return r.json()
```

---

### allure-pytest

**Что это:** плагин для `pytest`, который собирает результаты прогона и формирует Allure-отчёт: шаги, вложения, артефакты, метки.  
**Зачем в автоматизации:** человекочитаемые отчёты для команды + артефакты CI (скриншоты, логи, request/response).

#### Роль библиотеки во фреймворке
- Слой **Reporting**: стандартизация метаданных тестов (severity, feature/story, links).
- Доказательная база: прикрепление входных/выходных данных (payload, логи, дампы).
- Помогает быстро локализовать падения в CI/CD.

#### Мини-пример
```python
import allure

@allure.feature("Users")
@allure.story("Get user profile")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_user_profile(api_client):
    with allure.step("Запрашиваем профиль пользователя"):
        r = api_client.get("/users/123")
        allure.attach(r.text, name="response.json", attachment_type=allure.attachment_type.JSON)
    assert r.status_code == 200
```

---

### pydantic

**Что это:** типизированные модели данных + валидация и сериализация/десериализация.  
**Зачем в автоматизации:** надёжные контракты для API (request/response), конфигураций, объектов домена, событий, DTO.

#### Роль библиотеки во фреймворке
- Слой **Domain/DTO**: модели для ответа API и запросов.
- Валидация данных теста: раннее обнаружение “кривых” данных.
- Удобная сериализация: `model_dump()` → dict, `model_dump_json()` → JSON.

#### Мини-пример
```python
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

def parse_user(payload: dict) -> User:
    return User.model_validate(payload)
```

---

### pydantic-settings

**Что это:** модуль для описания настроек приложения/фреймворка как Pydantic-моделей с загрузкой из env-переменных и поддержкой префиксов, типов и дефолтов.  
**Зачем в автоматизации:** единый, типобезопасный способ управлять настройками окружения (DEV/STAGE), токенами, URL и параметрами инфраструктуры.

#### Роль библиотеки во фреймворке
- Слой **Configuration**: “источник истины” для настроек.
- Снижение ошибок: валидирует конфиги так же строго, как DTO.
- Поддержка разных окружений: переменные окружения / `.env`.

#### Мини-пример
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_base_url: str
    db_dsn: str
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"

    model_config = SettingsConfigDict(env_prefix="AUTOTEST_", env_file=".env")

settings = Settings()
```

---

### loguru

**Что это:** удобная библиотека логирования с “из коробки” форматированием, ротацией, уровневой фильтрацией и исключениями.  
**Зачем в автоматизации:** единые структурированные логи тестов и инфраструктурных слоёв (API-клиенты, БД, очереди), полезные в CI.

#### Роль библиотеки во фреймворке
- Слой **Observability/Logging**: консольные логи + файлы с ротацией.
- Ускоряет анализ падений: stacktrace, контекст, корреляционные поля (если добавить).

#### Мини-пример
```python
from loguru import logger
import sys

def configure_logging():
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    logger.add("logs/tests.log", rotation="10 MB", retention="7 days", level="DEBUG")

configure_logging()
logger.info("Запуск тестов")
```

---

### python-dotenv

**Что это:** загрузка переменных окружения из `.env` файла (локальный запуск).  
**Зачем в автоматизации:** простой способ хранить локальные настройки (без коммита секретов в репозиторий) и поднимать окружение разработчика.

#### Роль библиотеки во фреймворке
- Слой **Configuration (local dev)**: подхватывает `.env` при локальном запуске.
- Часто используется в связке с `pydantic-settings`.

#### Мини-пример
```python
from dotenv import load_dotenv

load_dotenv(".env")  # теперь os.environ содержит переменные из файла
```

---

### SQLAlchemy

**Что это:** ORM/SQL toolkit для работы с БД: построение запросов, маппинг моделей, транзакции, соединения, пул.  
**Зачем в автоматизации:** подготовка тестовых данных, проверка данных в БД, очистка после тестов, интеграционные тесты.

#### Роль библиотеки во фреймворке
- Слой **Data Access / Repository**: абстракция доступа к БД.
- Тестовые фикстуры: создание данных и teardown.
- Поддержка нескольких СУБД (теоретически) через разные драйверы/DSN.

#### Мини-пример (SQLAlchemy 2.x, Core/ORM-сессия)
```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql+psycopg2://user:pass@localhost:5432/app", pool_pre_ping=True)
Session = sessionmaker(bind=engine)

def get_user_email(user_id: int) -> str:
    with Session() as s:
        row = s.execute(text("SELECT email FROM users WHERE id = :id"), {"id": user_id}).one()
        return row[0]
```

---

### psycopg2-binary

**Что это:** бинарная сборка драйвера `psycopg2` для PostgreSQL.  
**Зачем в автоматизации:** “низкоуровневый” драйвер, через который SQLAlchemy подключается к Postgres (и/или прямые запросы без ORM при необходимости).

#### Роль библиотеки во фреймворке
- Слой **DB Driver**: транспорт для соединения с PostgreSQL.
- Обычно используется не напрямую, а как зависимость для `sqlalchemy` DSN `postgresql+psycopg2://...`.

#### Мини-пример (прямое подключение)
```python
import psycopg2

def ping_db(dsn: str) -> bool:
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            return cur.fetchone()[0] == 1
```

---

### mimesis

**Что это:** генератор синтетических данных (имена, адреса, телефоны, документы, даты, тексты и т.д.) с локалями.  
**Зачем в автоматизации:** быстрый и управляемый выпуск тестовых данных для API/БД, особенно для параметризации и property-like тестов.

#### Роль библиотеки во фреймворке
- Слой **Test Data Factory**: фабрики данных для тестов.
- Уменьшает “хрупкость” тестов: меньше статических фикстур, больше разнообразия.
- Помогает покрывать валидации и edge cases.

#### Мини-пример
```python
from mimesis import Person, Address
from mimesis.locales import Locale

person = Person(Locale.RU)
address = Address(Locale.RU)

user_payload = {
    "firstName": person.first_name(),
    "lastName": person.last_name(),
    "email": person.email(),
    "city": address.city(),
}
```

---

### pika

**Что это:** клиент для RabbitMQ/AMQP: publish/consume сообщений, каналы, очереди, exchanges.  
**Зачем в автоматизации:** интеграционные тесты событийных систем (event-driven), проверка публикации/потребления сообщений, e2e сценарии.

#### Роль библиотеки во фреймворке
- Слой **Messaging/Integration**: обёртки над брокером сообщений.
- Проверка side-effects: “после запроса в API должно уйти событие”.
- Упрощает тестовый consumer (временно слушаем очередь, проверяем payload, чистим).

#### Мини-пример (публикация и чтение одного сообщения)
```python
import pika
import json

def publish_event(amqp_url: str, exchange: str, routing_key: str, payload: dict) -> None:
    params = pika.URLParameters(amqp_url)
    with pika.BlockingConnection(params) as conn:
        ch = conn.channel()
        ch.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=json.dumps(payload).encode("utf-8"),
            properties=pika.BasicProperties(content_type="application/json"),
        )

def consume_one(amqp_url: str, queue: str) -> bytes | None:
    params = pika.URLParameters(amqp_url)
    with pika.BlockingConnection(params) as conn:
        ch = conn.channel()
        method, props, body = ch.basic_get(queue=queue, auto_ack=True)
        return body if method else None
```

---
