from __future__ import annotations

from typing import Any, Optional


class LLMProviderFactory:
    @staticmethod
    def create_openai_provider(
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        **kwargs: Any,
    ) -> Any:
        from orchestration.llm_provider import LLMProvider
        return LLMProvider(
            api_key=api_key,
            model=model,
            **kwargs,
        )

    @staticmethod
    def create_mock_provider(
        model: str = "gpt-4o",
        **kwargs: Any,
    ) -> Any:
        from orchestration.llm_provider import LLMProvider
        return LLMProvider(
            api_key=None,
            model=model,
            **kwargs,
        )

    @staticmethod
    def create_provider(
        provider_name: str,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        **kwargs: Any,
    ) -> Any:
        if provider_name == "openai":
            return LLMProviderFactory.create_openai_provider(
                api_key=api_key,
                model=model,
                **kwargs,
            )
        if provider_name == "mock":
            return LLMProviderFactory.create_mock_provider(
                model=model,
                **kwargs,
            )
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Supported: openai, mock"
        )

    @staticmethod
    def create_from_env(
        model: str = "gpt-4o",
    ) -> Any:
        import os

        api_key = os.getenv("LLM_API_KEY")
        provider_name = os.getenv("LLM_PROVIDER", "openai")
        return LLMProviderFactory.create_provider(
            provider_name,
            api_key=api_key,
            model=model,
        )