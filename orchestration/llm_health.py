from __future__ import annotations

from typing import Any


class LLMIntegrationHealthCheck:
    def __init__(self) -> None:
        self._checks: dict[str, Any] = {}
        self._results: dict[str, Any] = {}

    def register_check(
        self, name: str, check_fn: Any
    ) -> None:
        self._checks[name] = check_fn

    async def run_checks(self) -> dict[str, Any]:
        results: dict[str, Any] = {}
        for name, check_fn in self._checks.items():
            try:
                if callable(check_fn):
                    import asyncio
                    if asyncio.iscoroutinefunction(check_fn):
                        result = await check_fn()
                    else:
                        result = check_fn()
                    results[name] = {
                        "status": "healthy",
                        "result": result,
                    }
                else:
                    results[name] = {
                        "status": "healthy",
                        "result": check_fn,
                    }
            except Exception as exc:
                results[name] = {
                    "status": "unhealthy",
                    "error": str(exc),
                }
        self._results = results
        return results

    def get_status(self) -> str:
        if not self._results:
            return "unknown"
        return "healthy" if all(
            v.get("status") == "healthy"
            for v in self._results.values()
        ) else "degraded"

    def is_healthy(self) -> bool:
        if not self._results:
            return len(self._checks) > 0
        return all(
            v.get("status") == "healthy"
            for v in self._results.values()
        )