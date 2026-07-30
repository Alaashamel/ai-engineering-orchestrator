import pytest
from orchestration.llm_router import (
    LLMIntegrationRouter,
    LLMIntegrationRouterManager,
)


class TestLLMIntegrationRouterManager:
    def test_add_route(self):
        manager = LLMIntegrationRouterManager()
        route = manager.add_route(
            "default",
            "openai",
            priority=0,
        )
        assert route.route_name == "default"
        assert route.target == "openai"

    def test_remove_route(self):
        manager = LLMIntegrationRouterManager()
        manager.add_route("default", "openai")
        assert manager.remove_route("default") is True
        assert manager.remove_route("default") is False

    def test_find_route(self):
        manager = LLMIntegrationRouterManager()
        manager.add_route(
            "premium",
            "gpt-4o",
            conditions={"tier": "premium"},
            priority=10,
        )
        manager.add_route(
            "free",
            "gpt-3.5",
            conditions={"tier": "free"},
            priority=5,
        )
        route = manager.find_route({"tier": "premium"})
        assert route is not None
        assert route.target == "gpt-4o"

    def test_find_route_no_match(self):
        manager = LLMIntegrationRouterManager()
        manager.add_route(
            "premium",
            "gpt-4o",
            conditions={"tier": "premium"},
        )
        route = manager.find_route({"tier": "unknown"})
        assert route is None

    def test_list_routes(self):
        manager = LLMIntegrationRouterManager()
        manager.add_route("r1", "target1")
        manager.add_route("r2", "target2")
        assert len(manager.list_routes()) == 2