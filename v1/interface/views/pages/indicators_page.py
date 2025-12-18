# interface/views/pages/indicators_page.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
except Exception:
    QWebEngineView = None

from interface.views.pages.indicators_template import render_html

class IndicatorsPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.lay = QVBoxLayout(self)
        t = QLabel('Indicadores')
        t.setObjectName('HeaderTitle')
        self.lay.addWidget(t)
        self.view = QWebEngineView() if QWebEngineView else None

    def load(self):
        # Limpa layout (exceto view)
        for i in reversed(range(self.lay.count())):
            w = self.lay.itemAt(i).widget()
            if w and w is not getattr(self, 'view', None):
                w.deleteLater()

        if self.view and self.controller and getattr(self.controller, 'resumos', None) and 'Indicadores Gerais' in self.controller.resumos:
            html = render_html(self.controller.resumos)
            self.view.setHtml(html)
            self.lay.addWidget(self.view)
        else:
            aviso = QLabel('Nenhum dado disponível. Consolide os dados para visualizar os indicadores.')
            aviso.setStyleSheet("font-size:18px; color:#E0652F; font-weight:bold; font-family:'Montserrat';")
            aviso.setWordWrap(True)
            self.lay.addWidget(aviso)
