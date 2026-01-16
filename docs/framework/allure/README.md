# Документация по **allure-pytest**

---

## 1. Введение

### 1.1. Что такое Allure и allure-pytest
**Allure Report** — система формирования тестовых отчётов, которая собирает результаты выполнения тестов и визуализирует их в виде удобного HTML-интерфейса.

**allure-pytest** — плагин для pytest, который:
- собирает результаты выполнения тестов и метаданные Allure (аннотации, шаги, labels/tags, severity),
- сохраняет их в формате `allure-results` (набор JSON + вложения),
- позволяет построить HTML-отчёт через Allure CLI (`allure-commandline`).

### 1.2. Какие задачи решает и зачем нужен в автоматизации
Allure полезен, когда нужно:
- быстро понять **что упало**, **где упало** и **почему** (стек-трейс, шаги, вложения),
- сделать отчёт понятным не только автоматизаторам,
- хранить артефакты: запрос/ответ API, логи, скриншоты, дампы, файлы,
- стандартизировать описание тестов: заголовки, описание, принадлежность к подсистемам.

### 1.3. Преимущества визуализации отчётов
- **Читаемость**: группировка по Suites/Tags/Labels.
- **Диагностика**: шаги (Steps) + вложения (Attachments) ускоряют разбор падений.
- **Единый формат**: одинаковый подход для API/UI/интеграции.
- **CI-friendly**: результаты/отчёт можно хранить как артефакты пайплайна.

---

## 2. Установка и настройка

### 2.1. Установка зависимостей

#### Python-зависимость: `allure-pytest`
```bash
pip install -U allure-pytest
```

#### Allure CLI: `allure-commandline`
Нужен для генерации/открытия HTML-отчёта.
Ставится отдельно (пакетный менеджер ОС / скачивание релиза / Docker), т.к. это не Python-пакет.

> `allure-pytest` создаёт `allure-results`, а HTML-страницу строит **Allure CLI**.

---

### 2.2. Интеграция в проект на pytest
Минимальная интеграция:
1) установить `allure-pytest`,
2) запускать `pytest` с `--alluredir=<папка>`.

Рекомендуется зафиксировать базовые настройки в `pytest.ini`:

```ini
[pytest]
testpaths = tests
addopts = -ra
markers =
    smoke: быстрые проверки критического пути
    regression: регресс
    slow: долгие тесты
```

---

### 2.3. Пример `requirements.txt`
```txt
pytest>=8.3.0
allure-pytest>=2.13.5
# (опционально)
# pytest-xdist>=3.6.1
# pytest-rerunfailures>=14.0
```

---

## 3. Сборка и просмотр отчёта

### 3.1. Запуск тестов с генерацией результатов
```bash
pytest --alluredir=allure-results
```

Просмотр отчёта (быстро, через локальный сервер):
```bash
allure serve allure-results
```

---

### 3.2. Как сохранить отчёт и открыть локально

#### Генерация статического HTML-отчёта
```bash
allure generate allure-results -o allure-report --clean
```

#### Открытие ранее сгенерированного отчёта
```bash
allure open allure-report
```

> Отличие:
> - `allure serve` — генерирует и сразу открывает.
> - `allure generate` — сохраняет статический отчёт (удобно для CI-артефактов).
> - `allure open` — открывает уже сгенерированный отчёт.

---

## 4. Аннотации Allure

Подключение:
```python
import allure
```

### 4.1. `@allure.title("Название теста")`
Меняет отображаемое имя теста в отчёте.

```python
import allure

@allure.title("Создание пользователя возвращает 201")
def test_create_user_returns_201(api_client):
    r = api_client.post("/users", json={"name": "Ivan"})
    assert r.status_code == 201
```

---

### 4.2. `@allure.description("Описание теста")`
Описание в карточке теста: что проверяем, условия, ожидаемый результат.

```python
import allure

@allure.description("Проверяем, что /health возвращает 200 и корректный payload.")
def test_health(api_client):
    r = api_client.get("/health")
    assert r.status_code == 200
```

> Также бывает `@allure.description_html(...)`, если нужно HTML-описание.

---

### 4.3. Suites: `@allure.suite`, `@allure.sub_suite`, `@allure.parent_suite`
Группировка тестов в дереве Suites.

```python
import allure

@allure.parent_suite("API")
@allure.suite("Users")
@allure.sub_suite("Create")
def test_create_user(api_client):
    ...
```

Рекомендации:
- `parent_suite` — слой/тип: API/UI/Integration.
- `suite` — модуль/домен: Users/Orders/Payments.
- `sub_suite` — сценарий/раздел: Create/Update/Delete.

---

### 4.4. Severity: `@allure.severity(allure.severity_level.CRITICAL)`
Severity помогает выделять критичные падения и фильтровать отчёт.

Уровни: `BLOCKER`, `CRITICAL`, `NORMAL`, `MINOR`, `TRIVIAL`.

```python
import allure

@allure.severity(allure.severity_level.CRITICAL)
def test_payment_must_succeed(payment_client):
    ...
```

---

### 4.5. `@allure.tag`, `@allure.label`
- `@allure.tag(...)` — теги (читаемые метки).
- `@allure.label(name, value)` — универсальные labels (owner/layer/component и т.п.).

```python
import allure

@allure.tag("smoke", "api")
@allure.label("owner", "aqa-team")
@allure.label("layer", "api")
def test_smoke_health(api_client):
    ...
```

Практика договорённостей по labels:
- `layer`: unit/api/ui/integration
- `component`: users/orders/payments
- `owner`: команда/ответственный

---

## 5. Степы (Steps) в отчёте

Steps делают отчёт «сценарным»: видно, на каком шаге упало и с какими параметрами.

### 5.1. `@allure.step`
Оформление шага через декоратор.

```python
import allure

@allure.step("Шаг с параметром: {param}")
def step_with_param(param):
    pass
```

Пример с аргументами и вложенными шагами:
```python
import allure

@allure.step("Отправляем запрос на создание пользователя: {payload}")
def create_user(api_client, payload):
    return api_client.post("/users", json=payload)

@allure.step("Проверяем статус ответа: ожидаем {expected}")
def assert_status(response, expected):
    assert response.status_code == expected

def test_create_user(api_client):
    payload = {"name": "Ivan"}
    r = create_user(api_client, payload)
    assert_status(r, 201)
```

---

### 5.2. `with allure.step("...")` внутри тестов
Удобно для локальных шагов без выноса в отдельные функции.

```python
import allure

def test_login(ui_app):
    with allure.step("Открываем страницу логина"):
        ui_app.open_login()

    with allure.step("Вводим креды и логинимся"):
        ui_app.login("user", "pass")

    with allure.step("Проверяем, что пользователь вошёл"):
        assert ui_app.is_logged_in()
```

---

## 6. Примеры полного теста

### 6.1. Простой тест с аннотациями и шагами
```python
import allure

@allure.parent_suite("API")
@allure.suite("Health")
@allure.title("Healthcheck возвращает 200")
@allure.severity(allure.severity_level.CRITICAL)
@allure.tag("smoke", "api")
def test_health(api_client):
    with allure.step("Делаем запрос /health"):
        r = api_client.get("/health")

    with allure.step("Проверяем статус 200"):
        assert r.status_code == 200
```

---

### 6.2. Тест с фикстурами и вложенными шагами
`conftest.py`:
```python
import pytest

@pytest.fixture
def user_payload():
    return {"name": "Ivan", "age": 30}

@pytest.fixture
def created_user(api_client, user_payload):
    r = api_client.post("/users", json=user_payload)
    user_id = r.json()["id"]
    yield user_id
    api_client.delete(f"/users/{user_id}")
```

Тест:
```python
import allure

@allure.parent_suite("API")
@allure.suite("Users")
@allure.sub_suite("Lifecycle")
@allure.title("Созданного пользователя можно получить по id")
@allure.severity(allure.severity_level.NORMAL)
@allure.tag("regression", "api")
def test_get_created_user(api_client, created_user):
    with allure.step(f"Получаем пользователя по id={created_user}"):
        r = api_client.get(f"/users/{created_user}")

    with allure.step("Проверяем статус 200"):
        assert r.status_code == 200

    with allure.step("Проверяем, что id совпадает"):
        assert r.json()["id"] == created_user
```

---

## 7. Дополнительные возможности

### 7.1. Скриншоты и вложения: `allure.attach`
Вложения — ключ к быстрой диагностике: логи, JSON, HTML, скриншоты, файлы.

```python
import allure

allure.attach(
    "Пример текста",
    name="Text Log",
    attachment_type=allure.attachment_type.TEXT
)
```

---

### 7.2. Форматы вложений
- `TEXT`
- `HTML`
- `JSON`
- `PNG`

Примеры:

**TEXT**
```python
allure.attach("some log lines", name="App Log", attachment_type=allure.attachment_type.TEXT)
```

**JSON**
```python
import json
payload = {"user": "Ivan", "role": "admin"}
allure.attach(
    json.dumps(payload, ensure_ascii=False, indent=2),
    name="Request JSON",
    attachment_type=allure.attachment_type.JSON
)
```

**HTML**
```python
html = "<h1>Debug</h1><p>Something happened</p>"
allure.attach(html, name="HTML Debug", attachment_type=allure.attachment_type.HTML)
```

**PNG (пример для UI)**
```python
# bytes_png = driver.get_screenshot_as_png()
# allure.attach(bytes_png, name="Screenshot", attachment_type=allure.attachment_type.PNG)
```

---

## 8. Best practices и советы

### 8.1. Как структурировать тесты и фикстуры
- Договориться о стабильной схеме `parent_suite/suite/sub_suite`.
- Выносить повторяемые действия в `@allure.step`-функции (клиенты/обёртки/PO).
- Прикладывать request/response и ключевые логи там, где это помогает дебагу.
- Не превращать каждую мелочь в step — отчёт должен оставаться читаемым.

### 8.2. Использование `conftest.py` для мета-информации
В `conftest.py` удобно централизовать:
- общие фикстуры (clients, auth, config),
- хуки pytest для автоматических вложений при падении (особенно UI: скриншоты/логи),
- единые labels/tags по договорённости (owner/layer/component).

### 8.3. Общие рекомендации по поддержанию читаемого отчёта
- `@allure.title` — «человеческие» заголовки: действие + ожидаемый результат.
- `@allure.description` — коротко фиксировать смысл сценария и важные условия.
- `severity` — использовать как сигнал приоритета.
- `tag/label` — ограниченный словарь и документация договорённостей.
- Для API: request/response, headers, correlation-id, service logs (если доступны).
- Для UI: скриншот/DOM/логи браузера при падении (если уместно).

---

## 9. Полезные ссылки

### Официальная документация
- Allure Report docs: https://allurereport.org/docs/
- Pytest plugin (Allure): https://allurereport.org/docs/pytest/

### GitHub-репозитории
- Allure Report: https://github.com/allure-framework/allure2
- allure-python (включая allure-pytest): https://github.com/allure-framework/allure-python

---

## Приложение: быстрый старт
```bash
pip install -U pytest allure-pytest
pytest --alluredir=allure-results
allure serve allure-results
```
