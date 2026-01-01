from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ItemBase(BaseModel):
    sku: str = Field(..., min_length=3)
    name: str
    category: Optional[str]
    quantity: int = Field(ge=0)
    price: float = Field(gt=0)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str]
    category: Optional[str]
    quantity: Optional[int] = Field(ge=0)
    price: Optional[float] = Field(gt=0)
    is_active: Optional[bool]


class ItemResponse(ItemBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)