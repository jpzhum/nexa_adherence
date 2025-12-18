import pandas as pd

from v2.utils.validators import normalize_headers, validate_required_columns

REQUIRED_COLUMNS = ["Equipamento", "Agrup Equipamento"]


def load_equipamentos(path: str) -> pd.DataFrame:
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)
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

    ok, missing = validate_required_columns(df, REQUIRED_COLUMNS)
    if not ok:
        raise ValueError(f"Colunas obrigatorias ausentes: {', '.join(missing)}")

    return df
