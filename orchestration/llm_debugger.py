from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationDebugger(BaseModel):
    name: str
    debug_fn: Any = None


class LLMIntegrationDebuggerManager:
    def __init__(self) -> None:
        self._debuggers: dict[str, LLMIntegrationDebugger] = {}

    def register(self, debugger: LLMIntegrationDebugger) -> None:
        self._debuggers[debugger.name] = debugger

    def unregister(self, name: str) -> bool:
        if name in self._debuggers:
            del self._debuggers[name]
            return True
        return False

    def get(self, name: str) -> LLMIntegrationDebugger | None:
        return self._debuggers.get(name)

    def debug(
        self, name: str, data: Any
    ) -> dict[str, Any]:
        debugger = self._debuggers.get(name)
        if debugger is None:
            raise ValueError(
                f"Debugger '{name}' not found"
            )
        if debugger.debug_fn is not None:
            return debugger.debug_fn(data)
        return {"debugged": True}

    def list_debuggers(self) -> list[str]:
        return list(self._debuggers.keys())