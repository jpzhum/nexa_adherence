import json
from datetime import datetime
from typing import Any, Dict, Optional

from v2.db.connection import get_connection


def _serialize(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True)


def _deserialize(raw: Optional[str]) -> Any:
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def is_empty() -> bool:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS total FROM configs;").fetchone()
        return (row["total"] if row else 0) == 0


def list_configs() -> Dict[str, Any]:
    with get_connection() as conn:
        rows = conn.execute("SELECT key, value FROM configs;").fetchall()
    return {row["key"]: _deserialize(row["value"]) for row in rows}


def get_value(key: str, default: Any = None) -> Any:
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM configs WHERE key = ?;", (key,)).fetchone()
    if row is None:
        return default
    return _deserialize(row["value"])


def upsert_value(key: str, value: Any) -> None:
    now = datetime.utcnow().isoformat()
    payload = _serialize(value)
    with get_connection() as conn:
        existing = conn.execute("SELECT key FROM configs WHERE key = ?;", (key,)).fetchone()
        if existing:
            conn.execute(
                "UPDATE configs SET value = ?, updated_at = ? WHERE key = ?;",
                (payload, now, key),
            )
        else:
            conn.execute(
                """
                INSERT INTO configs (key, value, created_at, updated_at)
                VALUES (?, ?, ?, ?);
                """,
                (key, payload, now, now),
            )
        conn.commit()


def upsert_many(values: Dict[str, Any]) -> None:
    if not values:
        return
    now = datetime.utcnow().isoformat()
    payloads = {key: _serialize(value) for key, value in values.items()}
    with get_connection() as conn:
        for key, payload in payloads.items():
            existing = conn.execute("SELECT key FROM configs WHERE key = ?;", (key,)).fetchone()
            if existing:
                conn.execute(
                    "UPDATE configs SET value = ?, updated_at = ? WHERE key = ?;",
                    (payload, now, key),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO configs (key, value, created_at, updated_at)
                    VALUES (?, ?, ?, ?);
                    """,
                    (key, payload, now, now),
                )
        conn.commit()
