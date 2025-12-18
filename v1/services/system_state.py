from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SystemState:
    """
    Tracks prerequisites for operations (bases carregadas, etc.).
    Extended in later steps to consult SQLite and enforce UI guards.
    """
    bases: Dict[str, bool] = field(default_factory=dict)
    last_errors: List[str] = field(default_factory=list)

    def set_base_status(self, name: str, ok: bool) -> None:
        self.bases[name] = ok

    def is_base_ok(self, name: str) -> bool:
        return bool(self.bases.get(name))

    def add_error(self, message: str) -> None:
        self.last_errors.append(message)

    def ready_for_consolidation(self) -> bool:
        return self.is_base_ok("equipamentos")
