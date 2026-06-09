"""LIMS API — Work Orders & Bead Pools (port 8001)."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mock_apis.utils import auto_register

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WORKORDERS = {
    "WO-1234": {"workorder_id": "WO-1234", "product": "BeadChip", "units_required": 500,
                "priority": "high", "status": "pending", "created_date": "2026-06-01",
                "due_date": "2026-06-10", "assigned_fab": "fab-sd"},
    "WO-1235": {"workorder_id": "WO-1235", "product": "NextSeq", "units_required": 200,
                "priority": "medium", "status": "in_progress", "created_date": "2026-06-03",
                "due_date": "2026-06-12", "assigned_fab": "fab-sg"},
    "WO-1236": {"workorder_id": "WO-1236", "product": "HiSeq", "units_required": 800,
                "priority": "low", "status": "completed", "created_date": "2026-05-28",
                "due_date": "2026-06-08", "assigned_fab": "fab-sd"},
}

BEAD_POOLS = {
    "BP-456": {"pool_id": "BP-456", "total_beads": 1_000_000, "available_beads": 750_000,
               "chemistry": "amplification-ready", "expiration": "2026-07-01", "quality_grade": "A"},
    "BP-457": {"pool_id": "BP-457", "total_beads": 500_000, "available_beads": 120_000,
               "chemistry": "amplification-ready", "expiration": "2026-06-20", "quality_grade": "B"},
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    auto_register({
        "name": "Get Work Order",
        "description": "Fetch work order details and production status from LIMS",
        "endpoint": "http://localhost:8001/lims/workorder",
        "method": "GET",
        "parameters": ["id"],
        "owner_team": "LIMS Team",
        "auth_type": "none",
        "dependencies": [],
    })
    auto_register({
        "name": "Get Bead Pool",
        "description": "Fetch bead pool inventory and quality grade from LIMS",
        "endpoint": "http://localhost:8001/lims/bead-pool",
        "method": "GET",
        "parameters": ["id"],
        "owner_team": "LIMS Team",
        "auth_type": "none",
        "dependencies": [],
    })
    yield


app = FastAPI(title="LIMS API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/lims/workorder")
def get_workorder(id: str):
    """Return work order details for a given work order ID."""
    if id not in WORKORDERS:
        raise HTTPException(status_code=404, detail=f"Work order '{id}' not found")
    return WORKORDERS[id]


@app.get("/lims/bead-pool")
def get_bead_pool(id: str):
    """Return bead pool availability and quality grade."""
    if id not in BEAD_POOLS:
        raise HTTPException(status_code=404, detail=f"Bead pool '{id}' not found")
    return BEAD_POOLS[id]


@app.get("/health")
def health():
    return {"service": "LIMS API", "status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mock_apis.lims_api:app", host="0.0.0.0", port=8001, reload=True)
