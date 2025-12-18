
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QListWidget

class SettingsPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel('Configurações'))
        # Diretório de dados
        self.data_dir = QLineEdit(); self.data_dir.setPlaceholderText('Diretório de dados (opcional)')
        lay.addWidget(self.data_dir)
        btn_dir = QPushButton('Salvar Diretório'); btn_dir.clicked.connect(self._save_dir)
        lay.addWidget(btn_dir)

        # Exclusões
        lay.addWidget(QLabel('Excluir Agrupamentos e Frotas (será aplicado na consolidação)'))
        hl = QHBoxLayout(); lay.addLayout(hl)
        self.lista_agrup = QListWidget(); self.lista_frota = QListWidget()
        hl.addWidget(self.lista_agrup); hl.addWidget(self.lista_frota)
        b_load = QPushButton('Carregar opções (BD EQP/BD SUPERVISOR)'); b_load.clicked.connect(self._load_options)
        lay.addWidget(b_load)
        b_add_agr = QPushButton('Adicionar Agrupamento Selecionado'); b_add_agr.clicked.connect(lambda: self._add_exclusion('agrup'))
        b_add_fro = QPushButton('Adicionar Frota Selecionada'); b_add_fro.clicked.connect(lambda: self._add_exclusion('frota'))
        lay.addWidget(b_add_agr); lay.addWidget(b_add_fro)
        b_clear = QPushButton('Limpar Exclusões'); b_clear.clicked.connect(self._clear_exclusions)
        lay.addWidget(b_clear)
        b_save = QPushButton('Salvar Exclusões'); b_save.setObjectName('Primary'); b_save.clicked.connect(self._save_exclusions)
        lay.addWidget(b_save)

        self._refresh()

    def _save_dir(self):
        from interface.services.config_service import update_data_dir
        ok = update_data_dir(self.data_dir.text().strip())
        QMessageBox.information(self, 'Configurações', 'Diretório atualizado' if ok else 'Diretório inválido ou não encontrado')

    def _refresh(self):
        from interface.services.config_service import get_config
        cfg = get_config()
        self.data_dir.setText(cfg.get('data_dir',''))
        # Mostrar exclusões atuais
        excl_agr = cfg.get('exclusions_agrup', [])
        excl_fro = cfg.get('exclusions_frota', [])
        self.lista_agrup.clear(); self.lista_frota.clear()
        for e in excl_agr: self.lista_agrup.addItem(e)
        for e in excl_fro: self.lista_frota.addItem(e)

    def _load_options(self):
        from interface.services.data_service import carregar_equipamentos, carregar_supervisores
        try:
            sup = carregar_supervisores()
            eqp = carregar_equipamentos()
            # Preenche listas com opções disponíveis (sem duplicar)
            a_set = set(self._list_items(self.lista_agrup))
            f_set = set(self._list_items(self.lista_frota))
            for a in sorted(set(sup['Agrup Equipamento'].astype(str).str.strip().unique())):
                if a and a not in a_set: self.lista_agrup.addItem(a)
            for f in sorted(set(eqp['Equipamento'].astype(str).str.strip().unique())):
                if f and f not in f_set: self.lista_frota.addItem(f)
        except Exception as e:
            QMessageBox.critical(self, 'Erro', 'Falha ao carregar opções: ' + str(e))

    def _list_items(self, lw):
        return [lw.item(i).text() for i in range(lw.count())]

    def _add_exclusion(self, tipo):
        from PyQt5.QtWidgets import QInputDialog
        txt, ok = QInputDialog.getText(self, 'Adicionar ' + ('Agrupamento' if tipo=='agrup' else 'Frota'), 'Nome:')
        if ok and txt.strip():
            if tipo=='agrup': self.lista_agrup.addItem(txt.strip())
            else: self.lista_frota.addItem(txt.strip())

    def _clear_exclusions(self):
        self.lista_agrup.clear(); self.lista_frota.clear()

    def _save_exclusions(self):
        from interface.services.config_service import update_exclusions
        excl_agr = self._list_items(self.lista_agrup)
        excl_fro = self._list_items(self.lista_frota)
        update_exclusions(excl_agr, excl_fro)
        QMessageBox.information(self, 'Sucesso', 'Exclusões salvas. Elas serão aplicadas na próxima consolidação.')
