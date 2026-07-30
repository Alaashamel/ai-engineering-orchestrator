import pytest
from orchestration.llm_analyzer import (
    LLMIntegrationAnalyzer,
    LLMIntegrationAnalyzerManager,
)


class TestLLMIntegrationAnalyzerManager:
    def test_register_and_analyze(self):
        manager = LLMIntegrationAnalyzerManager()
        manager.register(
            LLMIntegrationAnalyzer(
                name="sentiment",
                analyze_fn=lambda d: {"sentiment": "positive"},
            )
        )
        result = manager.analyze("sentiment", {"text": "hello"})
        assert result["sentiment"] == "positive"

    def test_unregister(self):
        manager = LLMIntegrationAnalyzerManager()
        manager.register(
            LLMIntegrationAnalyzer(
                name="a1",
                analyze_fn=lambda d: {},
            )
        )
        assert manager.unregister("a1") is True

    def test_list_analyzers(self):
        manager = LLMIntegrationAnalyzerManager()
        manager.register(
            LLMIntegrationAnalyzer(
                name="a1",
                analyze_fn=lambda d: {},
            )
        )
        manager.register(
            LLMIntegrationAnalyzer(
                name="a2",
                analyze_fn=lambda d: {},
            )
        )
        assert len(manager.list_analyzers()) == 2