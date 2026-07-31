from __future__ import annotations

from typing import Any

from pydantic import BaseModel


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
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._mock_mode = api_key is None

    @property
    def mock_mode(self) -> bool:
        return self._mock_mode

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
    ) -> BaseModel:
        if self.mock_mode:
            return self._mock_response(response_model)
        return await self._real_call(
            system_prompt, user_prompt, response_model
        )

    async def _real_call(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
    ) -> BaseModel:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
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