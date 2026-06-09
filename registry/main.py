"""Central REST API Registry — FastAPI service on port 9000."""

import logging
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from registry.models import (
    APIRegistration,
    APIRecord,
    RegisterResponse,
    SearchResponse,
    DeregisterResponse,
)
from registry.storage import APIRegistry

LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.WARNING), format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="REST API Registry for AI Agents",
    description="Central registry where teams self-register endpoints and AI agents discover them.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static UI files
app.mount("/static", StaticFiles(directory="ui/static"), name="static")

registry = APIRegistry()


# ─── Registry Endpoints ──────────────────────────────────────────────────────

@app.post("/registry/register", response_model=RegisterResponse, status_code=201)
def register_api(payload: APIRegistration):
    """Register a new API endpoint in the registry."""
    record = APIRecord(**payload.model_dump())
    registry.register(record)
    logger.info("Registered API: %s (%s) from %s", record.name, record.api_id, record.owner_team)
    return RegisterResponse(
        api_id=record.api_id,
        status="registered",
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@app.get("/registry/search", response_model=SearchResponse)
def search_apis(
    query: str = Query(..., description="Keyword to search for"),
    limit: int = Query(default=10, ge=1, le=50),
):
    """Search registered APIs by keyword (name, description, team)."""
    results = registry.search(query, limit=limit)
    logger.info("Search '%s' → %d results", query, len(results))
    return SearchResponse(total=len(results), apis=results)


@app.get("/registry/list", response_model=SearchResponse)
def list_apis():
    """List all registered APIs."""
    all_apis = registry.list_all()
    return SearchResponse(total=len(all_apis), apis=all_apis)


@app.delete("/registry/api/{api_id}", response_model=DeregisterResponse)
def deregister_api(api_id: str):
    """Remove an API from the registry."""
    if not registry.delete(api_id):
        raise HTTPException(status_code=404, detail=f"API '{api_id}' not found")
    logger.info("Deregistered API: %s", api_id)
    return DeregisterResponse(status="deregistered", api_id=api_id)


@app.get("/registry/api/{api_id}")
def get_api(api_id: str):
    """Get details of a specific registered API."""
    record = registry.get(api_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"API '{api_id}' not found")
    return record


# ─── Chat / UI Endpoints ─────────────────────────────────────────────────────

@app.get("/registry-ui")
def registry_ui():
    return FileResponse("ui/register_ui.html")


@app.get("/browse-ui")
def browse_ui():
    return FileResponse("ui/browse_ui.html")


@app.get("/chat-ui")
def chat_ui():
    return FileResponse("ui/chat_ui.html")


@app.post("/chat")
def chat(request: dict):
    """Invoke the orchestrator agent with a user question."""
    from orchestrator.agent import orchestrate
    question = request.get("question", "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required")
    answer = orchestrate(question)
    return {"answer": answer}


@app.get("/health")
def health():
    return {"status": "ok", "registered_apis": len(registry.list_all())}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("registry.main:app", host="0.0.0.0", port=9000, reload=True)
