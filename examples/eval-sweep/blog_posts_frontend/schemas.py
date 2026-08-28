from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class PostBase(BaseModel):
    title: str
    description: str | None = None

class PostCreate(PostBase):
    pass

class PostRead(PostBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    completed: bool = False
    created_at: datetime

class PostUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
