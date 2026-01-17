# Документация: Python

---

## Введение

Python — универсальный язык с низким порогом входа и богатой экосистемой библиотек.  
В тестировании он особенно хорош тем, что позволяет писать **короткие, читаемые тесты** и выносить сложность в переиспользуемые компоненты (клиенты, DTO, фикстуры, утилиты).

---

## Оглавление

- [Введение](#введение)
- [1. Что такое Python и его особенности в контексте автоматизации](#1-что-такое-python-и-его-особенности-в-контексте-автоматизации)
  - [1.1. Ключевые особенности Python](#11-ключевые-особенности-python)
  - [1.2. Почему Python стал стандартом де-факто для тестирования](#12-почему-python-стал-стандартом-де-факто-для-тестирования)
- [2. Основы ООП в Python](#2-основы-ооп-в-python)
  - [2.1. Классы и объекты](#21-классы-и-объекты)
  - [2.2. Инкапсуляция](#22-инкапсуляция)
  - [2.3. Наследование](#23-наследование)
  - [2.4. Полиморфизм](#24-полиморфизм)
- [3. Работа с методами: `@staticmethod`, `@classmethod`, `@property`](#3-работа-с-методами-staticmethod-classmethod-property)
  - [3.1. Чем они отличаются](#31-чем-они-отличаются)
  - [3.2. Когда и зачем использовать](#32-когда-и-зачем-использовать)
  - [3.3. Пример](#33-пример)
- [4. Декораторы](#4-декораторы)
  - [4.1. Как работают функции высшего порядка](#41-как-работают-функции-высшего-порядка)
  - [4.2. Примеры декораторов](#42-примеры-декораторов)
  - [4.3. Как написать свой декоратор](#43-как-написать-свой-декоратор)
- [5. PEP8 и стиль написания кода](#5-pep8-и-стиль-написания-кода)
  - [5.1. Коротко о PEP8](#51-коротко-о-pep8)
  - [5.2. Инструменты: black, flake8, isort](#52-инструменты-black-flake8-isort)
  - [5.3. pre-commit хуки](#53-pre-commit-хуки)
- [6. Best Practices для Python в тестировании](#6-best-practices-для-python-в-тестировании)
  - [6.1. Ясность и читаемость кода](#61-ясность-и-читаемость-кода)
  - [6.2. Минимум логики в тестах, максимум в бизнес-объектах](#62-минимум-логики-в-тестах-максимум-в-бизнес-объектах)
  - [6.3. `assert` и pytest-фикстуры](#63-assert-и-pytest-фикстуры)
  - [6.4. Переиспользуемые helpers/утилиты](#64-переиспользуемые-helpersутилиты)
- [7. Полезные паттерны](#7-полезные-паттерны)
  - [7.1. Контекст-менеджеры (`with`)](#71-контекст-менеджеры-with)
  - [7.2. `dataclass` для DTO](#72-dataclass-для-dto)
  - [7.3. Конфигурация через `pydantic-settings`](#73-конфигурация-через-pydantic-settings)
- [8. Работа с датой и временем в Python](#8-работа-с-датой-и-временем-в-python)
  - [8.1. Обзор стандартных библиотек](#81-обзор-стандартных-библиотек)
  - [8.2. Получение текущего времени](#82-получение-текущего-времени)
  - [8.3. Парсинг и форматирование](#83-парсинг-и-форматирование)
  - [8.4. Разница между датами (timedelta)](#84-разница-между-датами-timedelta)
  - [8.5. Работа с временными зонами (`zoneinfo`)](#85-работа-с-временными-зонами-zoneinfo)
  - [8.6. Где полезно: логи, Allure, отчёты, проверки TTL](#86-где-полезно-логи-allure-отчёты-проверки-ttl)
- [Заключение](#заключение)
- [Советы по обучению и адаптации](#советы-по-обучению-и-адаптации)
- [Полезные ссылки](#полезные-ссылки)

---

## 1. Что такое Python и его особенности в контексте автоматизации

### 1.1. Ключевые особенности Python
- **Динамическая типизация**: типы есть, но часто определяются во время выполнения.
- **Интерпретируемость**: быстрый цикл «написал → запустил».
- **Читаемость**: код ближе к псевдокоду, меньше «шумных» конструкций.
- **Богатая стандартная библиотека**: JSON, HTTP, даты, файлы, логирование и т.д.
- **Экосистема**: pytest, httpx/requests, pydantic, allure, sqlalchemy и т.п.

### 1.2. Почему Python стал стандартом де-факто для тестирования
- pytest даёт **простую структуру тестов**, мощные фикстуры и отличную диагностику `assert`.
- Много готовых библиотек для API/UI/интеграционных тестов.
- Простая интеграция с CI/CD и отчётностью.
- Быстро прототипировать: удобно поднимать «обвязку» тестового фреймворка.

---

## 2. Основы ООП в Python

Python — объектно-ориентированный язык: «почти всё — объект». ООП используется в тестовых фреймворках для:
- API-клиентов,
- PageObject/Screenplay (UI),
- DTO/моделей,
- утилит и сервисов (логирование, конфиги, генераторы данных).

### 2.1. Классы и объекты
Пример простого класса:

```python
class User:
    def __init__(self, user_id: int, name: str):
        self.user_id = user_id
        self.name = name

user = User(1, "Ivan")
assert user.user_id == 1
```

### 2.2. Инкапсуляция
В Python нет «жёстких» модификаторов доступа. Обычно используют соглашения:
- `name` — публично,
- `_name` — «внутреннее», не трогать снаружи без причины,
- `__name` — name mangling (используется редко и осторожно).

```python
class TokenStore:
    def __init__(self):
        self._token = None  # внутреннее поле

    def set_token(self, token: str) -> None:
        self._token = token

    def get_token(self) -> str:
        return self._token
```

### 2.3. Наследование
```python
class ApiClient:
    def get(self, path: str):
        ...

class AuthenticatedApiClient(ApiClient):
    def __init__(self, token: str):
        self.token = token

    def get(self, path: str):
        # расширяем поведение
        ...
```

### 2.4. Полиморфизм
Полиморфизм в Python чаще «утиный» (duck typing): важнее *что объект умеет*, а не *какого он класса*.

```python
def run_healthcheck(client):
    # важно, что у client есть метод get()
    r = client.get("/health")
    return r.status_code
```

---

## 3. Работа с методами: `@staticmethod`, `@classmethod`, `@property`

### 3.1. Чем они отличаются
- **Обычный метод** (`def method(self, ...)`): работает с экземпляром (`self`).
- **`@staticmethod`**: не получает `self`/`cls`, это «функция внутри класса».
- **`@classmethod`**: получает класс (`cls`), удобно для альтернативных конструкторов.
- **`@property`**: делает метод «как поле», удобно для вычисляемых значений.

### 3.2. Когда и зачем использовать
- `@property`: вычисляемые поля (например, URL из частей).
- `@classmethod`: создание объекта из конфигурации/сырого ответа.
- `@staticmethod`: небольшие помощники, логически принадлежащие классу.

### 3.3. Пример
```python
class Example:
    class_var = 0

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @classmethod
    def from_config(cls, config):
        return cls(config["value"])

    @staticmethod
    def helper_method(x):
        return x * 2
```

---

## 4. Декораторы

Декоратор — функция, которая принимает функцию/класс и возвращает «обёртку» с изменённым поведением.

### 4.1. Как работают функции высшего порядка
```python
def apply_twice(fn, x):
    return fn(fn(x))

assert apply_twice(lambda v: v + 1, 10) == 12
```

### 4.2. Примеры декораторов
#### `@property`
```python
class Config:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    @property
    def url(self):
        return f"http://{self.host}:{self.port}"
```

#### `@lru_cache`
```python
from functools import lru_cache

@lru_cache(maxsize=1)
def load_schema():
    return {"type": "object"}
```

#### `@pytest.mark`
```python
import pytest

@pytest.mark.smoke
def test_health(api_client):
    r = api_client.get("/health")
    assert r.status_code == 200
```

### 4.3. Как написать свой декоратор
```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before call")
        result = func(*args, **kwargs)
        print("After call")
        return result
    return wrapper
```

Улучшенная версия (с сохранением метаданных):
```python
from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Before call")
        result = func(*args, **kwargs)
        print("After call")
        return result
    return wrapper
```

---

## 5. PEP8 и стиль написания кода

### 5.1. Коротко о PEP8
- Отступы: **4 пробела**.
- Имена: `snake_case` (функции/переменные), `PascalCase` (классы), `UPPER_CASE` (константы).
- Импорты: стандартная библиотека → сторонние → локальные.

### 5.2. Инструменты: black, flake8, isort
- **black** — автоформатирование.
- **isort** — сортировка импортов.
- **flake8** — линтер.

```bash
pip install black flake8 isort
```

### 5.3. pre-commit хуки
```bash
pip install pre-commit
pre-commit install
```

`.pre-commit-config.yaml` (пример):
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black

  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/PyCQA/flake8
    rev: 7.1.1
    hooks:
      - id: flake8
```

Запуск:
```bash
pre-commit run --all-files
```

---

## 6. Best Practices для Python в тестировании

### 6.1. Ясность и читаемость кода
- Тест — документация: пишите, чтобы было понятно «что проверяем».
- Сложную логику выносите в клиенты/утилиты/DTO.

### 6.2 Минимум логики в тестах, максимум в бизнес-объектах
```python
def test_create_user(api_client):
    r = api_client.create_user({"name": "Ivan"})
    assert r.status_code == 201
```

### 6.3 `assert` и pytest-фикстуры
- `assert` должен быть конкретным и диагностируемым.
- фикстуры — для подготовки окружения и зависимостей.

```python
import pytest

@pytest.fixture
def api_client(settings):
    return ApiClient(base_url=settings.BASE_URL)
```

### 6.4 Переиспользуемые helpers/утилиты
- повторяемые проверки → `assert_*` функции,
- повторяемые действия → шаги/клиенты,
- минимум побочных эффектов.

---

## 7. Полезные паттерны

### 7.1. Контекст-менеджеры (`with`)
```python
with open("data.json", "r", encoding="utf-8") as f:
    content = f.read()
```

Свой контекст-менеджер:
```python
from contextlib import contextmanager

@contextmanager
def temp_value(container: dict, key: str, value):
    old = container.get(key)
    container[key] = value
    try:
        yield
    finally:
        if old is None:
            container.pop(key, None)
        else:
            container[key] = old
```

### 7.2. `dataclass` для DTO
```python
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    is_active: bool
```

### 7.3. Конфигурация через `pydantic-settings`
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MODE: str = "local"
    BASE_URL: str
    TIMEOUT: float = 10.0
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")

settings = Settings()
```

---

## 8. Работа с датой и временем в Python

В тестовой автоматизации дата/время встречаются постоянно: в логах и отчётах, проверках **TTL/expiration**, сравнениях временных меток, генерации тестовых данных и валидации времени ответа.

### 8.1. Обзор стандартных библиотек

- **`datetime`** — основной модуль для дат/времени (date/time/datetime/timedelta).
- **`time`** — низкоуровневые функции времени (timestamp, sleep, измерение длительности).
- **`dateutil`** (пакет `python-dateutil`) — удобные расширения: гибкий парсинг дат, относительные смещения (`relativedelta`), timezone-утилиты. Полезен, когда стандартного `datetime` недостаточно.

> В большинстве тестов достаточно `datetime` + `zoneinfo`.

---

### 8.2. Получение текущего времени

```python
from datetime import datetime
now = datetime.now()
print(now.isoformat())
```

---

### 8.3. Парсинг и форматирование

```python
from datetime import datetime

date_str = "2023-01-01 14:30"
dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
print(dt.strftime("%d.%m.%Y"))
```

---

### 8.4. Разница между датами (timedelta)

```python
from datetime import datetime, timedelta
yesterday = datetime.now() - timedelta(days=1)
```

---

### 8.5. Работа с временными зонами (`zoneinfo`)

```python
from datetime import datetime
from zoneinfo import ZoneInfo

dt = datetime.now(ZoneInfo("Europe/Moscow"))
print(dt.isoformat())
```

---

### 8.6. Где полезно: логи, Allure, отчёты, проверки TTL
- **Логи**: человеко-читаемые timestamp’ы, измерение длительности шагов.
- **Allure/отчёты**: вложения с временем, метки запуска, диагностические данные.
- **Проверки TTL/expiration**: токены, кэш, подписанные URL, временные доступы.

---

## Заключение

Python в автоматизации — это про простые тесты, мощный pytest, DTO/конфиги и аккуратный стиль кода.  
Единые правила (PEP8 + pre-commit + архитектура клиентов/фикстур/DTO) сильно ускоряют развитие фреймворка.

---

## Полезные ссылки
- Python docs: https://docs.python.org/3/
- PEP8: https://peps.python.org/pep-0008/
- pytest docs: https://docs.pytest.org/
- Real Python (гайды): https://realpython.com/
