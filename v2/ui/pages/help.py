from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class HelpPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("[?] Ajuda")
        header.setObjectName("HeaderTitle")
        layout.addWidget(header)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.addWidget(
            QLabel("Fluxo: Importar -> Consolidar -> Indicadores/Dashboard -> Exportar -> E-mail")
        )
        layout.addWidget(card)
