
import os
import pandas as pd
from interface.services.config_service import get_config

DATA_DIR_WINDOWS = r"C:\Sistema de Análise 2.0\TransicaoPY_Dados"

def base_dir_dados():
    cfg = get_config()
    env = os.environ.get('TRANSICAO_PY_DIR')
    if cfg.get('data_dir') and os.path.isdir(cfg['data_dir']):
        return cfg['data_dir']
    if env and os.path.isdir(env):
        return env
    if os.name == 'nt':
        if os.path.isdir(DATA_DIR_WINDOWS):
            return DATA_DIR_WINDOWS
        return os.path.join(os.path.expanduser('~'), 'TransicaoPY_Dados')
    return os.path.join(os.path.expanduser('~'), 'TransicaoPY_Dados')

def resource_path(relative_path):
    base = base_dir_dados()
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, relative_path)

def carregar_dados_arquivo(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError('Arquivo não encontrado: ' + file_path)
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip().str.title()
    return df

def carregar_equipamentos(path=None):
    path = path or resource_path('BD EQP.xlsx')
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip().str.title()
    if 'Equipamento Ativo' in df.columns:
        df.rename(columns={'Equipamento Ativo':'Equipamento'}, inplace=True)
    for col, default in [('Equipamento','Não Informado'), ('Dsc Classe','Não Informado'), ('Agrup Equipamento','Não Informado')]:
        if col not in df.columns: df[col] = default
    return df

def carregar_supervisores(path=None):
    path = path or resource_path('BD SUPERVISOR.xlsx')
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip().str.title()
    if 'Agrupamento' in df.columns:
        df.rename(columns={'Agrupamento':'Agrup Equipamento'}, inplace=True)
    for col, default in [('Agrup Equipamento','Não Informado'), ('Gestor','Não Informado')]:
        if col not in df.columns: df[col] = default
    return df
