"""Basic tests for the API Registry endpoints."""

import pytest
from fastapi.testclient import TestClient

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from registry.main import app

client = TestClient(app)

SAMPLE_API = {
    "name": "Test API",
    "description": "A simple test endpoint",
    "endpoint": "http://localhost:9999/test",
    "method": "GET",
    "parameters": ["id"],
    "owner_team": "Test Team",
    "auth_type": "none",
}


def test_register_api():
    resp = client.post("/registry/register", json=SAMPLE_API)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "registered"
    assert "api_id" in data
    return data["api_id"]


def test_list_apis():
    client.post("/registry/register", json=SAMPLE_API)
    resp = client.get("/registry/list")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_search_apis():
    client.post("/registry/register", json=SAMPLE_API)
    resp = client.get("/registry/search", params={"query": "test"})
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_deregister_api():
    reg = client.post("/registry/register", json=SAMPLE_API).json()
    api_id = reg["api_id"]
    resp = client.delete(f"/registry/api/{api_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "deregistered"


def test_deregister_nonexistent():
    resp = client.delete("/registry/api/does-not-exist")
    assert resp.status_code == 404


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
