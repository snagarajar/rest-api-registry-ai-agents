"""Inventory router — GET list/item, POST consume/restock."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from lab_app.database import get_db
from lab_app.models import InventoryItem

router = APIRouter(prefix="/lab/inventory", tags=["Inventory"])


def _fmt(item: InventoryItem) -> dict:
    return {
        "item_id": f"INV-{item.id:03d}",
        "item_name": item.item_name,
        "category": item.category,
        "quantity": item.quantity,
        "unit": item.unit,
        "reorder_threshold": item.reorder_threshold,
        "low_stock": item.quantity <= item.reorder_threshold,
        "location": item.location,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
    }


class AdjustRequest(BaseModel):
    quantity: int
    reason: Optional[str] = ""


@router.get("")
def list_inventory(category: Optional[str] = None, low_stock: Optional[bool] = None,
                   db: Session = Depends(get_db)):
    """List all inventory items, optionally filtered by category or low_stock flag."""
    q = db.query(InventoryItem)
    if category:
        q = q.filter(InventoryItem.category == category)
    items = q.order_by(InventoryItem.item_name).all()
    if low_stock is not None:
        items = [i for i in items if (i.quantity <= i.reorder_threshold) == low_stock]
    return [_fmt(i) for i in items]


@router.get("/{item_id}")
def get_item(item_id: str, db: Session = Depends(get_db)):
    """Get inventory details for a specific item."""
    try:
        num = int(item_id.replace("INV-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")
    item = db.query(InventoryItem).filter(InventoryItem.id == num).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return _fmt(item)


@router.post("/{item_id}/consume")
def consume_item(item_id: str, body: AdjustRequest, db: Session = Depends(get_db)):
    """Consume (reduce) inventory for an item."""
    try:
        num = int(item_id.replace("INV-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")
    item = db.query(InventoryItem).filter(InventoryItem.id == num).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    if body.quantity > item.quantity:
        raise HTTPException(status_code=400,
                            detail=f"Not enough stock: {item.quantity} available, {body.quantity} requested")
    item.quantity -= body.quantity
    item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return {**_fmt(item), "consumed": body.quantity}


@router.post("/{item_id}/restock")
def restock_item(item_id: str, body: AdjustRequest, db: Session = Depends(get_db)):
    """Restock (increase) inventory for an item."""
    try:
        num = int(item_id.replace("INV-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")
    item = db.query(InventoryItem).filter(InventoryItem.id == num).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    item.quantity += body.quantity
    item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return {**_fmt(item), "restocked": body.quantity}
