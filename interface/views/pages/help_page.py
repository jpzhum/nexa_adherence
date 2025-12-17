
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class HelpPage(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        title = QLabel('Ajuda')
        subtitle = QLabel('Fluxo: Importar -> Consolidar -> Indicadores/Dashboard -> Exportar -> E-mail')
        lay.addWidget(title)
        lay.addWidget(subtitle)
