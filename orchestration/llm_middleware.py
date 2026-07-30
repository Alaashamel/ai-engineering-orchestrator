from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationMiddleware:
    def __init__(self) -> None:
        self._middlewares: list[Any] = []

    def add(self, middleware: Any) -> None:
        self._middlewares.append(middleware)

    def remove(self, middleware: Any) -> bool:
        if middleware in self._middlewares:
            self._middlewares.remove(middleware)
            return True
        return False

    async def process_request(
        self,
        request: dict[str, Any],
    ) -> dict[str, Any]:
        processed = request
        for mw in self._middlewares:
            if callable(mw):
                processed = await self._call_middleware(mw, processed)
        return processed

    async def process_response(
        self,
        response: dict[str, Any],
    ) -> dict[str, Any]:
        processed = response
        for mw in reversed(self._middlewares):
            if callable(mw):
                processed = await self._call_middleware(mw, processed)
        return processed

    async def _call_middleware(
        self,
        middleware: Any,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        import asyncio

        if asyncio.iscoroutinefunction(middleware):
            return await middleware(data)
        if callable(middleware):
            result = middleware(data)
            if asyncio.iscoroutine(result):
                return await result
            return result
        return data