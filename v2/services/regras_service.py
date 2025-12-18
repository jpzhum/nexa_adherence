from typing import Dict, List

from v2.db.repositories.regras_repo import list_regras


def load_regras() -> Dict[str, Dict[str, Dict[str, str]]]:
    regras = list_regras()
    regras_por_tipo = {"agrupamento": {}, "frota": {}}
    for regra in regras:
        tipo = (regra["tipo"] or "").strip().lower()
        nome = (regra["nome"] or "").strip().lower()
        if tipo not in regras_por_tipo or not nome:
            continue
        regras_por_tipo[tipo][nome] = {
            "turno": (regra["turno"] or "").strip().upper(),
            "escala": (regra["escala"] or "").strip().upper(),
        }
    return regras_por_tipo
