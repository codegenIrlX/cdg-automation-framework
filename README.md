# Test Automation Framework

[![Release](https://img.shields.io/github/v/release/codegenIrlX/cdg-automation-framework?style=flat-square&label=release)](https://github.com/codegenIrlX/cdg-automation-framework/releases)
[![CI](https://img.shields.io/github/actions/workflow/status/codegenIrlX/cdg-automation-framework/smoke-tests.yml?style=flat-square)](https://github.com/codegenIrlX/cdg-automation-framework/actions)
[![Last commit](https://img.shields.io/github/last-commit/codegenIrlX/cdg-automation-framework?style=flat-square)](https://github.com/codegenIrlX/cdg-automation-framework/commits/main)

## Оглавление

- [1. Документация](#1-документация)
- [2. Базовые требования Plusofon API](#2-базовые-требования-plusofon-api)
  - [2.1. Коды статусов и ошибок](#21-коды-статусов-и-ошибок)
- [3. Быстрый старт](#3-быстрый-старт)
  - [3.1 Отчеты Allure (Windows)](#31-отчеты-allure-windows)
- [4. Docker Compose](#4-docker-compose)
  - [4.1. Предусловия](#41-предусловия)
  - [4.2. Быстрый старт](#42-быстрый-старт)
  - [4.3. Развернутые сервисы](#43-развернутые-сервисы)
  - [4.4. Сервисы и порты](#44-сервисы-и-порты)
  - [4.5. Переменные окружения](#45-переменные-окружения)
  - [4.6. Healthcheck](#46-healthcheck)
  - [4.7. Инициализация PostgreSQL (seed/DDL)](#47-инициализация-postgresql-seedddl)
  - [4.8. Остановка и очистка](#48-остановка-и-очистка)
  - [4.9. Полезные команды](#49-полезные-команды)
- [5. .env переменные](#5-env-переменные)

## 1. Документация

| Название | Ссылка на документацию |
| --- | --- |
| Python-код | [Документация по Python-коду](https://github.com/codegenIrlX/cdg-automation-framework/tree/dev/docs/python) |
| Фреймворк | [Документация по работе с фреймворком](https://github.com/codegenIrlX/cdg-automation-framework/tree/dev/docs/framework) |
| Фреймворк / Allure | [Документация по Allure](https://github.com/codegenIrlX/cdg-automation-framework/tree/dev/docs/framework/allure) |
| Фреймворк / Библиотеки | [Документация по библиотекам](https://github.com/codegenIrlX/cdg-automation-framework/tree/dev/docs/framework/dependencies) |
| Фреймворк / HTTPX | [Документация по HTTPX](https://github.com/codegenIrlX/cdg-automation-framework/tree/dev/docs/framework/httpx) |
| Фреймворк / Pydantic | [Документация по Pydantic](https://github.com/codegenIrlX/cdg-automation-framework/tree/dev/docs/framework/pydantic) |
| Фреймворк / Pytest | [Документация по Pytest](https://github.com/codegenIrlX/cdg-automation-framework/tree/dev/docs/framework/pytest) |
| Тест-кейсы | [Документация по тест-кейсам](https://github.com/codegenIrlX/cdg-automation-framework/tree/dev/docs/test_cases) |

## 2. Базовые требования Plusofon API

- [Документация по работе с API](https://help.plusofon.ru/api/v1)
- Адрес: `https://restapi.plusofon.ru`
- Авторизация: тип `Bearer Token`
- Обязательный заголовок `Client`: значение `10553`

### 2.1. Коды статусов и ошибок

| Код | Описание |
| --- | --- |
| 200 | запрос успешно выполнен |
| 201 | сущность успешно создана |
| 400 | параметр указан некорректно |
| 404 | целевая сущность не найдена |
| 500 | нет доступа |

## 3. Быстрый старт

1. Скопировать `.env.example` в `.env` и заполнить значения.
2. Установить зависимости: `python -m pip install -e .`
3. Запустить тесты: `pytest`.
4. Если IDE подсвечивает импорты, отметить `src` как **Sources Root** и выполнить **Invalidate Caches / Restart**.

### 3.1. Отчеты Allure (Windows)

Установка Allure в Windows (через Scoop):

```bash
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
scoop install allure
allure --version
```

Генерация и отображение отчета Allure:

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

## 4. Docker Compose

Для локального запуска инфраструктуры (PostgreSQL + RabbitMQ + Kafka + Kafka UI) используется файл `docker-compose.yml`.

### 4.1. Предусловия

- Установлен Docker Desktop / Docker Engine
- Доступна команда `docker compose` (Compose v2)

### 4.2. Быстрый старт

```bash
# поднять сервисы в фоне
docker compose up -d

# проверить статус
docker compose ps

# посмотреть логи
docker compose logs -f
```

### 4.3. Развернутые сервисы

| Сервис | URL | Описание |
| --- | --- | --- |
| RabbitMQ UI | http://localhost:15672 | Web UI для просмотра очередей/сообщений и управления RabbitMQ |
| Kafka UI | http://localhost:8080 | Web UI для просмотра кластеров/топиков/сообщений Kafka |
| PostgreSQL | `127.0.0.1:5432` | Подключение к БД (например, через psql/IDE/DB-клиент) |

### 4.4. Сервисы и порты

- **PostgreSQL**: `127.0.0.1:5432` (image: `postgres:16-alpine`)
- **RabbitMQ**: `127.0.0.1:5672` (AMQP) и `127.0.0.1:15672` (Management UI) (image: `rabbitmq:3-management`)
- **Kafka**: `127.0.0.1:9092` (Broker) (image: зависит от compose)
- **Kafka UI**: `http://localhost:8080` (Web UI) (image: зависит от compose)

> Порты проброшены только на `127.0.0.1`, поэтому сервисы доступны **только локально**.

### 4.5. Переменные окружения

`docker-compose.yml` ожидает переменные из `.env` (или из окружения), например:

- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `RABBITMQ_USER`, `RABBITMQ_PASSWORD`, `RABBITMQ_VHOST`

### 4.6. Healthcheck

В compose настроены healthcheck’и:

- PostgreSQL: `pg_isready`
- RabbitMQ: `rabbitmq-diagnostics check_running`

Статус можно увидеть через:

```bash
docker compose ps
```

### 4.7. Инициализация PostgreSQL (seed/DDL)

При старте контейнера PostgreSQL монтируется каталог:

- `./docker-entrypoint-initdb.d` → `/docker-entrypoint-initdb.d` (read-only)

Положите туда `.sql`/`.sh` файлы — они выполнятся **один раз** при первом создании volume.

### 4.8. Остановка и очистка

```bash
# остановить сервисы
docker compose down

# остановить и удалить volumes (сотрёт данные БД/очереди)
docker compose down -v
```

### 4.9. Полезные команды

```bash
# пересобрать (если есть build-секции) и перезапустить
docker compose up -d --force-recreate

# перезапустить один сервис
docker compose restart postgres
docker compose restart rabbitmq

# создать Kafka-топик вручную (для тестирования)
docker compose exec kafka bash -lc "kafka-topics --bootstrap-server localhost:9092 --create --topic test.topic --partitions 1 --replication-factor 1"
```

## 5. .env переменные

| Переменная | Описание |
| --- |----------|
| BASE_URL | -        |
| API_TOKEN | -        |
| CLIENT_ID | -        |
| TIMEOUT_SECONDS | -        |
| VERIFY_SSL | -        |
| LOG_LEVEL | -        |
| POSTGRES_DB | -        |
| POSTGRES_USER | -        |
| POSTGRES_PASSWORD | -        |
| DB_ECHO | -        |
| RABBITMQ_HOST | -        |
| RABBITMQ_PORT | -        |
| RABBITMQ_USER | -        |
| RABBITMQ_PASSWORD | -        |
| RABBITMQ_VHOST | -        |
