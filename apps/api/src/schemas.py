from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class WorkflowStartResponse(BaseModel):
    status: str
    state: dict


class ApprovalResponse(BaseModel):
    status: str
    state: dict


class RollbackResponse(BaseModel):
    status: str
    phase: str
    phase_history: list[dict]


class ErrorResponse(BaseModel):
    detail: str
