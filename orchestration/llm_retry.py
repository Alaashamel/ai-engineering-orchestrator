from __future__ import annotations

import asyncio
import time
from typing import Callable, TypeVar

from orchestration.llm_config import LLMProviderConfig

T = TypeVar("T")


class LLMRetryHandler:
    def __init__(self, config: LLMProviderConfig):
        self.max_retries = config.max_retries
        self.base_delay = 1.0
        self.max_delay = 60.0
        self.backoff_factor = 2.0

    async def execute_with_retry(
        self, func: Callable[..., T], *args: object, **kwargs: object
    ) -> T:
        last_exception: Exception | None = None
        delay = self.base_delay

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                last_exception = exc
                if attempt < self.max_retries:
                    await asyncio.sleep(delay)
                    delay = min(delay * self.backoff_factor, self.max_delay)

        raise last_exception  # type: ignore[misc]

    @staticmethod
    def is_retryable(error: Exception) -> bool:
        msg = str(error).lower()
        retryable = [
            "timeout",
            "rate limit",
            "429",
            "503",
            "502",
            "504",
            "connection",
            "network",
        ]
        return any(keyword in msg for keyword in retryable)