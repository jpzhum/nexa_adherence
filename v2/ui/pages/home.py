from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame

from v2.services.system_state import SystemStateService


class HomePage(QWidget):
    def __init__(self, state: SystemStateService):
        super().__init__()
        self.state = state
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        title = QLabel("[H] Status do sistema")
        title.setObjectName("HeaderTitle")
        subtitle = QLabel("Visao geral das bases e importacoes recentes")
        subtitle.setObjectName("Muted")
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        self.eqp_label = QLabel("BD EQP: desconhecido")
        self.sup_label = QLabel("BD Supervisor: desconhecido")
        self.imp_label = QLabel("Apontamentos: desconhecido")
        card_layout.addWidget(self.eqp_label)
        card_layout.addWidget(self.sup_label)
        card_layout.addWidget(self.imp_label)
        card_layout.addWidget(QLabel("Ultima importacao: -"))
        layout.addWidget(card)

        self.refresh_state()

    def refresh_state(self):
        self.state.refresh()
        self.eqp_label.setText(f"BD EQP: {self.state.status_label('equipamentos')}")
        self.sup_label.setText(f"BD Supervisor: {self.state.status_label('supervisores')}")
        self.imp_label.setText(f"Apontamentos: {self.state.status_label('apontamentos')}")
