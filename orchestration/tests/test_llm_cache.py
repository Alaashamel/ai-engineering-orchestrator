import pytest
from orchestration.llm_cache import LLMResultCache
from orchestration.llm_validator import LLMConfigValidator


class TestLLMResultCache:
    def test_cache_set_and_get(self, tmp_path):
        cache = LLMResultCache(cache_dir=str(tmp_path))
        cache.set("hello", "gpt-4o", {"result": "world"})
        result = cache.get("hello", "gpt-4o")
        assert result == {"result": "world"}

    def test_cache_miss(self, tmp_path):
        cache = LLMResultCache(cache_dir=str(tmp_path))
        result = cache.get("nonexistent", "gpt-4o")
        assert result is None

    def test_cache_invalidate(self, tmp_path):
        cache = LLMResultCache(cache_dir=str(tmp_path))
        cache.set("hello", "gpt-4o", {"result": "world"})
        assert cache.invalidate("hello", "gpt-4o") is True
        assert cache.get("hello", "gpt-4o") is None

    def test_cache_clear(self, tmp_path):
        cache = LLMResultCache(cache_dir=str(tmp_path))
        cache.set("hello", "gpt-4o", {"result": "world"})
        cache.set("foo", "gpt-4o", {"result": "bar"})
        assert cache.size() == 2
        cache.clear()
        assert cache.size() == 0


class TestLLMConfigValidator:
    def test_valid_config(self):
        class MockConfig:
            provider = "openai"
            model = "gpt-4o"
            temperature = 0.7
            max_tokens = 4096
            timeout = 30

        result = LLMConfigValidator.validate_provider_config(MockConfig())
        assert result["valid"] is True
        assert result["errors"] == []

    def test_invalid_temperature(self):
        class MockConfig:
            provider = "openai"
            model = "gpt-4o"
            temperature = 2.5
            max_tokens = 4096

        result = LLMConfigValidator.validate_provider_config(MockConfig())
        assert result["valid"] is False
        assert any("Temperature" in e for e in result["errors"])

    def test_invalid_api_key(self):
        result = LLMConfigValidator.validate_api_key(None, "openai")
        assert result["valid"] is False
        assert "API key is required" in result["error"]

    def test_valid_api_key(self):
        result = LLMConfigValidator.validate_api_key("sk-test123", "openai")
        assert result["valid"] is True

    def test_invalid_api_key_format(self):
        result = LLMConfigValidator.validate_api_key("invalid-key", "openai")
        assert result["valid"] is False
        assert "must start with" in result["error"]