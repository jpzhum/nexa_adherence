from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from v2.db.connection import get_connection
from v2.services.config_service import load_config, update_data_dir, update_exclusions


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("[S] Configuracoes")
        header.setObjectName("HeaderTitle")
        layout.addWidget(header)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.addWidget(QLabel("Diretorios, exclusoes e preferencias"))

        self.data_dir = QLineEdit()
        self.data_dir.setPlaceholderText("Diretorio de dados (opcional)")
        card_layout.addWidget(self.data_dir)
        btn_dir = QPushButton("Salvar diretorio")
        btn_dir.clicked.connect(self._save_dir)
        card_layout.addWidget(btn_dir)

        card_layout.addWidget(QLabel("Exclua itens do dashboard marcando na lista"))
        lists = QHBoxLayout()
        self.lista_agrup = QListWidget()
        self.lista_frota = QListWidget()
        self.lista_agrup.setObjectName("ListCard")
        self.lista_frota.setObjectName("ListCard")
        lists.addWidget(self._with_title("Agrupamentos (supervisores)", self.lista_agrup))
        lists.addWidget(self._with_title("Frotas (equipamentos)", self.lista_frota))
        card_layout.addLayout(lists)

        b_reload = QPushButton("Recarregar do banco")
        b_reload.clicked.connect(self._load_options)
        card_layout.addWidget(b_reload)

        b_save = QPushButton("Salvar exclusoes")
        b_save.setObjectName("Primary")
        b_save.clicked.connect(self._save_exclusions)
        card_layout.addWidget(b_save)

        layout.addWidget(card)
        self._refresh()

    def _save_dir(self):
        ok = update_data_dir(self.data_dir.text().strip())
        QMessageBox.information(
            self,
            "Configuracoes",
            "Diretorio atualizado" if ok else "Diretorio invalido ou nao encontrado",
        )

    def _refresh(self):
        cfg = load_config()
        self.data_dir.setText(cfg.get("data_dir", ""))
        self._load_options()

    def _load_options(self):
        try:
            cfg = load_config()
            excl_agr = set(cfg.get("exclusions_agrup", []))
            excl_fro = set(cfg.get("exclusions_frota", []))
            with get_connection() as conn:
                agr_rows = conn.execute(
                    "SELECT DISTINCT agrupamento FROM supervisores WHERE agrupamento IS NOT NULL;"
                ).fetchall()
                fro_rows = conn.execute(
                    "SELECT DISTINCT codigo FROM equipamentos WHERE codigo IS NOT NULL;"
                ).fetchall()
            agr_values = {row["agrupamento"] for row in agr_rows}
            fro_values = {row["codigo"] for row in fro_rows}
            self._populate_checklist(self.lista_agrup, sorted(agr_values | excl_agr), excl_agr)
            self._populate_checklist(self.lista_frota, sorted(fro_values | excl_fro), excl_fro)
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Falha ao carregar opcoes: {exc}")

    def _populate_checklist(self, lw: QListWidget, values, excluded):
        lw.clear()
        for value in sorted({str(v).strip() for v in values if str(v).strip()}):
            item = QListWidgetItem(value)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if value in excluded else Qt.Unchecked)
            lw.addItem(item)

    def _list_checked(self, lw: QListWidget):
        selected = []
        for i in range(lw.count()):
            item = lw.item(i)
            if item.checkState() == Qt.Checked:
                selected.append(item.text())
        return selected

    def _save_exclusions(self):
        excl_agr = self._list_checked(self.lista_agrup)
        excl_fro = self._list_checked(self.lista_frota)
        update_exclusions(excl_agr, excl_fro)
        QMessageBox.information(self, "Sucesso", "Exclusoes salvas.")

    def _with_title(self, title: str, widget: QWidget) -> QWidget:
        wrap = QFrame()
        layout = QVBoxLayout(wrap)
        layout.setSpacing(6)
        label = QLabel(title)
        label.setObjectName("Muted")
        layout.addWidget(label)
        layout.addWidget(widget)
        return wrap
