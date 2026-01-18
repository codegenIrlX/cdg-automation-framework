# Документация: **pydantic** и **pydantic-settings**

---


## Оглавление

- [1. Введение](#1-введение)
  - [1.1. Краткое определение: pydantic и pydantic-settings](#11-краткое-определение-pydantic-и-pydantic-settings)
  - [1.2. Зачем они используются в тестовых и backend‑фреймворках](#12-зачем-они-используются-в-тестовых-и-backendфреймворках)
  - [1.3. Преимущества использования](#13-преимущества-использования)
- [2. Установка](#2-установка)
- [3. Создание DTO с помощью Pydantic](#3-создание-dto-с-помощью-pydantic)
  - [3.1. Простой пример модели](#31-простой-пример-модели)
  - [3.2. Обработка вложенных моделей](#32-обработка-вложенных-моделей)
  - [3.3. Валидация данных и кастомные ошибки](#33-валидация-данных-и-кастомные-ошибки)
  - [3.4. Пример использования в тестах или API](#34-пример-использования-в-тестах-или-api)
- [4. Конфигурация проекта с помощью Pydantic Settings](#4-конфигурация-проекта-с-помощью-pydantic-settings)
  - [4.1. Пример `BaseSettings` + `.env`](#41-пример-basesettings-env)
  - [4.2. Как работает `SettingsConfigDict` и зачем нужен `.env`](#42-как-работает-settingsconfigdict-и-зачем-нужен-env)
  - [4.3. Как внедрять конфигурации в проект (тесты, фикстуры, main)](#43-как-внедрять-конфигурации-в-проект-тесты-фикстуры-main)
  - [4.4. Как обрабатывать переменные окружения](#44-как-обрабатывать-переменные-окружения)
- [5. Best Practices](#5-best-practices)
  - [5.1. Отделение DTO от бизнес‑логики](#51-отделение-dto-от-бизнеслогики)
  - [5.2. Как правильно использовать BaseSettings в тестовой архитектуре](#52-как-правильно-использовать-basesettings-в-тестовой-архитектуре)
  - [5.3. Как валидировать значения при запуске](#53-как-валидировать-значения-при-запуске)
- [6. Ошибки и отладка](#6-ошибки-и-отладка)
  - [6.1. Что делать при отсутствии переменной окружения](#61-что-делать-при-отсутствии-переменной-окружения)
  - [6.2. Как обрабатывать ошибки валидации](#62-как-обрабатывать-ошибки-валидации)
- [7. Полезные ссылки](#7-полезные-ссылки)
  - [Официальная документация](#официальная-документация)
  - [GitHub-репозитории](#github-репозитории)
  - [Туториалы и гайды](#туториалы-и-гайды)
- [Приложение: краткая памятка](#приложение-краткая-памятка)
  - [DTO](#dto)
  - [Settings](#settings)


## 1. Введение

### 1.1. Краткое определение: pydantic и pydantic-settings
**pydantic** — библиотека для создания моделей данных на основе Python type hints. Она:
- приводит входные данные к ожидаемым типам (parsing/coercion),
- валидирует значения,
- формирует понятные ошибки валидации,
- сериализует/десериализует данные (dict/json).

**pydantic-settings** — надстройка над pydantic для конфигураций проекта:
- читает переменные окружения (`ENV`),
- умеет подхватывать `.env`,
- валидирует конфигурацию при старте,
- позволяет собрать типобезопасный объект настроек.

---

### 1.2. Зачем они используются в тестовых и backend‑фреймворках
В проектах автоматизации и в бекенде pydantic обычно решает две крупные задачи:

1) **DTO / Контракты данных**
- Строго описать структуру входных/выходных данных (API payloads, ответы сервисов, сообщения брокеров).
- Валидировать контракты на уровне автотестов (вместо ручных assert по полям).
- Минимизировать «рассыпание» тестов из‑за неявных изменений схем.

2) **Конфигурация проекта**
- Единый объект настроек (BASE_URL, DB_URL, креды, таймауты, режим запуска).
- Предсказуемое и валидируемое чтение из `ENV`/`.env`.
- Раннее выявление ошибок конфигурации (до запуска тестов/приложения).

---

### 1.3. Преимущества использования
- **Валидация**: данные проверяются автоматически и централизованно.
- **Типизация**: IDE/линтеры помогают быстрее и безопаснее писать код.
- **Читаемость**: схема данных описана в одном месте, а не размазана по тестам.
- **Удобство конфигурации**: переменные окружения превращаются в типобезопасный объект.
- **Надёжность**: ошибки конфигурации и данных обнаруживаются раньше.

---

## 2) Установка

```bash
pip install pydantic pydantic-settings
```

> Рекомендуется фиксировать версии в `requirements.txt`/`pyproject.toml`, чтобы избежать неожиданных изменений поведения при обновлении.

---

## 3. Создание DTO с помощью Pydantic

### 3.1. Простой пример модели
```python
from pydantic import BaseModel

class UserDTO(BaseModel):
    id: int
    name: str
    is_active: bool
```

Использование:
```python
payload = {"id": 1, "name": "Ivan", "is_active": True}
user = UserDTO(**payload)

assert user.id == 1
assert user.name == "Ivan"
assert user.is_active is True
```

#### Зачем DTO в тестах
- тесты читаются как «контракт»,
- меньше ручных проверок структуры,
- валидируется типизация и обязательность полей.

---

### 3.2. Обработка вложенных моделей
DTO часто имеют вложенные структуры: профиль, адрес, роли и т.д.

```python
from pydantic import BaseModel

class AddressDTO(BaseModel):
    city: str
    street: str
    zip_code: str

class UserDTO(BaseModel):
    id: int
    name: str
    is_active: bool
    address: AddressDTO
```

Использование:
```python
payload = {
    "id": 10,
    "name": "Ivan",
    "is_active": True,
    "address": {"city": "Amsterdam", "street": "Damrak", "zip_code": "1012"},
}

user = UserDTO(**payload)
assert user.address.city == "Amsterdam"
```

> Pydantic автоматически создаёт `AddressDTO` из словаря.

---

### 3.3. Валидация данных и кастомные ошибки

#### Базовая валидация и ошибки
Если данные не соответствуют схеме, pydantic выбросит `ValidationError`:

```python
from pydantic import BaseModel, ValidationError

class UserDTO(BaseModel):
    id: int
    name: str
    is_active: bool

try:
    UserDTO(id="abc", name=123, is_active="yes")
except ValidationError as e:
    print(e)
```

Что важно:
- ошибка содержит список проблем по каждому полю,
- удобно логировать/прикладывать в Allure как attachment.

#### Кастомная валидация (пример)
В pydantic v2 применяется `@field_validator`:

```python
from pydantic import BaseModel, field_validator

class UserDTO(BaseModel):
    id: int
    name: str
    is_active: bool

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be empty")
        return v
```

---

### 3.4. Пример использования в тестах или API

#### Пример: проверка ответа API
```python
from pydantic import BaseModel

class UserDTO(BaseModel):
    id: int
    name: str
    is_active: bool

def test_get_user(api_client):
    r = api_client.get("/users/1")
    assert r.status_code == 200

    user = UserDTO(**r.json())
    assert user.id == 1
    assert user.is_active is True
```

---

## 4. Конфигурация проекта с помощью Pydantic Settings

### 4.1. Пример `BaseSettings` + `.env`
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MODE: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DB_URL(self):
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

---

### 4.2. Как работает `SettingsConfigDict` и зачем нужен `.env`
`SettingsConfigDict` — конфигурация поведения settings‑модели. Частые параметры:
- `env_file`: путь к `.env` файлу (локальная конфигурация),
- `env_prefix`: префикс переменных (например, `APP_`),
- `case_sensitive`: чувствительность к регистру (по необходимости),
- `extra`: поведение для лишних переменных (в зависимости от политики проекта).

`.env` удобен для:
- локальной разработки/запуска тестов без ручного экспорта переменных,
- стандартизации окружения для команды,
- хранения некритичных настроек.

Пример `.env`:
```dotenv
MODE=local
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=app_db
```

> Важно: реальные секреты (пароли/токены) лучше хранить в секрет‑хранилищах CI, а `.env` держать в `.gitignore` или использовать `.env.example`.

---

### 4.3. Как внедрять конфигурации в проект (тесты, фикстуры, main)

#### Вариант A: единый объект settings в `src/config.py`
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MODE: str = "local"
    BASE_URL: str
    TIMEOUT: float = 10.0
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

Использование в клиенте:
```python
from src.config import settings

class ApiClient:
    def __init__(self):
        self.base_url = settings.BASE_URL
        self.timeout = settings.TIMEOUT
```

#### Вариант B: инъекция settings через фикстуры pytest
```python
# tests/conftest.py
import pytest
from src.config import settings

@pytest.fixture(scope="session")
def cfg():
    return settings

@pytest.fixture(scope="session")
def api_client(cfg):
    return ApiClient(base_url=cfg.BASE_URL, timeout=cfg.TIMEOUT)
```

#### Вариант C: в main‑приложении
```python
from src.config import settings

def main():
    print("MODE =", settings.MODE)
    # инициализация приложения/ресурсов
```

---

### 4.4. Как обрабатывать переменные окружения
Рекомендации:
- В CI/CD задавайте переменные окружения через секреты/настройки job.
- `.env` используйте для локального запуска (без секретов или под `.gitignore`).
- Договоритесь о `MODE` (local/stage/prod), который переключает окружения.

Пример с префиксом:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BASE_URL: str
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env")

# Ожидается APP_BASE_URL
```

---

## 5. Best Practices

### 5.1. Отделение DTO от бизнес‑логики
- DTO описывают **данные**, а не процесс.
- Не превращайте DTO в сервисный слой.
- Для преобразований используйте отдельные функции/мапперы.

Рекомендуемая структура:
```
src/
  dto/
    user.py
    order.py
  config.py
  clients/
    api_client.py
tests/
  ...
```

---

### 5.2. Как правильно использовать BaseSettings в тестовой архитектуре
- Создайте **один** объект `settings` на сессию (`scope="session"`), чтобы не пересоздавать на каждый тест.
- Не разносите чтение `ENV` по проекту — только в одном месте (`config.py`).
- Для разных окружений используйте `MODE` + переопределение переменных в CI.

---

### 5.3. Как валидировать значения при запуске
Сильная сторона settings‑модели: если переменная отсутствует или тип неверный — вы получите ошибку сразу при создании `Settings()`.

Практика:
- создавать settings на старте тестового прогона (при импорте `config.py`),
- логировать/прикладывать часть конфигурации в отчёты (без секретов).

---

## 6. Ошибки и отладка

### 6.1. Что делать при отсутствии переменной окружения
Если переменная обязательна и не задана, при создании settings будет `ValidationError`.

Решения:
- задать значение в `.env` (локально),
- экспортировать `ENV` в окружении,
- добавить дефолт (если допустимо):
```python
class Settings(BaseSettings):
    MODE: str = "local"
```

---

### 6.2. Как обрабатывать ошибки валидации
Не «глотайте» ошибки, делайте их максимально информативными:
- логируйте `ValidationError`,
- прикладывайте в Allure как TEXT/JSON (если используете отчёты),
- явно указывайте требуемые переменные.

Пример:
```python
from pydantic import ValidationError

try:
    settings = Settings()
except ValidationError as e:
    raise RuntimeError(f"Invalid configuration: {e}") from e
```

> Важно: не логируйте секреты (пароли/токены) в чистом виде.

---

## 7. Полезные ссылки

### Официальная документация
- Pydantic: https://docs.pydantic.dev/
- pydantic-settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/

### GitHub-репозитории
- Pydantic: https://github.com/pydantic/pydantic
- pydantic-settings: https://github.com/pydantic/pydantic-settings

### Туториалы и гайды
- Официальные примеры в документации Pydantic: Models/Validation/Serialization.
- Документация pydantic-settings: Settings, env/.env, config options.
- Поисковые запросы: `pydantic v2 field_validator`, `pydantic settings BaseSettings env_file`.

---

## Приложение: краткая памятка

### DTO
- Используйте `BaseModel` для описания контрактов.
- Валидируйте ответы API через DTO — это уменьшает количество ручных проверок.

### Settings
- `BaseSettings` + `SettingsConfigDict(env_file=".env")` для локального запуска.
- В CI задавайте переменные окружения через секреты/секрет‑хранилища.
- Валидируйте конфигурацию на старте.
