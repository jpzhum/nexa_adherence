from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from v2.services.dashboard_layout_service import get_layout
from v2.services.dashboard_service import (
    grafico_situacao_geral,
    grafico_aderencia_qtd_turno,
    grafico_agrupamento_percent,
    grafico_agrupamento_qtd,
    grafico_evolucao_diaria,
)
from v2.services.result_store import result_store


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("[D] Dashboard")
        header.setObjectName("HeaderTitle")
        layout.addWidget(header)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

    def load(self):
        self.tabs.clear()
        final_df = result_store.get_result()
        if final_df is None or final_df.empty:
            lbl = QLabel("[i] Nenhum dado consolidado.")
            self.tabs.addTab(lbl, "Aviso")
            return

        layout = get_layout()
        chart_map = {
            "grafico_situacao_geral": grafico_situacao_geral,
            "grafico_aderencia_qtd_turno": grafico_aderencia_qtd_turno,
            "grafico_agrupamento_percent": grafico_agrupamento_percent,
            "grafico_agrupamento_qtd": grafico_agrupamento_qtd,
            "grafico_evolucao_diaria": grafico_evolucao_diaria,
        }
        for sec in layout.get("sections", []):
            title = sec.get("title", "Secao")
            chart_id = sec.get("chart")
            fn = chart_map.get(chart_id)
            if not fn:
                self.tabs.addTab(QLabel(f"Chart nao encontrado: {chart_id}"), title)
                continue
            try:
                fig = fn(final_df)
                self.tabs.addTab(FigureCanvas(fig), title)
            except Exception as exc:
                self.tabs.addTab(QLabel(f"Falha ao gerar grafico: {exc}"), title)
