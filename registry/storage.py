"""SQLite-backed persistent storage for the API Registry."""

import json
import os
import sqlite3
from typing import List, Optional

from registry.models import APIRecord

DB_PATH = os.getenv("REGISTRY_DB_PATH", "registry/registry.db")


def _get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS api_registry (
                api_id       TEXT PRIMARY KEY,
                name         TEXT NOT NULL,
                description  TEXT NOT NULL,
                endpoint     TEXT NOT NULL,
                method       TEXT NOT NULL DEFAULT 'GET',
                parameters   TEXT NOT NULL DEFAULT '[]',
                owner_team   TEXT NOT NULL,
                auth_type    TEXT NOT NULL DEFAULT 'none',
                dependencies TEXT NOT NULL DEFAULT '[]',
                registered_at TEXT NOT NULL,
                status       TEXT NOT NULL DEFAULT 'active'
            )
        """)
        conn.commit()


_init_db()


def _row_to_record(row: sqlite3.Row) -> APIRecord:
    return APIRecord(
        api_id=row["api_id"],
        name=row["name"],
        description=row["description"],
        endpoint=row["endpoint"],
        method=row["method"],
        parameters=json.loads(row["parameters"]),
        owner_team=row["owner_team"],
        auth_type=row["auth_type"],
        dependencies=json.loads(row["dependencies"]),
        registered_at=row["registered_at"],
        status=row["status"],
    )


class APIRegistry:
    """SQLite-backed persistent store for registered APIs."""

    def register(self, record: APIRecord) -> APIRecord:
        with _get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO api_registry
                  (api_id, name, description, endpoint, method, parameters,
                   owner_team, auth_type, dependencies, registered_at, status)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (
                record.api_id, record.name, record.description, record.endpoint,
                record.method, json.dumps(record.parameters), record.owner_team,
                record.auth_type, json.dumps(record.dependencies),
                record.registered_at, record.status,
            ))
            conn.commit()
        return record

    def get(self, api_id: str) -> Optional[APIRecord]:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM api_registry WHERE api_id = ?", (api_id,)
            ).fetchone()
        return _row_to_record(row) if row else None

    def delete(self, api_id: str) -> bool:
        with _get_conn() as conn:
            cur = conn.execute(
                "DELETE FROM api_registry WHERE api_id = ?", (api_id,)
            )
            conn.commit()
        return cur.rowcount > 0

    def list_all(self) -> List[APIRecord]:
        with _get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM api_registry ORDER BY registered_at DESC"
            ).fetchall()
        return [_row_to_record(r) for r in rows]

    def search(self, query: str, limit: int = 10) -> List[APIRecord]:
        q = f"%{query.lower()}%"
        with _get_conn() as conn:
            rows = conn.execute("""
                SELECT * FROM api_registry
                WHERE lower(name)        LIKE ?
                   OR lower(description) LIKE ?
                   OR lower(owner_team)  LIKE ?
                   OR lower(parameters)  LIKE ?
                ORDER BY registered_at DESC
                LIMIT ?
            """, (q, q, q, q, limit)).fetchall()
        return [_row_to_record(r) for r in rows]
