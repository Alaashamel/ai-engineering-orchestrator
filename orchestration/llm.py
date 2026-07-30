from __future__ import annotations

import os
from typing import TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def _first_json_block(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON block found in response")
    raw = text[start : end + 1]
    return raw.replace("\n", " ").replace("\\n", " ")


class LLMProvider:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        self.mock_mode = not bool(self.api_key)

    async def generate_structured(
        self, system_prompt: str, user_prompt: str, response_model: type[T]
    ) -> T:
        if self.mock_mode:
            return self._mock_response(system_prompt, user_prompt, response_model)
        return await self._real_call(system_prompt, user_prompt, response_model)

    async def _real_call(self, system_prompt: str, user_prompt: str, response_model: type[T]) -> T:
        completion = await self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=response_model,
        )
        raw = completion.choices[0].message.content
        if not raw:
            raise ValueError("Empty LLM response")
        try:
            return response_model.model_validate_json(raw)
        except Exception:
            cleaned = _first_json_block(raw)
            return response_model.model_validate_json(cleaned)

    def _mock_response(self, system_prompt: str, user_prompt: str, response_model: type[T]) -> T:
        return response_model.model_validate(self._build_mock(response_model))

    def _build_mock(self, model_class: type[BaseModel]) -> dict:
        schema = model_class.model_json_schema()
        defs = schema.get("$defs", {})
        properties = schema.get("properties", {})
        result: dict = {}

        for field_name, field_info in properties.items():
            result[field_name] = self._mock_value(field_name, field_info, defs)

        return result

    def _mock_value(self, name: str, info: dict, defs: dict) -> object:
        if "$ref" in info:
            ref_key = info["$ref"].split("/")[-1]
            ref_schema = defs.get(ref_key, {})
            return self._mock_object(ref_key, ref_schema, defs)

        field_type = info.get("type", "string")

        if field_type == "string":
            if "enum" in info:
                return info["enum"][0]
            if "title" in name.lower() or "name" in name.lower():
                return "Sample Project"
            if "description" in name.lower():
                return "A sample project description for demonstration."
            if "vision" in name.lower():
                return "Build a scalable platform that solves user needs."
            if "reasoning" in name.lower():
                return "Standard engineering best practice."
            if "status" in name.lower() or "priority" in name.lower():
                enums = info.get("enum", ["pending"])
                return enums[0]
            if "risk" in name.lower():
                return "low"
            if "id" in name.lower():
                import uuid
                return str(uuid.uuid4())[:8]
            return f"mock_{name}"

        if field_type == "array":
            items_info = info.get("items", {})
            if "$ref" in items_info:
                ref_key = items_info["$ref"].split("/")[-1]
                ref_schema = defs.get(ref_key, {})
                return [self._mock_object(f"{name}_item", ref_schema, defs)]
            return [self._mock_value(f"{name}_0", items_info, defs)]

        if field_type == "object":
            sub_props = info.get("properties", {})
            if sub_props:
                result = {}
                for pn, pi in sub_props.items():
                    result[pn] = self._mock_value(pn, pi, defs)
                return result
            return {}

        if field_type in ("integer", "number"):
            return 1

        if field_type == "boolean":
            return True

        return None

    def _mock_object(self, name: str, schema: dict, defs: dict) -> dict:
        props = schema.get("properties", {})
        result: dict = {}
        for prop_name, prop_info in props.items():
            result[prop_name] = self._mock_value(prop_name, prop_info, defs)
        return result
