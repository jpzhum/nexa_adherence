from pathlib import Path

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QPushButton, QFileDialog, QMessageBox

from v2.services.export_service import exportar_excel
from v2.services.exportbi_service import atualizar_bd_excel
from v2.services.result_store import result_store


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("[R] Relatorios")
        header.setObjectName("HeaderTitle")
        layout.addWidget(header)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)

        btn_excel = QPushButton("Exportar Excel")
        btn_excel.setObjectName("Primary")
        btn_excel.clicked.connect(self._export_excel)
        card_layout.addWidget(btn_excel)

        btn_bi = QPushButton("Exportar Power BI (bd BI.xlsx)")
        btn_bi.clicked.connect(self._export_bi)
        card_layout.addWidget(btn_bi)

        layout.addWidget(card)

    def _get_results(self):
        final_df = result_store.get_result()
        resumos = result_store.get_resumos()
        if final_df is None or resumos is None:
            QMessageBox.warning(self, "Aviso", "Consolide os dados antes de exportar.")
            return None, None
        return final_df, resumos

    def _export_excel(self):
        final_df, resumos = self._get_results()
        if final_df is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Relatorio", "", "Excel (*.xlsx)")
        if not path:
            return
        if not path.lower().endswith(".xlsx"):
            path = f"{path}.xlsx"
        try:
            exportar_excel(final_df, resumos, path)
            QMessageBox.information(self, "Sucesso", f"Relatorio salvo em: {path}")
        except Exception as exc:
            QMessageBox.warning(self, "Falha", f"Nao foi possivel exportar o relatorio: {exc}")

    def _export_bi(self):
        final_df, resumos = self._get_results()
        if final_df is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salvar bd BI.xlsx", "", "Excel (*.xlsx)")
        if not path:
            return
        if not path.lower().endswith(".xlsx"):
            path = f"{path}.xlsx"
        out_dir = str(Path(path).parent)
        file_name = Path(path).name
        try:
            saved = atualizar_bd_excel(final_df, resumos, out_dir=out_dir, filename=file_name)
            QMessageBox.information(self, "Sucesso", f"BD Power BI salvo em: {saved}")
        except Exception as exc:
            QMessageBox.warning(self, "Falha", f"Nao foi possivel exportar o BD Power BI: {exc}")
