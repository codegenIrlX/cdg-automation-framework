from __future__ import annotations

from typing import Any, Mapping


class SensitiveHeadersMasker:
    """Маскировка чувствительных заголовков."""

    _sensitive_keys = {"authorization"}

    def mask(self, headers: Mapping[str, Any]) -> dict[str, Any]:
        masked = dict(headers)
        for key in list(masked.keys()):
            if key.lower() in self._sensitive_keys:
                masked[key] = "***"
        return masked
