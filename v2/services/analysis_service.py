import unicodedata
from typing import Optional

import pandas as pd

EXPECTED_TURNOS = ("TURNO A", "TURNO B", "TURNO C")
OUTROS_TURNO = "OUTROS"


def _normalize_text(value: object) -> str:
    text = str(value or "").strip().upper()
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return " ".join(text.split())


def normalize_turno_label(value: object) -> str:
    text = _normalize_text(value)
    if not text:
        return ""
    alias = {
        "TURNO ADM": "TURNO A",
        "CATACAO": "TURNO A",
        "CATAÇÃO": "TURNO A",
        "CATA?AO": "TURNO A",
        "ADM": "TURNO A",
        "A": "TURNO A",
        "B": "TURNO B",
        "C": "TURNO C",
    }
    if text in alias:
        return alias[text]
    if text in EXPECTED_TURNOS:
        return text
    return OUTROS_TURNO


def normalize_turnos(df: pd.DataFrame) -> pd.DataFrame:
    if "Desc.Turno" not in df.columns or "Data Cabecalho" not in df.columns:
        raise ValueError("Colunas obrigatorias ausentes: Desc.Turno ou Data Cabecalho")
    df["Desc.Turno"] = df["Desc.Turno"].map(normalize_turno_label)
    df["Data Cabecalho"] = pd.to_datetime(df["Data Cabecalho"], dayfirst=True, errors="coerce")
    if "Equipamento" in df.columns:
        df["Equipamento"] = df["Equipamento"].astype(str).str.strip().str.upper()
    return df


def create_base(df_equipamentos: pd.DataFrame, data_inicio, data_fim) -> pd.DataFrame:
    if "Equipamento" not in df_equipamentos.columns:
        raise ValueError("Coluna 'Equipamento' ausente.")
    df_equipamentos["Equipamento"] = (
        df_equipamentos["Equipamento"].astype(str).str.strip().str.upper()
    )
    frotas = df_equipamentos["Equipamento"]
    frotas = frotas[(frotas != "") & (frotas != "NAN") & (frotas != "NONE")].dropna().unique()
    if len(frotas) == 0:
        raise ValueError("Base de equipamentos sem codigos validos.")
    datas = pd.date_range(data_inicio, data_fim)
    return pd.MultiIndex.from_product(
        [datas, frotas], names=["Data Cabecalho", "Equipamento"]
    ).to_frame(index=False)


def pivot_turnos(df: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    df["Data Cabecalho"] = pd.to_datetime(df["Data Cabecalho"], errors="coerce")
    base["Data Cabecalho"] = pd.to_datetime(base["Data Cabecalho"], errors="coerce")
    df["Equipamento"] = df["Equipamento"].astype(str).str.strip().str.upper()
    base["Equipamento"] = base["Equipamento"].astype(str).str.strip().str.upper()

    if df.empty:
        for turno in EXPECTED_TURNOS:
            base[turno] = "-"
        return base

    pivot_df = pd.crosstab(
        index=[df["Data Cabecalho"], df["Equipamento"]], columns=df["Desc.Turno"]
    )
    pivot_df = pivot_df.apply(lambda col: col.map(lambda x: "OK" if x > 0 else "-"))
    pivot_df = pivot_df.reset_index()
    merged = base.merge(pivot_df, on=["Data Cabecalho", "Equipamento"], how="left").fillna("-")
    for turno in EXPECTED_TURNOS:
        if turno not in merged.columns:
            merged[turno] = "-"
    return merged


def apply_rules(
    df_base: pd.DataFrame, feriados: Optional[list] = None, regras: Optional[dict] = None
) -> pd.DataFrame:
    if "Escala" not in df_base.columns:
        df_base["Escala"] = "PADRAO"
    df_base["Escala"] = df_base["Escala"].fillna("PADRAO")
    df_base["Escala"] = df_base["Escala"].astype(str).str.strip().str.upper()
    if "Data Cabecalho" in df_base.columns:
        df_base["Data Cabecalho"] = pd.to_datetime(df_base["Data Cabecalho"], errors="coerce")
    if "Equipamento" in df_base.columns:
        df_base["Equipamento"] = df_base["Equipamento"].astype(str).str.strip().str.lower()
    if "Agrup Equipamento" in df_base.columns:
        df_base["Agrup Equipamento"] = (
            df_base["Agrup Equipamento"].astype(str).str.strip().str.lower()
        )

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
    feriados = pd.to_datetime(feriados or [], errors="coerce")
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
        df_base.loc[df_base["Equipamento"].isin({"NAN", "NONE"}), "Equipamento"] = ""
    if "Agrup Equipamento" in df_base.columns:
        df_base["Agrup Equipamento"] = df_base["Agrup Equipamento"].astype(str)
        df_base.loc[
            df_base["Agrup Equipamento"].str.upper().isin({"NAN", "NONE"}),
            "Agrup Equipamento",
        ] = "Nao Informado"
    return df_base


def apply_exclusions(
    df_base: pd.DataFrame,
    exclusions_agrup: Optional[list] = None,
    exclusions_frota: Optional[list] = None,
) -> pd.DataFrame:
    exclusions_agrup = exclusions_agrup or []
    exclusions_frota = exclusions_frota or []
    if exclusions_agrup and "Agrup Equipamento" in df_base.columns:
        excluded_agrup = {e.strip().upper() for e in exclusions_agrup if e and e.strip()}
        df_base = df_base[
            ~df_base["Agrup Equipamento"].astype(str).str.strip().str.upper().isin(excluded_agrup)
        ]
    if exclusions_frota and "Equipamento" in df_base.columns:
        excluded_frota = {e.strip().upper() for e in exclusions_frota if e and e.strip()}
        df_base = df_base[
            ~df_base["Equipamento"].astype(str).str.strip().str.upper().isin(excluded_frota)
        ]
    return df_base


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    for t in EXPECTED_TURNOS:
        if t not in df.columns:
            df[t] = "-"
    if "Escala" not in df.columns:
        df["Escala"] = "PADRAO"

    def entregues(row):
        if row["Escala"] == "ADM":
            return 1 if row["TURNO A"] == "OK" else 0
        return sum(1 for t in EXPECTED_TURNOS if row[t] == "OK")

    df["Entregues"] = df.apply(entregues, axis=1)
    df["Faltantes"] = df.apply(
        lambda r: (1 if r["Escala"] == "ADM" else len(EXPECTED_TURNOS)) - r["Entregues"], axis=1
    )
    df["Aderencia"] = df.apply(
        lambda r: round(
            (r["Entregues"] / (1 if r["Escala"] == "ADM" else len(EXPECTED_TURNOS))) * 100, 2
        ),
        axis=1,
    )
    df["Status"] = df.apply(
        lambda r: "Completo"
        if r["Entregues"] == (1 if r["Escala"] == "ADM" else 3)
        else ("Ausente" if r["Entregues"] == 0 else "Incompleto"),
        axis=1,
    )
    return df


def build_resumos(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "Resumo Status": pd.DataFrame(),
            "Aderencia Agrupamento": pd.Series(dtype=float),
            "Indicadores Gerais": pd.DataFrame(
                {"Aderencia Media Global": [0.0], "Total Esperado": [0], "Total Entregue": [0]}
            ),
        }
    if "Gestor" not in df.columns:
        df["Gestor"] = "Nao Informado"
    if "Agrup Equipamento" not in df.columns:
        df["Agrup Equipamento"] = "Nao Informado"

    resumo_status = (
        df.groupby(["Gestor", "Agrup Equipamento", "Status"]).size().unstack(fill_value=0)
    )
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
