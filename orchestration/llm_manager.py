from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orchestration.llm_config import LLMProviderConfig
from orchestration.llm_cost import LLMCostTracker, LLMCostConfig
from orchestration.llm_retry import LLMRetryHandler
from orchestration.llm_streaming import LLMStreamingHandler
from orchestration.llm_parser import LLMOutputParser
from orchestration.llm_benchmark import LLMBenchmarkSuite
from orchestration.llm_errors import LLMError, classify_llm_error
from orchestration.llm_registry import LLMProviderRegistry
from orchestration.llm_secrets import LLMSecretManager
from orchestration.llm_metrics import LLMMetricsCollector


class LLMIntegrationManager:
    def __init__(self, config: LLMProviderConfig) -> None:
        self.config = config
        self.cost_tracker = LLMCostTracker(LLMCostConfig())
        self.retry_handler = LLMRetryHandler(config)
        self.streaming_handler = LLMStreamingHandler()
        self.output_parser = LLMOutputParser()
        self.benchmark_suite = LLMBenchmarkSuite()
        self.registry = LLMProviderRegistry()
        self.secret_manager = LLMSecretManager()
        self.metrics = LLMMetricsCollector()

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[Any],
    ) -> Any:
        start = self._now_ms()
        try:
            result = await self.retry_handler.execute_with_retry(
                self._call_llm,
                system_prompt,
                user_prompt,
                response_model,
            )
            latency = self._now_ms() - start
            self.metrics.record(
                model=self.config.model,
                operation="generate",
                latency_ms=latency,
                tokens_used=0,
                success=True,
            )
            return result
        except Exception as exc:
            latency = self._now_ms() - start
            self.metrics.record(
                model=self.config.model,
                operation="generate",
                latency_ms=latency,
                tokens_used=0,
                success=False,
                error=str(exc),
            )
            raise classify_llm_error(exc)

    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[Any],
    ) -> Any:
        provider = self.registry.get_provider()
        return await provider.generate_structured(
            system_prompt, user_prompt, response_model
        )

    def run_evaluation(
        self,
        eval_config: Any,
    ) -> dict[str, Any]:
        return self.benchmark_suite.get_summary()

    def get_cost_report(self) -> dict[str, Any]:
        return self.cost_tracker.get_summary()

    def get_metrics_report(self) -> dict[str, Any]:
        return self.metrics.get_summary()

    def switch_provider(self, name: str) -> bool:
        return self.registry.switch_provider(
            self.registry._default_provider, name
        )

    def validate_config(self) -> dict[str, Any]:
        errors: list[str] = []
        if not self.config.api_key and not self.config.mock_mode:
            errors.append("API key is required for non-mock mode")
        if self.config.temperature < 0 or self.config.temperature > 2:
            errors.append("Temperature must be between 0 and 2")
        if self.config.max_tokens < 1:
            errors.append("Max tokens must be positive")
        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def _now_ms() -> float:
        return time.time() * 1000


import time