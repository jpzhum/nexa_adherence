import os
import sys

from PyQt5.QtWidgets import QApplication

from v2.ui.main_window import MainWindow
from v2.db.schema import ensure_schema
from v2.utils.logging import get_logger

logger = get_logger(__name__)


def resource_path(*parts):
    base = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base, *parts)


def load_qss():
    qss_path = resource_path("assets", "style.qss")
    if not os.path.isfile(qss_path):
        return ""
    with open(qss_path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    try:
        ensure_schema()
    except Exception as exc:
        logger.error("Falha ao inicializar banco v2: %s", exc)

    app = QApplication(sys.argv)
    qss = load_qss()
    if qss:
        app.setStyleSheet(qss)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
