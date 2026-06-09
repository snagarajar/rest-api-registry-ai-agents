"""Lab App — FastAPI service on port 8500 with 4 modules and SQLite backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lab_app.database import engine
from lab_app.models import Base  # noqa: F401 — registers all ORM models
from lab_app.seed import seed_data
from lab_app.routers import orders, inventory, finance, products

# Create tables and seed data on startup
Base.metadata.create_all(bind=engine)
seed_data()

app = FastAPI(
    title="Illumina Lab Application",
    description=(
        "Lab LIMS / Inventory / Finance / Products service. "
        "Single SQLite-backed app exposing 4 domain modules for the AI agent demo."
    ),
    version="1.0.0",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(orders.router)
app.include_router(inventory.router)
app.include_router(finance.router)
app.include_router(products.router)


@app.get("/health")
def health():
    return {"service": "Illumina Lab App", "status": "ok", "port": 8500}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("lab_app.main:app", host="0.0.0.0", port=8500, reload=True)
