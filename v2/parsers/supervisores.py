import pandas as pd

from v2.parsers.common import ensure_required_columns, read_table_file
from v2.utils.validators import normalize_headers

REQUIRED_COLUMNS = ["Gestor", "Agrup Equipamento"]


def load_supervisores(path: str) -> pd.DataFrame:
    df = read_table_file(path)
    df = normalize_headers(df)

    if "Supervisor" in df.columns and "Gestor" not in df.columns:
        df = df.rename(columns={"Supervisor": "Gestor"})
    if "Nome" in df.columns and "Gestor" not in df.columns:
        df = df.rename(columns={"Nome": "Gestor"})
    if "Agrupamento" in df.columns:
        df = df.rename(columns={"Agrupamento": "Agrup Equipamento"})
    if "Agrup. Equipamento" in df.columns:
        df = df.rename(columns={"Agrup. Equipamento": "Agrup Equipamento"})
    if "E-Mail" in df.columns and "Email" not in df.columns:
        df = df.rename(columns={"E-Mail": "Email"})

    ensure_required_columns(df, REQUIRED_COLUMNS, "Supervisores")

    return df
