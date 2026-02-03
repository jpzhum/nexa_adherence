from typing import Dict, List

from v2.db.repositories.equipamentos_repo import upsert_equipamentos
from v2.db.repositories.supervisores_repo import upsert_supervisores
from v2.parsers.equipamentos import load_equipamentos
from v2.parsers.supervisores import load_supervisores


def _dedup_records(records: List[dict], key: str) -> List[dict]:
    dedup = {}
    for rec in records:
        dedup[rec[key]] = rec
    return list(dedup.values())


def update_equipamentos_from_excel(path: str) -> Dict[str, int]:
    df = load_equipamentos(path)
    records = []
    for _, row in df.iterrows():
        codigo = str(row.get("Equipamento", "")).strip().upper()
        if not codigo:
            continue
        agrupamento = str(row.get("Agrup Equipamento", "")).strip().upper()
        records.append(
            {
                "codigo": codigo,
                "descricao": str(row.get("Descricao", "")).strip() or None,
                "classe": str(row.get("Dsc Classe", "")).strip() or None,
                "agrupamento": agrupamento or None,
                "ativo": 1,
            }
        )

    records = _dedup_records(records, "codigo")
    return upsert_equipamentos(records)


def _build_supervisor_key(row) -> str:
    email = str(row.get("Email", "")).strip().lower()
    matricula = str(row.get("Matricula", "")).strip()
    id_supervisor = str(row.get("Id Supervisor", "")).strip()
    nome = str(row.get("Gestor", "")).strip()
    agrup = str(row.get("Agrup Equipamento", "")).strip().upper()

    if email:
        return email
    if matricula:
        return f"matricula:{matricula}"
    if id_supervisor:
        return f"id:{id_supervisor}"
    return f"{nome}|{agrup}".strip("|")


def update_supervisores_from_excel(path: str) -> Dict[str, int]:
    df = load_supervisores(path)
    records = []
    for _, row in df.iterrows():
        nome = str(row.get("Gestor", "")).strip()
        agrup = str(row.get("Agrup Equipamento", "")).strip().upper()
        if not nome and not agrup:
            continue
        records.append(
            {
                "chave": _build_supervisor_key(row),
                "nome": nome or None,
                "email": str(row.get("Email", "")).strip().lower() or None,
                "matricula": str(row.get("Matricula", "")).strip() or None,
                "agrupamento": agrup or None,
            }
        )

    records = _dedup_records(records, "chave")
    return upsert_supervisores(records)
