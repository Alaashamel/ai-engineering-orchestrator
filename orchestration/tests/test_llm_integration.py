import pytest
from orchestration.llm_config import LLMProviderConfig, LLMCostConfig, LLMEvaluationConfig, LLMStreamingConfig
from orchestration.llm_retry import LLMRetryHandler
from orchestration.llm_cost import LLMCostTracker, TokenUsage, LLMCostRecord
from orchestration.llm_eval import LLEvalHarness, EvalResult
from orchestration.llm_streaming import LLMStreamingHandler
from orchestration.llm_parser import LLMOutputParser
from orchestration.llm_benchmark import LLMBenchmarkSuite, LLMBenchmarkResult
from orchestration.llm_errors import (
    LLMError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMValidationError,
    LLMProviderError,
    classify_llm_error,
)
from orchestration.llm_registry import LLMProviderRegistry
from orchestration.llm_secrets import LLMSecretManager
from orchestration.llm_metrics import LLMMetricsCollector


class TestLLMProviderConfig:
    def test_default_config(self):
        config = LLMProviderConfig()
        assert config.provider == "openai"
        assert config.model == "gpt-4o"
        assert config.max_retries == 3
        assert config.temperature == 0.7

    def test_custom_config(self):
        config = LLMProviderConfig(
            provider="anthropic",
            model="claude-3",
            max_retries=5,
            temperature=0.3,
        )
        assert config.provider == "anthropic"
        assert config.model == "claude-3"
        assert config.max_retries == 5
        assert config.temperature == 0.3


class TestLLMRetryHandler:
    def test_retry_handler_initialization(self):
        config = LLMProviderConfig(max_retries=3)
        handler = LLMRetryHandler(config)
        assert handler.max_retries == 3
        assert handler.base_delay == 1.0

    def test_is_retryable(self):
        assert LLMRetryHandler.is_retryable(Exception("timeout")) is True
        assert LLMRetryHandler.is_retryable(Exception("rate limit")) is True
        assert LLMRetryHandler.is_retryable(Exception("429")) is True
        assert LLMRetryHandler.is_retryable(Exception("503")) is True
        assert LLMRetryHandler.is_retryable(Exception("connection error")) is True
        assert LLMRetryHandler.is_retryable(Exception("validation error")) is False


class TestLLMCostTracker:
    def test_cost_tracker_initialization(self):
        config = LLMCostConfig()
        tracker = LLMCostTracker(config)
        assert tracker.total_cost == 0.0
        assert tracker.total_tokens == 0

    def test_record_cost(self):
        config = LLMCostConfig(cost_per_1k_tokens=0.01)
        tracker = LLMCostTracker(config)
        usage = TokenUsage(prompt_tokens=100, completion_tokens=200, total_tokens=300)
        record = tracker.record("gpt-4o", usage)
        assert record.cost == 0.003
        assert tracker.total_cost == 0.003
        assert tracker.total_tokens == 300

    def test_get_summary(self):
        config = LLMCostConfig()
        tracker = LLMCostTracker(config)
        usage = TokenUsage(prompt_tokens=100, completion_tokens=200, total_tokens=300)
        tracker.record("gpt-4o", usage)
        summary = tracker.get_summary()
        assert summary["total_tokens"] == 300
        assert summary["total_requests"] == 1


class TestLLEvalHarness:
    def test_eval_harness_initialization(self):
        config = EvalSuiteConfig(name="test_suite")
        harness = LLEvalHarness(config)
        assert harness.config.name == "test_suite"

    def test_add_test_case(self):
        from pydantic import BaseModel

        class DummyModel(BaseModel):
            name: str

        config = EvalSuiteConfig(name="test_suite")
        harness = LLEvalHarness(config)
        harness.add_test_case(
            name="test_1",
            prompt="Say hello",
            expected_output={"name": "hello"},
            response_model=DummyModel,
        )
        assert len(harness.config.test_cases) == 1

    def test_get_summary_empty(self):
        config = EvalSuiteConfig(name="test_suite")
        harness = LLEvalHarness(config)
        summary = harness.get_summary()
        assert summary["total_tests"] == 0
        assert summary["pass_rate"] == 0.0


class TestLLMOutputParser:
    def test_extract_json(self):
        text = 'Here is the result: {"key": "value"}'
        result = LLMOutputParser.extract_json(text)
        assert result == '{"key": "value"}'

    def test_extract_code_block(self):
        text = "```json\n{\"key\": \"value\"}\n```"
        result = LLMOutputParser.extract_code_block(text)
        assert result == '{"key": "value"}'

    def test_sanitize_output(self):
        text = "```json\n{\"key\": \"value\"}\n```"
        result = LLMOutputParser.sanitize_output(text)
        assert result == '{"key": "value"}'


class TestLLMBenchmarkSuite:
    def test_benchmark_suite_initialization(self):
        suite = LLMBenchmarkSuite()
        assert len(suite.results) == 0

    def test_add_result(self):
        suite = LLMBenchmarkSuite()
        result = LLMBenchmarkResult(
            model="gpt-4o",
            test_name="test_1",
            latency_ms=100.0,
            tokens_used=500,
            cost=0.005,
            passed=True,
            score=1.0,
        )
        suite.add_result(result)
        assert len(suite.results) == 1

    def test_get_summary(self):
        suite = LLMBenchmarkSuite()
        result = LLMBenchmarkResult(
            model="gpt-4o",
            test_name="test_1",
            latency_ms=100.0,
            tokens_used=500,
            cost=0.005,
            passed=True,
            score=1.0,
        )
        suite.add_result(result)
        summary = suite.get_summary()
        assert summary["total"] == 1
        assert summary["passed"] == 1
        assert summary["pass_rate"] == 1.0


class TestLLMProviderRegistry:
    def test_registry_initialization(self):
        registry = LLMProviderRegistry()
        assert registry.list_providers() == []

    def test_register_and_get(self):
        registry = LLMProviderRegistry()
        mock_provider = object()
        registry.register("mock", mock_provider)
        assert registry.get_provider("mock") is mock_provider

    def test_switch_provider(self):
        registry = LLMProviderRegistry()
        provider_a = object()
        provider_b = object()
        registry.register("a", provider_a)
        registry.register("b", provider_b)
        result = registry.switch_provider("a", "b")
        assert result is True


class TestLLMSecretManager:
    def test_store_and_get_secret(self, tmp_path):
        manager = LLMSecretManager(secrets_dir=str(tmp_path))
        manager.store_secret("api_key", "secret123")
        value = manager.get_secret("api_key")
        assert value == "secret123"

    def test_delete_secret(self, tmp_path):
        manager = LLMSecretManager(secrets_dir=str(tmp_path))
        manager.store_secret("api_key", "secret123")
        result = manager.delete_secret("api_key")
        assert result is True
        assert manager.get_secret("api_key") is None


class TestLLMMetricsCollector:
    def test_record_and_stats(self):
        collector = LLMMetricsCollector()
        collector.record("gpt-4o", "generate", 100.0, 500, True)
        collector.record("gpt-4o", "generate", 200.0, 1000, True)
        stats = collector.get_model_stats("gpt-4o")
        assert stats["requests"] == 2
        assert stats["successes"] == 2
        assert stats["avg_latency_ms"] == 150.0

    def test_get_summary(self):
        collector = LLMMetricsCollector()
        collector.record("gpt-4o", "generate", 100.0, 500, True)
        collector.record("gpt-3.5", "generate", 200.0, 1000, False, "error")
        summary = collector.get_summary()
        assert summary["total_requests"] == 2
        assert summary["total_successes"] == 1


class TestLLMErrorClassification:
    def test_timeout_error(self):
        error = Exception("request timed out")
        classified = classify_llm_error(error)
        assert isinstance(classified, LLMTimeoutError)

    def test_rate_limit_error(self):
        error = Exception("rate limit exceeded 429")
        classified = classify_llm_error(error)
        assert isinstance(classified, LLMRateLimitError)

    def test_validation_error(self):
        error = Exception("validation failed schema mismatch")
        classified = classify_llm_error(error)
        assert isinstance(classified, LLMValidationError)

    def test_provider_error(self):
        error = Exception("unknown provider error")
        classified = classify_llm_error(error)
        assert isinstance(classified, LLMProviderError)