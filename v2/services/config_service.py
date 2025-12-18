import json
import os
from typing import Any, Dict, List

from v2.db.repositories.configs_repo import is_empty, list_configs, upsert_many, upsert_value


DEFAULTS: Dict[str, Any] = {
    "data_dir": "",
    "exclusions_agrup": [],
    "exclusions_frota": [],
}


def _legacy_config_path() -> str:
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, "config.json")


def _load_legacy_config() -> Dict[str, Any]:
    path = _legacy_config_path()
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _bootstrap_if_empty() -> None:
    if not is_empty():
        return
    legacy = _load_legacy_config()
    merged = DEFAULTS.copy()
    for key, value in legacy.items():
        if key in merged:
            merged[key] = value
    upsert_many(merged)


def load_config() -> Dict[str, Any]:
    _bootstrap_if_empty()
    cfg = DEFAULTS.copy()
    stored = list_configs()
    for key, value in stored.items():
        if key in cfg:
            cfg[key] = value
    return cfg


def update_data_dir(path: str) -> bool:
    path = (path or "").strip()
    if not path:
        upsert_value("data_dir", "")
        return True
    if os.path.isdir(path):
        upsert_value("data_dir", path)
        return True
    return False


def _unique_clean(values: List[str]) -> List[str]:
    seen = {}
    for value in values:
        text = (value or "").strip()
        if text:
            seen[text] = True
    return list(seen.keys())


def update_exclusions(excl_agr: List[str], excl_fro: List[str]) -> None:
    upsert_value("exclusions_agrup", _unique_clean(excl_agr))
    upsert_value("exclusions_frota", _unique_clean(excl_fro))
