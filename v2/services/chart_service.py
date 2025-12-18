from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List, Optional

import pandas as pd


@dataclass
class QuerySpec:
    metric: str
    group_by: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    exclude_groups: Optional[List[str]] = None


@dataclass
class ChartConfig:
    name: str
    query: QuerySpec


def _apply_date_filter(df: pd.DataFrame, start_date: Optional[str], end_date: Optional[str]) -> pd.DataFrame:
    if "Data Cabecalho" not in df.columns:
        return df
    df = df.copy()
    df["Data Cabecalho"] = pd.to_datetime(df["Data Cabecalho"], errors="coerce")
    if start_date:
        df = df[df["Data Cabecalho"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["Data Cabecalho"] <= pd.to_datetime(end_date)]
    return df


def _apply_exclusions(df: pd.DataFrame, group_by: str, exclude: Optional[Iterable[str]]) -> pd.DataFrame:
    if not exclude:
        return df
    values = {str(v).strip().lower() for v in exclude}
    return df[~df[group_by].astype(str).str.strip().str.lower().isin(values)]


def build_dataset(df: pd.DataFrame, query: QuerySpec) -> pd.DataFrame:
    df = _apply_date_filter(df, query.start_date, query.end_date)

    if query.group_by not in df.columns:
        raise ValueError(f"Agrupamento invalido: {query.group_by}")
    df = _apply_exclusions(df, query.group_by, query.exclude_groups)

    if query.metric == "aderencia_media":
        result = df.groupby(query.group_by)["Aderencia"].mean().round(2).reset_index()
        result = result.rename(columns={"Aderencia": "Valor"})
        return result
    if query.metric == "entregues":
        result = df.groupby(query.group_by)["Entregues"].sum().reset_index()
        result = result.rename(columns={"Entregues": "Valor"})
        return result
    if query.metric == "faltantes":
        result = df.groupby(query.group_by)["Faltantes"].sum().reset_index()
        result = result.rename(columns={"Faltantes": "Valor"})
        return result

    raise ValueError(f"Metrica invalida: {query.metric}")


def config_to_dict(cfg: ChartConfig) -> Dict:
    raw = asdict(cfg)
    return raw
