from pathlib import Path
from typing import Sequence

import pandas as pd

SUPPORTED_INPUT_EXTENSIONS = (".xlsx", ".xls", ".xlsm", ".csv")


def read_table_file(path: str) -> pd.DataFrame:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED_INPUT_EXTENSIONS:
        raise ValueError(
            "Formato de arquivo nao suportado. "
            f"Use um dos formatos: {', '.join(SUPPORTED_INPUT_EXTENSIONS)}"
        )

    if suffix == ".csv":
        for encoding in ("utf-8-sig", "latin1"):
            try:
                return pd.read_csv(file_path, encoding=encoding, sep=None, engine="python")
            except UnicodeDecodeError:
                continue
            except pd.errors.ParserError:
                try:
                    return pd.read_csv(file_path, encoding=encoding, sep=";")
                except Exception:
                    continue
        raise ValueError("Falha ao ler CSV: encoding invalido ou arquivo corrompido.")

    try:
        return pd.read_excel(file_path)
    except ValueError as exc:
        raise ValueError("Falha ao ler planilha: arquivo invalido ou sem aba legivel.") from exc


def ensure_required_columns(df: pd.DataFrame, required: Sequence[str], source_name: str) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"{source_name}: colunas obrigatorias ausentes: {', '.join(missing)}")
