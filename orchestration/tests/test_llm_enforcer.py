import pytest
from orchestration.llm_enforcer import (
    LLMIntegrationEnforcer,
    LLMIntegrationEnforcerManager,
)


class TestLLMIntegrationEnforcerManager:
    def test_register_and_enforce(self):
        manager = LLMIntegrationEnforcerManager()
        manager.register(
            LLMIntegrationEnforcer(
                name="max_length",
                enforce_fn=lambda d: len(str(d)) <= 1000,
            )
        )
        result = manager.enforce("max_length", "hello")
        assert result is True

    def test_unregister(self):
        manager = LLMIntegrationEnforcerManager()
        manager.register(
            LLMIntegrationEnforcer(
                name="enforce1",
                enforce_fn=lambda d: True,
            )
        )
        assert manager.unregister("enforce1") is True

    def test_list_enforcers(self):
        manager = LLMIntegrationEnforcerManager()
        manager.register(
            LLMIntegrationEnforcer(
                name="e1",
                enforce_fn=lambda d: True,
            )
        )
        manager.register(
            LLMIntegrationEnforcer(
                name="e2",
                enforce_fn=lambda d: True,
            )
        )
        assert len(manager.list_enforcers()) == 2