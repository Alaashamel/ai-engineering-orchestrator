from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationWrapper(BaseModel):
    name: str
    wrap_fn: Any = None


class LLMIntegrationWrapperManager:
    def __init__(self) -> None:
        self._wrappers: dict[str, LLMIntegrationWrapper] = {}

    def register(self, wrapper: LLMIntegrationWrapper) -> None:
        self._wrappers[wrapper.name] = wrapper

    def unregister(self, name: str) -> bool:
        if name in self._wrappers:
            del self._wrappers[name]
            return True
        return False

    def get(self, name: str) -> LLMIntegrationWrapper | None:
        return self._wrappers.get(name)

    def wrap(
        self, name: str, data: Any
    ) -> Any:
        wrapper = self._wrappers.get(name)
        if wrapper is None:
            raise ValueError(
                f"Wrapper '{name}' not found"
            )
        if wrapper.wrap_fn is not None:
            return wrapper.wrap_fn(data)
        return data

    def list_wrappers(self) -> list[str]:
        return list(self._wrappers.keys())