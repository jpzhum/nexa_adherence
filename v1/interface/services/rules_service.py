
import os
import pandas as pd

def resource_path(relative_path):
    base_dir = os.path.join(os.path.expanduser('~'), 'TransicaoPY_Dados')
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, relative_path)

REGRAS_FILE = resource_path('RegrasTurnos.xlsx')
if not os.path.exists(REGRAS_FILE):
    pd.DataFrame(columns=['Tipo','Nome','Turno','Escala']).to_excel(REGRAS_FILE, index=False)

def salvar_regra(tipo, nome, turno, escala):
    nova = pd.DataFrame([[tipo, nome, turno, escala]], columns=['Tipo','Nome','Turno','Escala'])
    df = pd.read_excel(REGRAS_FILE) if os.path.exists(REGRAS_FILE) else pd.DataFrame(columns=['Tipo','Nome','Turno','Escala'])
    df.columns = df.columns.str.strip().str.title()
    df = df[~((df['Tipo'].str.lower()==tipo.lower()) & (df['Nome'].str.lower()==nome.lower()))]
    df = pd.concat([df, nova], ignore_index=True)
    df.to_excel(REGRAS_FILE, index=False)

def listar_regras(tipo=None, nome=None, turno=None):
    if not os.path.exists(REGRAS_FILE):
        return pd.DataFrame(columns=['Tipo','Nome','Turno','Escala'])
    df = pd.read_excel(REGRAS_FILE)
    df.columns = df.columns.str.strip().str.title()
    if tipo: df = df[df['Tipo'].str.lower()==tipo.strip().lower()]
    if nome: df = df[df['Nome'].str.lower()==nome.strip().lower()]
    if turno: df = df[df['Turno'].str.upper()==turno.strip().upper()]
    return df.reset_index(drop=True)

def excluir_regra(tipo, nome):
    if not os.path.exists(REGRAS_FILE): return
    df = pd.read_excel(REGRAS_FILE)
    df.columns = df.columns.str.strip().str.title()
    df = df[~((df['Tipo'].str.lower()==tipo.lower()) & (df['Nome'].str.lower()==nome.lower()))]
    df.to_excel(REGRAS_FILE, index=False)

def exportar_regras(path):
    if os.path.exists(REGRAS_FILE):
        df = pd.read_excel(REGRAS_FILE)
        df.to_excel(path, index=False)

def buscar_regra(tipo, nome):
    if not os.path.exists(REGRAS_FILE): return None
    df = pd.read_excel(REGRAS_FILE)
    df.columns = df.columns.str.strip().str.title()
    r = df[(df['Tipo'].str.lower()==tipo.strip().lower()) & (df['Nome'].str.lower()==nome.strip().lower())]
    return None if r.empty else r.iloc[0].to_dict()

def aplicar_regras(df_base, feriados):
    if 'Escala' not in df_base.columns:
        df_base['Escala'] = None
    if 'Agrup Equipamento' not in df_base.columns:
        df_base['Agrup Equipamento'] = ''
    df_base['Equipamento'] = df_base['Equipamento'].astype(str).str.strip().str.lower()
    df_base['Agrup Equipamento'] = df_base['Agrup Equipamento'].astype(str).str.strip().str.lower()
    if not pd.api.types.is_datetime64_any_dtype(df_base['Data Cabeçalho']):
        df_base['Data Cabeçalho'] = pd.to_datetime(df_base['Data Cabeçalho'], errors='coerce')
    # Se não existir arquivo de regras, padrão
    if not os.path.exists(REGRAS_FILE):
        df_base['Escala'] = 'PADRÃO'; return df_base
    regras = pd.read_excel(REGRAS_FILE)
    regras.columns = regras.columns.str.strip().str.title()
    if 'Tipo' not in regras.columns: regras['Tipo'] = 'Frota'
    if 'Frota' in regras.columns: regras.rename(columns={'Frota':'Nome'}, inplace=True)
    regras['Nome'] = regras['Nome'].astype(str).str.strip().str.lower()
    regras['Turno'] = regras['Turno'].astype(str).str.strip().str.upper()
    regras['Escala'] = regras['Escala'].astype(str).str.strip().str.upper()
    rg_agr = regras[regras['Tipo'].str.lower()=='agrupamento'].set_index('Nome')[['Turno','Escala']].to_dict('index')
    df_base['Escala'] = df_base.apply(lambda r: rg_agr.get(r['Agrup Equipamento'], {}).get('Escala', r['Escala']), axis=1)
    rg_fro = regras[regras['Tipo'].str.lower()=='frota'].set_index('Nome')[['Turno','Escala']].to_dict('index')
    df_base['Escala'] = df_base.apply(lambda r: rg_fro.get(r['Equipamento'], {}).get('Escala', r['Escala']), axis=1)
    mask_adm = df_base['Escala'] == 'ADM'
    for t in ['TURNO B','TURNO C']:
        if t in df_base.columns:
            df_base.loc[mask_adm, t] = '-'
    is_weekend = df_base['Data Cabeçalho'].dt.weekday >= 5
    is_feriado = df_base['Data Cabeçalho'].isin(feriados)
    remover = df_base[mask_adm & (is_weekend | is_feriado)].index
    if len(remover)>0:
        df_base = df_base.drop(remover)
    df_base['Escala'] = df_base['Escala'].fillna('PADRÃO')
    # Volta para maiúsculas originais
    df_base['Equipamento'] = df_base['Equipamento'].astype(str).str.upper()
    df_base['Agrup Equipamento'] = df_base['Agrup Equipamento'].astype(str)
    return df_base
