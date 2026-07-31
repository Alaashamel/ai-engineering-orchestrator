from __future__ import annotations

from pydantic import BaseModel


class LLMIntegrationPipeline(BaseModel):
    name: str
    steps: list[str] = []
    enabled: bool = True


class LLMIntegrationPipelineManager:
    def __init__(self) -> None:
        self._pipelines: dict[str, LLMIntegrationPipeline] = {}

    def create_pipeline(
        self, name: str, steps: list[str]
    ) -> LLMIntegrationPipeline:
        pipeline = LLMIntegrationPipeline(
            name=name, steps=steps
        )
        self._pipelines[name] = pipeline
        return pipeline

    def get_pipeline(self, name: str) -> LLMIntegrationPipeline | None:
        return self._pipelines.get(name)

    def delete_pipeline(self, name: str) -> bool:
        if name in self._pipelines:
            del self._pipelines[name]
            return True
        return False

    def add_step(self, pipeline_name: str, step: str) -> bool:
        pipeline = self._pipelines.get(pipeline_name)
        if pipeline:
            pipeline.steps.append(step)
            return True
        return False

    def remove_step(self, pipeline_name: str, step: str) -> bool:
        pipeline = self._pipelines.get(pipeline_name)
        if pipeline and step in pipeline.steps:
            pipeline.steps.remove(step)
            return True
        return False

    def enable_pipeline(self, name: str) -> bool:
        pipeline = self._pipelines.get(name)
        if pipeline:
            pipeline.enabled = True
            return True
        return False

    def disable_pipeline(self, name: str) -> bool:
        pipeline = self._pipelines.get(name)
        if pipeline:
            pipeline.enabled = False
            return True
        return False

    def list_pipelines(self) -> list[str]:
        return list(self._pipelines.keys())