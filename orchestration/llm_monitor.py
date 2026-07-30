from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationMonitor(BaseModel):
    name: str
    monitor_fn: Any = None


class LLMIntegrationMonitorManager:
    def __init__(self) -> None:
        self._monitors: dict[str, LLMIntegrationMonitor] = {}

    def register(self, monitor: LLMIntegrationMonitor) -> None:
        self._monitors[monitor.name] = monitor

    def unregister(self, name: str) -> bool:
        if name in self._monitors:
            del self._monitors[name]
            return True
        return False

    def get(self, name: str) -> LLMIntegrationMonitor | None:
        return self._monitors.get(name)

    def monitor(
        self, name: str, data: Any
    ) -> dict[str, Any]:
        monitor = self._monitors.get(name)
        if monitor is None:
            raise ValueError(
                f"Monitor '{name}' not found"
            )
        if monitor.monitor_fn is not None:
            return monitor.monitor_fn(data)
        return {"monitored": True}

    def list_monitors(self) -> list[str]:
        return list(self._monitors.keys())