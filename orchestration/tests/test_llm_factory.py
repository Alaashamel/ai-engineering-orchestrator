import pytest
from orchestration.llm_factory import LLMProviderFactory


class TestLLMProviderFactory:
    def test_create_mock_provider(self):
        provider = LLMProviderFactory.create_mock_provider()
        assert provider.mock_mode is True
        assert provider.model == "gpt-4o"

    def test_create_openai_provider_with_key(self):
        provider = LLMProviderFactory.create_openai_provider(
            api_key="sk-test123",
        )
        assert provider.mock_mode is False
        assert provider.api_key == "sk-test123"

    def test_create_provider_unknown(self):
        with pytest.raises(ValueError, match="Unknown provider"):
            LLMProviderFactory.create_provider("unknown")

    def test_create_from_env_without_key(self):
        import os
        os.environ.pop("LLM_API_KEY", None)
        provider = LLMProviderFactory.create_from_env()
        assert provider.mock_mode is True

    def test_create_from_env_with_key(self):
        import os
        os.environ["LLM_API_KEY"] = "sk-test123"
        provider = LLMProviderFactory.create_from_env()
        assert provider.mock_mode is False
        os.environ.pop("LLM_API_KEY", None)