from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationEnforcer(BaseModel):
    name: str
    enforce_fn: Any = None


class LLMIntegrationEnforcerManager:
    def __init__(self) -> None:
        self._enforcers: dict[str, LLMIntegrationEnforcer] = {}

    def register(self, enforcer: LLMIntegrationEnforcer) -> None:
        self._enforcers[enforcer.name] = enforcer

    def unregister(self, name: str) -> bool:
        if name in self._enforcers:
            del self._enforcers[name]
            return True
        return False

    def get(self, name: str) -> LLMIntegrationEnforcer | None:
        return self._enforcers.get(name)

    def enforce(
        self, name: str, data: Any
    ) -> bool:
        enforcer = self._enforcers.get(name)
        if enforcer is None:
            raise ValueError(
                f"Enforcer '{name}' not found"
            )
        if enforcer.enforce_fn is not None:
            return bool(enforcer.enforce_fn(data))
        return True

    def list_enforcers(self) -> list[str]:
        return list(self._enforcers.keys())