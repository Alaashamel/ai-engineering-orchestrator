from orchestration.llm_profiler import (
    LLMIntegrationProfiler,
    LLMIntegrationProfilerManager,
)


class TestLLMIntegrationProfilerManager:
    def test_register_and_profile(self):
        manager = LLMIntegrationProfilerManager()
        manager.register(
            LLMIntegrationProfiler(
                name="perf",
                profile_fn=lambda d: {"latency": 100},
            )
        )
        result = manager.profile("perf", {"data": "test"})
        assert result["latency"] == 100

    def test_unregister(self):
        manager = LLMIntegrationProfilerManager()
        manager.register(
            LLMIntegrationProfiler(
                name="p1",
                profile_fn=lambda d: {},
            )
        )
        assert manager.unregister("p1") is True

    def test_list_profilers(self):
        manager = LLMIntegrationProfilerManager()
        manager.register(
            LLMIntegrationProfiler(
                name="p1",
                profile_fn=lambda d: {},
            )
        )
        manager.register(
            LLMIntegrationProfiler(
                name="p2",
                profile_fn=lambda d: {},
            )
        )
        assert len(manager.list_profilers()) == 2