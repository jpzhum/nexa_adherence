
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QToolButton, QStackedWidget, QStatusBar, QLabel
from PyQt5.QtCore import Qt, QSize
from interface.views.pages.home_page import HomePage
from interface.views.pages.import_page import ImportPage
from interface.views.pages.consolidate_page import ConsolidatePage
from interface.views.pages.dashboard_page import DashboardPage
from interface.views.pages.indicators_page import IndicatorsPage
from interface.views.pages.reports_page import ReportsPage
from interface.views.pages.rules_page import RulesPage
from interface.views.pages.recipients_page import RecipientsPage
from interface.views.pages.email_page import EmailPage
from interface.views.pages.settings_page import SettingsPage
from interface.views.pages.help_page import HelpPage
from interface.controllers.main_controller import MainController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Nexa — Relatórios de Aderência (UI v4)')
        self.setMinimumSize(1200, 800)
        self.status = QStatusBar(); self.setStatusBar(self.status)
        self.atualizar_status('Sistema iniciado', 'info')

        cont = QWidget(); self.setCentralWidget(cont)
        hl = QHBoxLayout(cont); hl.setContentsMargins(0,0,0,0); hl.setSpacing(0)

        side = QFrame(); side.setObjectName('Sidebar'); side.setFixedWidth(240)
        sl = QVBoxLayout(side); sl.setAlignment(Qt.AlignTop); sl.setContentsMargins(12,12,12,12); sl.setSpacing(6)
        self._btns = {}
        for key, text in [
            ('home','Home'), ('import','Importar Dados'), ('cons','Consolidar'), ('dash','Dashboard'),
            ('indic','Indicadores'), ('rep','Relatórios'), ('rules','Regras'), ('recp','Destinatários'),
            ('mail','E-mail'), ('set','Configurações'), ('help','Ajuda')]:
            b = QToolButton(); b.setText(text); b.setObjectName('SidebarItem'); b.setProperty('active', False)
            b.setToolButtonStyle(Qt.ToolButtonTextOnly)
            b.setIconSize(QSize(22,22))
            sl.addWidget(b); self._btns[key]=b
        hl.addWidget(side)

        right = QWidget(); rl = QVBoxLayout(right); rl.setContentsMargins(16,16,16,16); rl.setSpacing(12)
        header = QFrame(); header.setObjectName('HeaderFrame')
        hv = QVBoxLayout(header); hv.setContentsMargins(12,10,12,10)
        self.header_title = QLabel('Home'); self.header_title.setObjectName('HeaderTitle')
        self.header_sub = QLabel('UI v4 — configurações com exclusões e melhorias gerais'); self.header_sub.setObjectName('HeaderSubtitle')
        hv.addWidget(self.header_title); hv.addWidget(self.header_sub)
        self.stack = QStackedWidget()
        rl.addWidget(header)
        rl.addWidget(self.stack, 1)
        hl.addWidget(right, 1)

        self.controller = MainController(self)
        self.pages = {
            'home': HomePage(self.controller),
            'import': ImportPage(self.controller),
            'cons': ConsolidatePage(self.controller),
            'dash': DashboardPage(self.controller),
            'indic': IndicatorsPage(self.controller),
            'rep': ReportsPage(self.controller),
            'rules': RulesPage(self.controller),
            'recp': RecipientsPage(),
            'mail': EmailPage(self.controller),
            'set': SettingsPage(self.controller),
            'help': HelpPage(),
        }
        order = ['home','import','cons','dash','indic','rep','rules','recp','mail','set','help']
        for k in order: self.stack.addWidget(self.pages[k])

        self._btns['home'].clicked.connect(lambda: self.set_page('home','Home'))
        self._btns['import'].clicked.connect(lambda: self.set_page('import','Importar Dados'))
        self._btns['cons'].clicked.connect(lambda: self.set_page('cons','Consolidação'))
        self._btns['dash'].clicked.connect(lambda: (self.set_page('dash','Dashboard'), self.pages['dash'].load()))
        self._btns['indic'].clicked.connect(lambda: (self.set_page('indic','Indicadores'), self.pages['indic'].load()))
        self._btns['rep'].clicked.connect(lambda: self.set_page('rep','Relatórios'))
        self._btns['rules'].clicked.connect(lambda: self.set_page('rules','Regras'))
        self._btns['recp'].clicked.connect(lambda: self.set_page('recp','Destinatários'))
        self._btns['mail'].clicked.connect(lambda: self.set_page('mail','E-mail'))
        self._btns['set'].clicked.connect(lambda: self.set_page('set','Configurações'))
        self._btns['help'].clicked.connect(lambda: self.set_page('help','Ajuda'))

        self.set_page('home','Home')

    def set_page(self, name: str, title: str):
        order = ['home','import','cons','dash','indic','rep','rules','recp','mail','set','help']
        idx = order.index(name)
        self.stack.setCurrentIndex(idx)
        self.header_title.setText(title)
        for k,b in self._btns.items():
            b.setProperty('active', k==name)
            b.style().unpolish(b); b.style().polish(b)

    def atualizar_status(self, texto, tipo='info'):
        icones = {'info':'[i]','warn':'[!]','error':'[x]'}
        self.status.showMessage(f"{icones.get(tipo,'[i]')} {texto}")
