
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QTableView
from PyQt5.QtCore import Qt, QAbstractTableModel
import pandas as pd

class HomePage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        lay = QVBoxLayout(self)
        t = QLabel('Painel Principal'); t.setObjectName('HeaderTitle')
        s = QLabel('Resumo rápido + prévia da base consolidada'); s.setObjectName('HeaderSubtitle')
        lay.addWidget(t); lay.addWidget(s)

        # KPIs simples
        card = QFrame(); card.setObjectName('Card')
        lay.addWidget(card)
        kpi = QLabel(); kpi.setText(self._kpi_text()); kpi.setWordWrap(True)
        lay.addWidget(kpi)

        # Tabela preview
        self.view = QTableView(); lay.addWidget(self.view)
        self._load_table()

    def _kpi_text(self):
        df = getattr(self.controller, 'final_df', None)
        if df is None or len(df)==0:
            return 'Consolide para ver KPIs — Aderência Média Global, Entregues e Faltantes.'
        try:
            ader = round(df['% Aderência'].mean(),2)
            ent = int(df['Entregues'].sum())
            fal = int(df['Faltantes'].sum())
            return f"Aderência Média: {ader}% | Entregues: {ent} | Faltantes: {fal}"
        except Exception:
            return 'KPIs indisponíveis (colunas ausentes).'

    def _load_table(self):
        df = getattr(self.controller, 'final_df', None)
        if df is None or len(df)==0:
            # Tabela vazia com mensagem
            data = pd.DataFrame({'Dica':['Importe e Consolide para ver a prévia aqui.']})
        else:
            data = df.copy()
            cols = ['Data Cabeçalho','Equipamento','Agrup Equipamento','Gestor','TURNO A','TURNO B','TURNO C','Entregues','Faltantes','% Aderência','Status']
            data = data[[c for c in cols if c in data.columns]].head(25)
        self.view.setModel(PandasTableModel(data))
        self.view.resizeColumnsToContents()

class PandasTableModel(QAbstractTableModel):
    def __init__(self, df, parent=None):
        super().__init__(parent)
        self.df = df
    def rowCount(self, parent=None):
        return len(self.df)
    def columnCount(self, parent=None):
        return len(self.df.columns)
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return None
        if role==Qt.DisplayRole:
            val = self.df.iat[index.row(), index.column()]
            return '' if pd.isna(val) else str(val)
        return None
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role!=Qt.DisplayRole: return None
        if orientation==1: return self.df.columns[section]
        return section+1
