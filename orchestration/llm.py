from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from dotenv import load_dotenv
from openai import AsyncOpenAI, APIError, RateLimitError
from pydantic import BaseModel

_load_dotenv = load_dotenv(Path(__file__).resolve().parent.parent / ".env")

T = TypeVar("T", bound=BaseModel)


def _extract_jsons(text: str) -> list[str]:
    decoder = json.JSONDecoder()
    results: list[str] = []
    i = 0
    while i < len(text):
        if text[i] == "{":
            try:
                obj, idx = decoder.raw_decode(text, i)
                block = text[i:idx]
                if block not in results:
                    results.append(block)
                i = idx
                continue
            except json.JSONDecodeError:
                pass
        i += 1
    return results


def _try_parse(text: str, model_class: type[BaseModel]) -> BaseModel | None:
    candidates: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("data: ") and stripped.endswith("}"):
            candidates.append(stripped[6:])
        elif stripped.startswith("{") and stripped.endswith("}"):
            candidates.append(stripped)
    for extracted in _extract_jsons(text):
        if extracted not in candidates:
            candidates.append(extracted)
    for candidate in candidates:
        try:
            return model_class.model_validate_json(candidate)
        except Exception:
            continue
    return None


def has_api_key() -> bool:
    import os
    return bool(os.getenv("LLM_API_KEY"))


class LLMProvider:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        import os
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def generate_structured(
        self, system_prompt: str, user_prompt: str, response_model: type[T]
    ) -> T:
        if not self.client:
            return self._mock(response_model)
        try:
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
            parsed = _try_parse(raw, response_model)
            if parsed is not None:
                return parsed
            raise ValueError(f"JSON parsing failed: {raw}")
        except (RateLimitError, APIError, ValueError):
            return self._mock(response_model)

    def _mock(self, model_class: type[T]) -> T:
        return model_class.model_validate(self._build_mock(model_class))

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
