import pytest
from orchestration.llm_debugger import (
    LLMIntegrationDebugger,
    LLMIntegrationDebuggerManager,
)


class TestLLMIntegrationDebuggerManager:
    def test_register_and_debug(self):
        manager = LLMIntegrationDebuggerManager()
        manager.register(
            LLMIntegrationDebugger(
                name="trace",
                debug_fn=lambda d: {"traced": True},
            )
        )
        result = manager.debug("trace", {"data": "test"})
        assert result["traced"] is True

    def test_unregister(self):
        manager = LLMIntegrationDebuggerManager()
        manager.register(
            LLMIntegrationDebugger(
                name="d1",
                debug_fn=lambda d: {},
            )
        )
        assert manager.unregister("d1") is True

    def test_list_debuggers(self):
        manager = LLMIntegrationDebuggerManager()
        manager.register(
            LLMIntegrationDebugger(
                name="d1",
                debug_fn=lambda d: {},
            )
        )
        manager.register(
            LLMIntegrationDebugger(
                name="d2",
                debug_fn=lambda d: {},
            )
        )
        assert len(manager.list_debuggers()) == 2