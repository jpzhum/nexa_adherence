import pandas as pd

from v2.parsers.common import ensure_required_columns, read_table_file
from v2.utils.validators import normalize_headers

REQUIRED_COLUMNS = ["Equipamento", "Agrup Equipamento"]


def load_equipamentos(path: str) -> pd.DataFrame:
    df = read_table_file(path)
    df = normalize_headers(df)

    if "Equipamento Ativo" in df.columns:
        df = df.rename(columns={"Equipamento Ativo": "Equipamento"})
    if "Frota" in df.columns and "Equipamento" not in df.columns:
        df = df.rename(columns={"Frota": "Equipamento"})
    if "Agrupamento" in df.columns:
        df = df.rename(columns={"Agrupamento": "Agrup Equipamento"})
    if "Agrup. Equipamento" in df.columns:
        df = df.rename(columns={"Agrup. Equipamento": "Agrup Equipamento"})
    if "Classe" in df.columns and "Dsc Classe" not in df.columns:
        df = df.rename(columns={"Classe": "Dsc Classe"})
    if "Descricao Equipamento" in df.columns and "Descricao" not in df.columns:
        df = df.rename(columns={"Descricao Equipamento": "Descricao"})

    ensure_required_columns(df, REQUIRED_COLUMNS, "Equipamentos")

    return df
