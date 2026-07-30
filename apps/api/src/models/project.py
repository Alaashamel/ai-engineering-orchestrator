import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="discovery", server_default=text("'discovery'")
    )
    meta_data: Mapped[dict] = mapped_column(JSON, default=dict, server_default=text("'{}'::json"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        server_default=text("now()"),
        onupdate=datetime.utcnow,
    )
