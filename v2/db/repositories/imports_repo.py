from datetime import datetime
from typing import Dict, Optional

from v2.db.connection import get_connection


def get_import_by_hash(file_hash: str) -> Optional[Dict[str, str]]:
    with get_connection() as conn:
        row = conn.execute("SELECT id, status FROM imports WHERE file_hash = ?;", (file_hash,)).fetchone()
        return {"id": row["id"], "status": row["status"]} if row else None


def create_import(file_name: str, file_hash: str, status: str, rows_imported: int = 0, message: str = "") -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO imports (file_name, file_hash, imported_at, status, rows_imported, message)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (file_name, file_hash, datetime.utcnow().isoformat(), status, rows_imported, message),
        )
        conn.commit()
        return int(cur.lastrowid)


def update_import_status(import_id: int, status: str, rows_imported: int = 0, message: str = "") -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE imports
            SET status = ?, rows_imported = ?, message = ?
            WHERE id = ?;
            """,
            (status, rows_imported, message, import_id),
        )
        conn.commit()


def log_error(import_id: Optional[int], file_name: str, error_message: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO erros (import_id, file_name, error_message) VALUES (?, ?, ?);",
            (import_id, file_name, error_message),
        )
        conn.commit()
