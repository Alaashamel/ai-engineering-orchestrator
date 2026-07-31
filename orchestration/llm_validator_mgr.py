from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationValidator(BaseModel):
    name: str
    validate_fn: Any = None
    error_message: str = ""


class LLMIntegrationValidatorManager:
    def __init__(self) -> None:
        self._validators: list[LLMIntegrationValidator] = []

    def add_validator(
        self,
        name: str,
        validate_fn: Any,
        error_message: str = "",
    ) -> LLMIntegrationValidator:
        validator = LLMIntegrationValidator(
            name=name,
            validate_fn=validate_fn,
            error_message=error_message,
        )
        self._validators.append(validator)
        return validator

    def remove_validator(self, name: str) -> bool:
        for i, v in enumerate(self._validators):
            if v.name == name:
                del self._validators[i]
                return True
        return False

    def get_validator(self, name: str) -> LLMIntegrationValidator | None:
        for v in self._validators:
            if v.name == name:
                return v
        return None

    def validate(
        self, data: Any
    ) -> tuple[bool, list[str]]:
        errors: list[str] = []
        for validator in self._validators:
            if validator.validate_fn is not None:
                try:
                    result = validator.validate_fn(data)
                    if result is not True:
                        errors.append(
                            validator.error_message
                            or f"Validation failed for {validator.name}"
                        )
                except Exception as exc:
                    errors.append(str(exc))
        return len(errors) == 0, errors

    def list_validators(self) -> list[str]:
        return [v.name for v in self._validators]

    def clear(self) -> None:
        self._validators.clear()