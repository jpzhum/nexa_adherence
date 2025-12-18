import pandas as pd
from typing import Callable, Optional, Tuple

from v2.db.connection import get_connection
from v2.services.analysis_service import (
    normalize_turnos,
    create_base,
    pivot_turnos,
    apply_rules,
    apply_exclusions,
    calculate_metrics,
    build_resumos,
)
from v2.services.regras_service import load_regras
from v2.services.config_service import load_config


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
    return df


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
    return df


def consolidate_period(
    data_inicio,
    data_fim,
    progress: Optional[Callable[[int, str], None]] = None,
) -> Tuple[pd.DataFrame, dict]:
    if progress:
        progress(0, "Carregando bases")

    di = data_inicio if isinstance(data_inicio, str) else data_inicio.isoformat()
    df = data_fim if isinstance(data_fim, str) else data_fim.isoformat()

    with get_connection() as conn:
        eqp_df = _load_equipamentos(conn)
        sup_df = _load_supervisores(conn)
        ap_df = _load_apontamentos(conn, di, df)

    if eqp_df.empty:
        raise ValueError("Base de equipamentos vazia.")
    if sup_df.empty:
        raise ValueError("Base de supervisores vazia.")

    if progress:
        progress(1, "Normalizando turnos")

    ap_df = normalize_turnos(ap_df)

    if progress:
        progress(2, "Criando base completa")

    base = create_base(eqp_df, di, df)
    cons = pivot_turnos(ap_df, base)

    if progress:
        progress(3, "Aplicando regras e metricas")

    escala_map = ap_df.groupby(["Data Cabecalho", "Equipamento"])["Escala"].first().reset_index()
    cons = cons.merge(escala_map, on=["Data Cabecalho", "Equipamento"], how="left")
    cons = cons.merge(eqp_df[["Equipamento", "Agrup Equipamento"]], on="Equipamento", how="left")
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
