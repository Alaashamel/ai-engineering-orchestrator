from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    actor: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    phase: Mapped[str | None] = mapped_column(String(50), nullable=True)
    outcome: Mapped[str] = mapped_column(String(20), default="success")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, server_default=text("now()")
    )
