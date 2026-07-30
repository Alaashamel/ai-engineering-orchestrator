from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationTransformer(BaseModel):
    name: str
    transform_fn: Any = None
    order: int = 0


class LLMIntegrationTransformerManager:
    def __init__(self) -> None:
        self._transformers: list[LLMIntegrationTransformer] = []

    def add_transformer(
        self,
        name: str,
        transform_fn: Any,
        order: int = 0,
    ) -> LLMIntegrationTransformer:
        transformer = LLMIntegrationTransformer(
            name=name,
            transform_fn=transform_fn,
            order=order,
        )
        self._transformers.append(transformer)
        self._transformers.sort(key=lambda t: t.order)
        return transformer

    def remove_transformer(self, name: str) -> bool:
        for i, t in enumerate(self._transformers):
            if t.name == name:
                del self._transformers[i]
                return True
        return False

    def get_transformer(self, name: str) -> LLMIntegrationTransformer | None:
        for t in self._transformers:
            if t.name == name:
                return t
        return None

    def transform(
        self, data: Any
    ) -> Any:
        result = data
        for transformer in self._transformers:
            if transformer.transform_fn is not None:
                result = transformer.transform_fn(result)
        return result

    def list_transformers(self) -> list[str]:
        return [t.name for t in self._transformers]

    def clear(self) -> None:
        self._transformers.clear()