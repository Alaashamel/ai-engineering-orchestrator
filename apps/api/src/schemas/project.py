from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    status: str
    meta_data: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
