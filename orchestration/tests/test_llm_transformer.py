from orchestration.llm_transformer import (
    LLMIntegrationTransformerManager,
)


class TestLLMIntegrationTransformerManager:
    def test_add_transformer(self):
        manager = LLMIntegrationTransformerManager()
        transformer = manager.add_transformer(
            "uppercase",
            lambda data: data.upper(),
            order=0,
        )
        assert transformer.name == "uppercase"

    def test_remove_transformer(self):
        manager = LLMIntegrationTransformerManager()
        manager.add_transformer("upper", lambda d: d)
        assert manager.remove_transformer("upper") is True
        assert manager.remove_transformer("upper") is False

    def test_transform(self):
        manager = LLMIntegrationTransformerManager()
        manager.add_transformer(
            "upper",
            lambda data: data.upper(),
            order=0,
        )
        result = manager.transform("hello")
        assert result == "HELLO"

    def test_transform_order(self):
        manager = LLMIntegrationTransformerManager()
        manager.add_transformer(
            "strip",
            lambda data: data.strip(),
            order=1,
        )
        manager.add_transformer(
            "upper",
            lambda data: data.upper(),
            order=0,
        )
        result = manager.transform("  hello  ")
        assert result == "HELLO"

    def test_list_transformers(self):
        manager = LLMIntegrationTransformerManager()
        manager.add_transformer("t1", lambda d: d)
        manager.add_transformer("t2", lambda d: d)
        assert len(manager.list_transformers()) == 2