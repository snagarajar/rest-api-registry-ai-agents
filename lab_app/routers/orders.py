"""Lab Orders router — GET list/detail, POST create, PATCH status."""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from lab_app.database import get_db
from lab_app.models import LabOrder

router = APIRouter(prefix="/lab/orders", tags=["Lab Orders"])


def _fmt(order: LabOrder) -> dict:
    return {
        "order_id": f"ORD-{order.id:03d}",
        "sample_type": order.sample_type,
        "sample_count": order.sample_count,
        "assay": order.assay,
        "priority": order.priority,
        "status": order.status,
        "requester": order.requester,
        "notes": order.notes,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
    }


class CreateOrderRequest(BaseModel):
    sample_type: str
    sample_count: int
    assay: str
    priority: Optional[str] = "normal"
    requester: str
    notes: Optional[str] = ""


class UpdateStatusRequest(BaseModel):
    status: str


@router.get("")
def list_orders(status: Optional[str] = None, db: Session = Depends(get_db)):
    """List all lab orders, optionally filtered by status."""
    q = db.query(LabOrder)
    if status:
        q = q.filter(LabOrder.status == status)
    return [_fmt(o) for o in q.order_by(LabOrder.id.desc()).all()]


@router.get("/{order_id}")
def get_order(order_id: str, db: Session = Depends(get_db)):
    """Get details of a specific lab order by ID (e.g., ORD-001)."""
    try:
        num = int(order_id.replace("ORD-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order ID format")
    order = db.query(LabOrder).filter(LabOrder.id == num).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return _fmt(order)


@router.post("", status_code=201)
def create_order(body: CreateOrderRequest, db: Session = Depends(get_db)):
    """Create a new lab order."""
    order = LabOrder(**body.model_dump())
    db.add(order)
    db.commit()
    db.refresh(order)
    return _fmt(order)


@router.patch("/{order_id}/status")
def update_order_status(order_id: str, body: UpdateStatusRequest, db: Session = Depends(get_db)):
    """Update the status of a lab order."""
    valid = {"received", "processing", "completed", "cancelled"}
    if body.status not in valid:
        raise HTTPException(status_code=400, detail=f"status must be one of {valid}")
    try:
        num = int(order_id.replace("ORD-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order ID format")
    order = db.query(LabOrder).filter(LabOrder.id == num).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    order.status = body.status
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return _fmt(order)
