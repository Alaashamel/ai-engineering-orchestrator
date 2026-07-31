from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationScheduler(BaseModel):
    name: str
    schedule_fn: Any = None


class LLMIntegrationSchedulerManager:
    def __init__(self) -> None:
        self._schedulers: dict[str, LLMIntegrationScheduler] = {}

    def register(self, scheduler: LLMIntegrationScheduler) -> None:
        self._schedulers[scheduler.name] = scheduler

    def unregister(self, name: str) -> bool:
        if name in self._schedulers:
            del self._schedulers[name]
            return True
        return False

    def get(self, name: str) -> LLMIntegrationScheduler | None:
        return self._schedulers.get(name)

    def schedule(
        self, name: str, data: Any
    ) -> Any:
        scheduler = self._schedulers.get(name)
        if scheduler is None:
            raise ValueError(
                f"Scheduler '{name}' not found"
            )
        if scheduler.schedule_fn is not None:
            return scheduler.schedule_fn(data)
        return data

    def list_schedulers(self) -> list[str]:
        return list(self._schedulers.keys())