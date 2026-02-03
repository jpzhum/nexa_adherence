import sqlite3
from datetime import datetime
from typing import Optional

from v2.db.connection import get_connection
from v2.utils.logging import get_logger

logger = get_logger(__name__)

SCHEMA_VERSION = 4


def ensure_schema(conn: Optional[sqlite3.Connection] = None) -> None:
    owns_conn = conn is None
    conn = conn or get_connection()
    try:
        _bootstrap_version_table(conn)
        current_version = _get_current_version(conn)

        if current_version is None:
            logger.info("Criando schema v2 versao %s", SCHEMA_VERSION)
            _apply_migration_1(conn)
            _apply_migration_2(conn)
            _apply_migration_3(conn)
            _apply_migration_4(conn)
            _set_version(conn, SCHEMA_VERSION)
        elif current_version < SCHEMA_VERSION:
            logger.info("Migrando schema v2 de %s para %s", current_version, SCHEMA_VERSION)
            _run_migrations(conn, current_version)
    finally:
        if owns_conn:
            conn.close()


def _bootstrap_version_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER NOT NULL,
            applied_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def _get_current_version(conn: sqlite3.Connection) -> Optional[int]:
    cur = conn.execute("SELECT version FROM schema_version ORDER BY rowid DESC LIMIT 1;")
    row = cur.fetchone()
    return row["version"] if row else None


def _set_version(conn: sqlite3.Connection, version: int) -> None:
    conn.execute(
        "INSERT INTO schema_version (version, applied_at) VALUES (?, ?);",
        (version, datetime.utcnow().isoformat()),
    )
    conn.commit()


def _run_migrations(conn: sqlite3.Connection, current_version: int) -> None:
    if current_version < 1:
        _apply_migration_1(conn)
    if current_version < 2:
        _apply_migration_2(conn)
    if current_version < 3:
        _apply_migration_3(conn)
    if current_version < 4:
        _apply_migration_4(conn)
    _set_version(conn, SCHEMA_VERSION)


def _apply_migration_1(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS imports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            file_hash TEXT NOT NULL UNIQUE,
            imported_at TEXT NOT NULL,
            status TEXT NOT NULL,
            rows_imported INTEGER DEFAULT 0,
            message TEXT
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_imports_name ON imports(file_name);")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            descricao TEXT,
            classe TEXT,
            agrupamento TEXT,
            ativo INTEGER DEFAULT 1,
            atualizado_em TEXT
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_equipamentos_codigo ON equipamentos(codigo);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_equipamentos_agrup ON equipamentos(agrupamento);")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS apontamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            import_id INTEGER,
            data TEXT NOT NULL,
            equipamento TEXT NOT NULL,
            turno TEXT,
            escala TEXT,
            status TEXT,
            aderencia REAL,
            entregues INTEGER,
            faltantes INTEGER,
            raw_hash TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (data, equipamento, turno),
            FOREIGN KEY (import_id) REFERENCES imports(id) ON DELETE SET NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_apont_eqp_data ON apontamentos(equipamento, data);"
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_apont_status ON apontamentos(status);")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS erros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            import_id INTEGER,
            file_name TEXT,
            error_message TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (import_id) REFERENCES imports(id) ON DELETE CASCADE
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chart_presets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            config_json TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT
        )
        """
    )

    conn.commit()


def _apply_migration_2(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS supervisores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT NOT NULL UNIQUE,
            nome TEXT,
            email TEXT,
            matricula TEXT,
            agrupamento TEXT,
            atualizado_em TEXT
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_supervisores_chave ON supervisores(chave);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_supervisores_agrup ON supervisores(agrupamento);")
    conn.commit()


def _apply_migration_3(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS regras_turnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            nome TEXT NOT NULL,
            turno TEXT,
            escala TEXT,
            updated_at TEXT,
            UNIQUE (tipo, nome)
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_regras_tipo ON regras_turnos(tipo);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_regras_nome ON regras_turnos(nome);")
    conn.commit()


def _apply_migration_4(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS configs (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
