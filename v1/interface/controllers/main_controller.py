
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PyQt5.QtCore import Qt
import os
import pandas as pd
from interface.controllers.threads import ConsolidarThread
from interface.services.config_service import get_config

# >>> Importa o novo serviço de exportação para o “BD Excel”
from interface.services.exportbi_service import atualizar_bd_excel  # <<< novo

class MainController:
    def __init__(self, window):
        self.window = window
        self.caminho_dados = None
        self.final_df = None
        self.resumos = None
        # Config inicial
        self.config = get_config()

    def importar_dados(self):
        path, _ = QFileDialog.getOpenFileName(self.window, 'Importar Base de Dados', '', 'Excel (*.xlsx *.xls)')
        if not path:
            self.window.atualizar_status('Importação cancelada', 'warn'); return
        self.caminho_dados = path
        try:
            self.window.pages['import'].set_import_path(path)
        except Exception:
            pass
        QMessageBox.information(self.window, 'Importado', 'Arquivo selecionado:' + path)
        self.window.atualizar_status('Base importada: ' + os.path.basename(path), 'info')

    def consolidar_dados(self):
        if not self.caminho_dados:
            QMessageBox.warning(self.window, 'Aviso', 'Importe a base de dados antes de consolidar.')
            return
        di_q, df_q = self.window.pages['cons'].get_periodo()
        di = pd.to_datetime(di_q.toString('dd/MM/yyyy'), dayfirst=True)
        df = pd.to_datetime(df_q.toString('dd/MM/yyyy'), dayfirst=True)

        # >>> Corrigir operador; evitar &gt; que veio de HTML
        if di > df:
            QMessageBox.warning(self.window, 'Aviso', 'Data inicial não pode ser maior que a final.')
            return

        progress = QProgressDialog('Consolidando dados...', 'Cancelar', 0, 6, self.window)
        progress.setWindowModality(Qt.WindowModal); progress.setMinimumDuration(0); progress.setValue(0)
        # Lê exclusões
        cfg = get_config()
        excl_agr = cfg.get('exclusions_agrup', [])
        excl_fro = cfg.get('exclusions_frota', [])
        self.thread = ConsolidarThread(di, df, self.caminho_dados, excl_agr, excl_fro)
        self.thread.progresso.connect(lambda v,t: (progress.setValue(v), progress.setLabelText(t)))
        self.thread.concluido.connect(lambda df_final, res: self._concluido(df_final, res, progress))
        self.thread.erro.connect(lambda msg: QMessageBox.critical(self.window, 'Erro', 'Falha na consolidação: ' + msg))
        self.thread.start()

    def _concluido(self, final_df, resumos, progress):
        try: progress.close()
        except: pass
        self.final_df = final_df; self.resumos = resumos
        QMessageBox.information(self.window, 'Sucesso', 'Dados consolidados com sucesso!')

        # Carregar páginas (se aplicável)
        try:
            self.window.pages['indic'].load()
            self.window.pages['dash'].load()
        except Exception:
            pass

        self.window.atualizar_status('Dados consolidados com sucesso', 'info')

        # >>> NOVO: Atualiza automaticamente o “bd BI.xlsx” com as 4 abas
        try:
            export_dir = self.config.get('powerbi_export_dir') or os.path.expanduser("~/Documents/NexaPowerBI")
            export_file = self.config.get('powerbi_export_file') or "bd BI.xlsx"

            caminho_bd = atualizar_bd_excel(self.final_df, self.resumos, out_dir=export_dir, filename=export_file)
            # Mensagem amigável + status
            QMessageBox.information(self.window, 'BD Power BI',
                                    f'Banco Excel atualizado com sucesso!\n\nArquivo:\n{caminho_bd}')
            self.window.atualizar_status(f'BD Excel atualizado: {caminho_bd}', 'info')
        except Exception as e:
            # Se o arquivo estiver aberto no Excel ou houver permissão, o serviço pode salvar em sufixo _alt
            self.window.atualizar_status(f'Falha ao atualizar BD Excel: {e}', 'warn')
            QMessageBox.warning(self.window, 'Aviso',
                                'Não foi possível atualizar o BD Excel.\n'
                                'Feche o arquivo se estiver aberto e tente novamente.\n\n'
                                f'Detalhes: {e}')

