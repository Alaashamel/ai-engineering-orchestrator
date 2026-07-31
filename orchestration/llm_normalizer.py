from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationNormalizer(BaseModel):
    name: str
    normalize_fn: Any = None


class LLMIntegrationNormalizerManager:
    def __init__(self) -> None:
        self._normalizers: dict[str, LLMIntegrationNormalizer] = {}

    def register(self, normalizer: LLMIntegrationNormalizer) -> None:
        self._normalizers[normalizer.name] = normalizer

    def unregister(self, name: str) -> bool:
        if name in self._normalizers:
            del self._normalizers[name]
            return True
        return False

    def get(self, name: str) -> LLMIntegrationNormalizer | None:
        return self._normalizers.get(name)

    def normalize(
        self, name: str, data: Any
    ) -> Any:
        normalizer = self._normalizers.get(name)
        if normalizer is None:
            raise ValueError(
                f"Normalizer '{name}' not found"
            )
        if normalizer.normalize_fn is not None:
            return normalizer.normalize_fn(data)
        return data

    def list_normalizers(self) -> list[str]:
        return list(self._normalizers.keys())