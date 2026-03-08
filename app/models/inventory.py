from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class InventoryItemBase(BaseModel):
    name: str = Field(..., max_length=100)
    sku: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    category: str = Field(..., enum=["Electronics", "Clothing", "Food", "Furniture", "Books", "Tools", "Other"])
    quantity: int = Field(..., ge=0)
    min_stock_level: int = Field(10, ge=0)
    max_stock_level: int = Field(100, ge=0)
    unit_price: float = Field(..., ge=0)
    supplier: Optional[str] = None
    location: Optional[str] = None

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItemUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, enum=["Electronics", "Clothing", "Food", "Furniture", "Books", "Tools", "Other"])
    quantity: Optional[int] = Field(None, ge=0)
    min_stock_level: Optional[int] = Field(None, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)
    unit_price: Optional[float] = Field(None, ge=0)
    supplier: Optional[str] = None
    location: Optional[str] = None

class InventoryItem(InventoryItemBase):
    id: str
    status: str
    created_at: datetime
    last_updated: datetime
    
    class Config:
        orm_mode = True

class StockUpdate(BaseModel):
    type: str = Field(..., enum=["Stock In", "Stock Out", "Adjustment"])
    quantity: int = Field(..., ge=0)
    notes: Optional[str] = Field(None, max_length=200)
    reference: Optional[str] = None

class Transaction(BaseModel):
    id: str
    inventory_item_id: str
    type: str
    quantity: int
    reference: Optional[str]
    notes: Optional[str]
    user_id: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class TransactionCreate(BaseModel):
    inventory_item_id: str
    type: str
    quantity: int
    notes: Optional[str] = None
    reference: Optional[str] = None
    user_id: str
