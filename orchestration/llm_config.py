from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LLMProviderConfig:
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: str | None = None
    base_url: str | None = None
    max_retries: int = 3
    timeout: int = 30
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


@dataclass
class LLMCostConfig:
    enabled: bool = True
    cost_per_1k_tokens: float = 0.005
    alert_threshold: float = 10.0
    log_costs: bool = True


@dataclass
class LLMEvaluationConfig:
    enabled: bool = True
    test_suite: str = "regression"
    baseline_model: str = "gpt-4o"
    comparison_model: str | None = None
    tolerance: float = 0.95
    output_dir: str = "eval_results"


@dataclass
class LLMStreamingConfig:
    enabled: bool = True
    chunk_size: int = 1024
    buffer_size: int = 4096
    timeout: int = 60