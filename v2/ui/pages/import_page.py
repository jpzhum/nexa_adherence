from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QFileDialog,
    QMessageBox,
    QProgressBar,
)

from v2.services.import_service import import_folder
from v2.services.system_state import SystemStateService
from v2.ui.workers import ImportFolderWorker
from v2.utils.logging import get_logger

logger = get_logger(__name__)


class ImportPage(QWidget):
    def __init__(self, state: SystemStateService):
        super().__init__()
        self.state = state
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("[I] Importacao por pasta")
        header.setObjectName("HeaderTitle")
        layout.addWidget(header)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        self.req_label = QLabel("Pre-requisito: BD EQP carregada")
        card_layout.addWidget(self.req_label)
        card_layout.addWidget(QLabel("Selecione uma pasta com arquivos Excel ou CSV"))
        self.btn = QPushButton("Escolher pasta")
        self.btn.setObjectName("Primary")
        self.btn.clicked.connect(self._pick_folder)
        card_layout.addWidget(self.btn)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        card_layout.addWidget(self.progress)
        self.status_label = QLabel("Arquivos importados: -")
        card_layout.addWidget(self.status_label)
        layout.addWidget(card)

        self.refresh_state()

    def refresh_state(self):
        ok = self.state.can_import_apontamentos()
        self.btn.setEnabled(ok)
        if not self.state.base_status.get("db_ok", False):
            msg = "Banco indisponivel"
        elif not self.state.base_status.get("equipamentos_ready", False):
            msg = "BD EQP ausente"
        else:
            msg = "Pronto para importar"
        self.req_label.setText(f"Pre-requisito: {msg}")

    def _pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar pasta")
        if not folder:
            return

        self.btn.setEnabled(False)
        self.progress.setValue(0)
        self.status_label.setText("Importacao em andamento...")

        worker = ImportFolderWorker(import_folder, folder)
        worker.progress.connect(self._on_progress)
        worker.finished.connect(self._on_finished)
        worker.failed.connect(self._on_failed)
        worker.start()
        self._worker = worker

    def _on_progress(self, current: int, total: int, message: str):
        if total > 0:
            pct = int((current / total) * 100)
            self.progress.setValue(pct)
        self.status_label.setText(message)

    def _on_finished(self, summary: dict):
        self.progress.setValue(100)
        if summary.get("total", 0) == 0:
            self.status_label.setText("Nenhum arquivo encontrado na pasta.")
            QMessageBox.information(self, "Importacao concluida", "Nenhum arquivo valido encontrado.")
        else:
            self.status_label.setText(
                f"Importados: {summary['importados']} | Duplicados: {summary['duplicados']} | Falhas: {summary['falhas']}"
            )
            QMessageBox.information(self, "Importacao concluida", "Processo finalizado.")
        self.state.refresh()
        self.refresh_state()

    def _on_failed(self, message: str):
        self.progress.setValue(0)
        self.status_label.setText("Falha na importacao")
        logger.error("Falha na importacao por pasta: %s", message)
        QMessageBox.warning(self, "Falha", "Nao foi possivel concluir a importacao.")
        self.state.refresh()
        self.refresh_state()
