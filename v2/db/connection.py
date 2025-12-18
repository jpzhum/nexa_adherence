import os
import sqlite3
from typing import Optional

DEFAULT_DB_NAME = "nexa_v2.db"


def get_db_path() -> str:
    env_path = os.environ.get("NEXA_V2_DB_PATH")
    if env_path:
        return os.path.abspath(env_path)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, DEFAULT_DB_NAME)


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = db_path or get_db_path()
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
