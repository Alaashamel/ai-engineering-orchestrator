import pytest
from orchestration.llm_wrapper import (
    LLMIntegrationWrapper,
    LLMIntegrationWrapperManager,
)


class TestLLMIntegrationWrapperManager:
    def test_register_and_wrap(self):
        manager = LLMIntegrationWrapperManager()
        manager.register(
            LLMIntegrationWrapper(
                name="prefix",
                wrap_fn=lambda d: f"Result: {d}",
            )
        )
        result = manager.wrap("prefix", "hello")
        assert result == "Result: hello"

    def test_unregister(self):
        manager = LLMIntegrationWrapperManager()
        manager.register(
            LLMIntegrationWrapper(
                name="w1",
                wrap_fn=lambda d: d,
            )
        )
        assert manager.unregister("w1") is True

    def test_list_wrappers(self):
        manager = LLMIntegrationWrapperManager()
        manager.register(
            LLMIntegrationWrapper(
                name="w1",
                wrap_fn=lambda d: d,
            )
        )
        manager.register(
            LLMIntegrationWrapper(
                name="w2",
                wrap_fn=lambda d: d,
            )
        )
        assert len(manager.list_wrappers()) == 2