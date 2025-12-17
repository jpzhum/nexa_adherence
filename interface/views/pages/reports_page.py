
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox

class ReportsPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel('Relatórios'))
        btn = QPushButton('Exportar Excel'); btn.setObjectName('Primary')
        btn.clicked.connect(self._export)
        lay.addWidget(btn)
    def _export(self):
        if self.controller.final_df is None or self.controller.resumos is None:
            QMessageBox.warning(self, 'Aviso', 'Consolide os dados antes de exportar.')
            return
        path, _ = QFileDialog.getSaveFileName(self, 'Salvar Relatório', '', 'Excel (*.xlsx)')
        if path:
            from interface.services.export_service import exportar_excel
            exportar_excel(self.controller.final_df, self.controller.resumos, path)
            QMessageBox.information(self, 'Sucesso', 'Relatório salvo em: ' + path)
