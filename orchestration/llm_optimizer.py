from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationOptimizer(BaseModel):
    name: str
    optimize_fn: Any = None


class LLMIntegrationOptimizerManager:
    def __init__(self) -> None:
        self._optimizers: dict[str, LLMIntegrationOptimizer] = {}

    def register(self, optimizer: LLMIntegrationOptimizer) -> None:
        self._optimizers[optimizer.name] = optimizer

    def unregister(self, name: str) -> bool:
        if name in self._optimizers:
            del self._optimizers[name]
            return True
        return False

    def get(self, name: str) -> LLMIntegrationOptimizer | None:
        return self._optimizers.get(name)

    def optimize(
        self, name: str, data: Any
    ) -> Any:
        optimizer = self._optimizers.get(name)
        if optimizer is None:
            raise ValueError(
                f"Optimizer '{name}' not found"
            )
        if optimizer.optimize_fn is not None:
            return optimizer.optimize_fn(data)
        return data

    def list_optimizers(self) -> list[str]:
        return list(self._optimizers.keys())