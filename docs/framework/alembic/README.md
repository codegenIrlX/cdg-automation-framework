# Документация: Alembic. Миграции БД для автоматизации и CI/CD

---

## Оглавление

- [1. Введение](#1-введение)
  - [1.1 Что такое Alembic и зачем он нужен](#11-что-такое-alembic-и-зачем-он-нужен)
  - [1.2 Как Alembic связан с SQLAlchemy](#12-как-alembic-связан-с-sqlalchemy)
  - [1.3 Роль миграций в CI/CD и автоматизации тестирования](#13-роль-миграций-в-cicd-и-автоматизации-тестирования)
- [2. Установка и инициализация](#2-установка-и-инициализация)
  - [2.1 Установка через pip](#21-установка-через-pip)
  - [2.2 Инициализация проекта](#22-инициализация-проекта)
  - [2.3 Обзор структуры](#23-обзор-структуры)
- [3. Настройка подключения к БД](#3-настройка-подключения-к-бд)
  - [3.1 Поддержка драйверов (SQLAlchemy URL)](#31-поддержка-драйверов-sqlalchemy-url)
  - [3.2 Переменные окружения и `alembic.ini`](#32-переменные-окружения-и-alembicini)
  - [3.3 Настройка в `env.py` через env vars](#33-настройка-в-envpy-через-env-vars)
  - [3.4 Пример конфигурации для PostgreSQL и Oracle](#34-пример-конфигурации-для-postgresql-и-oracle)
- [4. Создание миграций](#4-создание-миграций)
  - [4.1 Автогенерация миграций](#41-автогенерация-миграций)
  - [4.2 Ручное написание миграций](#42-ручное-написание-миграций)
  - [4.3 Примеры: создание таблиц, добавление столбцов, удаление, изменение типов](#43-примеры-создание-таблиц-добавление-столбцов-удаление-изменение-типов)
  - [4.4 `op.execute()` для SQL-запросов напрямую](#44-opexecute-для-sql-запросов-напрямую)
- [5. Применение и откат миграций](#5-применение-и-откат-миграций)
  - [5.1 Применение](#51-применение)
  - [5.2 Откат](#52-откат)
  - [5.3 Версионирование](#53-версионирование)
- [6. Примеры SQL-запросов в Alembic](#6-примеры-sql-запросов-в-alembic)
  - [6.1 Вставка/обновление через `op.execute()`](#61-вставкаобновление-через-opexecute)
  - [6.2 Сложные запросы с JOIN и фильтрацией](#62-сложные-запросы-с-join-и-фильтрацией)
  - [6.3 Вызов функций и процедур](#63-вызов-функций-и-процедур)
- [7. Best Practices в автоматизации](#7-best-practices-в-автоматизации)
  - [7.1 Интеграция в pipeline](#71-интеграция-в-pipeline)
  - [7.2 Разделение структурных и data-миграций](#72-разделение-структурных-и-data-миграций)
  - [7.3 Проверка миграций в тестовой БД](#73-проверка-миграций-в-тестовой-бд)
  - [7.4 Фикстуры Alembic для запуска миграций в тестах](#74-фикстуры-alembic-для-запуска-миграций-в-тестах)
  - [7.5 alembic_utils и кастомные Alembic команды](#75-alembicutils-и-кастомные-alembic-команды)
- [8. Работа с несколькими БД и схемами](#8-работа-с-несколькими-бд-и-схемами)
  - [8.1 Подключение к разным базам (dev/stage/prod)](#81-подключение-к-разным-базам-devstageprod)
  - [8.2 Несколько схем в одной БД](#82-несколько-схем-в-одной-бд)
  - [8.3 Несколько конфигураций Alembic](#83-несколько-конфигураций-alembic)
- [9. Частые ошибки и отладка](#9-частые-ошибки-и-отладка)
  - [9.1 Конфликты ревизий (несколько heads)](#91-конфликты-ревизий-несколько-heads)
  - [9.2 Потеря версий / “can't locate revision”](#92-потеря-версий-cant-locate-revision)
  - [9.3 Несоответствие типов данных (БД vs модели)](#93-несоответствие-типов-данных-бд-vs-модели)
- [10. Заключение](#10-заключение)
  - [10.1 Сопровождение миграций](#101-сопровождение-миграций)
  - [10.2 Alembic vs raw SQL](#102-alembic-vs-raw-sql)
  - [10.3 Чистые и читаемые миграции](#103-чистые-и-читаемые-миграции)
- [Полезные ссылки](#полезные-ссылки)

---

## 1. Введение

### 1.1 Что такое Alembic и зачем он нужен
**Alembic** — инструмент миграций для Python-проектов, который позволяет версионировать изменения схемы БД (DDL) и управлять их применением/откатом.

Зачем:
- отслеживать эволюцию схемы БД во времени;
- синхронизировать схему между окружениями (локально, CI, stage);
- обеспечивать воспроизводимость тестов и развёртываний.

### 1.2 Как Alembic связан с SQLAlchemy
Alembic тесно интегрирован с **SQLAlchemy**:
- использует SQLAlchemy `Engine`/`Connection` для подключения;
- умеет автогенерировать миграции на основе `SQLAlchemy` моделей (`--autogenerate`);
- предоставляет операции через `alembic.op` (например, `op.create_table`, `op.add_column`).

### 1.3 Роль миграций в CI/CD и автоматизации тестирования
В автоматизации миграции нужны, чтобы:
- поднимать **чистую тестовую БД** перед прогоном;
- гарантировать, что тесты выполняются на **актуальной** версии схемы;
- проверять, что миграции применяются на разных СУБД/драйверах;
- избегать “works on my machine” из-за разных схем.

Типовой pipeline:
1) поднять БД (контейнер/сервер/managed),
2) применить миграции `alembic upgrade head`,
3) прогнать тесты,
4) (опционально) собрать артефакты и снепшоты схемы.

---

## 2. Установка и инициализация

### 2.1 Установка через pip
```bash
pip install alembic
```

Обычно Alembic используется вместе с SQLAlchemy и драйвером БД, например:
```bash
pip install sqlalchemy psycopg2-binary
```

### 2.2 Инициализация проекта
В корне репозитория:
```bash
alembic init alembic
```

### 2.3 Обзор структуры
После инициализации появятся:
- `alembic.ini` — базовая конфигурация Alembic (URL БД, логирование, script_location).
- `alembic/env.py` — «точка входа» (создание Engine/Connection, конфиг, target_metadata).
- `alembic/versions/` — каталог ревизий миграций (каждый файл — версия).

Пример структуры:
```
alembic.ini
alembic/
  env.py
  script.py.mako
  versions/
    20250101_1234_add_users_table.py
```

---

## 3. Настройка подключения к БД

### 3.1 Поддержка драйверов (SQLAlchemy URL)
Alembic использует URL формата SQLAlchemy:

- PostgreSQL: `postgresql+psycopg2://user:pass@host:5432/dbname`
- MySQL: `mysql+pymysql://user:pass@host:3306/dbname`
- Oracle: `oracle+cx_oracle://user:pass@host:1521/?service_name=ORCLPDB1`
- MSSQL: `mssql+pyodbc://user:pass@host:1433/dbname?driver=ODBC+Driver+17+for+SQL+Server`

> Важно: конкретные драйверы могут отличаться (например, `psycopg` vs `psycopg2`). Подбирайте URL под ваш драйвер.

### 3.2 Переменные окружения и `alembic.ini`
Подходы:
1) хранить URL в `alembic.ini` (удобно локально),
2) подставлять URL из переменных окружения (лучше для CI/CD и секретов).

Пример `alembic.ini`:
```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql+psycopg2://user:pass@localhost:5432/app
```

Рекомендация для CI: **не хранить креды в репо**, а отдавать через env.

### 3.3 Настройка в `env.py` через env vars
```python
import os
from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

db_url = os.getenv("DB_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

connectable = engine_from_config(
    config.get_section(config.config_ini_section),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
)
```

### 3.4 Пример конфигурации для PostgreSQL и Oracle
PostgreSQL:
```bash
export DB_URL="postgresql+psycopg2://user:pass@localhost:5432/app"
alembic upgrade head
```

Oracle (примерная форма):
```bash
export DB_URL="oracle+cx_oracle://user:pass@oracle-host:1521/?service_name=ORCLPDB1"
alembic upgrade head
```

---

## 4. Создание миграций

### 4.1 Автогенерация миграций
```bash
alembic revision --autogenerate -m "add users table"
```

Чтобы `--autogenerate` работал, в `env.py` нужно задать `target_metadata`:
```python
from app.db.base import Base  # Base = declarative_base()

target_metadata = Base.metadata
```

### 4.2 Ручное написание миграций
```bash
alembic revision -m "custom migration"
```

### 4.3 Примеры: создание таблиц, добавление столбцов, удаление, изменение типов
```python
from alembic import op
import sqlalchemy as sa

revision = "abcd1234"
down_revision = "prev1234"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("role_id", sa.Integer, nullable=True),
    )

def downgrade():
    op.drop_table("users")
```

Добавление столбца:
```python
def upgrade():
    op.add_column("users", sa.Column("is_active", sa.Boolean, server_default=sa.true(), nullable=False))

def downgrade():
    op.drop_column("users", "is_active")
```

Изменение типа:
```python
def upgrade():
    op.alter_column("users", "name", type_=sa.String(500))

def downgrade():
    op.alter_column("users", "name", type_=sa.String(255))
```

### 4.4 `op.execute()` для SQL-запросов напрямую
```python
def upgrade():
    op.execute("CREATE INDEX ix_users_name ON users (name)")

def downgrade():
    op.execute("DROP INDEX ix_users_name")
```

---

## 5. Применение и откат миграций

### 5.1 Применение
```bash
alembic upgrade head
```

### 5.2 Откат
```bash
alembic downgrade -1
```

### 5.3 Версионирование
Полезные команды:
```bash
alembic current
alembic history
alembic heads
alembic branches
```

---

## 6. Примеры SQL-запросов в Alembic

### 6.1 Вставка/обновление через `op.execute()`
```python
def upgrade():
    op.execute("INSERT INTO users (name) VALUES ('admin')")
```

### 6.2 Сложные запросы с JOIN и фильтрацией
```python
def upgrade():
    op.execute("""
        INSERT INTO audit_log (user_id, action)
        SELECT u.id, 'CREATED'
        FROM users u
        JOIN roles r ON r.id = u.role_id
        WHERE r.name = 'admin'
    """)
```

### 6.3 Вызов функций и процедур
```python
def upgrade():
    op.execute("CALL update_balance(123)")
    op.execute("SELECT calculate_tax(5000)")
```

---

## 7. Best Practices в автоматизации

### 7.1 Интеграция в pipeline
```bash
alembic upgrade head
pytest -m smoke
```

### 7.2 Разделение структурных и data-миграций
- **структурные миграции**: DDL (таблицы, индексы, колонки),
- **data-миграции**: изменения/инициализация данных.

Рекомендации:
- data-миграции делайте **идемпотентными**,
- продумывайте downgrade (или документируйте, почему он невозможен).

### 7.3 Проверка миграций в тестовой БД
- `upgrade head` на пустой БД,
- опционально `downgrade base` и снова `upgrade head` (если допустимо).

### 7.4 Фикстуры Alembic для запуска миграций в тестах
```python
import pytest
from alembic.config import Config
from alembic import command

@pytest.fixture(scope="session", autouse=True)
def migrate_test_db():
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    yield
```

### 7.5 alembic_utils и кастомные Alembic команды
- `alembic_utils` полезен для управления views/functions/triggers,
- кастомные команды помогают стандартизировать workflow в больших командах.

---

## 8. Работа с несколькими БД и схемами

### 8.1 Подключение к разным базам (dev/stage/prod)
```bash
DB_URL="postgresql+psycopg2://..." alembic upgrade head
```

### 8.2 Несколько схем в одной БД
- `include_schemas=True` в `context.configure` для autogenerate,
- использование `schema=` в op-операциях и/или `search_path`.

### 8.3 Несколько конфигураций Alembic
Варианты:
- несколько конфигов `alembic_*.ini`,
- или один конфиг + разные секции и `script_location`.

---

## 9. Частые ошибки и отладка

### 9.1 Конфликты ревизий (несколько heads)
Решение — merge:
```bash
alembic merge -m "merge heads" <head1> <head2>
```

### 9.2 Потеря версий / “can't locate revision”
Проверьте:
- наличие файлов в `alembic/versions/`,
- значение `alembic_version` в БД,
- корректность merge/rebase.

### 9.3 Несоответствие типов данных (БД vs модели)
Практики:
- явно задавать precision/scale (`Numeric(12, 2)`),
- проверять миграции на целевой СУБД,
- при необходимости использовать conditional SQL по dialect.

---

## 10. Заключение

### 10.1 Сопровождение миграций
- миграции должны быть атомарными и читаемыми,
- понятные сообщения `-m`,
- избегайте скрытых зависимостей,
- документируйте требования к расширениям/схемам/ролям.

### 10.2 Alembic vs raw SQL
- op API — для типовых изменений,
- `op.execute(raw_sql)` — для особенностей СУБД и сложных data migrations.

### 10.3 Чистые и читаемые миграции
- симметрия upgrade/downgrade (если возможно),
- явные индексы/ограничения,
- не смешивайте DDL и массовые data операции без необходимости.

---

## Полезные ссылки
- Alembic docs: https://alembic.sqlalchemy.org/
- SQLAlchemy docs: https://docs.sqlalchemy.org/
- SQLAlchemy URL формат: https://docs.sqlalchemy.org/en/latest/core/engines.html
