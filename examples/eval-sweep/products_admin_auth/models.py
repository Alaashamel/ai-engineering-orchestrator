from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean, Integer, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    owner_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    owner: Mapped['User | None'] = relationship()

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
