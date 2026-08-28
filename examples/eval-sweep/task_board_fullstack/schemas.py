from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class TaskBase(BaseModel):
    title: str
    description: str | None = None

class TaskCreate(TaskBase):
    pass

class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    completed: bool = False
    created_at: datetime

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
