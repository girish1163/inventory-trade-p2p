from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uvicorn
import os
from dotenv import load_dotenv
import json
import uuid

# Load environment variables
load_dotenv()

# Simple in-memory database for demo
DATABASE = {
    "users": [],
    "inventory": [],
    "billing": [],
    "notes": []
}

app = FastAPI(title="Inventory Management System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Models
class User(BaseModel):
    id: str
    username: str
    email: str
    role: str
    created_at: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class InventoryItem(BaseModel):
    id: str
    name: str
    sku: str
    description: Optional[str]
    category: str
    quantity: int
    min_stock_level: int
    max_stock_level: int
    unit_price: float
    supplier: Optional[str]
    location: Optional[str]
    status: str
    created_at: str
    last_updated: str

class InventoryItemCreate(BaseModel):
    name: str
    sku: str
    description: Optional[str]
    category: str
    quantity: int
    min_stock_level: int
    max_stock_level: int
    unit_price: float
    supplier: Optional[str]
    location: Optional[str]

class BillingItem(BaseModel):
    id: str
    invoice_number: str
    customer_name: str
    items: List[Dict[str, Any]]
    total_amount: float
    status: str
    created_at: str
    due_date: str

class BillingItemCreate(BaseModel):
    invoice_number: str
    customer_name: str
    items: List[Dict[str, Any]]
    total_amount: float
    due_date: str

class NoteItem(BaseModel):
    id: str
    title: str
    content: str
    category: str
    created_at: str
    updated_at: str

class NoteItemCreate(BaseModel):
    title: str
    content: str
    category: str

# Helper functions
def calculate_status(quantity: int, min_stock: int) -> str:
    if quantity == 0:
        return "Out of Stock"
    elif quantity <= min_stock:
        return "Low Stock"
    else:
        return "In Stock"

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Simple token validation for demo
    if credentials.credentials == "demo-token":
        return User(
            id="1",
            username="admin",
            email="admin@inventory.com",
            role="admin",
            created_at=datetime.now().isoformat()
        )
    raise HTTPException(status_code=401, detail="Invalid token")

# Initialize demo data
def init_demo_data():
    if not DATABASE["users"]:
        # Create default admin user
        DATABASE["users"].append({
            "id": "1",
            "username": "admin",
            "email": "admin@inventory.com",
            "password": "girish7890@A",
            "role": "admin",
            "created_at": datetime.now().isoformat()
        })
        
        # Create sample inventory items
        DATABASE["inventory"].extend([
            {
                "id": "1",
                "name": "Laptop Dell XPS 15",
                "sku": "LAP-001",
                "description": "High-performance laptop",
                "category": "Electronics",
                "quantity": 15,
                "min_stock_level": 5,
                "max_stock_level": 50,
                "unit_price": 1299.99,
                "supplier": "Dell Inc.",
                "location": "Warehouse A",
                "status": "In Stock",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "2",
                "name": "Office Chair Ergonomic",
                "sku": "CHR-001",
                "description": "Comfortable office chair",
                "category": "Furniture",
                "quantity": 3,
                "min_stock_level": 10,
                "max_stock_level": 30,
                "unit_price": 299.99,
                "supplier": "Office Supplies Co.",
                "location": "Warehouse B",
                "status": "Low Stock",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        ])
        
        # Create sample billing items
        DATABASE["billing"].extend([
            {
                "id": "1",
                "invoice_number": "INV-2024-001",
                "customer_name": "ABC Corporation",
                "items": [
                    {"sku": "LAP-001", "name": "Laptop Dell XPS 15", "quantity": 2, "price": 1299.99}
                ],
                "total_amount": 2599.98,
                "status": "Paid",
                "created_at": datetime.now().isoformat(),
                "due_date": "2024-02-15"
            }
        ])
        
        # Create sample notes
        DATABASE["notes"].extend([
            {
                "id": "1",
                "title": "Quarterly Inventory Review",
                "content": "Review all inventory levels and update reorder points",
                "category": "Management",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ])

# Authentication endpoints
@app.post("/api/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    # Handle default credentials
    if (user_credentials.email == "743663" and user_credentials.password == "girish7890@A") or \
       (user_credentials.email == "admin@inventory.com" and user_credentials.password == "girish7890@A"):
        
        user = User(
            id="1",
            username="admin",
            email="admin@inventory.com",
            role="admin",
            created_at=datetime.now().isoformat()
        )
        
        return Token(
            access_token="demo-token",
            token_type="bearer",
            user=user
        )
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Stock List endpoints
@app.get("/api/stock", response_model=List[InventoryItem])
async def get_stock_list(current_user: User = Depends(get_current_user)):
    return [InventoryItem(**item) for item in DATABASE["inventory"]]

@app.get("/api/stock/alerts", response_model=List[InventoryItem])
async def get_stock_alerts(current_user: User = Depends(get_current_user)):
    low_stock = [item for item in DATABASE["inventory"] if item["status"] == "Low Stock"]
    out_of_stock = [item for item in DATABASE["inventory"] if item["status"] == "Out of Stock"]
    return [InventoryItem(**item) for item in low_stock + out_of_stock]

# Inventory Management endpoints
@app.get("/api/inventory", response_model=List[InventoryItem])
async def get_inventory_items(current_user: User = Depends(get_current_user)):
    return [InventoryItem(**item) for item in DATABASE["inventory"]]

@app.post("/api/inventory", response_model=InventoryItem)
async def create_inventory_item(
    item: InventoryItemCreate, 
    current_user: User = Depends(get_current_user)
):
    new_item = {
        "id": str(uuid.uuid4()),
        **item.dict(),
        "status": calculate_status(item.quantity, item.min_stock_level),
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }
    DATABASE["inventory"].append(new_item)
    return InventoryItem(**new_item)

@app.put("/api/inventory/{item_id}", response_model=InventoryItem)
async def update_inventory_item(
    item_id: str,
    item: InventoryItemCreate,
    current_user: User = Depends(get_current_user)
):
    for i, inv_item in enumerate(DATABASE["inventory"]):
        if inv_item["id"] == item_id:
            updated_item = {
                **inv_item,
                **item.dict(),
                "status": calculate_status(item.quantity, item.min_stock_level),
                "last_updated": datetime.now().isoformat()
            }
            DATABASE["inventory"][i] = updated_item
            return InventoryItem(**updated_item)
    
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/api/inventory/{item_id}")
async def delete_inventory_item(item_id: str, current_user: User = Depends(get_current_user)):
    for i, item in enumerate(DATABASE["inventory"]):
        if item["id"] == item_id:
            DATABASE["inventory"].pop(i)
            return {"message": "Item deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Item not found")

# Billing endpoints
@app.get("/api/billing", response_model=List[BillingItem])
async def get_billing_items(current_user: User = Depends(get_current_user)):
    return [BillingItem(**item) for item in DATABASE["billing"]]

@app.post("/api/billing", response_model=BillingItem)
async def create_billing_item(
    billing: BillingItemCreate,
    current_user: User = Depends(get_current_user)
):
    new_billing = {
        "id": str(uuid.uuid4()),
        **billing.dict(),
        "status": "Pending",
        "created_at": datetime.now().isoformat()
    }
    DATABASE["billing"].append(new_billing)
    return BillingItem(**new_billing)

@app.put("/api/billing/{billing_id}/status")
async def update_billing_status(
    billing_id: str,
    status: str,
    current_user: User = Depends(get_current_user)
):
    for i, item in enumerate(DATABASE["billing"]):
        if item["id"] == billing_id:
            DATABASE["billing"][i]["status"] = status
            return {"message": "Billing status updated"}
    
    raise HTTPException(status_code=404, detail="Billing item not found")

# Notes endpoints
@app.get("/api/notes", response_model=List[NoteItem])
async def get_notes(current_user: User = Depends(get_current_user)):
    return [NoteItem(**item) for item in DATABASE["notes"]]

@app.post("/api/notes", response_model=NoteItem)
async def create_note(
    note: NoteItemCreate,
    current_user: User = Depends(get_current_user)
):
    new_note = {
        "id": str(uuid.uuid4()),
        **note.dict(),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    DATABASE["notes"].append(new_note)
    return NoteItem(**new_note)

@app.put("/api/notes/{note_id}", response_model=NoteItem)
async def update_note(
    note_id: str,
    note: NoteItemCreate,
    current_user: User = Depends(get_current_user)
):
    for i, existing_note in enumerate(DATABASE["notes"]):
        if existing_note["id"] == note_id:
            updated_note = {
                **existing_note,
                **note.dict(),
                "updated_at": datetime.now().isoformat()
            }
            DATABASE["notes"][i] = updated_note
            return NoteItem(**updated_note)
    
    raise HTTPException(status_code=404, detail="Note not found")

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: str, current_user: User = Depends(get_current_user)):
    for i, note in enumerate(DATABASE["notes"]):
        if note["id"] == note_id:
            DATABASE["notes"].pop(i)
            return {"message": "Note deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Note not found")

# Dashboard endpoint
@app.get("/api/dashboard")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    total_items = len(DATABASE["inventory"])
    low_stock = len([item for item in DATABASE["inventory"] if item["status"] == "Low Stock"])
    out_of_stock = len([item for item in DATABASE["inventory"] if item["status"] == "Out of Stock"])
    total_value = sum(item["quantity"] * item["unit_price"] for item in DATABASE["inventory"])
    pending_bills = len([bill for bill in DATABASE["billing"] if bill["status"] == "Pending"])
    total_notes = len(DATABASE["notes"])
    
    return {
        "total_items": total_items,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "total_value": total_value,
        "pending_bills": pending_bills,
        "total_notes": total_notes
    }

@app.get("/")
async def root():
    return {"message": "Inventory Management System API is running...", "database": "In-Memory Demo"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "In-Memory Demo"}

# Initialize demo data on startup
init_demo_data()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
