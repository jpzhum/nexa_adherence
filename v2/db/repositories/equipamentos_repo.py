from datetime import datetime
from typing import Dict, Iterable

from v2.db.connection import get_connection


def upsert_equipamentos(records: Iterable[Dict[str, str]]) -> Dict[str, int]:
    novos = 0
    atualizados = 0
    ignorados = 0
    now = datetime.utcnow().isoformat()

    with get_connection() as conn:
        for rec in records:
            codigo = rec["codigo"]
            row = conn.execute(
                "SELECT descricao, classe, agrupamento, ativo FROM equipamentos WHERE codigo = ?;",
                (codigo,),
            ).fetchone()

            if row is None:
                conn.execute(
                    """
                    INSERT INTO equipamentos (codigo, descricao, classe, agrupamento, ativo, atualizado_em)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (
                        codigo,
                        rec.get("descricao"),
                        rec.get("classe"),
                        rec.get("agrupamento"),
                        rec.get("ativo", 1),
                        now,
                    ),
                )
                novos += 1
                continue

            unchanged = (
                (row["descricao"] or "") == (rec.get("descricao") or "")
                and (row["classe"] or "") == (rec.get("classe") or "")
                and (row["agrupamento"] or "") == (rec.get("agrupamento") or "")
                and int(row["ativo"] or 0) == int(rec.get("ativo", 1))
            )
            if unchanged:
                ignorados += 1
                continue

            conn.execute(
                """
                UPDATE equipamentos
                SET descricao = ?, classe = ?, agrupamento = ?, ativo = ?, atualizado_em = ?
                WHERE codigo = ?;
                """,
                (
                    rec.get("descricao"),
                    rec.get("classe"),
                    rec.get("agrupamento"),
                    rec.get("ativo", 1),
                    now,
                    codigo,
                ),
            )
            atualizados += 1

        conn.commit()

    return {"novos": novos, "atualizados": atualizados, "ignorados": ignorados}
