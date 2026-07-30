from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationPlugin(BaseModel):
    name: str
    version: str
    enabled: bool = True
    config: dict[str, Any] = {}

    def initialize(self) -> bool:
        return True

    def shutdown(self) -> None:
        pass


class LLMIntegrationPluginManager:
    def __init__(self) -> None:
        self._plugins: dict[str, LLMIntegrationPlugin] = {}

    def register(self, plugin: LLMIntegrationPlugin) -> None:
        self._plugins[plugin.name] = plugin

    def unregister(self, name: str) -> bool:
        if name in self._plugins:
            del self._plugins[name]
            return True
        return False

    def get(self, name: str) -> LLMIntegrationPlugin | None:
        return self._plugins.get(name)

    def enable(self, name: str) -> bool:
        plugin = self._plugins.get(name)
        if plugin:
            plugin.enabled = True
            return True
        return False

    def disable(self, name: str) -> bool:
        plugin = self._plugins.get(name)
        if plugin:
            plugin.enabled = False
            return True
        return False

    def initialize_all(self) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for name, plugin in self._plugins.items():
            if plugin.enabled:
                results[name] = plugin.initialize()
        return results

    def shutdown_all(self) -> None:
        for plugin in self._plugins.values():
            plugin.shutdown()

    def list_plugins(self) -> list[str]:
        return list(self._plugins.keys())