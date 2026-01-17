# Документация: **assert в pytest** (проверки и масштабирование ассертов)

---

## Введение

`assert` — основной инструмент проверки ожидаемого поведения в тестах на pytest.  
Ключевая сила pytest в том, что он умеет **«переписывать» (assertion rewriting)** выражения `assert` и показывать *детальную разницу* при падении: значения переменных, отличия строк/списков/словарей и т.д. Это делает дебаг быстрее, а тесты — проще и чище.

---

## Оглавление

- [Введение](#введение)
- [1. Что такое assert в pytest и чем он отличается от стандартного assert в Python](#1-что-такое-assert-в-pytest-и-чем-он-отличается-от-стандартного-assert-в-python)
  - [1.1. Стандартный `assert` в Python](#11-стандартный-assert-в-python)
  - [1.2. Что добавляет pytest](#12-что-добавляет-pytest)
- [2. Роль assert в тестах: читаемость, дебаг, трассировка ошибок](#2-роль-assert-в-тестах-читаемость-дебаг-трассировка-ошибок)
- [3. Базовые примеры использования](#3-базовые-примеры-использования)
  - [3.1. Проверка булевых выражений](#31-проверка-булевых-выражений)
  - [3.2. Проверка на равенство](#32-проверка-на-равенство)
  - [3.3. Проверка на `None` и `not None`](#33-проверка-на-none-и-not-none)
  - [3.4. Примеры из практики](#34-примеры-из-практики)
- [4. Сложные проверки](#4-сложные-проверки)
  - [4.1. Сравнение списков (в т.ч. отсортированных)](#41-сравнение-списков-в-тч-отсортированных)
  - [4.2. Проверка подмножеств](#42-проверка-подмножеств)
  - [4.3. Проверка содержимого словарей и JSON-структур](#43-проверка-содержимого-словарей-и-json-структур)
- [5. Проверка большого количества полей](#5-проверка-большого-количества-полей)
  - [5.1 Как сравнить 500+ полей без 500 `assert`-ов](#51-как-сравнить-500-полей-без-500-assert-ов)
  - [5.2 dataclasses.asdict() или `.dict()`/`.model_dump()` из Pydantic](#52-dataclassesasdict-или-dictmodeldump-из-pydantic)
  - [5.3. Как выводить разницу между объектами при неудаче](#53-как-выводить-разницу-между-объектами-при-неудаче)
  - [5.4 Пример: валидация ответа API через Pydantic DTO](#54-пример-валидация-ответа-api-через-pydantic-dto)
- [6. Soft Assertions (мягкие ассерты)](#6-soft-assertions-мягкие-ассерты)
  - [6.1. Что это такое и зачем использовать](#61-что-это-такое-и-зачем-использовать)
  - [6.2. Реализация soft assert в pytest с помощью `pytest-check`](#62-реализация-soft-assert-в-pytest-с-помощью-pytest-check)
  - [6.3. Преимущества и ограничения](#63-преимущества-и-ограничения)
- [7. Аналоги matchers из Java (JUnit/Hamcrest) и подход в Python](#7-аналоги-matchers-из-java-junithamcrest-и-подход-в-python)
  - [7.1. Концепция matchers](#71-концепция-matchers)
  - [7.2. Сравнение с кастомными assertion-классами в Python](#72-сравнение-с-кастомными-assertion-классами-в-python)
  - [7.3. Пример кастомного Matcher-подхода в Python](#73-пример-кастомного-matcher-подхода-в-python)
  - [7.4. Рекомендации по структуре таких классов](#74-рекомендации-по-структуре-таких-классов)
- [8. Best practices](#8-best-practices)
  - [8.1. Как писать читаемые assert-сообщения](#81-как-писать-читаемые-assert-сообщения)
  - [8.2. Использование assert внутри вспомогательных методов](#82-использование-assert-внутри-вспомогательных-методов)
  - [8.3. Когда лучше использовать soft assert vs обычный](#83-когда-лучше-использовать-soft-assert-vs-обычный)
  - [8.4. Организация и группировка проверок](#84-организация-и-группировка-проверок)
- [9. Заключение и полезные ссылки](#9-заключение-и-полезные-ссылки)
  - [Официальная документация pytest](#официальная-документация-pytest)
  - [Плагины для расширения возможностей assert](#плагины-для-расширения-возможностей-assert)
  - [Статьи/туториалы по стратегиям assert](#статьитуториалы-по-стратегиям-assert)
- [Приложение: быстрые примеры](#приложение-быстрые-примеры)

## 1. Что такое assert в pytest и чем он отличается от стандартного assert в Python

### 1.1. Стандартный `assert` в Python
В Python `assert <expr>`:
- проверяет условие,
- если условие ложно — выбрасывает `AssertionError`.

Пример:
```python
assert 2 + 2 == 4
assert x > 0
```

Важно:
- `assert` может быть **отключён** при запуске Python с оптимизациями (`python -O`), и тогда утверждения не выполняются.
- В тестах на pytest это обычно не делают, но знать важно (особенно для «production-кода»).

### 1.2. Что добавляет pytest
pytest делает `assert` мощнее:
- **автоматически «раскрывает» выражение** и показывает, *что именно не совпало*,
- умеет красиво диффить строки, списки, dict/JSON,
- даёт понятную трассировку и подсказывает значения подвыражений.

Пример падения:
```python
assert response.status_code == 200
```
pytest покажет фактическое значение (например, 500) и контекст.

---

## 2. Роль assert в тестах: читаемость, дебаг, трассировка ошибок

Хороший `assert`:
- читается как спецификация: «ожидаю X»,
- точечно падает в правильном месте,
- даёт максимум информации, чтобы быстро понять причину.

Рекомендации:
- делайте утверждения **конкретными и проверяемыми**,
- группируйте проверки по смыслу (например: `status`, затем `body`, затем `headers`),
- не бойтесь 2–5 assert’ов в одном тесте, если они логически связаны.

---

## 3. Базовые примеры использования

### 3.1. Проверка булевых выражений
```python
assert is_valid is True
assert user.is_active
assert not errors
```

### 3.2. Проверка на равенство
```python
assert total == 100
assert response.status_code == 200
```

### 3.3. Проверка на `None` и `not None`
```python
assert result is not None
assert token is not None
assert error is None
```

### 3.4. Примеры из практики
```python
assert result is not None
assert len(users) == 5
assert "admin" in roles
assert response.status_code == 200
```

---

## 4. Сложные проверки

### 4.1. Сравнение списков (в т.ч. отсортированных)
Если порядок важен:
```python
assert actual_list == expected_list
```

Если порядок **не важен**:
```python
assert sorted(actual_list) == sorted(expected_list)
```

Если в списках могут быть дубликаты и важна мультисет-семантика — рассмотрите `collections.Counter`:
```python
from collections import Counter
assert Counter(actual_list) == Counter(expected_list)
```

---

### 4.2. Проверка подмножеств
Проверить, что набор ключей/значений содержит минимум требуемого:

```python
assert {"id", "name"} <= user_data.keys()
```

---

### 4.3. Проверка содержимого словарей и JSON-структур

#### Равенство целиком
```python
assert actual_json == expected_json
```

#### Частичное сравнение (важные поля)
```python
assert actual_json["id"] == expected_json["id"]
assert actual_json["name"] == expected_json["name"]
```

#### Проверка наличия ключей
```python
required = {"id", "name", "email"}
assert required <= actual_json.keys()
```

#### Проверка вложенной структуры
```python
assert actual_json["user"]["roles"]  # не пусто
assert "admin" in actual_json["user"]["roles"]
```

---

## 5. Проверка большого количества полей

### 5.1 Как сравнить 500+ полей без 500 `assert`-ов
Идея: сравнивать **объекты целиком**, а не каждое поле вручную.

Подходы:
- DTO в pydantic → сравнить через `.model_dump()` (v2) или `.dict()` (v1),
- dataclass → сравнить через `dataclasses.asdict()` или напрямую по `==` (если подходит),
- заранее нормализовать структуру (сортировки, преобразование дат) и сравнить.

---

### 5.2 dataclasses.asdict() или `.dict()`/`.model_dump()` из Pydantic

#### Dataclasses
```python
from dataclasses import dataclass, asdict

@dataclass
class User:
    id: int
    name: str

assert asdict(actual_user) == asdict(expected_user)
```

#### Pydantic
В pydantic v2 рекомендуется `model_dump()`:
```python
assert actual.model_dump() == expected.model_dump()
```

Если у вас используется `.dict()`:
```python
assert actual.dict() == expected.dict()
```

---

### 5.3. Как выводить разницу между объектами при неудаче
pytest обычно хорошо показывает diff для dict/списков, но можно улучшить читаемость:

1) Сравнивайте **приведённые** структуры (dict/JSON), а не объекты с кастомным `__repr__`.
2) Для больших структур можно использовать `pprint`/json pretty print в сообщении (осторожно с секретами).

Пример (короткое сообщение):
```python
assert actual.model_dump() == expected.model_dump(), "DTO mismatch (see diff above)"
```

Для сложных случаев полезно добавлять вложения в отчёт (например, Allure):
- actual.json (pretty),
- expected.json (pretty),
- diff (если формируете отдельно).

---

### 5.4 Пример: валидация ответа API через Pydantic DTO

Ниже — типовой паттерн для API-тестов: **получили JSON**, **провалидировали DTO**, и уже потом делаем asserts по полям/инвариантам.  
Плюс: если контракт «поплыл» (тип поля изменился, поле пропало, структура стала другой) — тест падает *на этапе валидации* с понятной ошибкой.

> Примеры ниже рассчитаны на **pydantic v2** (рекомендуемые методы: `model_validate`, `model_dump`).

#### DTO-модель ответа и валидация `response.json()`

```python
from pydantic import BaseModel, EmailStr, Field

class UserDTO(BaseModel):
    id: int
    name: str = Field(min_length=1)
    email: EmailStr
    is_active: bool

def test_get_user(api_client):
    response = api_client.get("/users/1")
    assert response.status_code == 200

    # 1) Валидация контракта ответа
    user = UserDTO.model_validate(response.json())

    # 2) Бизнес-проверки
    assert user.id == 1
    assert user.is_active is True
    assert user.name  # не пустая строка
```

#### Вложенные структуры: `UserDTO` + `AddressDTO`

```python
from pydantic import BaseModel

class AddressDTO(BaseModel):
    city: str
    street: str
    zip_code: str

class UserDTO(BaseModel):
    id: int
    name: str
    address: AddressDTO

def test_user_address(api_client):
    r = api_client.get("/users/1")
    assert r.status_code == 200

    user = UserDTO.model_validate(r.json())
    assert user.address.city is not None
```

#### Сравнение с ожидаемым DTO целиком (много полей без 500 assert-ов)

```python
from pydantic import BaseModel

class UserDTO(BaseModel):
    id: int
    name: str
    is_active: bool

def test_user_contract_full(api_client):
    r = api_client.get("/users/1")
    assert r.status_code == 200

    actual = UserDTO.model_validate(r.json())
    expected = UserDTO(id=1, name="Ivan", is_active=True)

    assert actual.model_dump() == expected.model_dump()
```

#### Понятные ошибки при невалидном JSON

```python
import json
from pydantic import ValidationError

def test_validation_errors_are_readable(api_client):
    r = api_client.get("/users/1")
    assert r.status_code == 200

    try:
        UserDTO.model_validate(r.json())
    except ValidationError as e:
        # Полезно для логов/отчётов:
        print(json.dumps(e.errors(), ensure_ascii=False, indent=2))
        raise
```

## 6. Soft Assertions (мягкие ассерты)

### 6.1. Что это такое и зачем использовать
Soft assert — подход, при котором тест **не останавливается** на первой ошибке, а собирает несколько падений и показывает их в конце. Это удобно когда:
- нужно проверить много полей и получить «полный список расхождений» за один прогон,
- важно быстро увидеть масштаб проблемы.

### 6.2. Реализация soft assert в pytest с помощью `pytest-check`

Установка:
```bash
pip install pytest-check
```

Пример:
```python
import pytest_check as check

def test_multiple_fields(user):
    check.equal(user.name, "John")
    check.is_not_none(user.id)
    check.in_("admin", user.roles)
```

### 6.3. Преимущества и ограничения
Плюсы:
- тест продолжает выполнение, даже если часть проверок провалилась,
- быстрее диагностировать «много проблем сразу».

Минусы:
- если дальнейшие шаги зависят от валидных данных, тест может «насыпать» вторичных ошибок,
- нужно аккуратно выбирать, где soft assert уместен.

Практика:
- используйте soft asserts для **валидации больших DTO/ответов**,
- используйте обычные asserts для **критичных «gating» проверок** (например, `status_code`, успешный логин), без которых смысл продолжать теряется.

---

## 7. Аналоги matchers из Java (JUnit/Hamcrest) и подход в Python

### 7.1. Концепция matchers
В Java часто используют «матчеры» (Hamcrest/AssertJ), чтобы писать читабельные проверки:
- `assertThat(actual, is(equalTo(expected)))`
- `assertThat(list, hasItem("admin"))`

Идея: отделить «сравнение» в отдельный слой и получать **хорошие сообщения об ошибках**.

### 7.2. Сравнение с кастомными assertion-классами в Python
В Python/pytest можно получить похожий эффект:
- выносить проверки в **assertion helpers**,
- делать **matcher-классы** или функции, которые:
  - принимают `actual/expected`,
  - выполняют набор проверок,
  - дают понятные сообщения.

---

### 7.3. Пример кастомного Matcher-подхода в Python
```python
class CustomerMatcher:
    def __init__(self, actual, expected):
        self.actual = actual
        self.expected = expected

    def check_all(self):
        assert self.actual.id == self.expected.id
        assert self.actual.name == self.expected.name
        assert self.actual.status == self.expected.status
        return self
```

Использование:
```python
CustomerMatcher(actual_customer, expected_customer).check_all()
```

### 7.4. Рекомендации по структуре таких классов
- Делайте методы «по смыслу»: `check_identity()`, `check_status()`, `check_profile()`.
- Возвращайте `self` для fluent-стиля (опционально).
- Для больших проверок используйте:
  - либо обычные asserts с хорошими сообщениями,
  - либо `pytest-check`, чтобы собрать все расхождения.

Пример с soft-assert внутри matcher:
```python
import pytest_check as check

class CustomerMatcher:
    def __init__(self, actual, expected):
        self.actual = actual
        self.expected = expected

    def check_all(self):
        check.equal(self.actual.id, self.expected.id, "id mismatch")
        check.equal(self.actual.name, self.expected.name, "name mismatch")
        check.equal(self.actual.status, self.expected.status, "status mismatch")
        return self
```

---

## 8. Best practices

### 8.1. Как писать читаемые assert-сообщения
В pytest чаще всего сообщение не нужно: он и так показывает детали.  
Но для бизнес-логики/контрактов иногда полезно:

```python
assert response.status_code == 200, "Expected 200 OK for /users"
```

Рекомендации:
- сообщение должно быть коротким и уточнять *ожидание/контекст*,
- не дублируйте то, что pytest и так покажет (например, «expected X got Y»).

---

### 8.2. Использование assert внутри вспомогательных методов
Это нормальная практика, если:
- метод делает одну логическую проверку (или группу связанных),
- имя метода отражает смысл.

Пример:
```python
def assert_user_is_admin(user):
    assert "admin" in user.roles
```

Плюсы:
- тесты становятся короче,
- проверки переиспользуются.

Минусы:
- если переборщить, тест «превратится в сценарий без проверок на виду».
Баланс: критичные asserts держите в тесте, детализацию — в helpers.

---

### 8.3. Когда лучше использовать soft assert vs обычный
Обычный `assert`:
- для критичных проверок, влияющих на смысл продолжения теста,
- когда падение на первом расхождении — нормально.

Soft assert:
- для «валидации объекта целиком» (много полей),
- для сравнений, где нужно собрать максимум расхождений за 1 прогон.

---

### 8.4. Организация и группировка проверок
- Сначала «гейты»: статус/успех операции.
- Потом структура: наличие ключей/полей.
- Потом значения: конкретные поля и инварианты.
- Для больших объектов: сравнение DTO → fallback на частичные проверки.

---

## 9. Заключение и полезные ссылки

### Официальная документация pytest
- https://docs.pytest.org/
- https://docs.pytest.org/en/stable/how-to/assert.html

### Плагины для расширения возможностей assert
- `pytest-check` (soft assertions): https://github.com/okken/pytest-check
- `pytest-assume` (альтернативный soft assert): https://github.com/astraw38/pytest-assume

### Статьи/туториалы по стратегиям assert
- Ищите: `pytest assertion rewriting`, `pytest soft assertions`, `pytest-check examples`

---

## Приложение: быстрые примеры
```python
assert result is not None
assert len(users) == 5
assert "admin" in roles
assert response.status_code == 200

assert sorted(actual_list) == sorted(expected_list)
assert {"id", "name"} <= user_data.keys()
```
