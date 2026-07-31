from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LLMQuotaError(Exception):
    """Raised when the API key has insufficient quota."""


class LLMProvider:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o",
        base_url: str | None = None,
        timeout: int = 30,
        max_retries: int = 3,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        auto_fallback: bool = True,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.auto_fallback = auto_fallback
        self._mock_mode = api_key is None
        self._quota_exhausted = False

    @property
    def mock_mode(self) -> bool:
        return self._mock_mode or self._quota_exhausted

    @property
    def quota_exhausted(self) -> bool:
        return self._quota_exhausted

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
    ) -> BaseModel:
        if self.mock_mode:
            return self._mock_response(response_model)
        try:
            return await self._real_call(
                system_prompt, user_prompt, response_model
            )
        except LLMQuotaError:
            if self.auto_fallback:
                logger.warning(
                    "LLM quota exhausted — falling back to mock. "
                    "Add billing to your API key for real responses."
                )
                self._quota_exhausted = True
                return self._mock_response(response_model)
            raise

    async def _real_call(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
    ) -> BaseModel:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        try:
            completion = await client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=response_model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
            )
        except Exception as exc:
            error_msg = str(exc)
            if "insufficient_quota" in error_msg or "quota" in error_msg.lower():
                raise LLMQuotaError(error_msg) from exc
            raise
        raw = completion.choices[0].message.content
        if not raw:
            raise ValueError("Empty LLM response")
        return response_model.model_validate_json(raw)

    def _mock_response(self, response_model: type[BaseModel]) -> BaseModel:
        schema = response_model.model_json_schema()
        properties = schema.get("properties", {})
        result: dict[str, Any] = {}
        for field_name, field_info in properties.items():
            result[field_name] = self._mock_field(field_name, field_info)
        return response_model.model_validate(result)

    def _mock_field(self, name: str, info: dict[str, Any]) -> Any:
        field_type = info.get("type", "string")
        if field_type == "string":
            if "enum" in info:
                return info["enum"][0]
            if "name" in name.lower():
                return "Sample Project"
            if "status" in name.lower():
                enums = info.get("enum", ["pending"])
                return enums[0]
            return f"mock_{name}"
        if field_type == "integer":
            return 1
        if field_type == "number":
            return 1.0
        if field_type == "boolean":
            return True
        if field_type == "array":
            return []
        if field_type == "object":
            return {}
        return None

    async def stream_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
    ) -> Any:
        if self.mock_mode:
            result = self._mock_response(response_model)
            yield result.model_dump_json()
            return
        yield await self.generate_structured(
            system_prompt, user_prompt, response_model
        ).model_dump_json()

    def get_model_info(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "provider": "openai",
            "mock_mode": self.mock_mode,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }