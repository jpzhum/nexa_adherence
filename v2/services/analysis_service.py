from typing import Optional

import pandas as pd


def normalize_turnos(df: pd.DataFrame) -> pd.DataFrame:
    if "Desc.Turno" not in df.columns or "Data Cabecalho" not in df.columns:
        raise ValueError("Colunas obrigatorias ausentes: Desc.Turno ou Data Cabecalho")
    df["Desc.Turno"] = df["Desc.Turno"].astype(str).str.upper().str.strip()
    df["Desc.Turno"] = df["Desc.Turno"].replace({"TURNO ADM": "TURNO A", "CATACAO": "TURNO A"})
    df["Data Cabecalho"] = pd.to_datetime(df["Data Cabecalho"], dayfirst=True, errors="coerce")
    if "Equipamento" in df.columns:
        df["Equipamento"] = df["Equipamento"].astype(str).str.strip()
    return df


def create_base(df_equipamentos: pd.DataFrame, data_inicio, data_fim) -> pd.DataFrame:
    if "Equipamento" not in df_equipamentos.columns:
        raise ValueError("Coluna 'Equipamento' ausente.")
    df_equipamentos["Equipamento"] = df_equipamentos["Equipamento"].astype(str).str.strip()
    frotas = df_equipamentos["Equipamento"].dropna().unique()
    datas = pd.date_range(data_inicio, data_fim)
    return pd.MultiIndex.from_product([datas, frotas], names=["Data Cabecalho", "Equipamento"]).to_frame(index=False)


def pivot_turnos(df: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    df["Data Cabecalho"] = pd.to_datetime(df["Data Cabecalho"], errors="coerce")
    base["Data Cabecalho"] = pd.to_datetime(base["Data Cabecalho"], errors="coerce")
    df["Equipamento"] = df["Equipamento"].astype(str).str.strip()
    base["Equipamento"] = base["Equipamento"].astype(str).str.strip()

    if df.empty:
        for turno in ["TURNO A", "TURNO B", "TURNO C"]:
            base[turno] = "-"
        return base

    pivot_df = pd.crosstab(index=[df["Data Cabecalho"], df["Equipamento"]], columns=df["Desc.Turno"])
    pivot_df = pivot_df.apply(lambda col: col.map(lambda x: "OK" if x > 0 else "-"))
    pivot_df = pivot_df.reset_index()
    return base.merge(pivot_df, on=["Data Cabecalho", "Equipamento"], how="left").fillna("-")


def apply_rules(df_base: pd.DataFrame, feriados: Optional[list] = None, regras: Optional[dict] = None) -> pd.DataFrame:
    if "Escala" not in df_base.columns:
        df_base["Escala"] = "PADRAO"
    df_base["Escala"] = df_base["Escala"].fillna("PADRAO")
    df_base["Escala"] = df_base["Escala"].astype(str).str.strip().str.upper()
    if "Data Cabecalho" in df_base.columns:
        df_base["Data Cabecalho"] = pd.to_datetime(df_base["Data Cabecalho"], errors="coerce")
    if "Equipamento" in df_base.columns:
        df_base["Equipamento"] = df_base["Equipamento"].astype(str).str.strip().str.lower()
    if "Agrup Equipamento" in df_base.columns:
        df_base["Agrup Equipamento"] = df_base["Agrup Equipamento"].astype(str).str.strip().str.lower()

    regras = regras or {}
    rg_agr = regras.get("agrupamento", {})
    rg_fro = regras.get("frota", {})
    if rg_agr and "Agrup Equipamento" in df_base.columns:
        df_base["Escala"] = df_base.apply(
            lambda r: rg_agr.get(r["Agrup Equipamento"], {}).get("escala", r["Escala"]), axis=1
        )
    if rg_fro and "Equipamento" in df_base.columns:
        df_base["Escala"] = df_base.apply(
            lambda r: rg_fro.get(r["Equipamento"], {}).get("escala", r["Escala"]), axis=1
        )
    feriados = feriados or []
    mask_adm = df_base["Escala"] == "ADM"
    for t in ["TURNO B", "TURNO C"]:
        if t in df_base.columns:
            df_base.loc[mask_adm, t] = "-"
    if "Data Cabecalho" in df_base.columns:
        is_weekend = df_base["Data Cabecalho"].dt.weekday >= 5
        is_feriado = df_base["Data Cabecalho"].isin(feriados)
        remover = df_base[mask_adm & (is_weekend | is_feriado)].index
        if len(remover) > 0:
            df_base = df_base.drop(remover)
    if "Equipamento" in df_base.columns:
        df_base["Equipamento"] = df_base["Equipamento"].astype(str).str.upper()
    if "Agrup Equipamento" in df_base.columns:
        df_base["Agrup Equipamento"] = df_base["Agrup Equipamento"].astype(str)
    return df_base


def apply_exclusions(
    df_base: pd.DataFrame, exclusions_agrup: Optional[list] = None, exclusions_frota: Optional[list] = None
) -> pd.DataFrame:
    exclusions_agrup = exclusions_agrup or []
    exclusions_frota = exclusions_frota or []
    if exclusions_agrup and "Agrup Equipamento" in df_base.columns:
        df_base = df_base[
            ~df_base["Agrup Equipamento"].astype(str).str.strip().isin([e.strip() for e in exclusions_agrup])
        ]
    if exclusions_frota and "Equipamento" in df_base.columns:
        df_base = df_base[
            ~df_base["Equipamento"].astype(str).str.strip().isin([e.strip() for e in exclusions_frota])
        ]
    return df_base


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    turnos = ["TURNO A", "TURNO B", "TURNO C"]
    for t in turnos:
        if t not in df.columns:
            df[t] = "-"
    if "Escala" not in df.columns:
        df["Escala"] = "PADRAO"

    def entregues(row):
        if row["Escala"] == "ADM":
            return 1 if row["TURNO A"] == "OK" else 0
        return sum(1 for t in turnos if row[t] == "OK")

    df["Entregues"] = df.apply(entregues, axis=1)
    df["Faltantes"] = df.apply(
        lambda r: (1 if r["Escala"] == "ADM" else len(turnos)) - r["Entregues"], axis=1
    )
    df["Aderencia"] = df.apply(
        lambda r: round((r["Entregues"] / (1 if r["Escala"] == "ADM" else len(turnos))) * 100, 2), axis=1
    )
    df["Status"] = df.apply(
        lambda r: "Completo"
        if r["Entregues"] == (1 if r["Escala"] == "ADM" else 3)
        else ("Ausente" if r["Entregues"] == 0 else "Incompleto"),
        axis=1,
    )
    return df


def build_resumos(df: pd.DataFrame) -> dict:
    if "Gestor" not in df.columns:
        df["Gestor"] = "Nao Informado"
    if "Agrup Equipamento" not in df.columns:
        df["Agrup Equipamento"] = "Nao Informado"

    resumo_status = df.groupby(["Gestor", "Agrup Equipamento", "Status"]).size().unstack(fill_value=0)
    resumo_aderencia = df.groupby(["Gestor", "Agrup Equipamento"])["Aderencia"].mean().round(2)
    indicadores = pd.DataFrame(
        {
            "Aderencia Media Global": [df["Aderencia"].mean().round(2)],
            "Total Esperado": [sum(1 if r.get("Escala") == "ADM" else 3 for _, r in df.iterrows())],
            "Total Entregue": [df["Entregues"].sum()],
        }
    )
    return {
        "Resumo Status": resumo_status,
        "Aderencia Agrupamento": resumo_aderencia,
        "Indicadores Gerais": indicadores,
    }
