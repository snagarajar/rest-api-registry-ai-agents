"""Seed initial data into the lab database."""

from datetime import datetime
from lab_app.database import SessionLocal, engine, Base
from lab_app import models  # noqa: F401 — ensures tables are registered


def create_tables():
    Base.metadata.create_all(bind=engine)


def seed_data():
    db = SessionLocal()
    try:
        # Only seed if tables are empty
        if db.query(models.LabOrder).count() > 0:
            return

        # Lab Orders
        db.add_all([
            models.LabOrder(sample_type="Blood", sample_count=24, assay="WGS",
                            priority="urgent", status="processing", requester="Dr. Smith"),
            models.LabOrder(sample_type="Tissue", sample_count=8, assay="RNA-Seq",
                            priority="normal", status="received", requester="Dr. Patel"),
            models.LabOrder(sample_type="Saliva", sample_count=50, assay="Microarray",
                            priority="low", status="completed", requester="Dr. Lee"),
        ])

        # Inventory Items
        db.add_all([
            models.InventoryItem(item_name="EDTA Tubes", category="consumable",
                                 quantity=500, unit="tubes", reorder_threshold=100, location="Lab-A"),
            models.InventoryItem(item_name="DNA Extraction Kit", category="reagent",
                                 quantity=40, unit="kits", reorder_threshold=10, location="Cold Storage"),
            models.InventoryItem(item_name="PCR Primer Mix", category="reagent",
                                 quantity=8, unit="vials", reorder_threshold=5, location="Freezer-2"),
            models.InventoryItem(item_name="NextSeq 2000 Flow Cell", category="consumable",
                                 quantity=15, unit="units", reorder_threshold=4, location="Lab-B"),
            models.InventoryItem(item_name="Centrifuge 5425", category="equipment",
                                 quantity=3, unit="units", reorder_threshold=1, location="Lab-A"),
        ])

        # Invoices
        db.add_all([
            models.Invoice(client="BioTech Diagnostics", amount=12500.00,
                           description="WGS sequencing services — May 2026",
                           due_date="2026-06-30", status="pending"),
            models.Invoice(client="GenomX Research", amount=8750.00,
                           description="RNA-Seq analysis batch #42",
                           due_date="2026-06-15", status="paid",
                           paid_at=datetime(2026, 6, 10)),
            models.Invoice(client="Illumina Internal", amount=3200.00,
                           description="Microarray consumables Q2",
                           due_date="2026-05-31", status="overdue"),
        ])

        # Products
        db.add_all([
            models.Product(name="NovaSeq X Plus", category="sequencing",
                           version="2.1", status="active", price=985000.00,
                           description="High-throughput sequencing platform"),
            models.Product(name="NextSeq 2000", category="sequencing",
                           version="1.5", status="active", price=335000.00,
                           description="Mid-throughput benchtop sequencer"),
            models.Product(name="DRAGEN Bio-IT Platform", category="software",
                           version="4.3", status="active", price=45000.00,
                           description="Ultra-rapid secondary analysis pipeline"),
            models.Product(name="HiSeq 2500", category="sequencing",
                           version="1.0", status="discontinued", price=0.00,
                           description="Legacy high-throughput sequencer"),
        ])

        db.commit()
    finally:
        db.close()
