import pytest
from orchestration.llm_normalizer import (
    LLMIntegrationNormalizer,
    LLMIntegrationNormalizerManager,
)


class TestLLMIntegrationNormalizerManager:
    def test_register_and_normalize(self):
        manager = LLMIntegrationNormalizerManager()
        manager.register(
            LLMIntegrationNormalizer(
                name="whitespace",
                normalize_fn=lambda d: str(d).strip(),
            )
        )
        result = manager.normalize("whitespace", "  hello  ")
        assert result == "hello"

    def test_unregister(self):
        manager = LLMIntegrationNormalizerManager()
        manager.register(
            LLMIntegrationNormalizer(
                name="norm1",
                normalize_fn=lambda d: d,
            )
        )
        assert manager.unregister("norm1") is True

    def test_list_normalizers(self):
        manager = LLMIntegrationNormalizerManager()
        manager.register(
            LLMIntegrationNormalizer(
                name="n1",
                normalize_fn=lambda d: d,
            )
        )
        manager.register(
            LLMIntegrationNormalizer(
                name="n2",
                normalize_fn=lambda d: d,
            )
        )
        assert len(manager.list_normalizers()) == 2