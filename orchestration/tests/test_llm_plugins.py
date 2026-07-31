from orchestration.llm_plugins import (
    LLMIntegrationPlugin,
    LLMIntegrationPluginManager,
)


class TestLLMIntegrationPluginManager:
    def test_register_and_get(self):
        manager = LLMIntegrationPluginManager()
        plugin = LLMIntegrationPlugin(
            name="cost_tracker",
            version="1.0",
        )
        manager.register(plugin)
        assert manager.get("cost_tracker") is not None

    def test_unregister(self):
        manager = LLMIntegrationPluginManager()
        plugin = LLMIntegrationPlugin(
            name="cost_tracker",
            version="1.0",
        )
        manager.register(plugin)
        assert manager.unregister("cost_tracker") is True
        assert manager.get("cost_tracker") is None

    def test_enable_disable(self):
        manager = LLMIntegrationPluginManager()
        plugin = LLMIntegrationPlugin(
            name="cost_tracker",
            version="1.0",
        )
        manager.register(plugin)
        assert manager.disable("cost_tracker") is True
        assert manager.get("cost_tracker").enabled is False
        assert manager.enable("cost_tracker") is True
        assert manager.get("cost_tracker").enabled is True

    def test_initialize_all(self):
        manager = LLMIntegrationPluginManager()
        plugin1 = LLMIntegrationPlugin(
            name="plugin1",
            version="1.0",
        )
        plugin2 = LLMIntegrationPlugin(
            name="plugin2",
            version="1.0",
        )
        manager.register(plugin1)
        manager.register(plugin2)
        results = manager.initialize_all()
        assert "plugin1" in results
        assert "plugin2" in results

    def test_list_plugins(self):
        manager = LLMIntegrationPluginManager()
        manager.register(
            LLMIntegrationPlugin(name="p1", version="1.0")
        )
        manager.register(
            LLMIntegrationPlugin(name="p2", version="1.0")
        )
        assert len(manager.list_plugins()) == 2