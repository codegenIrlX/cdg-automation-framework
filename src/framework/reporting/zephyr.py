from __future__ import annotations

from collections.abc import Iterable
from functools import wraps
from typing import Callable, TypeVar

import allure

from framework.config import settings

TCallable = TypeVar("TCallable", bound=Callable[..., object])


def _normalize_cases(cases: Iterable[str]) -> list[str]:
    if cases is None:
        raise ValueError("Нужно передать непустой список идентификаторов кейсов.")
    normalized: list[str] = []
    for case in cases:
        if not isinstance(case, str):
            raise ValueError("Идентификаторы кейсов должны быть строками.")
        case_id = case.strip()
        if not case_id:
            raise ValueError("Идентификаторы кейсов не должны быть пустыми.")
        normalized.append(case_id)
    if not normalized:
        raise ValueError("Нужно передать хотя бы один идентификатор кейса.")
    return normalized


def _resolve_base_url() -> str:
    base_url = settings.ZEPHYR_URL
    if not base_url:
        raise ValueError("Переменная ZEPHYR_URL не задана в окружении.")
    return base_url.rstrip("/")


def link(cases: Iterable[str]) -> Callable[[TCallable], TCallable]:
    """Добавляет ссылки на Zephyr кейсы в отчёт Allure."""

    case_ids = _normalize_cases(cases)

    def decorator(test_func: TCallable) -> TCallable:
        @wraps(test_func)
        def wrapper(*args: object, **kwargs: object) -> object:
            base_url = _resolve_base_url()
            for case_id in case_ids:
                url = f"{base_url}/{case_id}"
                allure.dynamic.link(url, name=case_id)
            return test_func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
