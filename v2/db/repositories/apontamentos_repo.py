from datetime import datetime
from typing import Dict, Iterable

from v2.db.connection import get_connection


def upsert_apontamentos(records: Iterable[Dict[str, str]]) -> Dict[str, int]:
    novos = 0
    atualizados = 0
    ignorados = 0
    now = datetime.utcnow().isoformat()

    with get_connection() as conn:
        for rec in records:
            row = conn.execute(
                "SELECT escala, raw_hash FROM apontamentos WHERE data = ? AND equipamento = ? AND turno = ?;",
                (rec["data"], rec["equipamento"], rec["turno"]),
            ).fetchone()

            if row is None:
                conn.execute(
                    """
                    INSERT INTO apontamentos
                    (import_id, data, equipamento, turno, escala, status, aderencia, entregues, faltantes, raw_hash, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        rec.get("import_id"),
                        rec["data"],
                        rec["equipamento"],
                        rec["turno"],
                        rec.get("escala"),
                        None,
                        None,
                        None,
                        None,
                        rec.get("raw_hash"),
                        now,
                    ),
                )
                novos += 1
                continue

            unchanged = (row["escala"] or "") == (rec.get("escala") or "") and (row["raw_hash"] or "") == (
                rec.get("raw_hash") or ""
            )
            if unchanged:
                ignorados += 1
                continue

            conn.execute(
                """
                UPDATE apontamentos
                SET escala = ?, raw_hash = ?
                WHERE data = ? AND equipamento = ? AND turno = ?;
                """,
                (rec.get("escala"), rec.get("raw_hash"), rec["data"], rec["equipamento"], rec["turno"]),
            )
            atualizados += 1

        conn.commit()

    return {"novos": novos, "atualizados": atualizados, "ignorados": ignorados}
