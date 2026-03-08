from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.models.inventory import (
    InventoryItem, 
    InventoryItemCreate, 
    InventoryItemUpdate,
    StockUpdate,
    Transaction,
    TransactionCreate
)
from app.utils.auth import get_current_user
from app.services.mongodb_db import get_db
import uuid
from datetime import datetime

router = APIRouter()

def calculate_status(quantity: int, min_stock_level: int) -> str:
    """Calculate item status based on quantity"""
    if quantity == 0:
        return "Out of Stock"
    elif quantity <= min_stock_level:
        return "Low Stock"
    else:
        return "In Stock"

@router.get("/", response_model=List[InventoryItem])
async def get_inventory_items(
    category: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get all inventory items with optional filtering"""
    db = await get_db()
    
    # Build query
    query = {}
    
    if category:
        query['category'] = category
    
    if status_filter:
        query['status'] = status_filter
    
    if search:
        search_lower = search.lower()
        query['$or'] = [
            {'name': {'$regex': search_lower, '$options': 'i'}},
            {'sku': {'$regex': search_lower, '$options': 'i'}},
            {'description': {'$regex': search_lower, '$options': 'i'}}
        ]
    
    items = await db.find_all('inventory_items', query)
    return items

@router.get("/{item_id}", response_model=InventoryItem)
async def get_inventory_item(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific inventory item by ID"""
    db = await get_db()
    item = await db.find_by_id('inventory_items', item_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return item

@router.post("/", response_model=InventoryItem)
async def create_inventory_item(
    item: InventoryItemCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new inventory item"""
    db = await get_db()
    
    # Check if SKU already exists
    existing_item = await db.find_one('inventory_items', {'sku': item.sku})
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists"
        )
    
    # Create new item
    new_item = {
        'name': item.name,
        'sku': item.sku,
        'description': item.description,
        'category': item.category,
        'quantity': item.quantity,
        'min_stock_level': item.min_stock_level,
        'max_stock_level': item.max_stock_level,
        'unit_price': item.unit_price,
        'supplier': item.supplier,
        'location': item.location,
        'status': calculate_status(item.quantity, item.min_stock_level),
        'created_at': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat()
    }
    
    item_id = await db.insert_one('inventory_items', new_item)
    new_item['id'] = item_id
    return new_item

@router.put("/{item_id}", response_model=InventoryItem)
async def update_inventory_item(
    item_id: str,
    item_update: InventoryItemUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an inventory item"""
    db = await get_db()
    
    # Get existing item
    existing_item = await db.find_by_id('inventory_items', item_id)
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Check if SKU already exists (if updating SKU)
    if item_update.sku and item_update.sku != existing_item.get('sku'):
        existing_sku = await db.find_one('inventory_items', {'sku': item_update.sku})
        if existing_sku and str(existing_sku.get('id')) != item_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SKU already exists"
            )
    
    # Update item
    update_data = item_update.dict(exclude_unset=True)
    
    # Recalculate status if quantity or min_stock_level is updated
    if 'quantity' in update_data or 'min_stock_level' in update_data:
        quantity = update_data.get('quantity', existing_item.get('quantity', 0))
        min_stock = update_data.get('min_stock_level', existing_item.get('min_stock_level', 10))
        update_data['status'] = calculate_status(quantity, min_stock)
    
    update_data['last_updated'] = datetime.now().isoformat()
    
    success = await db.update_one('inventory_items', item_id, update_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update item"
        )
    
    # Return updated item
    updated_item = await db.find_by_id('inventory_items', item_id)
    return updated_item

@router.delete("/{item_id}")
async def delete_inventory_item(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an inventory item"""
    db = await get_db()
    
    # Check if item exists
    existing_item = await db.find_by_id('inventory_items', item_id)
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Delete item
    success = await db.delete_one('inventory_items', item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item"
        )
    
    return {"message": "Item deleted successfully"}

@router.post("/{item_id}/stock")
async def update_stock(
    item_id: str,
    stock_update: StockUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update stock levels for an item"""
    db = await get_db()
    
    # Get existing item
    existing_item = await db.find_by_id('inventory_items', item_id)
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    current_quantity = existing_item.get('quantity', 0)
    new_quantity = current_quantity
    
    # Calculate new quantity based on transaction type
    if stock_update.type == "Stock In":
        new_quantity = current_quantity + stock_update.quantity
    elif stock_update.type == "Stock Out":
        if current_quantity < stock_update.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock"
            )
        new_quantity = current_quantity - stock_update.quantity
    elif stock_update.type == "Adjustment":
        new_quantity = stock_update.quantity
    
    # Update item quantity and status
    min_stock = existing_item.get('min_stock_level', 10)
    update_data = {
        'quantity': new_quantity,
        'status': calculate_status(new_quantity, min_stock),
        'last_updated': datetime.now().isoformat()
    }
    
    await db.update_one('inventory_items', item_id, update_data)
    
    # Create transaction record
    transaction = {
        'inventory_item_id': item_id,
        'type': stock_update.type,
        'quantity': stock_update.quantity,
        'reference': stock_update.reference,
        'notes': stock_update.notes,
        'user_id': current_user['id'],
        'created_at': datetime.now().isoformat()
    }
    
    transaction_id = await db.insert_one('transactions', transaction)
    transaction['id'] = transaction_id
    
    # Return updated item and transaction
    updated_item = await db.find_by_id('inventory_items', item_id)
    return {
        "item": updated_item,
        "transaction": transaction
    }

@router.get("/{item_id}/transactions", response_model=List[Transaction])
async def get_item_transactions(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all transactions for a specific item"""
    db = await get_db()
    
    # Check if item exists
    existing_item = await db.find_by_id('inventory_items', item_id)
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Get transactions for this item
    transactions = await db.find_all('transactions', {'inventory_item_id': item_id})
    
    # Sort by created_at (newest first)
    transactions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return transactions

@router.get("/alerts/low-stock", response_model=List[InventoryItem])
async def get_low_stock_items(current_user: dict = Depends(get_current_user)):
    """Get all items with low stock"""
    db = await get_db()
    low_stock_items = await db.find_all('inventory_items', {'status': 'Low Stock'})
    return low_stock_items
