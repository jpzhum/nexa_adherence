
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableView, QPushButton,
    QHBoxLayout, QLineEdit, QComboBox, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QAbstractTableModel
import pandas as pd
from interface.services.rules_service import listar_regras, salvar_regra, excluir_regra, exportar_regras

class RulesPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.df = listar_regras()
        lay = QVBoxLayout(self)
        title = QLabel('Regras de Turnos'); title.setObjectName('HeaderTitle')
        lay.addWidget(title)

        # Tabela
        self.view = QTableView()
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setSelectionMode(QTableView.SingleSelection)
        self._refresh_table()
        lay.addWidget(self.view)

        # Formulário
        form = QHBoxLayout(); lay.addLayout(form)
        self.tipo = QComboBox(); self.tipo.addItems(['Frota','Agrupamento'])
        self.nome = QLineEdit(); self.nome.setPlaceholderText('Nome da Frota/Agrupamento')
        self.turno = QComboBox(); self.turno.addItems(['TURNO A','TURNO B','TURNO C'])
        self.escala = QComboBox(); self.escala.addItems(['PADRÃO','ADM'])
        form.addWidget(self.tipo); form.addWidget(self.nome); form.addWidget(self.turno); form.addWidget(self.escala)

        # Botões
        btns = QHBoxLayout(); lay.addLayout(btns)
        add = QPushButton('Adicionar/Atualizar'); add.setObjectName('Primary'); add.clicked.connect(self._add_update)
        delete = QPushButton('Excluir selecionada'); delete.clicked.connect(self._delete_selected)
        export = QPushButton('Exportar Regras para Excel'); export.clicked.connect(self._export)
        btns.addWidget(add); btns.addWidget(delete); btns.addWidget(export)

    def _refresh_table(self):
        self.df = listar_regras()
        self.model = PandasModel(self.df)
        self.view.setModel(self.model)
        self.view.resizeColumnsToContents()

    def _add_update(self):
        tipo = self.tipo.currentText().strip()
        nome = self.nome.text().strip()
        turno = self.turno.currentText().strip()
        escala = self.escala.currentText().strip()
        if not nome:
            QMessageBox.warning(self, 'Aviso', 'Informe o nome.')
            return
        salvar_regra(tipo, nome, turno, escala)
        QMessageBox.information(self, 'Sucesso', 'Regra salva/atualizada.')
        self._refresh_table()

    def _delete_selected(self):
        idx = self.view.currentIndex()
        if not idx.isValid():
            QMessageBox.warning(self, 'Aviso', 'Selecione uma linha para excluir.')
            return
        row = idx.row()
        tipo = self.df.iloc[row]['Tipo']
        nome = self.df.iloc[row]['Nome']
        excluir_regra(tipo, nome)
        QMessageBox.information(self, 'Sucesso', 'Regra excluída.')
        self._refresh_table()

    def _export(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Salvar Regras', '', 'Excel (*.xlsx)')
        if path:
            exportar_regras(path)
            QMessageBox.information(self, 'Sucesso', 'Regras exportadas em: ' + path)

class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(parent)
        self._df = df
    def rowCount(self, parent=None):
        return len(self._df.index)
    def columnCount(self, parent=None):
        return len(self._df.columns)
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role in (Qt.DisplayRole, Qt.EditRole):
            val = self._df.iat[index.row(), index.column()]
            return '' if pd.isna(val) else str(val)
        return None
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._df.columns[section]
        else:
            return section+1
