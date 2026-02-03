import os
from typing import Callable, Dict, List, Optional

import pandas as pd

from v2.db.repositories.apontamentos_repo import upsert_apontamentos
from v2.db.repositories.imports_repo import (
    create_import,
    get_import_by_hash,
    log_error,
    update_import_status,
)
from v2.parsers.apontamentos import load_apontamentos
from v2.services.analysis_service import normalize_turno_label
from v2.utils.hash import file_sha256, stable_hash
from v2.utils.logging import get_logger

logger = get_logger(__name__)


def list_excel_files(folder: str) -> List[str]:
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Pasta nao encontrada: {folder}")
    files = []
    for root, _, filenames in os.walk(folder):
        for name in filenames:
            if name.lower().endswith((".xlsx", ".xls", ".xlsm", ".csv")):
                files.append(os.path.join(root, name))
    return sorted(files)


def _normalize_turno(value: str) -> str:
    return normalize_turno_label(value)


def _parse_records(df: pd.DataFrame) -> List[Dict[str, str]]:
    df["Data Cabecalho"] = pd.to_datetime(df["Data Cabecalho"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Data Cabecalho", "Equipamento", "Desc.Turno"])

    records = []
    for _, row in df.iterrows():
        data = row["Data Cabecalho"]
        data_iso = data.date().isoformat()
        equipamento = str(row.get("Equipamento", "")).strip().upper()
        turno = _normalize_turno(row.get("Desc.Turno", ""))
        escala = str(row.get("Escala", "")).strip() or None
        if not equipamento or not turno:
            continue

        raw_hash = stable_hash(data_iso, equipamento, turno, escala or "")
        records.append(
            {
                "data": data_iso,
                "equipamento": equipamento,
                "turno": turno,
                "escala": escala,
                "raw_hash": raw_hash,
            }
        )

    return records


def import_folder(
    folder: str, progress: Optional[Callable[[int, int, str], None]] = None
) -> Dict[str, int]:
    files = list_excel_files(folder)
    total = len(files)
    if total == 0:
        raise ValueError("Nenhum arquivo valido encontrado na pasta selecionada.")
    summary = {"total": total, "importados": 0, "duplicados": 0, "falhas": 0}

    for idx, path in enumerate(files, start=1):
        if progress:
            progress(idx, total, f"Processando {os.path.basename(path)}")
        result = import_file(path)
        if result == "duplicate":
            summary["duplicados"] += 1
        elif result == "success":
            summary["importados"] += 1
        else:
            summary["falhas"] += 1

    if progress:
        progress(total, total, "Finalizado")

    return summary


def import_file(path: str) -> str:
    file_hash = file_sha256(path)
    existing = get_import_by_hash(file_hash)
    if existing and existing["status"] != "error":
        return "duplicate"

    file_name = os.path.basename(path)
    if existing and existing["status"] == "error":
        import_id = existing["id"]
        update_import_status(import_id, "processing", 0, "reprocessamento")
    else:
        import_id = create_import(file_name, file_hash, "processing", 0, "")

    try:
        df = load_apontamentos(path)
        records = _parse_records(df)
        if not records:
            raise ValueError(
                "Arquivo sem linhas validas apos normalizacao (datas/equipamentos/turnos)."
            )
        for rec in records:
            rec["import_id"] = import_id
        resumo = upsert_apontamentos(records)
        rows = resumo["novos"] + resumo["atualizados"]
        update_import_status(import_id, "success", rows, "")
        return "success"
    except Exception as exc:
        logger.error("Falha ao importar %s: %s", path, exc)
        update_import_status(import_id, "error", 0, str(exc))
        log_error(import_id, file_name, str(exc))
        return "error"
