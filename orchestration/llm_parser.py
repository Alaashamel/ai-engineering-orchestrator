from __future__ import annotations

import json
import re
from typing import Any, Optional

from pydantic import BaseModel


class LLMOutputParser:
    @staticmethod
    def extract_json(text: str) -> str:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("No JSON block found in response")
        return text[start : end + 1]

    @staticmethod
    def extract_code_block(text: str, language: str = "json") -> str:
        pattern = rf"```{language}\s*\n(.*?)\n```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    @staticmethod
    def parse_to_model(text: str, response_model: type[BaseModel]) -> BaseModel:
        json_text = LLMOutputParser.extract_json(text)
        return response_model.model_validate_json(json_text)

    @staticmethod
    def parse_list(text: str, item_model: type[BaseModel]) -> list[BaseModel]:
        json_text = LLMOutputParser.extract_json(text)
        data = json.loads(json_text)
        if isinstance(data, list):
            return [item_model.model_validate(item) for item in data]
        raise ValueError("Expected a JSON array in the response")

    @staticmethod
    def validate_response(
        text: str, response_model: type[BaseModel]
    ) -> tuple[bool, Optional[str]]:
        try:
            LLMOutputParser.parse_to_model(text, response_model)
            return True, None
        except Exception as exc:
            return False, str(exc)

    @staticmethod
    def sanitize_output(text: str) -> str:
        text = text.strip()
        text = re.sub(r"^\s*```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
        return text.strip()