import pytest
from orchestration.llm_validator_mgr import (
    LLMIntegrationValidator,
    LLMIntegrationValidatorManager,
)


class TestLLMIntegrationValidatorManager:
    def test_add_validator(self):
        manager = LLMIntegrationValidatorManager()
        validator = manager.add_validator(
            "not_empty",
            lambda data: bool(data),
            error_message="Data cannot be empty",
        )
        assert validator.name == "not_empty"

    def test_remove_validator(self):
        manager = LLMIntegrationValidatorManager()
        manager.add_validator("v1", lambda d: True)
        assert manager.remove_validator("v1") is True
        assert manager.remove_validator("v1") is False

    def test_validate_pass(self):
        manager = LLMIntegrationValidatorManager()
        manager.add_validator(
            "not_empty",
            lambda data: bool(data),
            error_message="Empty",
        )
        passed, errors = manager.validate("hello")
        assert passed is True
        assert errors == []

    def test_validate_fail(self):
        manager = LLMIntegrationValidatorManager()
        manager.add_validator(
            "not_empty",
            lambda data: bool(data),
            error_message="Empty",
        )
        passed, errors = manager.validate("")
        assert passed is False
        assert len(errors) == 1

    def test_list_validators(self):
        manager = LLMIntegrationValidatorManager()
        manager.add_validator("v1", lambda d: True)
        manager.add_validator("v2", lambda d: True)
        assert len(manager.list_validators()) == 2