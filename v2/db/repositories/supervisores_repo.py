from datetime import datetime
from typing import Dict, Iterable

from v2.db.connection import get_connection


def upsert_supervisores(records: Iterable[Dict[str, str]]) -> Dict[str, int]:
    novos = 0
    atualizados = 0
    ignorados = 0
    now = datetime.utcnow().isoformat()

    with get_connection() as conn:
        for rec in records:
            chave = rec["chave"]
            row = conn.execute(
                "SELECT nome, email, matricula, agrupamento FROM supervisores WHERE chave = ?;",
                (chave,),
            ).fetchone()

            if row is None:
                conn.execute(
                    """
                    INSERT INTO supervisores (chave, nome, email, matricula, agrupamento, atualizado_em)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (
                        chave,
                        rec.get("nome"),
                        rec.get("email"),
                        rec.get("matricula"),
                        rec.get("agrupamento"),
                        now,
                    ),
                )
                novos += 1
                continue

            unchanged = (
                (row["nome"] or "") == (rec.get("nome") or "")
                and (row["email"] or "") == (rec.get("email") or "")
                and (row["matricula"] or "") == (rec.get("matricula") or "")
                and (row["agrupamento"] or "") == (rec.get("agrupamento") or "")
            )
            if unchanged:
                ignorados += 1
                continue

            conn.execute(
                """
                UPDATE supervisores
                SET nome = ?, email = ?, matricula = ?, agrupamento = ?, atualizado_em = ?
                WHERE chave = ?;
                """,
                (
                    rec.get("nome"),
                    rec.get("email"),
                    rec.get("matricula"),
                    rec.get("agrupamento"),
                    now,
                    chave,
                ),
            )
            atualizados += 1

        conn.commit()

    return {"novos": novos, "atualizados": atualizados, "ignorados": ignorados}
