import pytest
from orchestration.llm_auditor import (
    LLMIntegrationAuditor,
    LLMIntegrationAuditorManager,
)


class TestLLMIntegrationAuditorManager:
    def test_register_and_audit(self):
        manager = LLMIntegrationAuditorManager()
        manager.register(
            LLMIntegrationAuditor(
                name="compliance",
                audit_fn=lambda d: {"compliant": True},
            )
        )
        result = manager.audit("compliance", {"data": "test"})
        assert result["compliant"] is True

    def test_unregister(self):
        manager = LLMIntegrationAuditorManager()
        manager.register(
            LLMIntegrationAuditor(
                name="audit1",
                audit_fn=lambda d: {},
            )
        )
        assert manager.unregister("audit1") is True

    def test_list_auditors(self):
        manager = LLMIntegrationAuditorManager()
        manager.register(
            LLMIntegrationAuditor(
                name="a1",
                audit_fn=lambda d: {},
            )
        )
        manager.register(
            LLMIntegrationAuditor(
                name="a2",
                audit_fn=lambda d: {},
            )
        )
        assert len(manager.list_auditors()) == 2