import unicodedata
from typing import List, Sequence, Tuple


def normalize_headers(df):
    cleaned = []
    for col in df.columns:
        text = str(col).strip()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        text = " ".join(text.split())
        text = text.title()
        cleaned.append(text)
    df.columns = cleaned
    return df


def validate_required_columns(df, required: Sequence[str]) -> Tuple[bool, List[str]]:
    missing = [col for col in required if col not in df.columns]
    return len(missing) == 0, missing
