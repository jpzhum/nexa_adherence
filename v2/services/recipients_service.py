import json
import os
import re
from typing import List, Tuple

from v2.db.connection import get_db_path

DEFAULT_TO = ["email-removido@example.com"]
DEFAULT_CC = ["email-removido@example.com"]


def _env_emails(key: str, fallback: List[str]) -> List[str]:
    raw = os.getenv(key, "")
    if not raw.strip():
        return fallback
    parsed = [item.strip() for item in raw.split(",") if item.strip()]
    valid = [item for item in parsed if email_valid(item)]
    return valid or fallback


def _data_dir() -> str:
    return os.path.dirname(get_db_path())


def _recipients_path() -> str:
    return os.path.join(_data_dir(), "destinatarios.json")


def load_recipients() -> Tuple[List[str], List[str]]:
    default_to = _env_emails("NEXA_DEFAULT_TO", DEFAULT_TO)
    default_cc = _env_emails("NEXA_DEFAULT_CC", DEFAULT_CC)
    path = _recipients_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            destinatarios = _sanitize_list(data.get("destinatarios", default_to))
            cc = _sanitize_list(data.get("cc", default_cc))
            destinatarios = [value for value in destinatarios if email_valid(value)] or default_to
            cc = [value for value in cc if email_valid(value)] or default_cc
            return destinatarios, cc
        except Exception:
            return default_to, default_cc
    save_recipients(default_to, default_cc)
    return default_to, default_cc


def save_recipients(destinatarios: List[str], cc: List[str]) -> None:
    destinatarios = _sanitize_list(destinatarios)
    cc = _sanitize_list(cc)
    path = _recipients_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"destinatarios": destinatarios, "cc": cc}, handle, indent=2, ensure_ascii=True)


def email_valid(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email or "") is not None


def _sanitize_list(values: List[str]) -> List[str]:
    seen = {}
    for value in values or []:
        text = (value or "").strip()
        if text:
            seen[text] = True
    return list(seen.keys())
