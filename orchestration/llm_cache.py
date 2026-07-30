from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LLMResultCache:
    def __init__(self, cache_dir: str = ".llm_cache") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _cache_key(self, prompt: str, model: str) -> str:
        import hashlib
        key = f"{model}:{prompt}"
        return hashlib.sha256(key.encode()).hexdigest()

    def get(self, prompt: str, model: str) -> Any | None:
        key = self._cache_key(prompt, model)
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        return None

    def set(self, prompt: str, model: str, result: Any) -> None:
        key = self._cache_key(prompt, model)
        cache_file = self.cache_dir / f"{key}.json"
        with open(cache_file, "w") as f:
            json.dump(result, f, default=str)

    def clear(self) -> None:
        for file in self.cache_dir.glob("*.json"):
            file.unlink()

    def size(self) -> int:
        return len(list(self.cache_dir.glob("*.json")))

    def invalidate(self, prompt: str, model: str) -> bool:
        key = self._cache_key(prompt, model)
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            cache_file.unlink()
            return True
        return False