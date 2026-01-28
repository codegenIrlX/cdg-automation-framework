from __future__ import annotations

import time
from typing import Callable, TypeVar

from loguru import logger

T = TypeVar("T")


class RetryHelper:
    def __init__(
        self,
        attempts: int = 10,
        initial_delay_seconds: float = 0.2,
        backoff_multiplier: float = 2.0,
    ) -> None:
        if attempts < 1:
            raise ValueError("Количество попыток должно быть >= 1")
        if initial_delay_seconds <= 0:
            raise ValueError("Начальная задержка должна быть > 0")
        if backoff_multiplier <= 1:
            raise ValueError("Множитель задержки должен быть > 1")

        self._attempts = attempts
        self._initial_delay_seconds = initial_delay_seconds
        self._backoff_multiplier = backoff_multiplier

    def run(self, action: Callable[[], T]) -> T:
        delay = self._initial_delay_seconds
        last_exception: Exception | None = None

        for attempt in range(1, self._attempts + 1):
            try:
                return action()
            except Exception as exc:
                last_exception = exc
                if attempt == self._attempts:
                    break
                logger.info(
                    "Повтор операции после ошибки. Попытка {attempt}/{total}, задержка {delay:.2f}с",
                    attempt=attempt,
                    total=self._attempts,
                    delay=delay,
                )
                time.sleep(delay)
                delay *= self._backoff_multiplier

        if last_exception:
            raise last_exception
        raise RuntimeError("Операция не выполнена и ошибка не сохранена")
