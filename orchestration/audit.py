from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

logger = logging.getLogger(__name__)


class AuditLogger:
    def __init__(self, db_session_factory: Any | None = None):
        self._factory = db_session_factory
        self._buffer: list[dict[str, Any]] = []

    def log(
        self,
        project_id: str | UUID,
        actor: str,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        details: dict[str, Any] | None = None,
        phase: str | None = None,
        outcome: str = "success",
    ) -> None:
        entry = {
            "project_id": str(project_id),
            "actor": actor,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "phase": phase,
            "outcome": outcome,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._buffer.append(entry)

    async def flush(self) -> None:
        if not self._buffer or not self._factory:
            return
        try:
            async with self._factory() as session:
                from src.models.audit_log import AuditLog

                for entry in self._buffer:
                    session.add(
                        AuditLog(
                            project_id=UUID(entry["project_id"]),
                            actor=entry["actor"],
                            action=entry["action"],
                            resource_type=entry["resource_type"],
                            resource_id=entry["resource_id"],
                            details=entry["details"],
                            phase=entry["phase"],
                            outcome=entry["outcome"],
                        )
                    )
                await session.commit()
                self._buffer.clear()
        except Exception as exc:
            logger.warning("Audit flush failed: %s", exc)

    @property
    def entries(self) -> list[dict[str, Any]]:
        return list(self._buffer)


_global_logger = AuditLogger()


def get_audit_logger() -> AuditLogger:
    return _global_logger
