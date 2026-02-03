from typing import Dict

from v2.db.connection import get_connection


class SystemStateService:
    def __init__(self):
        self.base_counts: Dict[str, int] = {}
        self.base_status: Dict[str, bool] = {}
        self.refresh()

    def refresh(self) -> None:
        try:
            with get_connection() as conn:
                eqp = conn.execute("SELECT COUNT(*) AS total FROM equipamentos;").fetchone()[
                    "total"
                ]
                sup = conn.execute("SELECT COUNT(*) AS total FROM supervisores;").fetchone()[
                    "total"
                ]
                ap = conn.execute("SELECT COUNT(*) AS total FROM apontamentos;").fetchone()["total"]
                db_ok = True
        except Exception:
            eqp = 0
            sup = 0
            ap = 0
            db_ok = False
        self.base_counts = {"equipamentos": eqp, "supervisores": sup, "apontamentos": ap}
        self.base_status = {
            "db_ok": db_ok,
            "equipamentos_ready": eqp > 0,
            "supervisores_ready": sup > 0,
            "imports_ready": ap > 0,
        }

    def can_consolidate(self) -> bool:
        return (
            self.base_status.get("db_ok", False)
            and self.base_status.get("equipamentos_ready", False)
            and self.base_status.get("supervisores_ready", False)
            and self.base_status.get("imports_ready", False)
        )

    def can_import_apontamentos(self) -> bool:
        return self.base_status.get("db_ok", False) and self.base_status.get(
            "equipamentos_ready", False
        )

    def status_label(self, base_name: str) -> str:
        aliases = {
            "equipamentos": "equipamentos_ready",
            "supervisores": "supervisores_ready",
            "apontamentos": "imports_ready",
        }
        key = aliases.get(base_name, base_name)
        ok = self.base_status.get(key, False)
        return "OK" if ok else "Ausente"
