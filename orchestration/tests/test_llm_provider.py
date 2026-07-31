import pytest
from pydantic import BaseModel

from orchestration.llm_provider import LLMProvider


class TestResponse(BaseModel):
    name: str
    status: str
    count: int


class TestLLMProvider:
    def test_default_initialization(self):
        provider = LLMProvider()
        assert provider.model == "gpt-4o"
        assert provider.mock_mode is True
        assert provider.temperature == 0.7

    def test_custom_initialization(self):
        provider = LLMProvider(
            api_key="sk-test",
            model="gpt-4",
            temperature=0.3,
            max_tokens=2048,
        )
        assert provider.api_key == "sk-test"
        assert provider.model == "gpt-4"
        assert provider.mock_mode is False

    def test_get_model_info(self):
        provider = LLMProvider()
        info = provider.get_model_info()
        assert info["model"] == "gpt-4o"
        assert info["mock_mode"] is True
        assert info["provider"] == "openai"

    @pytest.mark.asyncio
    async def test_mock_response(self):
        provider = LLMProvider()
        result = await provider.generate_structured(
            system_prompt="You are a helper.",
            user_prompt="Generate a test response.",
            response_model=TestResponse,
        )
        assert isinstance(result, TestResponse)
        assert result.name == "Sample Project"
        assert result.status == "pending"
        assert result.count == 1

    @pytest.mark.asyncio
    async def test_stream_structured_mock(self):
        provider = LLMProvider()
        chunks = []
        async for chunk in provider.stream_structured(
            system_prompt="You are a helper.",
            user_prompt="Generate a test response.",
            response_model=TestResponse,
        ):
            chunks.append(chunk)
        assert len(chunks) > 0
        assert "Sample Project" in chunks[0]