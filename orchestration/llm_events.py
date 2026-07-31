from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationEvent(BaseModel):
    event_type: str
    model: str
    timestamp: str = ""
    data: dict[str, Any] = {}

    def __post_init__(self) -> None:
        if not self.timestamp:
            from datetime import datetime, timezone
            self.timestamp = datetime.now(timezone.utc).isoformat()


class LLMIntegrationEventListener:
    def __init__(self) -> None:
        self._listeners: dict[str, list[Any]] = {}

    def on(self, event_type: str, callback: Any) -> None:
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def off(self, event_type: str, callback: Any) -> None:
        if event_type in self._listeners:
            self._listeners[event_type].remove(callback)

    def emit(self, event: LLMIntegrationEvent) -> None:
        listeners = self._listeners.get(event.event_type, [])
        for callback in listeners:
            if callable(callback):
                callback(event)

    def get_listeners(self, event_type: str) -> list[Any]:
        return list(self._listeners.get(event_type, []))

    def clear(self) -> None:
        self._listeners.clear()