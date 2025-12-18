from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QFileDialog,
    QMessageBox,
    QProgressDialog,
)

from v2.services.bases_service import update_equipamentos_from_excel, update_supervisores_from_excel
from v2.services.system_state import SystemStateService
from v2.ui.workers import BaseImportWorker
from v2.utils.logging import get_logger

logger = get_logger(__name__)


class BasesPage(QWidget):
    def __init__(self, state: SystemStateService, on_state_changed=None):
        super().__init__()
        self.state = state
        self.on_state_changed = on_state_changed
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("[B] Bases auxiliares")
        header.setObjectName("HeaderTitle")
        layout.addWidget(header)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.addWidget(QLabel("BD EQP"))
        self.eqp_status = QLabel("Status: desconhecido")
        card_layout.addWidget(self.eqp_status)
        self.eqp_summary = QLabel("Resumo: -")
        card_layout.addWidget(self.eqp_summary)
        self.btn_eqp = QPushButton("Atualizar BD EQP")
        self.btn_eqp.setObjectName("Primary")
        self.btn_eqp.clicked.connect(self._update_eqp)
        card_layout.addWidget(self.btn_eqp)

        card_layout.addWidget(QLabel("BD Supervisor"))
        self.sup_status = QLabel("Status: desconhecido")
        card_layout.addWidget(self.sup_status)
        self.sup_summary = QLabel("Resumo: -")
        card_layout.addWidget(self.sup_summary)
        self.btn_sup = QPushButton("Atualizar BD Supervisor")
        self.btn_sup.setObjectName("Primary")
        self.btn_sup.clicked.connect(self._update_sup)
        card_layout.addWidget(self.btn_sup)
        layout.addWidget(card)

        self.refresh_state()

    def refresh_state(self):
        self.state.refresh()
        self.eqp_status.setText(f"Status: {self.state.status_label('equipamentos')}")
        self.sup_status.setText(f"Status: {self.state.status_label('supervisores')}")

    def _update_eqp(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Atualizar BD EQP", "", "Excel/CSV (*.xlsx *.xls *.csv)"
        )
        if not path:
            return
        self._run_import(update_equipamentos_from_excel, path, "BD EQP", self.eqp_summary)

    def _update_sup(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Atualizar BD Supervisor", "", "Excel/CSV (*.xlsx *.xls *.csv)"
        )
        if not path:
            return
        self._run_import(update_supervisores_from_excel, path, "BD Supervisor", self.sup_summary)

    def _after_update(self):
        self.refresh_state()
        if callable(self.on_state_changed):
            self.on_state_changed()

    def _run_import(self, fn, path: str, label: str, summary_label: QLabel):
        self._set_busy(True)
        progress = QProgressDialog(f"Atualizando {label}...", None, 0, 0, self)
        progress.setWindowTitle("Processando")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()

        worker = BaseImportWorker(fn, path)

        def on_finished(resumo):
            progress.close()
            summary_label.setText(
                f"Resumo: novos {resumo['novos']}, atualizados {resumo['atualizados']}, ignorados {resumo['ignorados']}"
            )
            QMessageBox.information(self, "Base atualizada", f"{label} atualizada com sucesso.")
            self._set_busy(False)
            self._after_update()

        def on_failed(msg):
            progress.close()
            logger.error("Falha ao atualizar %s: %s", label, msg)
            QMessageBox.warning(self, "Falha ao atualizar", "Nao foi possivel atualizar a base.")
            self._set_busy(False)

        worker.finished.connect(on_finished)
        worker.failed.connect(on_failed)
        worker.start()
        self._worker = worker

    def _set_busy(self, busy: bool):
        self.btn_eqp.setEnabled(not busy)
        self.btn_sup.setEnabled(not busy)
