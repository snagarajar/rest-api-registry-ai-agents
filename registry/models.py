"""Pydantic models for the API Registry."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


class APIRegistration(BaseModel):
    name: str = Field(..., description="Human-readable API name")
    description: str = Field(..., description="What this API does")
    endpoint: str = Field(..., description="Full URL of the endpoint")
    method: str = Field(default="GET", description="HTTP method")
    parameters: List[str] = Field(default_factory=list, description="Query/body parameters")
    owner_team: str = Field(..., description="Team that owns this API")
    auth_type: str = Field(default="none", description="none | api_key | oauth2 | mTLS")
    dependencies: List[str] = Field(default_factory=list, description="Other API IDs this depends on")


class APIRecord(APIRegistration):
    api_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    registered_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    status: str = "active"


class RegisterResponse(BaseModel):
    api_id: str
    status: str
    timestamp: str


class SearchResponse(BaseModel):
    total: int
    apis: List[APIRecord]


class DeregisterResponse(BaseModel):
    status: str
    api_id: str
