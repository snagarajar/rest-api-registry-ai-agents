"""In-memory storage for the API Registry."""

from typing import Dict, List, Optional
from registry.models import APIRecord


class APIRegistry:
    """Thread-safe in-memory store for registered APIs."""

    def __init__(self):
        self._store: dict[str, APIRecord] = {}

    def register(self, record: APIRecord) -> APIRecord:
        self._store[record.api_id] = record
        return record

    def get(self, api_id: str) -> Optional[APIRecord]:
        return self._store.get(api_id)

    def delete(self, api_id: str) -> bool:
        if api_id in self._store:
            del self._store[api_id]
            return True
        return False

    def list_all(self) -> List[APIRecord]:
        return list(self._store.values())

    def search(self, query: str, limit: int = 10) -> List[APIRecord]:
        """Simple keyword search across name, description, and owner_team."""
        q = query.lower()
        results = [
            api for api in self._store.values()
            if q in api.name.lower()
            or q in api.description.lower()
            or q in api.owner_team.lower()
            or any(q in p.lower() for p in api.parameters)
        ]
        return results[:limit]
