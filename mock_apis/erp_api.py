"""ERP API — Inventory & Procurement (port 8002)."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mock_apis.utils import auto_register

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

INVENTORY = {
    "BeadChip": {"product": "BeadChip", "units_available": 800, "units_in_transit": 200,
                 "reorder_point": 300, "warehouse_locations": ["SD-1", "SG-2"],
                 "last_updated": "2026-06-08T10:30:00Z"},
    "NextSeq":  {"product": "NextSeq",  "units_available": 45,  "units_in_transit": 100,
                 "reorder_point": 50,  "warehouse_locations": ["SD-1"],
                 "last_updated": "2026-06-08T09:00:00Z"},
    "HiSeq":    {"product": "HiSeq",    "units_available": 120, "units_in_transit": 0,
                 "reorder_point": 80,  "warehouse_locations": ["SG-2"],
                 "last_updated": "2026-06-07T18:00:00Z"},
}

PROCUREMENT = {
    "BeadChip": {"product": "BeadChip", "pending_orders": 2, "next_delivery": "2026-06-12",
                 "total_on_order": 5000, "supplier": "Illumina Manufacturing"},
    "NextSeq":  {"product": "NextSeq",  "pending_orders": 1, "next_delivery": "2026-06-15",
                 "total_on_order": 200,  "supplier": "Illumina Manufacturing"},
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    auto_register({
        "name": "Check Inventory",
        "description": "Query current inventory levels and warehouse locations from ERP",
        "endpoint": "http://localhost:8002/erp/inventory",
        "method": "GET",
        "parameters": ["product"],
        "owner_team": "ERP Team",
        "auth_type": "api_key",
        "dependencies": [],
    })
    auto_register({
        "name": "Check Procurement",
        "description": "Query pending procurement orders and next delivery dates from ERP",
        "endpoint": "http://localhost:8002/erp/procurement",
        "method": "GET",
        "parameters": ["product"],
        "owner_team": "ERP Team",
        "auth_type": "api_key",
        "dependencies": [],
    })
    yield


app = FastAPI(title="ERP API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/erp/inventory")
def get_inventory(product: str):
    """Return inventory levels for a product."""
    if product not in INVENTORY:
        raise HTTPException(status_code=404, detail=f"Product '{product}' not found in inventory")
    return INVENTORY[product]


@app.get("/erp/procurement")
def get_procurement(product: str):
    """Return pending procurement orders for a product."""
    if product not in PROCUREMENT:
        raise HTTPException(status_code=404, detail=f"No procurement orders found for '{product}'")
    return PROCUREMENT[product]


@app.get("/health")
def health():
    return {"service": "ERP API", "status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mock_apis.erp_api:app", host="0.0.0.0", port=8002, reload=True)
