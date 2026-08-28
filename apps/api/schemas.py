from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ItemBase(BaseModel):
    title: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class ItemRead(ItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    completed: bool = False
    created_at: datetime

class ItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
