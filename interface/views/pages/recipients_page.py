
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QLineEdit, QPushButton, QMessageBox

class RecipientsPage(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel('Destinatários'))
        self.list_to = QListWidget(); self.input_to = QLineEdit(); self.input_to.setPlaceholderText('Adicionar destinatário...')
        self.list_cc = QListWidget(); self.input_cc = QLineEdit(); self.input_cc.setPlaceholderText('Adicionar CC...')
        lay.addWidget(self.list_to); lay.addWidget(self.input_to)
        b1 = QPushButton('Adicionar Destinatário'); b1.clicked.connect(lambda: self._add(self.input_to, self.list_to))
        lay.addWidget(b1)
        lay.addWidget(self.list_cc); lay.addWidget(self.input_cc)
        b2 = QPushButton('Adicionar CC'); b2.clicked.connect(lambda: self._add(self.input_cc, self.list_cc))
        lay.addWidget(b2)
        save = QPushButton('Salvar'); save.clicked.connect(self._save)
        lay.addWidget(save)
        from interface.services.recipients_service import carregar_destinatarios
        to, cc = carregar_destinatarios()
        for e in to: self.list_to.addItem(e)
        for e in cc: self.list_cc.addItem(e)
    def _add(self, edit, listw):
        from interface.services.recipients_service import email_valido
        em = edit.text().strip()
        if email_valido(em):
            listw.addItem(em); edit.clear()
        else:
            QMessageBox.warning(self, 'Aviso', 'Digite um e-mail válido.')
    def _save(self):
        from interface.services.recipients_service import salvar_destinatarios
        to = [self.list_to.item(i).text() for i in range(self.list_to.count())]
        cc = [self.list_cc.item(i).text() for i in range(self.list_cc.count())]
        salvar_destinatarios(to, cc)
        QMessageBox.information(self, 'Sucesso', 'Destinatários salvos.')
