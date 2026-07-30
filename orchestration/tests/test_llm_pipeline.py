import pytest
from orchestration.llm_pipeline import (
    LLMIntegrationPipeline,
    LLMIntegrationPipelineManager,
)


class TestLLMIntegrationPipelineManager:
    def test_create_pipeline(self):
        manager = LLMIntegrationPipelineManager()
        pipeline = manager.create_pipeline(
            "default",
            ["validate", "generate", "parse"],
        )
        assert pipeline.name == "default"
        assert len(pipeline.steps) == 3

    def test_get_pipeline(self):
        manager = LLMIntegrationPipelineManager()
        manager.create_pipeline(
            "default",
            ["validate", "generate"],
        )
        pipeline = manager.get_pipeline("default")
        assert pipeline is not None
        assert pipeline.name == "default"

    def test_delete_pipeline(self):
        manager = LLMIntegrationPipelineManager()
        manager.create_pipeline("default", ["step1"])
        assert manager.delete_pipeline("default") is True
        assert manager.get_pipeline("default") is None

    def test_add_remove_step(self):
        manager = LLMIntegrationPipelineManager()
        manager.create_pipeline("default", ["step1"])
        assert manager.add_step("default", "step2") is True
        assert manager.remove_step("default", "step1") is True

    def test_enable_disable(self):
        manager = LLMIntegrationPipelineManager()
        manager.create_pipeline("default", ["step1"])
        assert manager.disable_pipeline("default") is True
        assert manager.enable_pipeline("default") is True

    def test_list_pipelines(self):
        manager = LLMIntegrationPipelineManager()
        manager.create_pipeline("p1", ["step1"])
        manager.create_pipeline("p2", ["step2"])
        assert len(manager.list_pipelines()) == 2