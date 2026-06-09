"""SQLAlchemy ORM models for the Lab App."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from lab_app.database import Base


class LabOrder(Base):
    __tablename__ = "lab_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sample_type = Column(String(100), nullable=False)
    sample_count = Column(Integer, nullable=False)
    assay = Column(String(100), nullable=False)
    priority = Column(String(20), default="normal")   # urgent / normal / low
    status = Column(String(30), default="received")   # received / processing / completed / cancelled
    requester = Column(String(100), nullable=False)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InventoryItem(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50), nullable=False)   # reagent / equipment / consumable
    quantity = Column(Integer, default=0)
    unit = Column(String(20), default="units")
    reorder_threshold = Column(Integer, default=10)
    location = Column(String(100), default="")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(5), default="USD")
    status = Column(String(20), default="pending")   # pending / paid / overdue / cancelled
    description = Column(Text, default="")
    due_date = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50), nullable=False)   # sequencing / array / reagent / software
    version = Column(String(20), default="1.0")
    status = Column(String(20), default="active")   # active / discontinued / beta
    price = Column(Float, default=0.0)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
