from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationRouter(BaseModel):
    route_name: str
    conditions: dict[str, Any] = {}
    target: str = ""
    priority: int = 0


class LLMIntegrationRouterManager:
    def __init__(self) -> None:
        self._routes: list[LLMIntegrationRouter] = []

    def add_route(
        self,
        route_name: str,
        target: str,
        conditions: dict[str, Any] | None = None,
        priority: int = 0,
    ) -> LLMIntegrationRouter:
        route = LLMIntegrationRouter(
            route_name=route_name,
            target=target,
            conditions=conditions or {},
            priority=priority,
        )
        self._routes.append(route)
        self._routes.sort(key=lambda r: r.priority, reverse=True)
        return route

    def remove_route(self, route_name: str) -> bool:
        for i, route in enumerate(self._routes):
            if route.route_name == route_name:
                del self._routes[i]
                return True
        return False

    def find_route(
        self, context: dict[str, Any]
    ) -> LLMIntegrationRouter | None:
        for route in self._routes:
            if self._matches_conditions(
                route.conditions, context
            ):
                return route
        return None

    def _matches_conditions(
        self,
        conditions: dict[str, Any],
        context: dict[str, Any],
    ) -> bool:
        for key, value in conditions.items():
            if key not in context:
                return False
            if context[key] != value:
                return False
        return True

    def list_routes(self) -> list[str]:
        return [r.route_name for r in self._routes]

    def clear(self) -> None:
        self._routes.clear()