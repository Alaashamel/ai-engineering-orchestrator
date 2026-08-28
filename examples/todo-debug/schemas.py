from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class NoteBase(BaseModel):
    title: str
    description: str | None = None

class NoteCreate(NoteBase):
    pass

class NoteRead(NoteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    completed: bool = False
    created_at: datetime

class NoteUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
