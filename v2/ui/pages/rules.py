from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QHBoxLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)

from v2.db.repositories.regras_repo import delete_regra, list_regras, upsert_regra


class RulesPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("[R] Regras")
        header.setObjectName("HeaderTitle")
        layout.addWidget(header)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)

        form = QHBoxLayout()
        self.tipo = QComboBox()
        self.tipo.addItems(["Frota", "Agrupamento"])
        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Nome da frota ou agrupamento")
        self.turno = QComboBox()
        self.turno.addItems(["", "TURNO A", "TURNO B", "TURNO C"])
        self.escala = QComboBox()
        self.escala.addItems(["PADRAO", "ADM"])
        btn_add = QPushButton("Salvar regra")
        btn_add.clicked.connect(self._save_rule)

        form.addWidget(self.tipo)
        form.addWidget(self.nome)
        form.addWidget(self.turno)
        form.addWidget(self.escala)
        form.addWidget(btn_add)

        card_layout.addLayout(form)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Id", "Tipo", "Nome", "Turno", "Escala"])
        self.table.setColumnHidden(0, True)
        card_layout.addWidget(self.table)

        btn_delete = QPushButton("Excluir regra selecionada")
        btn_delete.clicked.connect(self._delete_selected)
        card_layout.addWidget(btn_delete)

        layout.addWidget(card)

        self._load()

    def _load(self):
        regras = list_regras()
        self.table.setRowCount(0)
        for regra in regras:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(regra["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(regra["tipo"]))
            self.table.setItem(row, 2, QTableWidgetItem(regra["nome"]))
            self.table.setItem(row, 3, QTableWidgetItem(regra.get("turno") or ""))
            self.table.setItem(row, 4, QTableWidgetItem(regra.get("escala") or ""))

    def _save_rule(self):
        tipo = self.tipo.currentText().strip()
        nome = self.nome.text().strip()
        turno = self.turno.currentText().strip()
        escala = self.escala.currentText().strip()
        if not nome:
            QMessageBox.warning(self, "Campo obrigatorio", "Informe o nome da frota ou agrupamento.")
            return
        upsert_regra(tipo, nome, turno, escala)
        self.nome.setText("")
        self._load()
        QMessageBox.information(self, "Regra salva", "Regra salva com sucesso.")

    def _delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return
        rule_id = self.table.item(row, 0).text()
        delete_regra(int(rule_id))
        self._load()
