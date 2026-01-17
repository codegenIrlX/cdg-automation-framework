# Test Automation Framework

[![Release](https://img.shields.io/github/v/release/codegenIrlX/cdg-automation-framework?style=flat-square&label=release)](https://github.com/codegenIrlX/cdg-automation-framework/releases)
[![CI](https://img.shields.io/github/actions/workflow/status/codegenIrlX/cdg-automation-framework/smoke-tests.yml?style=flat-square)](https://github.com/codegenIrlX/cdg-automation-framework/actions)
[![Last commit](https://img.shields.io/github/last-commit/codegenIrlX/cdg-automation-framework?style=flat-square)](https://github.com/codegenIrlX/cdg-automation-framework/commits/main)

## Оглавление

- [Введение](#введение)
- [Документация](#документация)
- [Базовые требования Plusofon API](#базовые-требования-plusofon-api)
  - [Коды статусов и ошибок](#коды-статусов-и-ошибок)
- [Быстрый старт](#быстрый-старт)
- [Docker Compose](#docker-compose)
  - [Предусловия](#предусловия)
  - [Быстрый старт](#быстрый-старт-1)
  - [Сервисы и порты](#сервисы-и-порты)
  - [Переменные окружения](#переменные-окружения)
  - [Healthcheck](#healthcheck)
  - [Инициализация PostgreSQL (seed/DDL)](#инициализация-postgresql-seedddl)
  - [Остановка и очистка](#остановка-и-очистка)
  - [Полезные команды](#полезные-команды)
- [.env переменные](#env-переменные)

## Введение

Данный тестовый фреймворк демонстрирует подходы к автоматизации интеграционных проверок: работу с **REST API**, асинхронными сообщениями через **RabbitMQ**, взаимодействие с **базами данных** и обработку событий/стримов через **Kafka**.

## Документация

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

## Базовые требования Plusofon API

- [Документация по работе с API](https://help.plusofon.ru/api/v1)
- Адрес: `https://restapi.plusofon.ru`
- Авторизация: тип `Bearer Token`
- Обязательный заголовок `Client`: значение `10553`

### Коды статусов и ошибок

| Код | Описание |
| --- | --- |
| 200 | запрос успешно выполнен |
| 201 | сущность успешно создана |
| 400 | параметр указан некорректно |
| 404 | целевая сущность не найдена |
| 500 | нет доступа |

## Быстрый старт

1. Скопировать `.env.example` в `.env` и заполнить значения.
2. Установить зависимости: `python -m pip install -e .`
3. Запустить тесты: `pytest`.
4. Если IDE подсвечивает импорты, отметить `src` как **Sources Root** и выполнить **Invalidate Caches / Restart**.

## Docker Compose

Для локального запуска инфраструктуры (PostgreSQL + RabbitMQ) используется файл `docker-compose.yml`.

### Предусловия
- Установлен Docker Desktop / Docker Engine
- Доступна команда `docker compose` (Compose v2)

### Быстрый старт
```bash
# поднять сервисы в фоне
docker compose up -d

# проверить статус
docker compose ps

# посмотреть логи
docker compose logs -f
```

### Сервисы и порты
- **PostgreSQL**: `127.0.0.1:5432` (image: `postgres:16-alpine`)
- **RabbitMQ**: `127.0.0.1:5672` (AMQP) и `127.0.0.1:15672` (Management UI) (image: `rabbitmq:3-management`)

> Порты проброшены только на `127.0.0.1`, поэтому сервисы доступны **только локально**.

### Переменные окружения
`docker-compose.yml` ожидает переменные из `.env` (или из окружения), например:
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `RABBITMQ_USER`, `RABBITMQ_PASSWORD`, `RABBITMQ_VHOST`

### Healthcheck
В compose настроены healthcheck’и:
- PostgreSQL: `pg_isready`
- RabbitMQ: `rabbitmq-diagnostics check_running`

Статус можно увидеть через:
```bash
docker compose ps
```

### Инициализация PostgreSQL (seed/DDL)
При старте контейнера PostgreSQL монтируется каталог:
- `./docker-entrypoint-initdb.d` → `/docker-entrypoint-initdb.d` (read-only)

Положите туда `.sql`/`.sh` файлы — они выполнятся **один раз** при первом создании volume.

### Остановка и очистка
```bash
# остановить сервисы
docker compose down

# остановить и удалить volumes (сотрёт данные БД/очереди)
docker compose down -v
```

### Полезные команды
```bash
# пересобрать (если есть build-секции) и перезапустить
docker compose up -d --force-recreate

# перезапустить один сервис
docker compose restart postgres
docker compose restart rabbitmq
```

## .env переменные

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
