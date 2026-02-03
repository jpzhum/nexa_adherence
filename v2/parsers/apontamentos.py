import pandas as pd

from v2.parsers.common import ensure_required_columns, read_table_file
from v2.utils.validators import normalize_headers

REQUIRED_COLUMNS = ["Data Cabecalho", "Equipamento", "Desc.Turno"]


def load_apontamentos(path: str) -> pd.DataFrame:
    df = read_table_file(path)
    df = normalize_headers(df)

    if "Data Cabecalho" not in df.columns and "Data" in df.columns:
        df = df.rename(columns={"Data": "Data Cabecalho"})
    if "Desc.Turno" not in df.columns:
        if "Desc Turno" in df.columns:
            df = df.rename(columns={"Desc Turno": "Desc.Turno"})
        elif "Turno" in df.columns:
            df = df.rename(columns={"Turno": "Desc.Turno"})
    if "Equipamento" not in df.columns and "Frota" in df.columns:
        df = df.rename(columns={"Frota": "Equipamento"})

    ensure_required_columns(df, REQUIRED_COLUMNS, "Apontamentos")

    return df
