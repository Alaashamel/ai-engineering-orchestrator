from orchestration.llm_filter import (
    LLMIntegrationFilter,
    LLMIntegrationFilterManager,
)


class TestLLMIntegrationFilterManager:
    def test_register_and_apply(self):
        manager = LLMIntegrationFilterManager()
        manager.register(
            LLMIntegrationFilter(
                name="non_empty",
                filter_fn=lambda d: d if d else None,
            )
        )
        result = manager.apply("non_empty", "hello")
        assert result == "hello"

    def test_unregister(self):
        manager = LLMIntegrationFilterManager()
        manager.register(
            LLMIntegrationFilter(
                name="filter1",
                filter_fn=lambda d: d,
            )
        )
        assert manager.unregister("filter1") is True

    def test_list_filters(self):
        manager = LLMIntegrationFilterManager()
        manager.register(
            LLMIntegrationFilter(
                name="f1",
                filter_fn=lambda d: d,
            )
        )
        manager.register(
            LLMIntegrationFilter(
                name="f2",
                filter_fn=lambda d: d,
            )
        )
        assert len(manager.list_filters()) == 2