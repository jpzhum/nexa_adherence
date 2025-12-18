from datetime import datetime
from typing import Dict, List, Optional

from v2.db.connection import get_connection


def list_regras() -> List[Dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, tipo, nome, turno, escala FROM regras_turnos ORDER BY tipo, nome;"
        ).fetchall()
        return [
            {
                "id": row["id"],
                "tipo": row["tipo"],
                "nome": row["nome"],
                "turno": row["turno"],
                "escala": row["escala"],
            }
            for row in rows
        ]


def get_regra(tipo: str, nome: str) -> Optional[Dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, tipo, nome, turno, escala FROM regras_turnos WHERE tipo = ? AND nome = ?;",
            (tipo, nome),
        ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "tipo": row["tipo"],
            "nome": row["nome"],
            "turno": row["turno"],
            "escala": row["escala"],
        }


def upsert_regra(tipo: str, nome: str, turno: str, escala: str) -> None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM regras_turnos WHERE tipo = ? AND nome = ?;",
            (tipo, nome),
        ).fetchone()
        if row is None:
            conn.execute(
                """
                INSERT INTO regras_turnos (tipo, nome, turno, escala, updated_at)
                VALUES (?, ?, ?, ?, ?);
                """,
                (tipo, nome, turno, escala, datetime.utcnow().isoformat()),
            )
        else:
            conn.execute(
                """
                UPDATE regras_turnos
                SET turno = ?, escala = ?, updated_at = ?
                WHERE tipo = ? AND nome = ?;
                """,
                (turno, escala, datetime.utcnow().isoformat(), tipo, nome),
            )
        conn.commit()


def delete_regra(rule_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM regras_turnos WHERE id = ?;", (rule_id,))
        conn.commit()
