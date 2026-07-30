from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationCache(BaseModel):
    name: str
    cache_fn: Any = None


class LLMIntegrationCacheManager:
    def __init__(self) -> None:
        self._caches: dict[str, LLMIntegrationCache] = {}

    def register(self, cache: LLMIntegrationCache) -> None:
        self._caches[cache.name] = cache

    def unregister(self, name: str) -> bool:
        if name in self._caches:
            del self._caches[name]
            return True
        return False

    def get(self, name: str) -> LLMIntegrationCache | None:
        return self._caches.get(name)

    def get_cached(
        self, name: str, key: str
    ) -> Any | None:
        cache = self._caches.get(name)
        if cache is None:
            raise ValueError(
                f"Cache '{name}' not found"
            )
        if cache.cache_fn is not None:
            return cache.cache_fn(key)
        return None

    def list_caches(self) -> list[str]:
        return list(self._caches.keys())