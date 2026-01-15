# Test Automation Framework

[![Release](https://img.shields.io/github/v/release/codegenIrlX/cdg-automation-framework?style=flat-square&label=release)](https://github.com/codegenIrlX/cdg-automation-framework/releases)
[![CI](https://img.shields.io/github/actions/workflow/status/codegenIrlX/cdg-automation-framework/smoke-tests.yml?style=flat-square)](https://github.com/codegenIrlX/cdg-automation-framework/actions)
[![Last commit](https://img.shields.io/github/last-commit/codegenIrlX/cdg-automation-framework?style=flat-square)](https://github.com/codegenIrlX/cdg-automation-framework/commits/main)

## Базовые требования Plusofon API

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
