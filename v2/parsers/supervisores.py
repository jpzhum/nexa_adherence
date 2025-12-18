import pandas as pd

from v2.utils.validators import normalize_headers, validate_required_columns

REQUIRED_COLUMNS = ["Gestor", "Agrup Equipamento"]


def load_supervisores(path: str) -> pd.DataFrame:
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)
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

    ok, missing = validate_required_columns(df, REQUIRED_COLUMNS)
    if not ok:
        raise ValueError(f"Colunas obrigatorias ausentes: {', '.join(missing)}")

    return df
