from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QStatusBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from v2.services.system_state import SystemStateService
from v2.ui.pages.bases import BasesPage
from v2.ui.pages.consolidate import ConsolidatePage
from v2.ui.pages.dashboard import DashboardPage
from v2.ui.pages.email import EmailPage
from v2.ui.pages.help import HelpPage
from v2.ui.pages.home import HomePage
from v2.ui.pages.import_page import ImportPage
from v2.ui.pages.indicators import IndicatorsPage
from v2.ui.pages.recipients import RecipientsPage
from v2.ui.pages.reports import ReportsPage
from v2.ui.pages.rules import RulesPage
from v2.ui.pages.settings import SettingsPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexa Aderencia v2")
        self.setMinimumSize(1200, 800)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Sistema iniciado")

        container = QWidget()
        self.setCentralWidget(container)
        root = QHBoxLayout(container)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setAlignment(Qt.AlignTop)
        side_layout.setContentsMargins(16, 16, 16, 16)
        side_layout.setSpacing(8)

        title = QLabel("Nexa Aderencia")
        title.setObjectName("SidebarTitle")
        side_layout.addWidget(title)

        self._buttons = {}
        items = [
            ("home", "Home"),
            ("bases", "Bases"),
            ("import", "Importacao"),
            ("cons", "Consolidacao"),
            ("dash", "Dashboard"),
            ("indic", "Indicadores"),
            ("reports", "Relatorios"),
            ("rules", "Regras"),
            ("recp", "Destinatarios"),
            ("mail", "E-mail"),
            ("settings", "Configuracoes"),
            ("help", "Ajuda"),
        ]
        for key, text in items:
            btn = QToolButton()
            btn.setText(text)
            btn.setObjectName("SidebarItem")
            btn.setProperty("active", False)
            btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
            btn.setIconSize(QSize(20, 20))
            side_layout.addWidget(btn)
            self._buttons[key] = btn

        root.addWidget(sidebar)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)

        header = QFrame()
        header.setObjectName("HeaderFrame")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(12, 10, 12, 10)
        self.header_title = QLabel("Home")
        self.header_title.setObjectName("HeaderTitle")
        self.header_subtitle = QLabel("Painel de status e navegacao")
        self.header_subtitle.setObjectName("HeaderSubtitle")
        header_layout.addWidget(self.header_title)
        header_layout.addWidget(self.header_subtitle)

        self.stack = QStackedWidget()

        right_layout.addWidget(header)
        right_layout.addWidget(self.stack, 1)
        root.addWidget(right, 1)

        self.state = SystemStateService()
        self.pages = {
            "home": HomePage(self.state),
            "bases": BasesPage(self.state, self.refresh_state),
            "import": ImportPage(self.state),
            "cons": ConsolidatePage(self.state, self._on_consolidated),
            "dash": DashboardPage(),
            "indic": IndicatorsPage(),
            "reports": ReportsPage(),
            "rules": RulesPage(),
            "recp": RecipientsPage(),
            "mail": EmailPage(),
            "settings": SettingsPage(),
            "help": HelpPage(),
        }
        order = [
            "home",
            "bases",
            "import",
            "cons",
            "dash",
            "indic",
            "reports",
            "rules",
            "recp",
            "mail",
            "settings",
            "help",
        ]
        for key in order:
            self.stack.addWidget(self.pages[key])

        self._buttons["home"].clicked.connect(lambda: self.set_page("home", "Home"))
        self._buttons["bases"].clicked.connect(lambda: self.set_page("bases", "Bases"))
        self._buttons["import"].clicked.connect(lambda: self.set_page("import", "Importacao"))
        self._buttons["cons"].clicked.connect(lambda: self.set_page("cons", "Consolidacao"))
        self._buttons["dash"].clicked.connect(
            lambda: (self.set_page("dash", "Dashboard"), self.pages["dash"].load())
        )
        self._buttons["indic"].clicked.connect(
            lambda: (self.set_page("indic", "Indicadores"), self.pages["indic"].load())
        )
        self._buttons["reports"].clicked.connect(lambda: self.set_page("reports", "Relatorios"))
        self._buttons["rules"].clicked.connect(lambda: self.set_page("rules", "Regras"))
        self._buttons["recp"].clicked.connect(lambda: self.set_page("recp", "Destinatarios"))
        self._buttons["mail"].clicked.connect(lambda: self.set_page("mail", "E-mail"))
        self._buttons["settings"].clicked.connect(
            lambda: self.set_page("settings", "Configuracoes")
        )
        self._buttons["help"].clicked.connect(lambda: self.set_page("help", "Ajuda"))

        self.set_page("home", "Home")
        self.refresh_state()

    def set_page(self, name: str, title: str):
        order = [
            "home",
            "bases",
            "import",
            "cons",
            "dash",
            "indic",
            "reports",
            "rules",
            "recp",
            "mail",
            "settings",
            "help",
        ]
        idx = order.index(name)
        self.stack.setCurrentIndex(idx)
        self.header_title.setText(title)
        for key, btn in self._buttons.items():
            btn.setProperty("active", key == name)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def refresh_state(self):
        self.state.refresh()
        for key in ["home", "cons", "import"]:
            page = self.pages.get(key)
            if hasattr(page, "refresh_state"):
                page.refresh_state()

    def _on_consolidated(self):
        dash = self.pages.get("dash")
        if dash and hasattr(dash, "load"):
            dash.load()
        indic = self.pages.get("indic")
        if indic and hasattr(indic, "load"):
            indic.load()
