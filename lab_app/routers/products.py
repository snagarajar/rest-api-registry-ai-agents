"""Products router — GET list/detail, POST create, PATCH update."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from lab_app.database import get_db
from lab_app.models import Product

router = APIRouter(prefix="/lab/products", tags=["Products"])


def _fmt(p: Product) -> dict:
    return {
        "product_id": f"PRD-{p.id:03d}",
        "name": p.name,
        "category": p.category,
        "version": p.version,
        "status": p.status,
        "price": p.price,
        "description": p.description,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


class CreateProductRequest(BaseModel):
    name: str
    category: str
    version: Optional[str] = "1.0"
    status: Optional[str] = "active"
    price: Optional[float] = 0.0
    description: Optional[str] = ""


class UpdateProductRequest(BaseModel):
    version: Optional[str] = None
    status: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None


@router.get("")
def list_products(category: Optional[str] = None, status: Optional[str] = None,
                  db: Session = Depends(get_db)):
    """List all products, optionally filtered by category or status."""
    q = db.query(Product)
    if category:
        q = q.filter(Product.category == category)
    if status:
        q = q.filter(Product.status == status)
    return [_fmt(p) for p in q.order_by(Product.name).all()]


@router.get("/{product_id}")
def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get details of a specific product."""
    try:
        num = int(product_id.replace("PRD-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid product ID format")
    p = db.query(Product).filter(Product.id == num).first()
    if not p:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return _fmt(p)


@router.post("", status_code=201)
def create_product(body: CreateProductRequest, db: Session = Depends(get_db)):
    """Create a new product in the catalog."""
    p = Product(**body.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return _fmt(p)


@router.patch("/{product_id}")
def update_product(product_id: str, body: UpdateProductRequest, db: Session = Depends(get_db)):
    """Update version, status, price, or description of a product."""
    try:
        num = int(product_id.replace("PRD-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid product ID format")
    p = db.query(Product).filter(Product.id == num).first()
    if not p:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    if body.version is not None:
        p.version = body.version
    if body.status is not None:
        p.status = body.status
    if body.price is not None:
        p.price = body.price
    if body.description is not None:
        p.description = body.description
    db.commit()
    db.refresh(p)
    return _fmt(p)
