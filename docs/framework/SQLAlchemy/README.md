# Документация: SQLAlchemy. ORM + Core, мульти‑БД (PostgreSQL/MySQL/Oracle/MSSQL)

---

## Оглавление

- [1. Введение](#1-введение)
  - [1.1 Что такое SQLAlchemy и зачем он нужен](#11-что-такое-sqlalchemy-и-зачем-он-нужен)
  - [1.2 Поддержка ORM и Core](#12-поддержка-orm-и-core)
  - [1.3 Почему SQLAlchemy полезен в автоматизации](#13-почему-sqlalchemy-полезен-в-автоматизации)
- [2. Установка и подключение к базам данных](#2-установка-и-подключение-к-базам-данных)
  - [2.1 Установка](#21-установка)
  - [2.2 Примеры строк подключения (SQLAlchemy URL)](#22-примеры-строк-подключения-sqlalchemy-url)
  - [2.3 Создание Engine](#23-создание-engine)
  - [2.4 Конфигурация через env/pydantic-settings (рекомендовано)](#24-конфигурация-через-envpydantic-settings-рекомендовано)
- [3. Создание моделей (ORM)](#3-создание-моделей-orm)
  - [3.1 Base и модель таблицы](#31-base-и-модель-таблицы)
  - [3.2 Создание таблиц через `Base.metadata.create_all(engine)`](#32-создание-таблиц-через-basemetadatacreateallengine)
  - [3.3 Работа с Alembic для миграций](#33-работа-с-alembic-для-миграций)
- [4. Основы работы с сессиями](#4-основы-работы-с-сессиями)
  - [4.1 Создание Session](#41-создание-session)
  - [4.2 Commit / rollback / close](#42-commit-rollback-close)
  - [4.3 Контекстный менеджер (рекомендуется)](#43-контекстный-менеджер-рекомендуется)
- [5. Чтение данных (SELECT)](#5-чтение-данных-select)
  - [5.1 Простой запрос](#51-простой-запрос)
  - [5.2 Сложные условия: `and_`, `or_`, `in_`](#52-сложные-условия-and-or-in)
  - [5.3 JOIN и eager loading](#53-join-и-eager-loading)
  - [5.4 Группировки, агрегаты, сортировки](#54-группировки-агрегаты-сортировки)
- [6. Вставка и обновление данных](#6-вставка-и-обновление-данных)
  - [6.1 Добавление записи](#61-добавление-записи)
  - [6.2 Массовое добавление](#62-массовое-добавление)
  - [6.3 Обновление данных](#63-обновление-данных)
  - [6.4 Удаление](#64-удаление)
- [7. Выполнение “сырых” SQL-запросов (Core)](#7-выполнение-сырых-sql-запросов-core)
  - [7.1 `text()` и параметры](#71-text-и-параметры)
  - [7.2 Получение результатов](#72-получение-результатов)
  - [7.3 Вызов функций и процедур](#73-вызов-функций-и-процедур)
- [8. Работа с разными СУБД](#8-работа-с-разными-субд)
  - [8.1 Специфика драйверов](#81-специфика-драйверов)
  - [8.2 Различия синтаксиса raw SQL](#82-различия-синтаксиса-raw-sql)
  - [8.3 Как писать кросс‑БД код](#83-как-писать-кроссбд-код)
- [9. Best Practices](#9-best-practices)
  - [9.1 Разделение ORM-слоя и бизнес-логики](#91-разделение-orm-слоя-и-бизнес-логики)
  - [9.2 Использование транзакций](#92-использование-транзакций)
  - [9.3 Тесты: фикстуры и мок‑БД](#93-тесты-фикстуры-и-мокбд)
  - [9.4 Пул соединений и `scoped_session`](#94-пул-соединений-и-scopedsession)
  - [9.5 Async и SQLAlchemy 2.0 (при необходимости)](#95-async-и-sqlalchemy-20-при-необходимости)
- [10. Частые ошибки и отладка](#10-частые-ошибки-и-отладка)
  - [10.1 Ошибки соединения и неверный DSN/URL](#101-ошибки-соединения-и-неверный-dsnurl)
  - [10.2 Потеря сессии / незакрытые соединения](#102-потеря-сессии-незакрытые-соединения)
  - [10.3 Ошибки в JOIN / N+1](#103-ошибки-в-join-n1)
  - [10.4 Ошибки в миграциях](#104-ошибки-в-миграциях)
- [11. Заключение](#11-заключение)
  - [11.1 Когда ORM, когда raw SQL/Core](#111-когда-orm-когда-raw-sqlcore)
  - [11.2 Полезные ссылки](#112-полезные-ссылки)

---

## 1. Введение

### 1.1 Что такое SQLAlchemy и зачем он нужен
**SQLAlchemy** — основной стандартный инструментарий для работы с базами данных в Python. Он предоставляет:
- **ORM** (объектно‑реляционное отображение): работа с таблицами как с классами Python;
- **Core / SQL Expression Language**: построение SQL-запросов на уровне выражений, ближе к “ручному” SQL.

SQLAlchemy полезен, когда нужно:
- стандартизировать доступ к БД в микросервисах и тестовом фреймворке;
- переиспользовать код между проектами и СУБД;
- повысить надёжность и читаемость работы с данными в тестах (валидация инвариантов, подготовка данных, очистка).

### 1.2 Поддержка ORM и Core
- **ORM** — удобно для:
  - чтения/сохранения доменных сущностей;
  - выражения связей (one-to-many, many-to-many);
  - простых и средних запросов.
- **Core** — удобно для:
  - сложных JOIN/CTE/оконных функций;
  - массовых операций и тонкого контроля;
  - выполнения SQL “как есть” (raw SQL через `text()`).

> В современных проектах часто используется гибрид: ORM для сущностей + Core для сложных выборок и оптимизаций.

### 1.3 Почему SQLAlchemy полезен в автоматизации
- **Гибкость**: ORM и Core в одном инструменте.
- **Масштабируемость**: нормальные транзакции, connection pooling, работа с большими данными.
- **Переносимость**: одинаковые паттерны кода для PostgreSQL/MySQL/Oracle/MSSQL (с учётом особенностей).
- **Управляемость**: централизованная конфигурация (settings), единые клиенты/репозитории, удобные фикстуры pytest.

---

## 2. Установка и подключение к базам данных

### 2.1 Установка
```bash
pip install sqlalchemy
```

Драйверы БД ставятся отдельно (примерно так):
- PostgreSQL: `psycopg2-binary` или `psycopg`
- MySQL: `pymysql` или `mysqlclient`
- Oracle: `cx_Oracle` (или `oracledb`)
- MSSQL: `pyodbc`

### 2.2 Примеры строк подключения (SQLAlchemy URL)
- PostgreSQL: `postgresql+psycopg2://user:pass@host:port/dbname`
- MySQL: `mysql+pymysql://user:pass@host:port/dbname`
- Oracle: `oracle+cx_oracle://user:pass@host:port/?service_name=svcname`
- MSSQL: `mssql+pyodbc://user:pass@dsn`

> Важно: формат URL зависит от драйвера и его возможностей. Для MSSQL часто используется DSN или строка с параметрами драйвера.

### 2.3 Создание Engine
Engine — “фабрика соединений” и основной объект SQLAlchemy.

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://user:pass@localhost:5432/app",
    pool_pre_ping=True,   # полезно для долгоживущих соединений
)
```

Часто полезные параметры:
- `pool_pre_ping=True` — проверка живости соединения перед использованием;
- `pool_size`, `max_overflow` — настройка пула;
- `echo=True` — вывод SQL (лучше включать точечно/локально).

### 2.4 Конфигурация через env/pydantic-settings (рекомендовано)
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_URL: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
engine = create_engine(settings.DB_URL, pool_pre_ping=True)
```

---

## 3. Создание моделей (ORM)

### 3.1 Base и модель таблицы
```python
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)
```

### 3.2 Создание таблиц через `Base.metadata.create_all(engine)`
Подходит для прототипов и локальных экспериментов:
```python
Base.metadata.create_all(engine)
```

В прод-проектах и автоматизации **предпочтительнее** миграции (Alembic), чтобы схема была версионируемой.

### 3.3 Работа с Alembic для миграций
Рекомендуемый workflow:
- модели меняются в коде,
- миграции создаются Alembic (`revision --autogenerate`),
- в CI/test прогоне выполняется `alembic upgrade head`.

> В тестовом фреймворке полезно иметь фикстуру, которая накатывает миграции перед тестами.

---

## 4. Основы работы с сессиями

### 4.1 Создание Session
```python
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()
```

> В SQLAlchemy 2.x часто используют `sessionmaker(engine, future=True)` и стиль “2.0”, но базовые принципы остаются те же.

### 4.2 Commit / rollback / close
Рекомендованный паттерн:
```python
session = Session()
try:
    # операции с БД
    session.commit()
except Exception:
    session.rollback()
    raise
finally:
    session.close()
```

### 4.3 Контекстный менеджер (рекомендуется)
В SQLAlchemy 2.0 удобнее использовать контекст:
```python
from sqlalchemy.orm import Session

with Session(engine) as session:
    with session.begin():
        # внутри begin() commit/rollback управляются автоматически
        ...
```

---

## 5. Чтение данных (SELECT)

### 5.1 Простой запрос
(Классический ORM‑стиль)
```python
user = session.query(User).filter_by(name="admin").first()
```

### 5.2 Сложные условия: `and_`, `or_`, `in_`
```python
from sqlalchemy import and_, or_

q = (
    session.query(User)
    .filter(
        and_(
            User.role.in_(["admin", "superadmin"]),
            or_(User.name == "admin", User.name.like("adm%")),
        )
    )
)

users = q.all()
```

### 5.3 JOIN и eager loading
JOIN (пример):
```python
# В примере предполагается модель Role и связь User.role_id -> Role.id
from sqlalchemy.orm import joinedload

users = (
    session.query(User)
    .join(Role)
    .filter(Role.name == "admin")
    .options(joinedload(User.role_rel))  # если есть relationship
    .all()
)
```

### 5.4 Группировки, агрегаты, сортировки
```python
from sqlalchemy import func

rows = (
    session.query(User.role, func.count(User.id).label("cnt"))
    .group_by(User.role)
    .order_by(func.count(User.id).desc())
    .all()
)
```

---

## 6. Вставка и обновление данных

### 6.1 Добавление записи
```python
new_user = User(name="test", role="user")
session.add(new_user)
session.commit()
```

### 6.2 Массовое добавление
```python
users = [User(name=f"user_{i}", role="user") for i in range(100)]
session.bulk_save_objects(users)
session.commit()
```

> `bulk_*` методы ускоряют операции, но могут обходить часть ORM‑механик (events, identity map). Используйте их осознанно.

### 6.3 Обновление данных
```python
session.query(User).filter(User.name == "test").update({"role": "admin"})
session.commit()
```

### 6.4 Удаление
```python
session.query(User).filter(User.name == "test").delete()
session.commit()
```

---

## 7. Выполнение “сырых” SQL-запросов (Core)

### 7.1 `text()` и параметры
```python
from sqlalchemy import text

result = session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 1})
row = result.first()
```

Преимущества параметров:
- защита от SQL-инъекций,
- корректные типы.

### 7.2 Получение результатов
```python
rows = session.execute(text("SELECT id, name FROM users")).mappings().all()
# rows: list[dict]
```

### 7.3 Вызов функций и процедур
Пример (зависит от СУБД):
```python
session.execute(text("CALL update_balance(:user_id)"), {"user_id": 123})
```

Функция:
```python
tax = session.execute(text("SELECT calculate_tax(:amount)"), {"amount": 5000}).scalar_one()
```

> В Oracle/MSSQL синтаксис вызова процедур может отличаться. Иногда проще использовать dialect‑специфичный SQL.

---

## 8. Работа с разными СУБД

### 8.1 Специфика драйверов
Типичные “подводные камни”:
- **Oracle**: особенности типов, `NUMBER`, работа с `CLOB`, ограничения на идентификаторы.
- **MSSQL**: особенности драйверов ODBC, параметры `driver=` и DSN.
- **MySQL**: транзакции/изоляция и различия движков (InnoDB).
- **PostgreSQL**: расширения, схемы, search_path.

### 8.2 Различия синтаксиса raw SQL
Если вы используете `text()`:
- не полагайтесь на одинаковый синтаксис LIMIT/OFFSET (в MSSQL свой стиль),
- аккуратно с кавычками/идентификаторами,
- функции дат/строк могут отличаться.

Практика:
- для кросс‑БД предпочтительнее **Core выражения** SQLAlchemy, а raw SQL использовать точечно.

### 8.3 Как писать кросс‑БД код
- избегайте dialect‑специфичных функций без необходимости,
- используйте SQLAlchemy типы (`Integer`, `String`, `Numeric(12,2)`),
- храните особенности БД в адаптерах/репозиториях,
- тестируйте миграции и критичные запросы на целевых СУБД.

---

## 9. Best Practices

### 9.1 Разделение ORM-слоя и бизнес-логики
Рекомендация:
- “слой доступа к данным” (repositories/DAOs) — отдельно,
- тесты — не должны содержать сложную бизнес‑логику и SQL “вперемешку”.

### 9.2 Использование транзакций
- используйте `session.begin()` для атомарных операций,
- откатывайте транзакции в тестах, если вам нужен “чистый мир”.

### 9.3 Тесты: фикстуры и мок‑БД
Варианты:
- интеграционные тесты на тестовой БД (контейнер),
- unit‑тесты репозиториев с моками/стабами,
- фикстуры для поднятия схемы (через Alembic) и очистки данных.

### 9.4 Пул соединений и `scoped_session`
Если тесты запускаются параллельно:
- контролируйте `pool_size`, `max_overflow`,
- подумайте про `scoped_session` (для потоков), но в pytest чаще проще явно прокидывать session фикстурами.

### 9.5 Async и SQLAlchemy 2.0 (при необходимости)
Если проект async (FastAPI и т.п.):
- используйте `AsyncEngine`, `AsyncSession`,
- драйверы: `asyncpg` (PostgreSQL), и т.д.
- в тестах подключайте `pytest-asyncio`.

---

## 10. Частые ошибки и отладка

### 10.1 Ошибки соединения и неверный DSN/URL
Симптомы:
- `OperationalError`, `InterfaceError`, таймауты.

Проверяйте:
- правильность URL (драйвер, host/port),
- доступность хоста/порта,
- креды,
- параметры ODBC driver для MSSQL.

### 10.2 Потеря сессии / незакрытые соединения
Симптомы:
- рост числа соединений,
- зависания тестов.

Практика:
- закрывайте session (или используйте контекстный менеджер),
- в pytest используйте фикстуру, которая делает `yield session` и `close()` в teardown.

### 10.3 Ошибки в JOIN / N+1
Симптом:
- много лишних запросов, медленные тесты.

Решения:
- `joinedload/selectinload`,
- профилирование SQL (`echo`, логирование на уровне engine),
- пересмотр модели/отношений.

### 10.4 Ошибки в миграциях
Симптомы:
- схемы расходятся, autogenerate создаёт неожиданные diffs.

Практика:
- поддерживать актуальный `target_metadata`,
- не редактировать историю миграций задним числом,
- проверять миграции в CI на пустой БД.

---

## 11. Заключение

### 11.1 Когда ORM, когда raw SQL/Core
- **ORM**: удобен для CRUD, связей и читаемого доменного доступа.
- **Core / text()**: полезен для сложных запросов, оптимизаций и диалектных особенностей.

Рекомендация для автоматизации:
- в сервисном/репозиторном слое используйте ORM/Core,
- в тестах держите вызовы простыми и декларативными (минимум SQL “в теле теста”).

### 11.2 Полезные ссылки
- SQLAlchemy Docs: https://docs.sqlalchemy.org/
- ORM Quickstart: https://docs.sqlalchemy.org/en/20/orm/quickstart.html
- Core Tutorial: https://docs.sqlalchemy.org/en/20/core/tutorial.html
- Engine/URLs: https://docs.sqlalchemy.org/en/20/core/engines.html
- Alembic: https://alembic.sqlalchemy.org/
