from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationFilter(BaseModel):
    name: str
    filter_fn: Any = None


class LLMIntegrationFilterManager:
    def __init__(self) -> None:
        self._filters: dict[str, LLMIntegrationFilter] = {}

    def register(self, filter: LLMIntegrationFilter) -> None:
        self._filters[filter.name] = filter

    def unregister(self, name: str) -> bool:
        if name in self._filters:
            del self._filters[name]
            return True
        return False

    def get(self, name: str) -> LLMIntegrationFilter | None:
        return self._filters.get(name)

    def apply(
        self, name: str, data: Any
    ) -> Any:
        filter = self._filters.get(name)
        if filter is None:
            raise ValueError(
                f"Filter '{name}' not found"
            )
        if filter.filter_fn is not None:
            return filter.filter_fn(data)
        return data

    def list_filters(self) -> list[str]:
        return list(self._filters.keys())