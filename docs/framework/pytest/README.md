# Документация по **pytest**

---


## Оглавление

- [1. Введение](#1-введение)
  - [Что такое pytest](#что-такое-pytest)
  - [Зачем pytest в тестовом фреймворке](#зачем-pytest-в-тестовом-фреймворке)
  - [Преимущества](#преимущества)
- [2. Установка и запуск тестов](#2-установка-и-запуск-тестов)
  - [Установка](#установка)
  - [Базовый запуск](#базовый-запуск)
  - [Запуск конкретных тестов](#запуск-конкретных-тестов)
  - [Фильтрация по имени (substring)](#фильтрация-по-имени-substring)
  - [Остановка на первой ошибке](#остановка-на-первой-ошибке)
  - [Перезапуск упавших тестов (при использовании плагинов)](#перезапуск-упавших-тестов-при-использовании-плагинов)
  - [Полезные флаги вывода](#полезные-флаги-вывода)
- [3. Структура тестов](#3-структура-тестов)
  - [Тесты-функции](#тесты-функции)
  - [Тесты-классы](#тесты-классы)
  - [Именование и читаемость](#именование-и-читаемость)
- [4. Фикстуры (Fixtures)](#4-фикстуры-fixtures)
  - [4.1. Как создавать фикстуры: `@pytest.fixture`](#41-как-создавать-фикстуры-pytestfixture)
  - [4.2. Scope фикстур: `function`, `class`, `module`, `session`](#42-scope-фикстур-function-class-module-session)
  - [4.3. Внедрение фикстур через аргументы](#43-внедрение-фикстур-через-аргументы)
  - [4.4. Размещение фикстур в `conftest.py` и переиспользование](#44-размещение-фикстур-в-conftestpy-и-переиспользование)
  - [4.5. Отличие setup/teardown от фикстур](#45-отличие-setupteardown-от-фикстур)
  - [4.6. Автофикстуры: `autouse=True` и когда использовать](#46-автофикстуры-autousetrue-и-когда-использовать)
- [5. Управление тестовым окружением: teardown и `yield`](#5-управление-тестовым-окружением-teardown-и-yield)
  - [5.1. Teardown через `yield`](#51-teardown-через-yield)
  - [5.2. setup/teardown в классах (когда нужно)](#52-setupteardown-в-классах-когда-нужно)
- [6. Параметризация](#6-параметризация)
  - [6.1. `@pytest.mark.parametrize`](#61-pytestmarkparametrize)
  - [6.2. Параметризация через фикстуры](#62-параметризация-через-фикстуры)
  - [6.3. Indirect параметризация (передать параметр в фикстуру)](#63-indirect-параметризация-передать-параметр-в-фикстуру)
- [7. Маркировка тестов (Markers)](#7-маркировка-тестов-markers)
  - [7.1. Использование `@pytest.mark.<tag>`](#71-использование-pytestmarktag)
  - [7.2) Запуск маркированных тестов через CLI](#72-запуск-маркированных-тестов-через-cli)
  - [7.3. Регистрация маркеров (важно!)](#73-регистрация-маркеров-важно)
- [8. Полезные команды CLI и best practices](#8-полезные-команды-cli-и-best-practices)
  - [Полезные команды](#полезные-команды)
  - [Best practices](#best-practices)
- [9. Рекомендации по организации проекта с pytest](#9-рекомендации-по-организации-проекта-с-pytest)
  - [Пример структуры проекта](#пример-структуры-проекта)
  - [Что хранить в `conftest.py`](#что-хранить-в-conftestpy)
  - [Что не хранить в `conftest.py`](#что-не-хранить-в-conftestpy)
- [10. Полезные ссылки](#10-полезные-ссылки)
- [Приложение: Мини-шпаргалка команды запуска](#приложение-мини-шпаргалка-команды-запуска)


## 1. Введение

### Что такое pytest
**pytest** — это популярный Python-фреймворк для написания и запуска автотестов. Он поддерживает:
- простой синтаксис тестов (функции/классы без «магии»),
- мощную систему **фикстур** (подготовка/очистка окружения),
- **параметризацию** (прогон теста на наборах данных),
- удобный **CLI** (фильтры, маркеры, отчёты, плагины),
- интеграцию с экосистемой (Allure, coverage, xdist и т.д.).

### Зачем pytest в тестовом фреймворке
В рамках тестового фреймворка pytest обычно отвечает за:
- **обнаружение тестов** (test discovery) по правилам именования,
- **управление жизненным циклом** теста (подготовка → выполнение → очистка),
- **зависимости тестов** через фикстуры (DB, API-клиенты, конфиги, тест-данные),
- **гибкий запуск** (smoke/regression, окружения, фильтры),
- **расширяемость** (хуки, плагины, собственные маркеры).

### Преимущества
- Минимальный boilerplate: тест = обычная функция `test_*`.
- Фикстуры вместо тяжёлых `setUp/tearDown`.
- Удобная параметризация.
- Отличная экосистема плагинов (Allure, parallel, rerun, mocking и др.).
- Прозрачные отчёты и диагностические сообщения (assert introspection).

---

## 2. Установка и запуск тестов

### Установка
```bash
pip install -U pytest
# или в составе зависимостей проекта:
pip install -r requirements.txt
```

Проверка версии:
```bash
pytest --version
```

### Базовый запуск
Запуск всех тестов в проекте:
```bash
pytest
```

Запуск с более подробным выводом:
```bash
pytest -v
```

### Запуск конкретных тестов
Запуск файла:
```bash
pytest tests/test_users.py
```

Запуск директории:
```bash
pytest tests/api/
```

Запуск одного теста по ноде (node id):
```bash
pytest tests/test_users.py::test_create_user
```

Запуск конкретного тестового класса:
```bash
pytest tests/test_users.py::TestUsers
```

### Фильтрация по имени (substring)
```bash
pytest -k "login"
pytest -k "login and not slow"
```

### Остановка на первой ошибке
```bash
pytest -x
```

### Перезапуск упавших тестов (при использовании плагинов)
> Часто используют `pytest-rerunfailures`:
```bash
pytest --reruns 2
```

### Полезные флаги вывода
Показать `print()` в консоли:
```bash
pytest -s
```

Показать локальные переменные при падении:
```bash
pytest -l
```

---

## 3. Структура тестов

### Тесты-функции
pytest «подхватывает» тестовые функции по умолчанию, если:
- файл называется `test_*.py` или `*_test.py`,
- функция называется `test_*`.

Пример:
```python
def test_sum():
    assert 1 + 1 == 2
```

### Тесты-классы
Классы должны начинаться с `Test*` (по умолчанию) и **не иметь** `__init__`.

Пример:
```python
class TestMath:
    def test_mul(self):
        assert 2 * 3 == 6
```

### Именование и читаемость
Рекомендации:
- имя теста описывает **ожидаемое поведение**: `test_create_user_returns_201`.
- избегайте «общих» имён вроде `test_1`, `test_ok`.
- структура папок отражает домены: `tests/api/`, `tests/ui/`, `tests/integration/`.

---

## 4. Фикстуры (Fixtures)

Фикстуры — это механизм pytest для:
- подготовки данных/окружения перед тестом,
- передачи зависимостей в тест через аргументы,
- выполнения очистки после теста,
- переиспользования общей логики между тестами.

### 4.1. Как создавать фикстуры: `@pytest.fixture`
Минимальный пример:
```python
import pytest

@pytest.fixture
def user_payload():
    return {"name": "Ivan", "age": 30}
```

Использование в тесте — просто как аргумент:
```python
def test_user_payload_has_name(user_payload):
    assert "name" in user_payload
```

---

### 4.2. Scope фикстур: `function`, `class`, `module`, `session`

**scope** определяет «время жизни» фикстуры:
- `function` — создаётся на **каждый тест** (дефолт).
- `class` — один раз на **класс**.
- `module` — один раз на **файл** (модуль).
- `session` — один раз на **весь прогон** pytest.

Примеры:

#### scope="function" (по умолчанию)
```python
import pytest

@pytest.fixture(scope="function")
def fresh_object():
    return object()
```

#### scope="class"
```python
import pytest

@pytest.fixture(scope="class")
def token():
    return "class-token"
```

#### scope="module"
```python
import pytest

@pytest.fixture(scope="module")
def api_client():
    # создать клиент один раз для файла
    return MyApiClient(base_url="https://example.org")
```

#### scope="session"
Подходит для «дорогих» ресурсов: конфиги, подключение к внешним сервисам, общий контекст.

**Пример из требования:**
```python
import pytest

@pytest.fixture(scope='session', autouse=True)
def faker_session_locale():
    return ['ru_RU']
```

> Важно: если фикстура используется как «настройка» (например, локаль), убедитесь, что она реально применяется (например, используется библиотекой генерации данных), а не просто «возвращается».

---

### 4.3. Внедрение фикстур через аргументы
pytest сопоставляет параметры тестовой функции с именами фикстур:
```python
import pytest

@pytest.fixture
def db_connection():
    return connect_to_db()

def test_select_works(db_connection):
    rows = db_connection.select("select 1")
    assert rows == [(1,)]
```

---

### 4.4. Размещение фикстур в `conftest.py` и переиспользование

`conftest.py` — специальный файл pytest, который:
- **автоматически** подхватывается pytest (импортировать не нужно),
- используется для хранения общих фикстур, хуков, настроек,
- действует **в пределах директории и её поддиректорий**.

Пример структуры:
```
project/
  tests/
    conftest.py
    api/
      test_users.py
    ui/
      test_login.py
```

`tests/conftest.py`:
```python
import pytest

@pytest.fixture(scope="session")
def base_url():
    return "https://api.example.org"
```

`tests/api/test_users.py`:
```python
def test_healthcheck(base_url):
    assert base_url.startswith("https://")
```

**Принципы переиспользования фикстур**
- Храните общие фикстуры в `tests/conftest.py`.
- Доменные/специфичные фикстуры — ближе к тестам (например, `tests/api/conftest.py`).
- Держите фикстуры «тонкими»: они должны **собирать** зависимости, а не содержать «всю бизнес-логику».
- Сложные построители данных выносите в helpers/factories.

---

### 4.5. Отличие setup/teardown от фикстур

**setup/teardown** (xUnit-стиль) — методы внутри классов:
- `setup_method(self)`, `teardown_method(self)`
- `setup_class(cls)`, `teardown_class(cls)`

Пример:
```python
class TestExample:
    def setup_method(self):
        self.data = []

    def teardown_method(self):
        self.data.clear()

    def test_append(self):
        self.data.append(1)
        assert self.data == [1]
```

**Фикстуры** — более гибкий и переиспользуемый механизм:
- не привязаны к классу,
- легко комбинируются,
- управляют scope,
- можно использовать `yield` для teardown,
- поддерживают параметризацию.

**Рекомендация:** в проектах автоматизации чаще используйте **фикстуры**, а `setup/teardown` оставляйте для редких случаев, когда это действительно упрощает конкретный тест-класс.

---

### 4.6. Автофикстуры: `autouse=True` и когда использовать

`autouse=True` означает, что фикстура применяется автоматически **без явного указания** в аргументах теста.

Пример:
```python
import pytest

@pytest.fixture(autouse=True)
def _set_test_mode(monkeypatch):
    monkeypatch.setenv("APP_MODE", "test")
```

**Когда использовать autouse**
- Единая настройка окружения для всех тестов (env vars, тестовый режим).
- Гарантированная очистка глобального состояния (в пределах разумного).
- Централизованные «защитные» меры (например, запрет real HTTP в unit-тестах).

**Когда НЕ использовать autouse**
- Если фикстура тяжёлая (DB reset, внешние вызовы) — лучше явно подключать.
- Если фикстура влияет на поведение тестов «скрытно» и усложняет дебаг.

---

## 5. Управление тестовым окружением: teardown и `yield`

### 5.1. Teardown через `yield`
Очень частый паттерн: «подготовили → отдали объект → после теста очистили».

```python
import pytest

@pytest.fixture
def temp_user(api_client):
    user_id = api_client.create_user({"name": "Temp"})
    yield user_id
    api_client.delete_user(user_id)
```

### 5.2. setup/teardown в классах (когда нужно)
Иногда удобно для набора тестов в одном классе, но помните, что фикстуры обычно гибче:

```python
class TestOrders:
    @classmethod
    def setup_class(cls):
        cls.client = MyApiClient()

    @classmethod
    def teardown_class(cls):
        cls.client.close()

    def test_create_order(self):
        assert self.client.create_order() is not None
```

---

## 6. Параметризация

### 6.1. `@pytest.mark.parametrize`
Прогон одного теста на разных входных данных.

```python
import pytest

@pytest.mark.parametrize(
    "a,b,expected",
    [
        (1, 1, 2),
        (2, 3, 5),
        (-1, 1, 0),
    ],
)
def test_add(a, b, expected):
    assert a + b == expected
```

Несколько параметров сразу:
```python
import pytest

@pytest.mark.parametrize("status", [200, 201, 204])
@pytest.mark.parametrize("method", ["GET", "POST"])
def test_methods(method, status):
    ...
```

### 6.2. Параметризация через фикстуры
Фикстуры можно параметризовать через `params=`:

```python
import pytest

@pytest.fixture(params=["chrome", "firefox"])
def browser_name(request):
    return request.param

def test_ui_smoke(browser_name):
    assert browser_name in ("chrome", "firefox")
```

### 6.3. Indirect параметризация (передать параметр в фикстуру)
Иногда нужно параметризовать не тест, а «внутренности» фикстуры:

```python
import pytest

@pytest.fixture
def user(request):
    role = request.param
    return {"name": "Ivan", "role": role}

@pytest.mark.parametrize("user", ["admin", "viewer"], indirect=True)
def test_user_role(user):
    assert user["role"] in ("admin", "viewer")
```

---

## 7. Маркировка тестов (Markers)

### 7.1. Использование `@pytest.mark.<tag>`
Маркер — это «тег» для теста: smoke/regression/slow и т.п.

```python
import pytest

@pytest.mark.smoke
def test_healthcheck():
    assert True

@pytest.mark.regression
def test_complex_flow():
    assert True
```

### 7.2) Запуск маркированных тестов через CLI
Запустить только smoke:
```bash
pytest -m smoke
```

Запустить regression, исключив slow:
```bash
pytest -m "regression and not slow"
```

### 7.3. Регистрация маркеров (важно!)
Чтобы pytest не ругался на неизвестные маркеры, добавьте их в `pytest.ini`.

`pytest.ini`:
```ini
[pytest]
markers =
    smoke: быстрые проверки критического пути
    regression: регрессионные тесты
    slow: долгие тесты
testpaths = tests
addopts = -ra
```

---

## 8. Полезные команды CLI и best practices

### Полезные команды
Показать список фикстур:
```bash
pytest --fixtures
pytest --fixtures-per-test
```

Показать, какие тесты будут запущены (без запуска):
```bash
pytest --collect-only
```

Показать краткую сводку причин скипа/xfail:
```bash
pytest -ra
```

Запуск с «короткими» трассировками:
```bash
pytest --tb=short
```

Запуск в несколько процессов (плагин `pytest-xdist`):
```bash
pytest -n auto
```

### Best practices
- **Делайте фикстуры маленькими и композиционными**: лучше 3 простые фикстуры, чем 1 огромная.
- **Не прячьте тяжёлую логику за `autouse`**: это ухудшает предсказуемость.
- **Изолируйте тесты**: каждый тест должен быть независимым и воспроизводимым.
- **Избегайте `sleep()`**: используйте ожидания/ретраи на уровне клиента/помощников.
- **Явно описывайте маркеры и договорённости** в `pytest.ini` и README.
- **Разделяйте уровни тестов** (unit/api/ui/integration) по папкам и маркерам.
- **Не смешивайте ответственность**: фикстура готовит окружение, а assert — в тесте.

---

## 9. Рекомендации по организации проекта с pytest

### Пример структуры проекта
```
project/
  src/
    app/
      ...
  tests/
    conftest.py
    api/
      conftest.py
      test_users.py
    ui/
      conftest.py
      test_login.py
    integration/
      test_db_migrations.py
  pytest.ini
  requirements.txt
  README.md
```

### Что хранить в `conftest.py`
- общие фикстуры (клиенты, конфиги, креды из env, фабрики данных),
- хуки pytest (если требуется),
- общие настройки окружения (с осторожностью).

### Что не хранить в `conftest.py`
- бизнес-логика тестов,
- «захардкоженные» секреты,
- слишком специфичные фикстуры, которые нужны только одному файлу (лучше держать рядом).

---

## 10. Полезные ссылки
- Официальная документация pytest
- Fixtures: фикстуры и scope
- Markers: маркировка и фильтрация
- Parametrize: параметризация тестов
- Plugins: экосистема плагинов

- https://docs.pytest.org/
- https://docs.pytest.org/en/stable/how-to/fixtures.html
- https://docs.pytest.org/en/stable/how-to/mark.html
- https://docs.pytest.org/en/stable/how-to/parametrize.html
- https://docs.pytest.org/en/stable/reference/plugin_list.html

---

## Приложение: Мини-шпаргалка команды запуска
```bash
pytest                           # запустить всё
pytest -v                        # подробный вывод
pytest tests/api/                # папка
pytest tests/test_x.py::test_y   # конкретный тест
pytest -k "login"                # фильтр по имени
pytest -m smoke                  # по маркеру
pytest -m "regression and not slow"
pytest -s                        # показать print()
pytest -x                        # стоп на 1й ошибке
pytest --collect-only            # показать, что будет запущено
pytest --fixtures                # список фикстур
```
