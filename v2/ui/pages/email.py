from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QMessageBox,
    QFileDialog,
)

from v2.services.email_service import export_package, has_outlook, preparar_arquivos, enviar_email
from v2.services.recipients_service import load_recipients
from v2.services.result_store import result_store


class EmailPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("[M] E-mail")
        header.setObjectName("HeaderTitle")
        layout.addWidget(header)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)

        self.info = QLabel("Envio via Outlook com imagens inline")
        card_layout.addWidget(self.info)

        self.btn_prepare = QPushButton("Preparar (sem enviar)")
        self.btn_prepare.clicked.connect(self._prepare)
        card_layout.addWidget(self.btn_prepare)

        self.btn_send = QPushButton("Enviar")
        self.btn_send.setObjectName("Primary")
        self.btn_send.clicked.connect(self._send)
        card_layout.addWidget(self.btn_send)

        self.btn_export = QPushButton("Exportar pacote")
        self.btn_export.clicked.connect(self._export)
        card_layout.addWidget(self.btn_export)

        layout.addWidget(card)

        self._refresh_outlook()

    def _refresh_outlook(self):
        if not has_outlook():
            self.info.setText("Outlook nao encontrado. Use Exportar pacote.")
            self.btn_send.setEnabled(False)

    def _get_periodo(self) -> str:
        period = result_store.get_period()
        if not period:
            return "Periodo nao informado"
        di, df = period
        return f"{di:%d/%m/%Y} a {df:%d/%m/%Y}"

    def _get_final_df(self):
        final_df = result_store.get_result()
        if final_df is None:
            QMessageBox.warning(self, "Aviso", "Consolide os dados antes de enviar e-mail.")
            return None
        return final_df

    def _prepare(self):
        final_df = self._get_final_df()
        if final_df is None:
            return
        periodo = self._get_periodo()
        try:
            imagens, caminho_pdf = preparar_arquivos(final_df, gerar_pdf=False, periodo=periodo)
            detalhes = ", ".join(imagens.keys()) if imagens else "nenhum"
            if caminho_pdf:
                detalhes = f"{detalhes} | PDF: {caminho_pdf}"
            QMessageBox.information(self, "Sucesso", f"Imagens preparadas: {detalhes}")
        except Exception as exc:
            QMessageBox.warning(self, "Falha", f"Nao foi possivel preparar os arquivos: {exc}")

    def _send(self):
        final_df = self._get_final_df()
        if final_df is None:
            return
        periodo = self._get_periodo()
        try:
            imagens, caminho_pdf = preparar_arquivos(final_df, gerar_pdf=False, periodo=periodo)
            dest, cc = load_recipients()
            assunto = f"Relatorio de Aderencia - {periodo}"
            enviar_email(destinatarios=dest, cc=cc, assunto=assunto, imagens_inline=imagens, caminho_pdf=caminho_pdf)
            QMessageBox.information(self, "Sucesso", "E-mail enviado (ver Outlook).")
        except Exception as exc:
            QMessageBox.warning(
                self,
                "Aviso",
                f"Falha ao enviar via Outlook: {exc}\nUse Exportar pacote.",
            )

    def _export(self):
        final_df = self._get_final_df()
        if final_df is None:
            return
        output_dir = QFileDialog.getExistingDirectory(self, "Selecionar pasta")
        if not output_dir:
            return
        periodo = self._get_periodo()
        try:
            paths = export_package(final_df, output_dir, gerar_pdf=False, periodo=periodo)
            QMessageBox.information(
                self, "Sucesso", f"Pacote exportado em: {output_dir}\nHTML: {paths.get('html')}"
            )
        except Exception as exc:
            QMessageBox.warning(self, "Falha", f"Nao foi possivel exportar o pacote: {exc}")
