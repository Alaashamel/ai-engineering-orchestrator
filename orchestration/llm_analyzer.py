from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationAnalyzer(BaseModel):
    name: str
    analyze_fn: Any = None


class LLMIntegrationAnalyzerManager:
    def __init__(self) -> None:
        self._analyzers: dict[str, LLMIntegrationAnalyzer] = {}

    def register(self, analyzer: LLMIntegrationAnalyzer) -> None:
        self._analyzers[analyzer.name] = analyzer

    def unregister(self, name: str) -> bool:
        if name in self._analyzers:
            del self._analyzers[name]
            return True
        return False

    def get(self, name: str) -> LLMIntegrationAnalyzer | None:
        return self._analyzers.get(name)

    def analyze(
        self, name: str, data: Any
    ) -> dict[str, Any]:
        analyzer = self._analyzers.get(name)
        if analyzer is None:
            raise ValueError(
                f"Analyzer '{name}' not found"
            )
        if analyzer.analyze_fn is not None:
            return analyzer.analyze_fn(data)
        return {"analyzed": True}

    def list_analyzers(self) -> list[str]:
        return list(self._analyzers.keys())