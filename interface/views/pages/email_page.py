
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox

class EmailPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel('E-mail'))
        prep = QPushButton('Preparar (sem enviar)'); prep.clicked.connect(self._prep)
        send = QPushButton('Enviar'); send.clicked.connect(self._send)
        lay.addWidget(prep); lay.addWidget(send)
    def _prep(self):
        if self.controller.final_df is None:
            QMessageBox.warning(self, 'Aviso', 'Consolide os dados antes de preparar e-mail.')
            return
        from interface.services.email_service import preparar_arquivos
        imgs = preparar_arquivos(self.controller.final_df)
        QMessageBox.information(self, 'Sucesso', 'Imagens preparadas: ' + ", ".join(imgs.keys()))

# interface/views/pages/email_page.py (trecho)

    def _send(self):
        if self.controller.final_df is None:
            QMessageBox.warning(self, 'Aviso', 'Consolide os dados antes de enviar e-mail.')
            return

        from interface.services.email_service import enviar_email, preparar_arquivos
        from interface.services.recipients_service import carregar_destinatarios

        di_q, df_q = self.controller.window.pages['cons'].get_periodo()
        periodo = f"{di_q.toString('dd/MM/yyyy')} a {df_q.toString('dd/MM/yyyy')}"

        # ✅ Desempacotar corretamente
        imagens_inline, caminho_pdf = preparar_arquivos(self.controller.final_df, gerar_pdf=False, periodo=periodo)

        dest, cc = carregar_destinatarios()
        assunto = f"Relatório de Aderência - {periodo}"

        # ✅ Passar como argumentos nomeados
        enviar_email(
            destinatarios=dest,
            cc=cc,
            assunto=assunto,
            imagens_inline=imagens_inline,
            caminho_pdf=caminho_pdf,
            enviar=True
    )

        QMessageBox.information(self, 'Sucesso', 'E-mail enviado (ver Outlook).')
