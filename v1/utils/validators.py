from typing import Iterable, List, Sequence, Tuple


def validate_required_columns(df, required: Sequence[str]) -> Tuple[bool, List[str]]:
    """
    Confere se todas as colunas obrigatórias existem em um DataFrame pandas.
    Retorna (ok, faltantes).
    """
    faltantes = [col for col in required if col not in df.columns]
    return len(faltantes) == 0, faltantes


def normalize_headers(df):
    """
    Normaliza cabeçalhos: strip + title case. Mantém compatibilidade atual.
    """
    df.columns = df.columns.str.strip().str.title()
    return df
