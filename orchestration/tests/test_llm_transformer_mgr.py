from orchestration.llm_transformer_mgr import (
    LLMIntegrationTransformer,
    LLMIntegrationTransformerManager,
)


class TestLLMIntegrationTransformerManager:
    def test_register_and_transform(self):
        manager = LLMIntegrationTransformerManager()
        manager.register(
            LLMIntegrationTransformer(
                name="upper",
                transform_fn=lambda d: str(d).upper(),
            )
        )
        result = manager.transform("upper", "hello")
        assert result == "HELLO"

    def test_unregister(self):
        manager = LLMIntegrationTransformerManager()
        manager.register(
            LLMIntegrationTransformer(
                name="t1",
                transform_fn=lambda d: d,
            )
        )
        assert manager.unregister("t1") is True

    def test_list_transformers(self):
        manager = LLMIntegrationTransformerManager()
        manager.register(
            LLMIntegrationTransformer(
                name="t1",
                transform_fn=lambda d: d,
            )
        )
        manager.register(
            LLMIntegrationTransformer(
                name="t2",
                transform_fn=lambda d: d,
            )
        )
        assert len(manager.list_transformers()) == 2