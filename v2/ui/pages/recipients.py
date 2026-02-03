from PyQt5.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from v2.services.recipients_service import email_valid, load_recipients, save_recipients


class RecipientsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("[T] Destinatarios")
        header.setObjectName("HeaderTitle")
        layout.addWidget(header)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.addWidget(QLabel("Para"))
        self.list_to = QListWidget()
        self.input_to = QLineEdit()
        self.input_to.setPlaceholderText("Adicionar destinatario...")
        btn_add_to = QPushButton("Adicionar destinatario")
        btn_add_to.clicked.connect(lambda: self._add(self.input_to, self.list_to))
        card_layout.addWidget(self.list_to)
        card_layout.addWidget(self.input_to)
        card_layout.addWidget(btn_add_to)

        card_layout.addWidget(QLabel("CC"))
        self.list_cc = QListWidget()
        self.input_cc = QLineEdit()
        self.input_cc.setPlaceholderText("Adicionar CC...")
        btn_add_cc = QPushButton("Adicionar CC")
        btn_add_cc.clicked.connect(lambda: self._add(self.input_cc, self.list_cc))
        card_layout.addWidget(self.list_cc)
        card_layout.addWidget(self.input_cc)
        card_layout.addWidget(btn_add_cc)

        btn_save = QPushButton("Salvar")
        btn_save.setObjectName("Primary")
        btn_save.clicked.connect(self._save)
        card_layout.addWidget(btn_save)

        layout.addWidget(card)

        self._load()

    def _load(self):
        dest, cc = load_recipients()
        self.list_to.clear()
        self.list_cc.clear()
        for item in dest:
            self.list_to.addItem(item)
        for item in cc:
            self.list_cc.addItem(item)

    def _add(self, edit: QLineEdit, listw: QListWidget):
        value = edit.text().strip()
        if email_valid(value):
            listw.addItem(value)
            edit.clear()
        else:
            QMessageBox.warning(self, "Aviso", "Digite um e-mail valido.")

    def _save(self):
        dest = [self.list_to.item(i).text() for i in range(self.list_to.count())]
        cc = [self.list_cc.item(i).text() for i in range(self.list_cc.count())]
        save_recipients(dest, cc)
        QMessageBox.information(self, "Sucesso", "Destinatarios salvos.")
