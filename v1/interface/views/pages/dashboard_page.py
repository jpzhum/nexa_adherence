
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class DashboardPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        lay = QVBoxLayout(self)
        t = QLabel('Dashboard'); t.setObjectName('HeaderTitle')
        lay.addWidget(t)
        self.tabs = QTabWidget(); lay.addWidget(self.tabs)
    def load(self):
        self.tabs.clear()
        if self.controller.final_df is not None:
            from interface.services import dashboard_service
            from interface.services.dashboard_layout_service import get_layout
            layout = get_layout()
            chart_map = {
                'grafico_situacao_geral': dashboard_service.grafico_situacao_geral,
                'grafico_aderencia_qtd_turno': dashboard_service.grafico_aderencia_qtd_turno,
                'grafico_agrupamento_percent': dashboard_service.grafico_agrupamento_percent,
                'grafico_agrupamento_qtd': dashboard_service.grafico_agrupamento_qtd,
                'grafico_evolucao_diaria': dashboard_service.grafico_evolucao_diaria,
            }
            for sec in layout.get('sections', []):
                title = sec.get('title','Seção')
                chart_id = sec.get('chart')
                fn = chart_map.get(chart_id)
                if not fn:
                    w = QLabel(f'Chart não encontrado: {chart_id}')
                    self.tabs.addTab(w, title)
                    continue
                w = QWidget(); l = QVBoxLayout(w)
                fig = fn(self.controller.final_df)
                l.addWidget(FigureCanvas(fig))
                self.tabs.addTab(w, title)
        else:
            lbl = QLabel('Nenhum dado consolidado.'); self.tabs.addTab(lbl, 'Aviso')
