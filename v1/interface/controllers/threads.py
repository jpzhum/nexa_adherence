
from PyQt5.QtCore import QThread, pyqtSignal
from interface.services.data_service import carregar_dados_arquivo, carregar_equipamentos, carregar_supervisores
from interface.services.analysis_service import normalizar_turnos, consolidar

class ConsolidarThread(QThread):
    progresso = pyqtSignal(int, str)
    concluido = pyqtSignal(object, dict)
    erro = pyqtSignal(str)
    def __init__(self, data_inicio, data_fim, caminho_dados, excl_agr, excl_fro):
        super().__init__()
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.caminho_dados = caminho_dados
        self.excl_agr = excl_agr
        self.excl_fro = excl_fro
    def run(self):
        try:
            self.progresso.emit(0, 'Carregando dados...')
            dados_df = carregar_dados_arquivo(self.caminho_dados)
            self.progresso.emit(1, 'Carregando equipamentos...')
            eqp_df = carregar_equipamentos()
            self.progresso.emit(2, 'Carregando supervisores...')
            sup_df = carregar_supervisores()
            self.progresso.emit(3, 'Normalizando turnos...')
            dados_df = normalizar_turnos(dados_df)
            self.progresso.emit(4, 'Consolidando dados...')
            feriados = []
            final_df, resumos = consolidar(eqp_df, sup_df, dados_df, self.data_inicio, self.data_fim, feriados, self.excl_agr, self.excl_fro)
            self.progresso.emit(5, 'Finalizando...')
            self.concluido.emit(final_df, resumos)
        except Exception as e:
            self.erro.emit(str(e))
