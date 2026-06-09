"""Shared utilities for mock APIs — auto-registration helper."""

import logging
import requests
from typing import Optional

REGISTRY_URL = "http://localhost:9000"

logger = logging.getLogger(__name__)


def auto_register(api_meta: dict) -> Optional[str]:
    """POST to the registry on startup. Returns assigned api_id or None on failure."""
    try:
        resp = requests.post(f"{REGISTRY_URL}/registry/register", json=api_meta, timeout=5)
        resp.raise_for_status()
        api_id = resp.json().get("api_id")
        logger.info("Auto-registered '%s' → id=%s", api_meta["name"], api_id)
        return api_id
    except Exception as exc:
        logger.warning("Could not register '%s': %s (registry may not be running yet)", api_meta["name"], exc)
        return None
