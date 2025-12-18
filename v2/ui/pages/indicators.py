from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
except Exception:
    QWebEngineView = None

from v2.services.result_store import result_store
from v2.ui.pages.indicators_template import render_html


class IndicatorsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        title = QLabel("[G] Indicadores")
        title.setObjectName("HeaderTitle")
        self.layout.addWidget(title)
        self.view = QWebEngineView() if QWebEngineView else None

    def load(self):
        for i in reversed(range(self.layout.count())):
            w = self.layout.itemAt(i).widget()
            if w and w is not getattr(self, "view", None):
                w.deleteLater()

        resumos = result_store.get_resumos()
        if self.view and resumos and "Indicadores Gerais" in resumos:
            html = render_html(resumos)
            self.view.setHtml(html)
            self.layout.addWidget(self.view)
            return

        if self.view is None:
            texto = "[i] QtWebEngine nao instalado. Instale PyQtWebEngine para ver os indicadores."
            if resumos and "Indicadores Gerais" in resumos:
                ind = resumos.get("Indicadores Gerais")
                val = ind.iloc[0].to_dict() if hasattr(ind, "iloc") else {}
                aderencia = val.get("Aderencia Media Global", 0)
                total_esperado = val.get("Total Esperado", 0)
                total_entregue = val.get("Total Entregue", 0)
                texto = (
                    f"{texto}\n\nResumo:\n"
                    f"Aderencia Media Global: {aderencia}%\n"
                    f"Total Esperado: {total_esperado}\n"
                    f"Total Entregue: {total_entregue}"
                )
        else:
            texto = "[i] Nenhum dado disponivel. Consolide os dados para visualizar os indicadores."

        aviso = QLabel(texto)
        aviso.setObjectName("Muted")
        aviso.setWordWrap(True)
        aviso.setStyleSheet("color: #E5E7EB;")
        self.layout.addWidget(aviso)
