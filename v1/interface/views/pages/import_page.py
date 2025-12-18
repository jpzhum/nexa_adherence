
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class ImportPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        lay = QVBoxLayout(self)
        header = QLabel('Importar Dados (Excel único)'); header.setObjectName('HeaderTitle')
        lay.addWidget(header)
        btn = QPushButton('Selecionar arquivo Excel'); btn.setObjectName('Primary')
        btn.clicked.connect(self.controller.importar_dados)
        lay.addWidget(btn)
        self.info = QLabel('Nenhum arquivo importado.')
        lay.addWidget(self.info)
    def set_import_path(self, path: str):
        self.info.setText('Base importada: ' + path if path else 'Nenhum arquivo importado.')
