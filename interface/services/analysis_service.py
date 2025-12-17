
import pandas as pd
from interface.services.rules_service import aplicar_regras

def criar_base_completa(df_equipamentos, data_inicio, data_fim):
    if 'Equipamento' not in df_equipamentos.columns:
        raise ValueError("Coluna 'Equipamento' ausente.")
    df_equipamentos['Equipamento'] = df_equipamentos['Equipamento'].astype(str).str.strip()
    frotas = df_equipamentos['Equipamento'].dropna().unique()
    datas = pd.date_range(data_inicio, data_fim)
    return pd.MultiIndex.from_product([datas, frotas], names=['Data Cabeçalho','Equipamento']).to_frame(index=False)

def normalizar_turnos(df):
    if 'Desc.Turno' not in df.columns or 'Data Cabeçalho' not in df.columns:
        raise ValueError('Colunas obrigatórias ausentes: Desc.Turno ou Data Cabeçalho')
    df['Desc.Turno'] = df['Desc.Turno'].astype(str).str.upper().str.strip()
    df['Desc.Turno'] = df['Desc.Turno'].replace({'TURNO ADM':'TURNO A', 'CATAÇÃO':'TURNO A'})
    df['Data Cabeçalho'] = pd.to_datetime(df['Data Cabeçalho'], dayfirst=True, errors='coerce')
    if 'Equipamento' in df.columns:
        df['Equipamento'] = df['Equipamento'].astype(str).str.strip()
    return df

def pivotar_turnos(df, base_completa):
    df['Data Cabeçalho'] = pd.to_datetime(df['Data Cabeçalho'], errors='coerce')
    base_completa['Data Cabeçalho'] = pd.to_datetime(base_completa['Data Cabeçalho'], errors='coerce')
    df['Equipamento'] = df['Equipamento'].astype(str).str.strip()
    base_completa['Equipamento'] = base_completa['Equipamento'].astype(str).str.strip()
    pivot_df = pd.crosstab(index=[df['Data Cabeçalho'], df['Equipamento']], columns=df['Desc.Turno'])
    pivot_df = pivot_df.apply(lambda col: col.map(lambda x: 'OK' if x>0 else '-'))
    pivot_df = pivot_df.reset_index()
    return base_completa.merge(pivot_df, on=['Data Cabeçalho','Equipamento'], how='left').fillna('-')

def aplicar_exclusoes(df_base, exclusions_agrup, exclusions_frota):
    if exclusions_agrup:
        df_base = df_base[~df_base['Agrup Equipamento'].astype(str).str.strip().isin([e.strip() for e in exclusions_agrup])]
    if exclusions_frota:
        df_base = df_base[~df_base['Equipamento'].astype(str).str.strip().isin([e.strip() for e in exclusions_frota])]
    return df_base

def calcular_metricas(df):
    turnos = ['TURNO A','TURNO B','TURNO C']
    for t in turnos:
        if t not in df.columns: df[t] = '-'
    if 'Escala' not in df.columns:
        df['Escala'] = 'PADRÃO'
    df['Escala'] = df['Escala'].astype(str).str.strip().str.upper()
    def entregues(row):
        if row['Escala']=='ADM':
            return 1 if row['TURNO A']=='OK' else 0
        return sum(1 for t in turnos if row[t]=='OK')
    df['Entregues'] = df.apply(entregues, axis=1)
    df['Faltantes'] = df.apply(lambda r: (1 if r['Escala']=='ADM' else len(turnos)) - r['Entregues'], axis=1)
    df['% Aderência'] = df.apply(lambda r: round((r['Entregues']/(1 if r['Escala']=='ADM' else len(turnos)))*100,2), axis=1)
    df['Status'] = df.apply(lambda r: 'Completo' if r['Entregues']==(1 if r['Escala']=='ADM' else 3) else ('Ausente' if r['Entregues']==0 else 'Incompleto'), axis=1)
    return df

def criar_resumos_completos(df):
    if 'Gestor' not in df.columns: df['Gestor'] = 'Não Informado'
    if 'Agrup Equipamento' not in df.columns: df['Agrup Equipamento'] = 'Não Informado'
    resumo_status = df.groupby(['Gestor','Agrup Equipamento','Status']).size().unstack(fill_value=0)
    resumo_aderencia_agrup = df.groupby(['Gestor','Agrup Equipamento'])['% Aderência'].mean().round(2)
    indicadores = pd.DataFrame({
        'Aderência Média Global':[df['% Aderência'].mean().round(2)],
        'Total Esperado':[sum(1 if r.get('Escala')=='ADM' else 3 for _, r in df.iterrows())],
        'Total Entregue':[df['Entregues'].sum()]
    })
    return {'Resumo Status':resumo_status, 'Aderência Agrupamento':resumo_aderencia_agrup, 'Indicadores Gerais':indicadores}

def consolidar(df_equipamentos, df_supervisores, df_turnos, di, df, feriados, exclusions_agrup=None, exclusions_frota=None):
    base = criar_base_completa(df_equipamentos, di, df)
    cons = pivotar_turnos(df_turnos, base)
    cons = cons.merge(df_equipamentos[['Equipamento','Agrup Equipamento']], on='Equipamento', how='left')
    cons = cons.merge(df_supervisores[['Agrup Equipamento','Gestor']], on='Agrup Equipamento', how='left')
    cons['Agrup Equipamento'] = cons['Agrup Equipamento'].fillna('Não Informado')
    cons['Gestor'] = cons['Gestor'].fillna('Não Informado')
    cons = aplicar_regras(cons, feriados)
    cons = aplicar_exclusoes(cons, exclusions_agrup or [], exclusions_frota or [])
    final = calcular_metricas(cons)
    resumos = criar_resumos_completos(final)
    return final, resumos


