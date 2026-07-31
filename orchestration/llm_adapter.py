from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationAdapter(BaseModel):
    name: str
    provider: str
    config: dict[str, Any] = {}
    enabled: bool = True


class LLMIntegrationAdapterManager:
    def __init__(self) -> None:
        self._adapters: dict[str, LLMIntegrationAdapter] = {}

    def register(self, adapter: LLMIntegrationAdapter) -> None:
        self._adapters[adapter.name] = adapter

    def unregister(self, name: str) -> bool:
        if name in self._adapters:
            del self._adapters[name]
            return True
        return False

    def get(self, name: str) -> LLMIntegrationAdapter | None:
        return self._adapters.get(name)

    def enable(self, name: str) -> bool:
        adapter = self._adapters.get(name)
        if adapter:
            adapter.enabled = True
            return True
        return False

    def disable(self, name: str) -> bool:
        adapter = self._adapters.get(name)
        if adapter:
            adapter.enabled = False
            return True
        return False

    def list_adapters(self) -> list[str]:
        return list(self._adapters.keys())

    def get_enabled(self) -> list[LLMIntegrationAdapter]:
        return [
            a
            for a in self._adapters.values()
            if a.enabled
        ]