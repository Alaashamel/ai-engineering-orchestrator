from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ProductBase(BaseModel):
    title: str
    description: str | None = None

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    completed: bool = False
    created_at: datetime

class ProductUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
