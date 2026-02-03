import json
from datetime import datetime
from typing import Dict, List

from v2.db.connection import get_connection


def list_presets() -> List[Dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, config_json FROM chart_presets ORDER BY name;"
        ).fetchall()
        return [
            {"id": row["id"], "name": row["name"], "config": json.loads(row["config_json"])}
            for row in rows
        ]


def save_preset(name: str, config: Dict) -> None:
    payload = json.dumps(config, ensure_ascii=True)
    with get_connection() as conn:
        row = conn.execute("SELECT id FROM chart_presets WHERE name = ?;", (name,)).fetchone()
        if row is None:
            conn.execute(
                """
                INSERT INTO chart_presets (name, config_json, created_at)
                VALUES (?, ?, ?);
                """,
                (name, payload, datetime.utcnow().isoformat()),
            )
        else:
            conn.execute(
                """
                UPDATE chart_presets
                SET config_json = ?, updated_at = ?
                WHERE name = ?;
                """,
                (payload, datetime.utcnow().isoformat(), name),
            )
        conn.commit()
