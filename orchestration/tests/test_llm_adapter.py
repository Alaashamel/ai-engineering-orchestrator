from orchestration.llm_adapter import (
    LLMIntegrationAdapter,
    LLMIntegrationAdapterManager,
)


class TestLLMIntegrationAdapterManager:
    def test_register_and_get(self):
        manager = LLMIntegrationAdapterManager()
        adapter = LLMIntegrationAdapter(
            name="openai",
            provider="openai",
        )
        manager.register(adapter)
        assert manager.get("openai") is not None

    def test_unregister(self):
        manager = LLMIntegrationAdapterManager()
        adapter = LLMIntegrationAdapter(
            name="openai",
            provider="openai",
        )
        manager.register(adapter)
        assert manager.unregister("openai") is True
        assert manager.get("openai") is None

    def test_enable_disable(self):
        manager = LLMIntegrationAdapterManager()
        adapter = LLMIntegrationAdapter(
            name="openai",
            provider="openai",
        )
        manager.register(adapter)
        assert manager.disable("openai") is True
        assert manager.enable("openai") is True

    def test_list_adapters(self):
        manager = LLMIntegrationAdapterManager()
        manager.register(
            LLMIntegrationAdapter(
                name="openai", provider="openai"
            )
        )
        manager.register(
            LLMIntegrationAdapter(
                name="anthropic", provider="anthropic"
            )
        )
        assert len(manager.list_adapters()) == 2

    def test_get_enabled(self):
        manager = LLMIntegrationAdapterManager()
        manager.register(
            LLMIntegrationAdapter(
                name="openai", provider="openai"
            )
        )
        manager.register(
            LLMIntegrationAdapter(
                name="anthropic", provider="anthropic"
            )
        )
        manager.disable("anthropic")
        enabled = manager.get_enabled()
        assert len(enabled) == 1
        assert enabled[0].name == "openai"