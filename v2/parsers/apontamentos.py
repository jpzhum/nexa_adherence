import pandas as pd

from v2.utils.validators import normalize_headers, validate_required_columns

REQUIRED_COLUMNS = ["Data Cabecalho", "Equipamento", "Desc.Turno"]


def load_apontamentos(path: str) -> pd.DataFrame:
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)
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

    ok, missing = validate_required_columns(df, REQUIRED_COLUMNS)
    if not ok:
        raise ValueError(f"Colunas obrigatorias ausentes: {', '.join(missing)}")

    return df
