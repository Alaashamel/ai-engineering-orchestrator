from orchestration.llm_monitor import (
    LLMIntegrationMonitor,
    LLMIntegrationMonitorManager,
)


class TestLLMIntegrationMonitorManager:
    def test_register_and_monitor(self):
        manager = LLMIntegrationMonitorManager()
        manager.register(
            LLMIntegrationMonitor(
                name="health",
                monitor_fn=lambda d: {"healthy": True},
            )
        )
        result = manager.monitor("health", {"data": "test"})
        assert result["healthy"] is True

    def test_unregister(self):
        manager = LLMIntegrationMonitorManager()
        manager.register(
            LLMIntegrationMonitor(
                name="m1",
                monitor_fn=lambda d: {},
            )
        )
        assert manager.unregister("m1") is True

    def test_list_monitors(self):
        manager = LLMIntegrationMonitorManager()
        manager.register(
            LLMIntegrationMonitor(
                name="m1",
                monitor_fn=lambda d: {},
            )
        )
        manager.register(
            LLMIntegrationMonitor(
                name="m2",
                monitor_fn=lambda d: {},
            )
        )
        assert len(manager.list_monitors()) == 2