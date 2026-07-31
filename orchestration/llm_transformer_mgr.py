from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationTransformer(BaseModel):
    name: str
    transform_fn: Any = None


class LLMIntegrationTransformerManager:
    def __init__(self) -> None:
        self._transformers: dict[str, LLMIntegrationTransformer] = {}

    def register(self, transformer: LLMIntegrationTransformer) -> None:
        self._transformers[transformer.name] = transformer

    def unregister(self, name: str) -> bool:
        if name in self._transformers:
            del self._transformers[name]
            return True
        return False

    def get(self, name: str) -> LLMIntegrationTransformer | None:
        return self._transformers.get(name)

    def transform(
        self, name: str, data: Any
    ) -> Any:
        transformer = self._transformers.get(name)
        if transformer is None:
            raise ValueError(
                f"Transformer '{name}' not found"
            )
        if transformer.transform_fn is not None:
            return transformer.transform_fn(data)
        return data

    def list_transformers(self) -> list[str]:
        return list(self._transformers.keys())