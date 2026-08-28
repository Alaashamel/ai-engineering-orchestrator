from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean, Integer, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class Note(Base):
    __tablename__ = 'notes'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
