"""Finance / Invoices router — GET list/detail, POST create, PATCH pay."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from lab_app.database import get_db
from lab_app.models import Invoice

router = APIRouter(prefix="/lab/finance", tags=["Finance"])


def _fmt(inv: Invoice) -> dict:
    return {
        "invoice_id": f"INV-{inv.id:03d}",
        "client": inv.client,
        "amount": inv.amount,
        "currency": inv.currency,
        "status": inv.status,
        "description": inv.description,
        "due_date": inv.due_date,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
        "paid_at": inv.paid_at.isoformat() if inv.paid_at else None,
    }


class CreateInvoiceRequest(BaseModel):
    client: str
    amount: float
    description: str
    due_date: str
    currency: Optional[str] = "USD"


@router.get("")
def list_invoices(status: Optional[str] = None, db: Session = Depends(get_db)):
    """List all invoices, optionally filtered by status."""
    q = db.query(Invoice)
    if status:
        q = q.filter(Invoice.status == status)
    return [_fmt(i) for i in q.order_by(Invoice.id.desc()).all()]


@router.get("/{invoice_id}")
def get_invoice(invoice_id: str, db: Session = Depends(get_db)):
    """Get details of a specific invoice."""
    try:
        num = int(invoice_id.replace("INV-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid invoice ID format")
    inv = db.query(Invoice).filter(Invoice.id == num).first()
    if not inv:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
    return _fmt(inv)


@router.post("", status_code=201)
def create_invoice(body: CreateInvoiceRequest, db: Session = Depends(get_db)):
    """Create a new invoice."""
    inv = Invoice(**body.model_dump())
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return _fmt(inv)


@router.patch("/{invoice_id}/pay")
def mark_paid(invoice_id: str, db: Session = Depends(get_db)):
    """Mark an invoice as paid."""
    try:
        num = int(invoice_id.replace("INV-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid invoice ID format")
    inv = db.query(Invoice).filter(Invoice.id == num).first()
    if not inv:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
    if inv.status == "paid":
        raise HTTPException(status_code=400, detail="Invoice is already paid")
    inv.status = "paid"
    inv.paid_at = datetime.utcnow()
    db.commit()
    db.refresh(inv)
    return _fmt(inv)
