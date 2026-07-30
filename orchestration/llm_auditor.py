from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMIntegrationAuditor(BaseModel):
    name: str
    audit_fn: Any = None


class LLMIntegrationAuditorManager:
    def __init__(self) -> None:
        self._auditors: dict[str, LLMIntegrationAuditor] = {}

    def register(self, auditor: LLMIntegrationAuditor) -> None:
        self._auditors[auditor.name] = auditor

    def unregister(self, name: str) -> bool:
        if name in self._auditors:
            del self._auditors[name]
            return True
        return False

    def get(self, name: str) -> LLMIntegrationAuditor | None:
        return self._auditors.get(name)

    def audit(
        self, name: str, data: Any
    ) -> dict[str, Any]:
        auditor = self._auditors.get(name)
        if auditor is None:
            raise ValueError(
                f"Auditor '{name}' not found"
            )
        if auditor.audit_fn is not None:
            return auditor.audit_fn(data)
        return {"audited": True}

    def list_auditors(self) -> list[str]:
        return list(self._auditors.keys())