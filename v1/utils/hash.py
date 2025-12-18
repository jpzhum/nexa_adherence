import hashlib
from typing import Iterable


def file_sha256(path: str, chunk_size: int = 65536) -> str:
    """
    Calcula SHA-256 streaming para evitar carga de arquivos grandes em memória.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_hash(parts: Iterable[str]) -> str:
    """
    Gera hash estável a partir de partes de string (chave natural).
    """
    h = hashlib.sha256()
    for part in parts:
        h.update(str(part).encode("utf-8"))
        h.update(b"|")
    return h.hexdigest()
