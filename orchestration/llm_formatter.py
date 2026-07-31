from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationFormatter(BaseModel):
    name: str
    format_fn: Any = None


class LLMIntegrationFormatterManager:
    def __init__(self) -> None:
        self._formatters: dict[str, LLMIntegrationFormatter] = {}

    def register(self, formatter: LLMIntegrationFormatter) -> None:
        self._formatters[formatter.name] = formatter

    def unregister(self, name: str) -> bool:
        if name in self._formatters:
            del self._formatters[name]
            return True
        return False

    def get(self, name: str) -> LLMIntegrationFormatter | None:
        return self._formatters.get(name)

    def format(self, name: str, data: Any) -> str:
        formatter = self._formatters.get(name)
        if formatter is None:
            raise ValueError(
                f"Formatter '{name}' not found"
            )
        if formatter.format_fn is not None:
            return formatter.format_fn(data)
        return str(data)

    def list_formatters(self) -> list[str]:
        return list(self._formatters.keys())