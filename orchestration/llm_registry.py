from __future__ import annotations

from typing import Any


class LLMProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, Any] = {}
        self._default_provider: str = "openai"

    def register(self, name: str, provider: Any) -> None:
        self._providers[name] = provider

    def unregister(self, name: str) -> None:
        if name in self._providers:
            del self._providers[name]

    def get_provider(self, name: str | None = None) -> Any:
        provider_name = name or self._default_provider
        if provider_name not in self._providers:
            raise KeyError(
                f"Provider '{provider_name}' not registered. "
                f"Available: {list(self._providers.keys())}"
            )
        return self._providers[provider_name]

    def set_default(self, name: str) -> None:
        if name not in self._providers:
            raise KeyError(
                f"Provider '{name}' not registered. "
                f"Available: {list(self._providers.keys())}"
            )
        self._default_provider = name

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())

    def has_provider(self, name: str) -> bool:
        return name in self._providers

    def switch_provider(
        self, from_name: str, to_name: str
    ) -> bool:
        if from_name not in self._providers:
            return False
        if to_name not in self._providers:
            return False
        provider = self._providers.pop(from_name)
        self._providers[to_name] = provider
        if self._default_provider == from_name:
            self._default_provider = to_name
        return True