
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QDateEdit, QPushButton
from PyQt5.QtCore import QDate

class ConsolidatePage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        lay = QVBoxLayout(self)
        t = QLabel('Consolidação de Dados'); t.setObjectName('HeaderTitle')
        lay.addWidget(t)
        hl = QHBoxLayout()
        self.di = QDateEdit(); self.di.setDisplayFormat('dd/MM/yyyy'); self.di.setCalendarPopup(True)
        self.df = QDateEdit(); self.df.setDisplayFormat('dd/MM/yyyy'); self.df.setCalendarPopup(True)
        self.di.setDate(QDate.currentDate().addDays(-15))
        self.df.setDate(QDate.currentDate())
        hl.addWidget(QLabel('Data Inicial:')); hl.addWidget(self.di)
        hl.addWidget(QLabel('Data Final:')); hl.addWidget(self.df)
        lay.addLayout(hl)
        btn = QPushButton('Consolidar Dados'); btn.setObjectName('Primary')
        btn.clicked.connect(self.controller.consolidar_dados)
        lay.addWidget(btn)
    def get_periodo(self):
        return self.di.date(), self.df.date()
