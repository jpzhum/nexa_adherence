from typing import Callable, Optional, Tuple

import pandas as pd

from v2.db.connection import get_connection
from v2.services.analysis_service import (
    apply_exclusions,
    apply_rules,
    build_resumos,
    calculate_metrics,
    create_base,
    normalize_turnos,
    pivot_turnos,
)
from v2.services.config_service import load_config
from v2.services.regras_service import load_regras
from v2.utils.logging import get_logger

logger = get_logger(__name__)


def _dedup_supervisores_by_agrup(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Agrup Equipamento"] = df["Agrup Equipamento"].astype(str).str.strip().str.upper()
    df["Gestor"] = df["Gestor"].astype(str).str.strip()
    df = df[~df["Agrup Equipamento"].isin({"", "NAN", "NONE"})]

    duplicates = df[df["Agrup Equipamento"].duplicated(keep=False)]
    if not duplicates.empty:
        logger.warning(
            "Foram encontrados agrupamentos com mais de um gestor. Usando o primeiro por agrupamento."
        )
    return df.drop_duplicates(subset=["Agrup Equipamento"], keep="first")


def _load_equipamentos(conn) -> pd.DataFrame:
    df = pd.read_sql_query(
        "SELECT codigo, classe, agrupamento FROM equipamentos;",
        conn,
    )
    df = df.rename(
        columns={
            "codigo": "Equipamento",
            "classe": "Dsc Classe",
            "agrupamento": "Agrup Equipamento",
        }
    )
    return df


def _load_supervisores(conn) -> pd.DataFrame:
    df = pd.read_sql_query("SELECT nome, agrupamento FROM supervisores;", conn)
    df = df.rename(columns={"nome": "Gestor", "agrupamento": "Agrup Equipamento"})
    return _dedup_supervisores_by_agrup(df)


def _load_apontamentos(conn, data_inicio, data_fim) -> pd.DataFrame:
    df = pd.read_sql_query(
        "SELECT data, equipamento, turno, escala FROM apontamentos WHERE data BETWEEN ? AND ?;",
        conn,
        params=(data_inicio, data_fim),
    )
    df = df.rename(
        columns={
            "data": "Data Cabecalho",
            "equipamento": "Equipamento",
            "turno": "Desc.Turno",
            "escala": "Escala",
        }
    )
    df["Equipamento"] = df["Equipamento"].astype(str).str.strip().str.upper()
    return df


def consolidate_period(
    data_inicio,
    data_fim,
    progress: Optional[Callable[[int, str], None]] = None,
) -> Tuple[pd.DataFrame, dict]:
    if data_inicio > data_fim:
        raise ValueError("Data inicial maior que data final.")

    if progress:
        progress(0, "Carregando bases")

    data_inicio_iso = data_inicio if isinstance(data_inicio, str) else data_inicio.isoformat()
    data_fim_iso = data_fim if isinstance(data_fim, str) else data_fim.isoformat()

    with get_connection() as conn:
        eqp_df = _load_equipamentos(conn)
        sup_df = _load_supervisores(conn)
        ap_df = _load_apontamentos(conn, data_inicio_iso, data_fim_iso)

    if eqp_df.empty:
        raise ValueError("Base de equipamentos vazia.")
    if sup_df.empty:
        raise ValueError("Base de supervisores vazia.")

    if progress:
        progress(1, "Normalizando turnos")

    ap_df = normalize_turnos(ap_df)

    if progress:
        progress(2, "Criando base completa")

    base = create_base(eqp_df, data_inicio_iso, data_fim_iso)
    cons = pivot_turnos(ap_df, base)

    if progress:
        progress(3, "Aplicando regras e metricas")

    escala_map = ap_df.groupby(["Data Cabecalho", "Equipamento"])["Escala"].first().reset_index()
    cons = cons.merge(escala_map, on=["Data Cabecalho", "Equipamento"], how="left")
    eqp_df["Equipamento"] = eqp_df["Equipamento"].astype(str).str.strip().str.upper()
    eqp_df["Agrup Equipamento"] = eqp_df["Agrup Equipamento"].astype(str).str.strip().str.upper()
    cons = cons.merge(eqp_df[["Equipamento", "Agrup Equipamento"]], on="Equipamento", how="left")
    cons["Agrup Equipamento"] = cons["Agrup Equipamento"].astype(str).str.strip().str.upper()
    cons.loc[cons["Agrup Equipamento"].isin({"", "NAN", "NONE"}), "Agrup Equipamento"] = None
    cons = cons.merge(sup_df[["Agrup Equipamento", "Gestor"]], on="Agrup Equipamento", how="left")
    cons["Agrup Equipamento"] = cons["Agrup Equipamento"].fillna("Nao Informado")
    cons["Gestor"] = cons["Gestor"].fillna("Nao Informado")

    regras = load_regras()
    cons = apply_rules(cons, regras=regras)
    cfg = load_config()
    cons = apply_exclusions(
        cons,
        exclusions_agrup=cfg.get("exclusions_agrup", []),
        exclusions_frota=cfg.get("exclusions_frota", []),
    )
    final = calculate_metrics(cons)
    resumos = build_resumos(final)

    if progress:
        progress(4, "Finalizado")

    return final, resumos
