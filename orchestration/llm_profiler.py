from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationProfiler(BaseModel):
    name: str
    profile_fn: Any = None


class LLMIntegrationProfilerManager:
    def __init__(self) -> None:
        self._profilers: dict[str, LLMIntegrationProfiler] = {}

    def register(self, profiler: LLMIntegrationProfiler) -> None:
        self._profilers[profiler.name] = profiler

    def unregister(self, name: str) -> bool:
        if name in self._profilers:
            del self._profilers[name]
            return True
        return False

    def get(self, name: str) -> LLMIntegrationProfiler | None:
        return self._profilers.get(name)

    def profile(
        self, name: str, data: Any
    ) -> dict[str, Any]:
        profiler = self._profilers.get(name)
        if profiler is None:
            raise ValueError(
                f"Profiler '{name}' not found"
            )
        if profiler.profile_fn is not None:
            return profiler.profile_fn(data)
        return {"profiled": True}

    def list_profilers(self) -> list[str]:
        return list(self._profilers.keys())