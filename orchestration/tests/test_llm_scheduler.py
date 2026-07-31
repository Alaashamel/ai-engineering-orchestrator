from orchestration.llm_scheduler import (
    LLMIntegrationScheduler,
    LLMIntegrationSchedulerManager,
)


class TestLLMIntegrationSchedulerManager:
    def test_register_and_schedule(self):
        manager = LLMIntegrationSchedulerManager()
        manager.register(
            LLMIntegrationScheduler(
                name="cron",
                schedule_fn=lambda d: {"scheduled": True},
            )
        )
        result = manager.schedule("cron", {"task": "run"})
        assert result["scheduled"] is True

    def test_unregister(self):
        manager = LLMIntegrationSchedulerManager()
        manager.register(
            LLMIntegrationScheduler(
                name="s1",
                schedule_fn=lambda d: {},
            )
        )
        assert manager.unregister("s1") is True

    def test_list_schedulers(self):
        manager = LLMIntegrationSchedulerManager()
        manager.register(
            LLMIntegrationScheduler(
                name="s1",
                schedule_fn=lambda d: {},
            )
        )
        manager.register(
            LLMIntegrationScheduler(
                name="s2",
                schedule_fn=lambda d: {},
            )
        )
        assert len(manager.list_schedulers()) == 2