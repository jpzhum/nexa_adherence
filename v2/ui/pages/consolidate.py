from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QHBoxLayout,
    QDateEdit,
    QMessageBox,
    QProgressBar,
)

from v2.services.system_state import SystemStateService
from v2.services.consolidation_service import consolidate_period
from v2.services.result_store import result_store
from v2.ui.workers import ConsolidateWorker
from v2.utils.logging import get_logger

logger = get_logger(__name__)


class ConsolidatePage(QWidget):
    def __init__(self, state: SystemStateService, on_consolidated=None):
        super().__init__()
        self.state = state
        self.on_consolidated = on_consolidated
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("[C] Consolidacao")
        header.setObjectName("HeaderTitle")
        layout.addWidget(header)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        self.req_label = QLabel("Pre-requisitos: bases validas")
        card_layout.addWidget(self.req_label)

        dates = QHBoxLayout()
        self.di = QDateEdit()
        self.di.setCalendarPopup(True)
        self.di.setDisplayFormat("dd/MM/yyyy")
        self.df = QDateEdit()
        self.df.setCalendarPopup(True)
        self.df.setDisplayFormat("dd/MM/yyyy")
        self.di.setDate(QDate.currentDate().addDays(-15))
        self.df.setDate(QDate.currentDate())
        dates.addWidget(QLabel("Data inicial"))
        dates.addWidget(self.di)
        dates.addWidget(QLabel("Data final"))
        dates.addWidget(self.df)
        card_layout.addLayout(dates)

        self.btn = QPushButton("Consolidar dados")
        self.btn.setObjectName("Primary")
        self.btn.clicked.connect(self._start)
        card_layout.addWidget(self.btn)

        self.progress = QProgressBar()
        self.progress.setRange(0, 4)
        self.progress.setValue(0)
        card_layout.addWidget(self.progress)
        self.status_label = QLabel("[i] Aguardando consolidacao")
        card_layout.addWidget(self.status_label)
        layout.addWidget(card)

        self.refresh_state()

    def refresh_state(self):
        ok = self.state.can_consolidate()
        self.btn.setEnabled(ok)
        if not self.state.base_status.get("db_ok", False):
            msg = "Banco indisponivel"
        elif not self.state.base_status.get("equipamentos_ready", False):
            msg = "BD EQP ausente"
        elif not self.state.base_status.get("supervisores_ready", False):
            msg = "BD Supervisor ausente"
        elif not self.state.base_status.get("imports_ready", False):
            msg = "Apontamentos ausentes"
        else:
            msg = "Pronto para consolidar"
        self.req_label.setText(f"Pre-requisitos: {msg}")

    def _start(self):
        if self.di.date() > self.df.date():
            QMessageBox.warning(self, "Datas invalidas", "A data inicial nao pode ser maior que a final.")
            return
        self.btn.setEnabled(False)
        self.progress.setValue(0)
        self.status_label.setText("Consolidando...")

        di = self.di.date().toPyDate()
        df = self.df.date().toPyDate()
        self._last_period = (di, df)

        worker = ConsolidateWorker(consolidate_period, di, df)
        worker.progress.connect(self._on_progress)
        worker.finished.connect(self._on_finished)
        worker.failed.connect(self._on_failed)
        worker.start()
        self._worker = worker

    def _on_progress(self, step: int, message: str):
        self.progress.setValue(step)
        self.status_label.setText(message)

    def _on_finished(self, final_df, resumos: dict):
        result_store.set_result(final_df, resumos)
        if hasattr(self, "_last_period"):
            result_store.set_period(*self._last_period)
        if callable(self.on_consolidated):
            self.on_consolidated()
        self.progress.setValue(4)
        self.status_label.setText("Consolidacao concluida")
        QMessageBox.information(self, "Consolidacao concluida", "Dados consolidados com sucesso.")
        self.state.refresh()
        self.refresh_state()

    def _on_failed(self, message: str):
        self.progress.setValue(0)
        self.status_label.setText("Falha na consolidacao")
        logger.error("Falha na consolidacao: %s", message)
        QMessageBox.warning(self, "Falha", "Nao foi possivel consolidar os dados.")
        self.state.refresh()
        self.refresh_state()
