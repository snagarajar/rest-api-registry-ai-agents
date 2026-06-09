"""Manufacturing API — Instrument Status & Fab Capacity (port 8004)."""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

INSTRUMENTS = {
    "Watson":  {"instrument": "Watson",  "status": "available",    "next_maintenance": "2026-06-15",
                "capacity_remaining": 5000, "last_run": "2026-06-07T16:45:00Z"},
    "Crick":   {"instrument": "Crick",   "status": "in_use",       "next_maintenance": "2026-06-18",
                "capacity_remaining": 1200, "last_run": "2026-06-08T08:00:00Z"},
    "Darwin":  {"instrument": "Darwin",  "status": "maintenance",  "next_maintenance": "2026-06-09",
                "capacity_remaining": 0,    "last_run": "2026-06-06T12:00:00Z"},
}

FAB_CAPACITY = {
    "fab-sd": {"fab": "fab-sd", "total_capacity": 10000, "currently_processing": 3500,
               "available_capacity": 6500, "estimated_completion": "2026-06-09T18:00:00Z"},
    "fab-sg": {"fab": "fab-sg", "total_capacity": 8000,  "currently_processing": 7200,
               "available_capacity": 800,  "estimated_completion": "2026-06-10T06:00:00Z"},
}


app = FastAPI(title="Manufacturing API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/manufacturing/instrument")
def get_instrument(name: str):
    """Return instrument status and capacity."""
    if name not in INSTRUMENTS:
        raise HTTPException(status_code=404, detail=f"Instrument '{name}' not found")
    return INSTRUMENTS[name]


@app.get("/manufacturing/capacity")
def get_capacity(fab: str):
    """Return fabrication site capacity."""
    if fab not in FAB_CAPACITY:
        raise HTTPException(status_code=404, detail=f"Fab '{fab}' not found")
    return FAB_CAPACITY[fab]


@app.get("/health")
def health():
    return {"service": "Manufacturing API", "status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mock_apis.manufacturing_api:app", host="0.0.0.0", port=8004, reload=True)
